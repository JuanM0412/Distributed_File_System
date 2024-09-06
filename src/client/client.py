from src.proto import data_node_pb2, data_node_pb2_grpc
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
    def __init__(self, ip: str, port: int):
        print(f"Connecting to {ip}:{port}")
        self.channel = grpc.insecure_channel(f"{ip}:{port}")
        self.stub = data_node_pb2_grpc.DataNodeStub(self.channel)

    
    def UploadFile(self, filename: str):
        chunks = get_file_chunks(filename)
        response = self.stub.SendFile(chunks.__iter__())
        print(f'File uploaded, server reported length: {response.length}')