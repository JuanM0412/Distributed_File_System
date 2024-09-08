from src.proto import data_node_pb2, data_node_pb2_grpc, nameNode_pb2, nameNode_pb2_grpc
import grpc, os
from concurrent import futures


CHUNK_SIZE = 1024 * 1024 # 1MB


def get_file_chunks(file_path):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            print(f"Sending chunk of size: {len(chunk)} bytes")
            yield data_node_pb2.Chunk(buffer=chunk)


class Client:
    def __init__(self, server_ip: str, server_port: int):
        print(f"Connecting to {server_ip}:{server_port}")
        self.server_channel = grpc.insecure_channel(f"{server_ip}:{server_port}")
        self.server_stub = nameNode_pb2_grpc.nameNodeServiceStub(self.server_channel)

    # Add connection with the data_node
    """def UploadFile(self, filename: str):
        chunks = get_file_chunks(filename)
        data_node_channel = grpc.insecure_channel(f"{data_node_ip}:{data_node_port}")
        data_node_stub = nameNode_pb2_grpc.nameNodeServiceStub(data_node_channel)
        response = data_node_stub.SendFile(chunks.__iter__())
        print(f'File uploaded, server reported length: {response.length}')"""

    
    def Register(self, username: str, password: str):
        print('Register method')
        response = self.server_stub.AddUser(nameNode_pb2.AddUserRequest(username=username, password=password))
        print(f'Response: {response.status}')