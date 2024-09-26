from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
from utils.utils import GetFileSize, GetFileChunks, SaveChunksToFile
from src.client.manage_blocks import SplitFile
from config.db import database
from config import MB_IN_BYTES
import grpc, os
from src.file_manager.file_manager import FileManager
import random

class Client:
    def __init__(self, ip: str, port: int, server_ip: str, server_port: int):
        self.ip = ip
        self.port = port
        self.username = None

        self.users_collection = database.users

        self.file_manager = None

        print(f'Connecting to {server_ip}:{server_port}')

        options = [
            ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100 MB
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100 MB
        ]

        self.server_channel = grpc.insecure_channel(
            f'{server_ip}:{server_port}')
        self.server_stub = name_node_pb2_grpc.NameNodeServiceStub(
            self.server_channel)

    def GetDataNodesForUpload(self, filename: str, chunk_size: int, chunk_number: int):
        request = name_node_pb2.DataNodesUploadRequest(
            file=filename,
            size=chunk_size,
            username=self.username,
            chunk_number=chunk_number
        )

        response = self.server_stub.GetDataNodesForUpload(request)

        return response.nodes

    def GetDataNodesForDownload(self, filename: str):
        response = self.server_stub.GetDataNodesForDownload(
            name_node_pb2.DataNodesDownloadRequest(
                file=filename,
                username=self.username
            )
        )
        
        return response.nodes

    def GetDataNode(self, data_node):
        return data_node.ip, data_node.port

    def UploadFile(self, filename_: str):
        print(f'Uploading file {filename_}')
        file_size = int(GetFileSize(filename_))
        print(f'File size: {file_size}')
        
        blocks = list(SplitFile(filename_))
        total_blocks = len(blocks)
        
        print(f'Uploading file {filename_} of size {file_size} MB')
        print(f'Total blocks: {total_blocks}')

        options = [
            ('grpc.max_send_message_length', 200 * 1024 * 1024),  
            ('grpc.max_receive_message_length', 200 * 1024 * 1024),  
        ]
        
        for i, block in enumerate(blocks):
            print(f'Uploading block {i}')
            block_size_bytes = os.path.getsize(block)
            block_size_MB = block_size_bytes / MB_IN_BYTES
            print(f'Block size: {block_size_MB} MB')
            
            request = name_node_pb2.DataNodesUploadRequest(
                file=filename_,
                size=block_size_MB,
                username=self.username
            )

            user_ = self.username
            
            response = self.server_stub.GetDataNodesForUpload(request)
            
            print(f'Received response from server for block {i}')
            print(f'Number of data nodes available: {len(response.nodes)}')
            
            if not response.nodes:
                raise Exception(f"No available nodes to store block {i}")
            
            with open(block, 'rb') as f:
                block_data = f.read()
            
            block_chunk = data_node_pb2.BlockChunk(
                block_data=block_data,
                filename=filename_,
                block_number=i,
                total_blocks=total_blocks,
                username=self.username
            )
            
            for node in response.nodes:
                data_node_channel = grpc.insecure_channel(f'{node.ip}:{node.port}', options=options)
                data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)
                upload_response = data_node_stub.SendFile(block_chunk)
                print(f'Block {i} uploaded to node {node.id}, server reported success: {upload_response.length}')

        print(f'File {filename_} upload complete')


    def DownloadFile(self, filename: str):
        data_nodes = self.GetDataNodesForDownload(filename)
        
        node_position = random.randint(0, len(data_nodes) - 1)
        data_node = data_nodes[node_position]
        data_node_ip = data_node.ip
        data_node_port = data_node.port
        print(f'{data_node_ip}:{data_node_port}')

        data_node_channel = grpc.insecure_channel(f'{data_node_ip}:{data_node_port}')
        data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)

        response = data_node_stub.GetFile(
            data_node_pb2.GetFileRequest(
                filename=filename
            )
        )

        SaveChunksToFile(response, filename)


    def Register(self, username: str, password: str):
        response = self.server_stub.AddUser(
            name_node_pb2.AddUserRequest(
                username=username, password=password))
        self.username = username

        self.file_manager = FileManager(self.username, self.users_collection)

        if response.status == "User created successfully":
            self.users_collection.update_one(
                {"Username": self.username},
                {"$set": {"Directories": [
                    {
                        "Name": "/",
                        "IsDir": True,
                        "Contents": []
                    }
                ]}}
            )
        print(f'Response: {response.status}')

    def GetFileManager(self):
        return self.file_manager
