from src.proto import data_node_pb2, data_node_pb2_grpc, nameNode_pb2, nameNode_pb2_grpc
import grpc, os
from concurrent import futures


CHUNK_SIZE = 1024 * 1024 # 1MB


def save_chunks_to_file(chunks, filename):
    with open(filename, 'wb') as f:
        for i, chunk in enumerate(chunks):
            print(f"Received chunk {i+1}, size: {len(chunk.buffer)} bytes")
            f.write(chunk.buffer)
    print(f"File saved: {filename}")


class DataNode(data_node_pb2_grpc.DataNodeServicer):
    def __init__(self, server_port: int, server_ip: str, ip: str, port: int, dir: str):
        print(f'Listening on {ip}:{port}')
        self.ip = ip
        self.port = port
        self.dir = dir
        self.capacity = 1000 # Test value
        self.id = None

        self.name_node_channel = grpc.insecure_channel(f'{server_ip}:{server_port}')
        self.name_node_stub = nameNode_pb2_grpc.nameNodeServiceStub(self.name_node_channel)


    def SendFile(self, request_iterator, context):
        filename = os.path.join(self.dir, 'test.txt')
        save_chunks_to_file(request_iterator, filename)
        file_size = os.path.getsize(filename)
        return data_node_pb2.Reply(length=file_size)
    

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        data_node_pb2_grpc.add_DataNodeServicer_to_server(self, server)
        server.add_insecure_port(f'{self.ip}:{self.port}')
        server.start()
        server.wait_for_termination()


    def Register(self):
        response = self.name_node_stub.Register(nameNode_pb2.RegisterRequest(ip=self.ip, port=str(self.port), storage=self.capacity))
        self.id = response.id
        print(f'Registered with id: {self.id}')