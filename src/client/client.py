from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
from utils.utils import GetFileSize, GetFileChunks, SaveChunksToFile
from src.client.manage_blocks import SplitFile
from config.db import database
from config import MB_IN_BYTES, PARTITIONS_DIR, DOWNLOADS_DIR
import grpc
import os
from src.file_manager.file_manager import FileManager
import random
from bson import ObjectId
from google.protobuf.json_format import MessageToDict, MessageToJson


class Client:
    def __init__(self, ip: str, port: int, server_ip: str, server_port: int):
        self.ip = ip
        self.port = port
        self.username = None

        self.users_collection = database.users

        self.file_manager = None

        print(f'Connecting to {server_ip}:{server_port}')

        options = [
            ('grpc.max_send_message_length', 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1024 * 1024 * 1024),
        ]

        self.server_channel = grpc.insecure_channel(
            f'{server_ip}:{server_port}', options=options)
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

        return response.blocks

    def GetDataNodesForRemove(self, filename: str):
        response = self.server_stub.GetDataNodesForRemove(
            name_node_pb2.DataNodesRemoveRequest(
                file=filename,
                username=self.username
            )
        )
        return response.blocks

    def GetDataNode(self, data_node):
        return data_node.ip, data_node.port

    def UploadFile(self, virtual_path: str, filename_: str):
        file_size = int(GetFileSize(filename_))

        blocks = list(SplitFile(filename_))
        total_blocks = len(blocks)

        options = [
            ('grpc.max_send_message_length', 1 * 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1 * 1024 * 1024 * 1024),
        ]

        for i, block in enumerate(blocks):
            block_size_bytes = os.path.getsize(block)
            block_size_MB = block_size_bytes / MB_IN_BYTES

            request = name_node_pb2.DataNodesUploadRequest(
                file=virtual_path,
                size=block_size_MB,
                username=self.username,
            )

            response = self.server_stub.GetDataNodesForUpload(request)

            if not response.nodes:
                raise Exception(f"No available nodes to store block {i}")

            with open(block, 'rb') as f:
                block_data = f.read()

            block_chunk = data_node_pb2.BlockChunk(
                block_data=block_data,
                filename=virtual_path,
                block_number=i,
                username=self.username
            )

            for node in response.nodes:
                data_node_channel = grpc.insecure_channel(f'{node.ip}:{node.port}', options=options)
                data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)

                try:
                    upload_response = data_node_stub.SendFile(block_chunk)
                except Exception as e:

                    continue

        print(f'File {filename_} upload complete')

    def DownloadFile(self, filename: str):
        print("Filename in download:", filename)
        data_nodes = self.GetDataNodesForDownload(filename)

        options = [
            ('grpc.max_send_message_length', 1 * 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1 * 1024 * 1024 * 1024),
        ]

        file_data = b''
        data_nodes = dict(sorted(data_nodes.items()))
        filename_name = filename.split('.')[0]
        filename_extension = filename.split('.')[1]
        for node in data_nodes:
            data_node = database.dataNodes.find_one({'_id': ObjectId(data_nodes[node])})
            data_node_channel = grpc.insecure_channel(f'{data_node["Ip"]}:{data_node["Port"]}', options=options)
            data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)
            filename_ = filename_name + '_block_' + str(node) + '.' + filename_extension
            try:
                filename_ = filename_[1:]
                response = data_node_stub.GetFile(
                    data_node_pb2.GetFileRequest(
                        filename=filename_,
                        username=self.username
                    )
                )
                file_data += response.file_data
            except Exception as e:
                continue

        only_name = os.path.basename(filename)
        download_path = os.path.join(DOWNLOADS_DIR, only_name)
        with open(download_path, 'wb') as f:
            f.write(file_data)

        print(f'File {filename} download complete')

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

    def DeleteFile(self, filename: str):
        response = self.GetDataNodesForRemove(filename)
        if not response:
            print("Error: No response from GetDataNodesForRemove")
            return
        response_dict = [MessageToDict(block) for block in response]

        data_nodes = response_dict

        options = [
            ('grpc.max_send_message_length', 1 * 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1 * 1024 * 1024 * 1024),
        ]

        filename_name = filename.split('.')[0]
        filename_extension = filename.split('.')[1]

        for block_index, block_info in enumerate(data_nodes):
            for node in block_info.get('nodes', []):
                data_node = database.dataNodes.find_one({'_id': ObjectId(node["id"])})
                data_node_channel = grpc.insecure_channel(f'{data_node["Ip"]}:{data_node["Port"]}', options=options)
                data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)
                filename_ = filename_name + '_block_' + str(block_index) + '.' + filename_extension
                try:
                    filename_ = filename_[1:]
                    response = data_node_stub.DeleteFile(
                        data_node_pb2.DeleteFileRequest(
                            filename=filename_,
                            username=self.username
                        )
                    )

                except Exception as e:
                    continue

        print(f'File {filename} removed complete')

    def DeleteFiles(self, filenames: list):
        for filename in filenames:
            self.DeleteFile(filename)
