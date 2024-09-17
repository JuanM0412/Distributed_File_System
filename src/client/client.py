from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
from utils.utils import GetFileSize, GetFileChunks, SaveChunksToFile
from config.db import database
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

    def GetDataNodesForUpload(self, filename: str, file_size: int):
        response = self.server_stub.GetDataNodesForUpload(
            name_node_pb2.DataNodesUploadRequest(
                file=filename, size=file_size, username=self.username))
        return response.nodes

    def GetDataNodesForDownload(self, filename: str):
        response = self.server_stub.GetDataNodesForDownload(
            name_node_pb2.DataNodesDownloadRequest(
                file=filename, username=self.username))
        return response.nodes

    def GetDataNode(self, data_node):
        return data_node.ip, data_node.port

    def UploadFile(self, filename: str):
        file_size = GetFileSize(filename)
        data_nodes = self.GetDataNodesForUpload(filename, file_size)
        data_node_ip, data_node_port = self.GetDataNode(data_nodes[0])
        print(f'{data_node_ip}:{data_node_port}')

        chunks = GetFileChunks(filename)
        data_node_channel = grpc.insecure_channel(
            f'{data_node_ip}:{data_node_port}')
        data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)
        response = data_node_stub.SendFile(chunks.__iter__())
        print(f'File uploaded, server reported length: {response.length}')

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
            return self.file_manager.FindDirectory(directories, path)

    def directory_exists(self, path):
        print(f"Checking if directory exists: {path}")
        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return False

        print("Direcories : ", user_data["Directories"])
        result = self.FindDirectory(user_data['Directories'], path)
        print(f"FindDirectory result: {result}")
        return result is not None
