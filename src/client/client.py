from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
from utils.utils import GetFileSize, GetFileChunks, SaveChunksToFile
from config.db import database
import grpc


class Client:
    def __init__(self, ip: str, port: int, server_ip: str, server_port: int):
        self.ip = ip
        self.port = port
        self.username = None
        
        self.users_collection = database.users

        print(f'Connecting to {server_ip}:{server_port}')
        self.server_channel = grpc.insecure_channel(f'{server_ip}:{server_port}')
        self.server_stub = name_node_pb2_grpc.NameNodeServiceStub(self.server_channel)

    
    def GetDataNodesForUpload(self, filename: str, file_size: int):
        response = self.server_stub.GetDataNodesForUpload(name_node_pb2.DataNodesUploadRequest(file=filename, size=file_size, username=self.username))
        return response.nodes
    

    def GetDataNodesForDownload(self, filename: str):
        response = self.server_stub.GetDataNodesForDownload(name_node_pb2.DataNodesDownloadRequest(file=filename, username=self.username))
        return response.nodes
    
    
    def GetDataNode(self, data_node):
        return data_node.ip, data_node.port


    def UploadFile(self, filename: str):
        file_size = GetFileSize(filename)
        data_nodes = self.GetDataNodesForUpload(filename, file_size)
        data_node_ip, data_node_port = self.GetDataNode(data_nodes[0])
        print(f'{data_node_ip}:{data_node_port}')

        chunks = GetFileChunks(filename)
        data_node_channel = grpc.insecure_channel(f'{data_node_ip}:{data_node_port}')
        data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)
        response = data_node_stub.SendFile(chunks.__iter__())
        print(f'File uploaded, server reported length: {response.length}')


    def DownloadFile(self, filename: str):
        data_nodes = self.GetDataNodesForDownload(filename)
        data_node_ip, data_node_port = self.GetDataNode(data_nodes[0])
        print(f'{data_node_ip}:{data_node_port}')

        data_node_channel = grpc.insecure_channel(f'{data_node_ip}:{data_node_port}')
        data_node_stub = data_node_pb2_grpc.DataNodeStub(data_node_channel)

        response = data_node_stub.GetFile(data_node_pb2.GetFileRequest(filename=filename))

        SaveChunksToFile(response, filename)

    
    def Register(self, username: str, password: str):
        response = self.server_stub.AddUser(name_node_pb2.AddUserRequest(username=username, password=password))
        self.username = username

        if response.status == "User created successfully" : 
            self.users_collection.update_one(
                {"Username" : self.username},
                {"$set" : {"Directories" : [
                    {
                        "Name" : "/",
                        "IsDir" : True,
                        "Contents" : []
                    }
                ]}}
            )
        print(f'Response: {response.status}')
    
    def MakeDirectory(self, path: str):
        if self.username is None:
            print("Username is not set. Please register first")
            return

        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return

        directories = user_data['Directories']
        parts = path.strip('/').split('/')
        current_dir = self.FindDirectory(directories, "/")

        if current_dir is None:
            print("Root directory not found")
            return

        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                if not any(item['Name'] == part and item['IsDir'] for item in current_dir['Contents']):
                    current_dir['Contents'].append({
                        "Name": part,
                        "IsDir": True,
                        "Contents": []
                    })
                    print(f"Directory {path} created successfully.")
                else:
                    print(f"Directory {path} already exists.")
                break
            else:
                next_dir = next((item for item in current_dir['Contents'] if item['Name'] == part and item['IsDir']), None)
                if next_dir is None:
                    next_dir = {
                        "Name": part,
                        "IsDir": True,
                        "Contents": []
                    }
                    current_dir['Contents'].append(next_dir)
                current_dir = next_dir

        self.users_collection.update_one(
            {"Username": self.username},
            {"$set": {"Directories": directories}}
        )

    def FindDirectory(self, directories, path):
        if path == '/':
            return next((item for item in directories if item["Name"] == "/"), None)

        parts = path.strip('/').split('/')
        current_dir = next((item for item in directories if item["Name"] == "/"), None)

        for part in parts:
            if current_dir is None:
                return None
            current_dir = next((item for item in current_dir["Contents"] if item["IsDir"] and item["Name"] == part), None)

        return current_dir

    def RemoveDirectory(self, path: str, force: bool = False):
        if self.username is None:
            print("Username is not set. Please register first")
            return

        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return

        directories = user_data['Directories']
        parts = path.strip('/').split('/')
        
        if len(parts) == 1 and parts[0] == '':
            print("Cannot remove root directory")
            return

        parent_path = '/' + '/'.join(parts[:-1])
        dir_to_remove = parts[-1]

        parent_dir = self.FindDirectory(directories, parent_path)
        if parent_dir is None:
            print(f"Parent directory {parent_path} not found")
            return

        dir_index = next((i for i, item in enumerate(parent_dir['Contents']) 
                          if item['Name'] == dir_to_remove and item['IsDir']), None)
        
        if dir_index is None:
            print(f"Directory {path} not found")
            return

        dir_to_remove = parent_dir['Contents'][dir_index]

        if not force and len(dir_to_remove['Contents']) > 0:
            print(f"Directory {path} is not empty. Use force=True to remove non-empty directories")
            return

        del parent_dir['Contents'][dir_index]
        print(f"Directory {path} removed successfully")

        self.users_collection.update_one(
            {"Username": self.username},
            {"$set": {"Directories": directories}}
        )

    def ListDirectory(self, path: str):
        if self.username is None:
            print("Username is not set. Please register first")
            return

        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return

        directories = user_data['Directories']
        dir_to_list = self.FindDirectory(directories, path)

        if dir_to_list is None:
            print(f"Directory {path} not found")
            return

        print(f"Contents of {path}:")
        for item in dir_to_list['Contents']:
            item_type = "DIR" if item['IsDir'] else "FILE"
            print(f"{item_type:<4} {item['Name']}")