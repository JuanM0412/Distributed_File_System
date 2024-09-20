from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
from utils.utils import GetFileSize, GetFileChunks, SaveChunksToFile
from config import MB_IN_BYTES
import grpc
import os
from concurrent import futures


class DataNode(data_node_pb2_grpc.DataNodeServicer):
    def __init__(
            self,
            server_ip: str,
            server_port: int,
            ip: str,
            port: int,
            dir: str,
            capacity_MB: float):
        print(f'Listening on {ip}:{port}')
        self.ip = ip
        self.port = port
        self.dir = dir
        self.capacity_MB = capacity_MB
        self.id = None

        self.name_node_channel = grpc.insecure_channel(
            f'{server_ip}:{server_port}')
        self.name_node_stub = name_node_pb2_grpc.NameNodeServiceStub(
            self.name_node_channel)

    def SendFile(self, request, context):
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        
        storage_base_dir = os.path.join(current_dir,'storage')

        user_dir = os.path.join(storage_base_dir, request.username)
        os.makedirs(user_dir, exist_ok=True) 

        file_dir = os.path.join(user_dir, request.filename)
        os.makedirs(file_dir, exist_ok=True)  

        chunk_file_name = f"chunk_{request.chunk_number}"
        chunk_file_path = os.path.join(file_dir, chunk_file_name)

        with open(chunk_file_path, 'wb') as f:
            f.write(request.chunk_data)

        chunk_size_MB = len(request.chunk_data) / MB_IN_BYTES
        print(f"Received chunk {request.chunk_number} of size {chunk_size_MB} MB")
        print(f"Capacity before: {self.capacity_MB} MB")
        self.capacity_MB -= chunk_size_MB
        print(f"Capacity after: {self.capacity_MB} MB")
        
        file_size = os.path.getsize(chunk_file_path)
        return data_node_pb2.Reply(length=file_size)

    
    def GetFile(self, request, context):
        filename = os.path.join(self.dir, request.filename)
        if not os.path.exists(filename):
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"File {request.filename} not found")

        for chunk in GetFileChunks(filename):
            yield chunk

    def StartServer(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        data_node_pb2_grpc.add_DataNodeServicer_to_server(self, server)
        server.add_insecure_port(f'{self.ip}:{self.port}')
        server.start()
        server.wait_for_termination()

    def Register(self):
        response = self.name_node_stub.Register(
            name_node_pb2.RegisterRequest(
                ip=self.ip, port=str(
                    self.port), capacity_MB=float(
                    self.capacity_MB)))
        self.id = response.id
        print(f'Registered with id: {self.id}')
