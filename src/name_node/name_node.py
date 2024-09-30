from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2

import grpc
import json
from concurrent import futures
import random
import time

from src.models.datanode import DataNode
from src.models.namenode import Block, MetaData
from src.models.user import User

from config.db import database

class Server(name_node_pb2_grpc.NameNodeServiceServicer):
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.data_nodes_connections = {}

    def Register(self, request, context):
        ip = request.ip
        port = request.port
        capacity_MB = request.capacity_MB

        data_node_info = DataNode(
            Ip=ip,
            Port=port,
            CapacityMB=capacity_MB,
            IsActive=True,
            Blocks=[])
        print('data:', data_node_info.model_dump())

        print('After insert')
        data_node = database.dataNodes.insert_one(data_node_info.model_dump())
        print('data_node:', data_node.inserted_id)
        return name_node_pb2.RegisterResponse(id=str(data_node.inserted_id))

    def GetDataNodesForUpload(self, request, context):
        chunk_size = request.size
        response = name_node_pb2.DataNodesResponse()
        selected_nodes = set()

        while len(selected_nodes) < 3:
            selected_node = self.RandomWeight(chunk_size, selected_nodes) 
            if selected_node:
                selected_nodes.add(selected_node)
            else:
                break
        
        print(f"Selected nodes: {selected_nodes}")
        blocks = []
        blocks_counter = 0
        slaves = []
            
        for node_id in selected_nodes:
            data_node = database.dataNodes.find_one({'_id': node_id})

            if data_node:
                try:
                    data_node_info = name_node_pb2.DataNodeInfo(
                        id=str(data_node['_id']),
                        ip=data_node['Ip'],
                        port=data_node['Port'],
                        capacity_MB=data_node['CapacityMB']
                    )
                    print(f'Created DataNodeInfo: id={data_node_info.id}, ip={data_node_info.ip}, port={data_node_info.port}, capacity_MB={data_node_info.capacity_MB}')
                    response.nodes.append(data_node_info)

                    if blocks_counter == 0:
                        master_node = data_node_info.id
                    else:
                        slaves.append(data_node_info.id)
                    blocks_counter += 1

                except KeyError as e:
                    print(f"Error creating DataNodeInfo: Missing key {e}")
        
        if selected_nodes:
            block = Block(Master=master_node, Slaves=slaves)
            blocks.append(block)
        
            metadata = MetaData(
                Name=request.file, 
                SizeMB=request.size,
                Blocks=blocks,
                Owner=request.username
            )
            
            metadata = database.metaData.insert_one(metadata.model_dump())
            print(f'Metadata saved: {metadata}')
        
        return response
        
    def RandomWeight(self, chunk_size, excluded_nodes):
        data_nodes = list(database.dataNodes.find())
        filtered_data_nodes = []
        for data_node in data_nodes:
            if data_node.get('CapacityMB', 0) >= chunk_size and data_node['_id'] not in excluded_nodes:
                filtered_data_nodes.append(data_node)
    
        if not filtered_data_nodes:
            return None

        capacities = [data_node.get('CapacityMB', 0) for data_node in filtered_data_nodes]
        values = [data_node['_id'] for data_node in filtered_data_nodes]

        total_capacity = sum(capacities)
        probability = [c / total_capacity for c in capacities]
        accumulative_probability = [sum(probability[:i+1]) for i in range(len(probability))]
        random_ = random.uniform(0, 1)
        
        for i, prob in enumerate(accumulative_probability):
            if random_ <= prob:
                return values[i]

        return None

    def GetDataNodesForDownload(self, request, context):
        file = request.file
        username = request.username

        metadata = database.metaData.find_one({'Name': file, 'Owner': username})
        
        response = name_node_pb2.DataNodesResponse()
        
        if metadata:
            for block in metadata['Blocks']:
                master_node = database.dataNodes.find_one({'_id': block['Master']})
                if master_node:
                    data_node_info = name_node_pb2.DataNodeInfo(
                        id=str(master_node['_id']),
                        ip=master_node['Ip'],
                        port=master_node['Port'],
                        capacity_MB=master_node['CapacityMB']
                    )
                    response.nodes.append(data_node_info)
                
                for slave_id in block['Slaves']:
                    slave_node = database.dataNodes.find_one({'_id': slave_id})
                    if slave_node:
                        data_node_info = name_node_pb2.DataNodeInfo(
                            id=str(slave_node['_id']),
                            ip=slave_node['Ip'],
                            port=slave_node['Port'],
                            capacity_MB=slave_node['CapacityMB']
                        )
                        response.nodes.append(data_node_info)
        
        return response


    def AddUser(self, request, context):
        # Extract the info about the user.
        username = request.username
        password = request.password

        print('AddUser method')

        check_unique_name = database.users.find_one({'Username': username})
        if check_unique_name:
            return name_node_pb2.AddUserResponse(status='Name unavailable')

        # Instance of the model
        user_info = User(Username=username, Password=password)
        print('user:', user_info.model_dump())

        # Add the dataNode in the DB
        database.users.insert_one(user_info.model_dump())
        return name_node_pb2.AddUserResponse(
            status='User created successfully')

    def ValidateUser(self, request, context):
        # Extract the info about the user.
        username = request.username
        password = request.password

        # Validate that exist
        user = database.users.find_one(
            {'username': username, 'password': password})

        if user:
            return name_node_pb2.ValidateUserResponse(
                status='User logged successfully')
        else:
            return name_node_pb2.ValidateUserResponse(
                status='Invalid username or password')
        
    def CheckAliveDataNodes(self):
        while True:
            data_nodes = list(database.dataNodes.find({'IsActive': True}))
            print(f'Data nodes: {data_nodes}')
            input('Press Enter to continue...')
            for data_node in data_nodes:
                if data_node['_id'] not in self.data_nodes_connections:
                    self.data_nodes_connections[data_node['_id']] = 0
                try:
                    print(f'Checking data node: {data_node["Ip"]}:{data_node["Port"]}')
                    channel = grpc.insecure_channel(f'{data_node["Ip"]}:{data_node["Port"]}')
                    stub = data_node_pb2_grpc.DataNodeStub(channel)
                    print(f'Sending heartbeat to {data_node["Ip"]}:{data_node["Port"]}')
                    response = stub.Heartbeat(data_node_pb2.HeartbeatRequest())
                    print(f'Received response: {response.status}')
                    
                    if response.alive:
                        self.data_nodes_connections[data_node['_id']] = 0
                    else:
                        self.data_nodes_connections[data_node['_id']] += 3

                    if self.data_nodes_connections[data_node['_id']] >= 600:
                        result = database.dataNodes.update_one(
                            {'_id': data_node['_id']},
                            {'$set': {'IsActive': False}}
                        )
                        if result.modified_count == 1:
                            print(f'Data node {data_node["Ip"]}:{data_node["Port"]} marked as inactive')
                            self.RelocateBlocks(data_node['_id'])
                        else:
                            print(f'Failed to update IsActive for {data_node["Ip"]}:{data_node["Port"]}')
                except Exception as e:
                    print(f'Error checking data node: {e}')
                    self.data_nodes_connections[data_node['_id']] += 3

                    if self.data_nodes_connections[data_node['_id']] >= 600:            
                        result = database.dataNodes.update_one(
                            {'_id': data_node['_id']},
                            {'$set': {'IsActive': False}}
                        )
                        if result.modified_count == 1:
                            print(f'Data node {data_node["Ip"]}:{data_node["Port"]} marked as inactive due to errors')
                            self.RelocateBlocks(data_node['_id'])
                        else:
                            print(f'Failed to update IsActive for {data_node["Ip"]}:{data_node["Port"]}')
            
            print('\n' * 3)
            time.sleep(3)


    def RelocateBlocks(self, data_node_id):
        master_blocks = database.blocks.find({'Master': data_node_id})
        print(f'Master blocks: {master_blocks}')
        slave_blocks = database.blocks.find({'Slaves': data_node_id})
        print(f'Slave blocks: {slave_blocks}')

        for block in master_blocks:
            excluded_nodes = [data_node_id] + block.Slaves
            print(f'Excluded nodes: {excluded_nodes}')

            new_master_id = None
            while not new_master_id:
                new_master_id = self.RandomWeight(block.SizeMB, excluded_nodes)
            print(f'New master ID: {new_master_id}')

            new_master = database.dataNodes.find_one({'_id': new_master_id})
            channel = grpc.insecure_channel(f'{new_master["Ip"]}:{new_master["Port"]}')
            stub = data_node_pb2_grpc.DataNodeStub(channel)
            response = stub.AskForBlock(block['_id'], block.Slaves[0])
            print(f'Received response: {response.status}')

            database.blocks.update_one({'_id': block['_id']}, {'$set': {'Master': block.Master}})
            print(f'Block {block["_id"]} updated')

        for block in slave_blocks:
            excluded_nodes = [data_node_id] + block.Slaves
            print(f'Excluded nodes: {excluded_nodes}')

            new_slave_id = None
            while not new_slave_id:
                new_slave_id = self.RandomWeight(block.SizeMB, excluded_nodes)
            print(f'New slave ID: {new_slave_id}')

            new_slave = database.dataNodes.find_one({'_id': new_slave_id})
            channel = grpc.insecure_channel(f'{new_slave["Ip"]}:{new_slave["Port"]}')
            stub = data_node_pb2_grpc.DataNodeStub(channel)
            response = stub.AskForBlock(block['_id'], block.Master)
            print(f'Received response: {response.status}')

            new_slaves = block.Slaves.remove(data_node_id) + [new_slave_id]
            print(f'New slaves: {new_slaves}')

            database.blocks.update_one({'_id': block['_id']}, {'$set': {'Slaves': new_slaves}})
            print(f'Block {block["_id"]} updated')


def StartServer(ip: str, port: int):
    print('Server is running')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    name_node = Server(ip=ip, port=port)
    name_node_pb2_grpc.add_NameNodeServiceServicer_to_server(name_node, server)
    server.add_insecure_port(f'{ip}:{port}')
    server.start()
    # name_node.CheckAliveDataNodes()
    name_node.RelocateBlocks('66fa19128cb8fa64a6b198dc')
    server.wait_for_termination()
