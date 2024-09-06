from src.proto import data_node_pb2, data_node_pb2_grpc
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