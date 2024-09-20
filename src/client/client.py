from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
from utils.utils import GetFileSize, GetFileChunks, SaveChunksToFile
from config.db import database
from config import MB_IN_BYTES
import grpc
from src.file_manager.file_manager import FileManager


class Client:

    def __init__(self, ip: str, port: int, server_ip: str, server_port: int):
        self.ip = ip
        self.port = port
        self.username = None

        self.users_collection = database.users

        self.file_manager = None

        print(f'Connecting to {server_ip}:{server_port}')

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
                file=filename, username=self.username))
        
        return response.nodes

    def GetDataNode(self, data_node):
        return data_node.ip, data_node.port

    def UploadFile(self, filename_: str):
        print(f'Uploading file {filename_}')
        file_size = int(GetFileSize(filename_))
        print(f'File size: {file_size}')
        
        chunks = list(GetFileChunks(filename_))
        total_chunks = len(chunks)
        
        print(f'Uploading file {filename_} of size {file_size} bytes')
        print(f'Total chunks: {total_chunks}')
        
        for i, chunk in enumerate(chunks):
            print(f'Uploading chunk {i}')
            chunk_size_bytes = len(chunk.chunk_data)
            chunk_size = chunk_size_bytes / MB_IN_BYTES
            print(f'Chunk size: {chunk_size}')
            
            request = name_node_pb2.DataNodesUploadRequest(
                file=filename_,
                size=chunk_size,
                username=self.username
            )
            
            response = self.server_stub.GetDataNodesForUpload(request)
            
            print(f'Received response from server for chunk {i}')
            print(f'Number of data nodes available: {len(response.nodes)}')
            
            if not response.nodes:
                raise Exception(f"No available nodes to store chunk {i}")
            
            for node in response.nodes:
                print(f'Uploading chunk {i} to node: id={node.id}, ip={node.ip}, port={node.port}')
                
                data_node_channel = grpc.insecure_channel(f'{node.ip}:{node.port}')
                data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)
                file = data_node_pb2.FileChunk(
                        chunk_data=chunk.chunk_data,
                        filename=filename_,
                        chunk_number=i,
                        total_chunks=total_chunks,
                        username=self.username,
                    )
                print(file.filename, file.chunk_number, file.total_chunks)
                print(f'Uploading chunk {i} to node {node.id}')
                upload_response = data_node_stub.SendFile(
                    file
                )
                print(f'Chunk {i} uploaded to node {node.id}, server reported length: {upload_response.length}')

        print(f'File {filename_} upload complete')

    def DownloadFile(self, filename: str):
        data_nodes = self.GetDataNodesForDownload(filename)
        data_node_ip, data_node_port = self.GetDataNode(data_nodes[0])
        print(f'{data_node_ip}:{data_node_port}')

        data_node_channel = grpc.insecure_channel(
            f'{data_node_ip}:{data_node_port}')
        data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)

        response = data_node_stub.GetFile(
            data_node_pb2.GetFileRequest(
                filename=filename))

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

    def MakeDirectory(self, path: str):
        if self.file_manager:
            self.file_manager.MakeDirectory(path)

    def Put(self, path: str, file_name: str, file_size: int = 0):
        if self.file_manager:
            self.file_manager.Put(path, file_name, file_size)

    def RemoveDirectory(self, path: str, force: bool = False):
        if self.file_manager:
            self.file_manager.RemoveDirectory(path, force)

    def ListDirectory(self, path: str):
        if self.file_manager:
            self.file_manager.ListDirectory(path)

    def Rm(self, path: str, file_name: str):
        if self.file_manager:
            self.file_manager.Rm(path, file_name)

    def FindDirectory(self, directories, path):
        if self.file_manager:
            self.file_manager.FindDirectory(directories, path)

    def directory_exists(self, path):
        print(f"Checking if directory exists: {path}")
        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return False
        result = self.FindDirectory(user_data['Directories'], path)
        print(f"FindDirectory result: {result}")
        return result is not None
