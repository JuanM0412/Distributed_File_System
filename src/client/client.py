from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
from src.utils import *
import grpc


class Client:
    def __init__(self, ip: str, port: int, server_ip: str, server_port: int):
        self.ip = ip
        self.port = port

        print(f'Connecting to {server_ip}:{server_port}')
        self.server_channel = grpc.insecure_channel(f'{server_ip}:{server_port}')
        self.server_stub = name_node_pb2_grpc.nameNodeServiceStub(self.server_channel)

    
    def GetDataNodesForUpload(self, filename: str):
        response = self.server_stub.GetDataNodesForUpload(name_node_pb2.DataNodesRequest(file=filename))
        return response.nodes
    
    def GetDataNodesForDownload(self, filename: str):
        response = self.server_stub.GetDataNodesForDownload(name_node_pb2.DataNodesRequest(file=filename))
        return response.nodes
    
    
    def GetDataNode(self, data_node):
        return data_node.ip, data_node.port


    def UploadFile(self, filename: str):
        data_nodes = self.GetDataNodesForUpload(filename)
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
        print(f'Response: {response.status}')