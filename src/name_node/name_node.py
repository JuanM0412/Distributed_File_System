from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
import grpc
import threading
from concurrent import futures
import random
import time
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
        self.data_nodes_connections = {}

    def Register(self, request, context):
        ip = request.ip
        port = request.port
        capacity_MB = request.capacity_MB

        if database.dataNodes.find_one({'Ip': ip, 'Port': port}):
            database.dataNodes.update_one({'Ip': ip, 'Port': port}, {'$set': {'IsActive': True}})
            print(f'Data node {ip}:{port} was already registered')
            return name_node_pb2.RegisterResponse(id=str(database.dataNodes.find_one({'Ip': ip, 'Port': port})['_id']))

        data_node_info = DataNode(
            Ip=ip,
            Port=port,
            CapacityMB=capacity_MB,
            IsActive=True,
            Blocks=[])
        print('data:', data_node_info.model_dump())
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

        filename = request.file.replace('\\', '/').split('/')[-1]
        filename = "/" + filename
        if selected_nodes:
            block = {
                'Master': master_node,
                'Slaves': slaves
            }

            block_id = database.blocks.insert_one(block).inserted_id

            existing_metadata = database.metaData.find_one({'Name': filename, 'Owner': request.username})

            if existing_metadata:
                database.metaData.update_one(
                    {'_id': existing_metadata['_id']},
                    {'$push': {'Blocks': block_id}}
                )
            else:
                print("Filename in upload:", filename)
                metadata = MetaData(
                    Name=filename,
                    SizeMB=request.size,
                    Blocks=[str(block_id)],
                    Owner=request.username
                )
                database.metaData.insert_one(metadata.model_dump())
            response.block_id = str(block_id)

        return response

    def RandomWeight(self, chunk_size, excluded_nodes):
        data_nodes = list(database.dataNodes.find({'IsActive': True}))
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
        accumulative_probability = [sum(probability[:i + 1]) for i in range(len(probability))]
        random_ = random.uniform(0, 1)

        for i, prob in enumerate(accumulative_probability):
            if random_ <= prob:
                return values[i]

        return None

    def GetDataNodesForDownload(self, request, context):
        file = request.file
        file = file.split('/')[-1]
        file = "/" + file
        username = request.username
        print("File in download:", file)

        metadata_ = database.metaData.find({'Name': file, 'Owner': username})
        response = name_node_pb2.DataNodesDownloadResponse()

        metadata_list = list(metadata_)
        print("Metadata list:", metadata_list)

        for metadata in metadata_list:
            blocks_list = metadata['Blocks']

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

                response.blocks[i] = str(id_selected_node)
                i += 1

        print(f"Response: {len(response.blocks)}")
        return response

    def GetDataNodesForRemove(self, request, context):
        file = request.file
        file = file.split('/')[-1]
        file = "/" + file
        username = request.username

        metadata_ = database.metaData.find({'Name': file, 'Owner': username})
        response = name_node_pb2.DataNodesRemoveResponse()

        metadata_list = list(metadata_)

        for metadata in metadata_list:
            blocks_list = metadata['Blocks']

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

                master_node_info = name_node_pb2.DataNodeInfo(
                    id=str(master_node['_id']),
                    ip=master_node['Ip'],
                    port=master_node['Port'],
                    capacity_MB=master_node['CapacityMB']
                )
                block_info.nodes.append(master_node_info)

                for slave_id in block['Slaves']:
                    slave_node = database.dataNodes.find_one({'_id': ObjectId(slave_id)})

                    slave_node_info = name_node_pb2.DataNodeInfo(
                        id=str(slave_node['_id']),
                        ip=slave_node['Ip'],
                        port=slave_node['Port'],
                        capacity_MB=slave_node['CapacityMB']
                    )
                    block_info.nodes.append(slave_node_info)

                response.blocks.append(block_info)
                database.blocks.delete_one({'_id': block_id})

        print(f"Response: {len(response.blocks)}")

        database.metaData.delete_one({'Name': file, 'Owner': username})

        return response

    def AddUser(self, request, context):

        username = request.username
        password = request.password

        check_unique_name = database.users.find_one({'Username': username})
        if check_unique_name:
            return name_node_pb2.AddUserResponse(status='Name unavailable')

        user_info = User(Username=username, Password=password)

        database.users.insert_one(user_info.model_dump())
        return name_node_pb2.AddUserResponse(
            status='User created successfully')

    def ValidateUser(self, request, context):

        username = request.username
        password = request.password

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

            data_nodes = database.dataNodes.find({'IsActive': True})

            for data_node in data_nodes:
                if data_node['_id'] not in self.data_nodes_connections:
                    self.data_nodes_connections[data_node['_id']] = time.time()

                alive = False

                try:
                    with grpc.insecure_channel(f'{data_node["Ip"]}:{data_node["Port"]}') as channel:
                        stub = data_node_pb2_grpc.DataNodeStub(channel)
                        response = stub.Heartbeat(data_node_pb2.HeartbeatRequest())
                        alive = bool(response.alive)
                except Exception:
                    pass

                if alive:
                    self.data_nodes_connections[data_node['_id']] = time.time()
                else:
                    time_difference = time.time() - self.data_nodes_connections[data_node['_id']]
                    if time_difference >= 10:
                        print(f'Time difference: {time_difference}, Data node {data_node["_id"]} is dead')
                        database.dataNodes.update_one({'_id': data_node['_id']}, {'$set': {'IsActive': False}})
                        self.RelocateBlocks(str(data_node['_id']))
            
    def RelocateBlocks(self, data_node_id):

        try:
            master_blocks = list(database.blocks.find({'Master': data_node_id}))
            slave_blocks = list(database.blocks.find({'Slaves': data_node_id}))
            print(f'Master blocks: {master_blocks}')
            print(f'Slave blocks: {slave_blocks}')
        except Exception as e:
            print(f'Error fetching master or slave blocks: {e}')
            return

        for block in master_blocks:
            try:
                try:
                    block_metadata = dict(database.metaData.find_one({'Blocks': str(block['_id'])}))
                    block_id = str(block['_id'])
                    print(f'Block metadata (string ID): {block_metadata}')
                except:
                    block_metadata = dict(database.metaData.find_one({'Blocks': ObjectId(block['_id'])}))
                    block_id = str(block['_id'])
                    print(f'Block metadata (ObjectId): {block_metadata}')

                if not block_metadata:
                    print(f'Error: Block metadata not found for block {block_id}')
                    continue

                name, ext = block_metadata['Name'].rsplit('.', 1)
                block_index = block_metadata['Blocks'].index(block_id)
                block_file_name = f"{name[1:]}_block_{block_index}.{ext}"
                print(f'Block filename: {block_file_name}')
            except Exception as e:
                print(f'Error processing master block {block["_id"]}: {e}')
                continue

            try:
                excluded_nodes = [ObjectId(data_node_id), ObjectId(block['Slaves'][0]), ObjectId(block['Slaves'][1])]
                new_master_id = self.RandomWeight(128, excluded_nodes)
                new_master = dict(database.dataNodes.find_one({'_id': ObjectId(new_master_id)}))
                print(f'New master: {new_master}')
            except Exception as e:
                print(f'Error fetching new master for block {block["_id"]}: {e}')
                continue

            try:
                print(f'Moving block {block_file_name} to {new_master["Ip"]}:{new_master["Port"]}')
                channel = grpc.insecure_channel(f'{new_master["Ip"]}:{new_master["Port"]}')
                stub = data_node_pb2_grpc.DataNodeStub(channel)
                response = stub.AskForBlock(
                    data_node_pb2.AskForBlockRequest(
                        block_id=str(block['_id']),
                        node_id=str(block['Slaves'][0]),
                        filename=block_file_name
                    )
                )

                if response.status:
                    database.blocks.update_one({'_id': block['_id']}, {'$set': {'Master': new_master_id}})
                    print(f'Block {block_file_name} moved successfuly to {new_slave["Ip"]}:{new_slave["Port"]}')
                else:
                    print(f'Block {block["_id"]} not updated')
            except Exception as e:
                print(f'Error during gRPC call or block update for block {block["_id"]}: {e}')
                continue

        for block in slave_blocks:
            try:
                try:
                    block_metadata = dict(database.metaData.find_one({'Blocks': str(block['_id'])}))
                    block_id = str(block['_id'])
                    print(f'Block metadata (string ID): {block_metadata}')
                except:
                    block_metadata = dict(database.metaData.find_one({'Blocks': ObjectId(block['_id'])}))
                    block_id = str(block['_id'])
                    print(f'Block metadata (ObjectId): {block_metadata}')

                if not block_metadata:
                    print(f'Error: Block metadata not found for block {block_id}')
                    continue

                name, ext = block_metadata['Name'].rsplit('.', 1)
                try:
                    block_index = block_metadata['Blocks'].index(str(block_id))
                except:
                    block_index = block_metadata['Blocks'].index(ObjectId(block_id))
                block_file_name = f"{name[1:]}_block_{block_index}.{ext}"
                print(f'Block filename: {block_file_name}')
            except Exception as e:
                print(f'Error processing slave block {block["_id"]}: {e}')
                continue

            try:
                excluded_nodes = [ObjectId(data_node_id), ObjectId(block['Slaves'][0]), ObjectId(block['Slaves'][1])]
                new_slave_id = self.RandomWeight(128, excluded_nodes)
                new_slave = dict(database.dataNodes.find_one({'_id': ObjectId(new_slave_id)}))
                print(f'New slave: {new_slave}')
            except Exception as e:
                print(f'Error fetching new slave for block {block["_id"]}: {e}')
                continue

            try:
                print(f'Asking {new_slave["Ip"]}:{new_slave["Port"]} to get block {block_file_name} from {block["Master"]}')
                channel = grpc.insecure_channel(f'{new_slave["Ip"]}:{new_slave["Port"]}')
                stub = data_node_pb2_grpc.DataNodeStub(channel)
                response = stub.AskForBlock(
                    data_node_pb2.AskForBlockRequest(
                        block_id=str(block['_id']),
                        node_id=str(block['Master']),
                        filename=block_file_name
                    )
                )

                if response.status:
                    new_slaves = [str(slave) for slave in block['Slaves'] if slave != data_node_id] + [str(new_slave_id)]
                    database.blocks.update_one({'_id': block['_id']}, {'$set': {'Slaves': new_slaves}})
                    print(f'Block {block_file_name} moved successfuly to {new_slave["Ip"]}:{new_slave["Port"]}')
                else:
                    print(f'Block {block["_id"]} not updated')
            except Exception as e:
                print(f'Error during gRPC call or block update for slave block {block["_id"]}: {e}')
                continue



def StartServer(ip: str, port: int):
    print('Server is running')
    
    options = [
        ('grpc.max_send_message_length', 1024 * 1024 * 1024),
        ('grpc.max_receive_message_length', 1024 * 1024 * 1024)
    ]
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
    
    name_node = Server(ip=ip, port=port)
    
    name_node_pb2_grpc.add_NameNodeServiceServicer_to_server(name_node, server)
    
    server.add_insecure_port(f'{ip}:{port}')
    
    server.start()

    threading.Thread(target=name_node.CheckAliveDataNodes, daemon=True).start()

    server.wait_for_termination()
