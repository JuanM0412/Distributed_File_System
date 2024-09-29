from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
from utils.utils import GetFileSize, GetFileChunks, SaveChunksToFile
from config import MB_IN_BYTES
import grpc
import os
from concurrent import futures
from config.db import database


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
        
        storage_base_dir = os.path.join(current_dir, 'storage')

        user_dir = os.path.join(storage_base_dir, request.username)
        os.makedirs(user_dir, exist_ok=True) 

        file_dir = r'C:\Users\Sebastian\Downloads'
        print('File dir:', file_dir)
        os.makedirs(file_dir, exist_ok=True)  

        block_file_name = f"{request.filename}_{request.block_number}"
        block_file_path = os.path.join(file_dir, block_file_name)

        with open(block_file_path, 'wb') as f:
            f.write(request.block_data)

        block_size_MB = len(request.block_data) / MB_IN_BYTES
        print(f"Received block {request.block_number} of size {block_size_MB} MB")
        print(f"Capacity before: {self.capacity_MB} MB")
        self.capacity_MB -= block_size_MB
        print(f"Capacity after: {self.capacity_MB} MB")
        
        file_size = os.path.getsize(block_file_path)
        return data_node_pb2.Reply(length=file_size)    

    def GetFile(self, request, context):
        path = r'C:\Users\Sebastian\Downloads'
        print("Path in sendfile:", request.filename)
        filename = os.path.join(path, request.filename)

        print("Contenido del directorio Downloads:")
        for item in os.listdir(path):
            print(item)
        
        if not os.path.exists(filename):
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"File {request.filename} not found")

        file_data = b''.join(GetFileChunks(filename))

        return data_node_pb2.GetFileResponse(file_data=file_data)

    def StartServer(self):
        options = [
            ('grpc.max_send_message_length', 1*1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1*1024 * 1024 * 1024),
        ]
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),options=options)
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

    def DeleteFile(self, request, context):
        path = r'C:\Users\Sebastian\Downloads'
        print("Path in sendfile:", request.filename)
        filename = os.path.join(path, request.filename)

        print("Contenido del directorio Downloads:")
        for item in os.listdir(path):
            print(item)
        
        if not os.path.exists(filename):
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"File {request.filename} not found")

        try:
            os.remove(filename)
            print(f"File {request.filename} deleted successfully")
            return data_node_pb2.DeleteFileResponse(success=True)
        except Exception as e:
            print("Continue")
            
