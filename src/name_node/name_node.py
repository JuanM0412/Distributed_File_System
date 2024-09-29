from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
import grpc
import json
from concurrent import futures
import random
from src.models.datanode import DataNode
from src.models.namenode import Block, MetaData
from src.models.user import User
from bson import ObjectId
from config.db import database
from google.protobuf.json_format import MessageToDict, MessageToJson

class Server(name_node_pb2_grpc.NameNodeServiceServicer):
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

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
                    response.nodes.append(data_node_info)

                    if blocks_counter == 0:
                        master_node = data_node_info.id
                    else:
                        slaves.append(data_node_info.id)
                    blocks_counter += 1

                except KeyError as e:
                    print(f"Error creating DataNodeInfo: Missing key {e}")
        
        if selected_nodes:
            block = {
                'Master': master_node, 
                'Slaves': slaves
            }

            block_id = database.blocks.insert_one(block).inserted_id

            existing_metadata = database.metaData.find_one({'Name': request.file, 'Owner': request.username})

            if existing_metadata:
                database.metaData.update_one(
                    {'_id': existing_metadata['_id']},
                    {'$push': {'Blocks': block_id}}
                )
            else:
                metadata = MetaData(
                    Name=request.file, 
                    SizeMB=request.size,
                    Blocks=[str(block_id)],
                    Owner=request.username
                )
                database.metaData.insert_one(metadata.model_dump())
            response.block_id = str(block_id)
            
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
        print(f"File: {file}")
        print(f"Username: {username}")
                
        metadata_ = database.metaData.find({'Name': file, 'Owner': username})
        response = name_node_pb2.DataNodesDownloadResponse()  # Updated

        metadata_list = list(metadata_)

        for metadata in metadata_list:
            blocks_list = metadata['Blocks']
            print(f"Blocks list: {blocks_list}")

            i = 0
            for block_id in blocks_list:

                if isinstance(block_id, str):
                    block_id = ObjectId(block_id)

                block = database.blocks.find_one({'_id': block_id})
                if not block:
                    print(f"Block {block_id} not found")
                    continue
                
                blocks = []

                master_id = block['Master']
                master_node = database.dataNodes.find_one({'_id': ObjectId(master_id)})

                blocks.append(master_node)
                
                for slave_id in block['Slaves']:
                    slave_node = database.dataNodes.find_one({'_id': ObjectId(slave_id)})
                    blocks.append(slave_node)

                position = random.randint(0, len(blocks) - 1)
                id_selected_node = blocks[position]['_id']

                response.blocks[i] = str(id_selected_node)  # Updated
                i += 1

        print(f"Response: {len(response.blocks)}")
        return response
    
    def GetDataNodesForRemove(self, request, context):
        file = request.file
        username = request.username
        print(f"File: {file}")
        print(f"Username: {username}")
                
        metadata_ = database.metaData.find({'Name': file, 'Owner': username})
        response = name_node_pb2.DataNodesRemoveResponse()  

        metadata_list = list(metadata_)

        for metadata in metadata_list:
            blocks_list = metadata['Blocks']
            print(f"Blocks list: {blocks_list}")

            for block_id in blocks_list:

                if isinstance(block_id, str):
                    block_id = ObjectId(block_id)

                block = database.blocks.find_one({'_id': block_id})
                if not block:
                    print(f"Block {block_id} not found")
                    continue
                
                block_info = name_node_pb2.BlockInfo()

                master_id = block['Master']
                master_node = database.dataNodes.find_one({'_id': ObjectId(master_id)})

                # Convert master_node to gRPC message object
                master_node_info = name_node_pb2.DataNodeInfo(
                    id=str(master_node['_id']),
                    ip=master_node['Ip'],
                    port=master_node['Port'],
                    capacity_MB=master_node['CapacityMB']
                )
                block_info.nodes.append(master_node_info)
                
                for slave_id in block['Slaves']:
                    slave_node = database.dataNodes.find_one({'_id': ObjectId(slave_id)})
                    
                    # Convert slave_node to gRPC message object
                    slave_node_info = name_node_pb2.DataNodeInfo(
                        id=str(slave_node['_id']),
                        ip=slave_node['Ip'],
                        port=slave_node['Port'],
                        capacity_MB=slave_node['CapacityMB']
                    )
                    block_info.nodes.append(slave_node_info)

                response.blocks.append(block_info)

        print(f"Response: {len(response.blocks)}")
    
    
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


def StartServer(ip: str, port: int):
    print('Server is running')
    options = [
        ('grpc.max_send_message_length', 1024 * 1024 * 1024), 
        ('grpc.max_receive_message_length', 1024 * 1024 * 1024)  
    ]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
    name_node_pb2_grpc.add_NameNodeServiceServicer_to_server(
        Server(ip=ip, port=port), server)
    server.add_insecure_port(f'{ip}:{port}')
    server.start()
    server.wait_for_termination()
