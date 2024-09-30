from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2

import grpc
import json
from concurrent import futures
import random

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
        # Extract the info about the dataNode.
        ip = request.ip
        port = request.port
        capacity_MB = request.capacity_MB

        # Instance of the model
        data_node_info = DataNode(
            Ip=ip,
            Port=port,
            CapacityMB=capacity_MB,
            IsActive=True,
            Blocks=[])
        print('data:', data_node_info.model_dump())

        # Add the dataNode in the DB
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
        data_nodes = list(database.dataNodes.find())

        response = name_node_pb2.DataNodesResponse()
        for data_node in data_nodes:
            data_node_info = name_node_pb2.DataNodeInfo(
                id=str(
                    data_node['_id']), ip=str(
                    data_node['ip']), port=str(
                    data_node['port']), capacity_MB=data_node['storage'])
            response.nodes.append(data_node_info)
            # This break will be in this for while we realize how choose in
            # which datanodes we are going to save a file. For the same reason
            # I asked for the filename. In this way, we are going to add the
            # files just in the first data_node, then it will be different
            break

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
        data_nodes = list(database.dataNodes.find({'IsActive': True}))
        for data_node in data_nodes:
            try:
                channel = grpc.insecure_channel(f'{data_node["Ip"]}:{data_node["Port"]}')
                stub = data_node_pb2_grpc.DataNodeStub(channel)
                response = stub.Heartbeat(data_node_pb2.HeartbeatRequest())
                if response.status == 'Alive':
                    self.data_nodes_connections[data_node['_id']] = 0
                else:
                    self.data_nodes_connections[data_node['_id']] += 3
                if self.data_nodes_connections[data_node['_id']] >= 600:
                    database.dataNodes.update_one({'_id': data_node['_id']}, {'$set': {'IsActive': False}})
            except Exception:
                self.data_nodes_connections[data_node['_id']] += 3
                if self.data_nodes_connections[data_node['_id']] >= 600:
                    database.dataNodes.update_one({'_id': data_node['_id']}, {'$set': {'IsActive': False}})

    def RelocateBlocks(self, data_node_id):
        master_blocks = database.blocks.find({'Master': data_node_id})
        slave_blocks = database.blocks.find({'Slaves': data_node_id})

        for block in master_blocks:
            print(f'Moving block {block} from {data_node_id} to {block.Master}')
            database.blocks.update_one({'_id': block['_id']}, {'$set': {'Master': block.Master}})

        for block in slave_blocks:
            master = database.dataNodes.find_one({'_id': block.Master})

            new_master_id = self.RandomWeight(block.SizeMB, [data_node_id, block.Slaves[0], block.Slaves[1]])
            if new_master_id:
                new_node = database.dataNodes.find_one({'_id': new_master_id})
                channel = grpc.insecure_channel(f'{new_node["Ip"]}:{new_node["Port"]}')
                stub = data_node_pb2_grpc.DataNodeStub(channel)
                stub.AskForBlock(block['_id'], block.Slaves[0])

            database.blocks.update_one({'_id': block['_id']}, {'$set': {'Slaves': block.Slaves}})

def StartServer(ip: str, port: int):
    print('Server is running')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    name_node_pb2_grpc.add_NameNodeServiceServicer_to_server(
        Server(ip=ip, port=port), server)
    server.add_insecure_port(f'{ip}:{port}')
    server.start()
    server.wait_for_termination()
