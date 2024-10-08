from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
from src.rpc.data_node import data_node_pb2_grpc, data_node_pb2
from utils.utils import GetFileSize, GetFileChunks, SaveChunksToFile
from config import MB_IN_BYTES, DOWNLOADS_DIR, PARTITIONS_DIR
import grpc
import os
from bson import ObjectId
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
        file_dir = PARTITIONS_DIR

        os.makedirs(file_dir, exist_ok=True)

        filename = request.filename.replace('\\', '/').split('/')[-1]
        name, ext = filename.rsplit('.', 1)
        block_file_name = f"{name}_block_{request.block_number}.{ext}"
        block_file_path = os.path.join(file_dir, block_file_name) if not block_file_name.startswith('/') else os.path.join(file_dir, block_file_name.lstrip('/'))

        with open(block_file_path, 'wb') as f:
            f.write(request.block_data)

        block_size_MB = len(request.block_data) / MB_IN_BYTES
        self.capacity_MB -= block_size_MB

        file_size = os.path.getsize(block_file_path)
        return data_node_pb2.Reply(length=file_size)

    def GetFile(self, request, context):
        path = PARTITIONS_DIR
        print("Path in getfile:", path)
        filename = os.path.join(path, request.filename).replace('\\', '/')
        print("Filename in getfile:", filename)

        if not os.path.exists(filename):
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"File {request.filename} not found")

        file_data = b''.join(GetFileChunks(filename))

        return data_node_pb2.GetFileResponse(file_data=file_data)

    def StartServer(self):
        options = [
            ('grpc.max_send_message_length', 1 * 1024 * 1024 * 1024),
            ('grpc.max_receive_message_length', 1 * 1024 * 1024 * 1024),
        ]
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
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
        path = PARTITIONS_DIR
        filename = os.path.join(path, request.filename)

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

    def Heartbeat(self, request, context):
        return data_node_pb2.HeartbeatResponse(alive=True)

    def AskForBlock(self, request, context):
        try:
            print(f"Received request for block ID: {request.block_id} from node ID: {request.node_id}")
            
            node_to_ask_id = ObjectId(request.node_id)
            node_to_ask = dict(database.dataNodes.find_one({'_id': node_to_ask_id}))
            
            if node_to_ask is None:
                print(f"Error: Node {node_to_ask_id} not found in dataNodes.")
                return data_node_pb2.AskForBlockResponse(status=False)
            
            print(f"Node to ask: {node_to_ask}")
            try:
                block_metadata = dict(database.metaData.find_one({'Blocks': str(request.block_id)}))
            except:
                block_metadata = dict(database.metaData.find_one({'Blocks': ObjectId(request.block_id)}))

            if block_metadata is None:
                print(f"Error: Block {request.block_id} not found in metaData.")
                return data_node_pb2.AskForBlockResponse(status=False)
            
            print(f"Block metadata: {block_metadata}")

            filename = request.filename
            print(f"Filename to retrieve: {filename}")

            try:
                print(f"Connecting to node {node_to_ask['Ip']}:{node_to_ask['Port']}")
                channel = grpc.insecure_channel(f'{node_to_ask["Ip"]}:{node_to_ask["Port"]}')
                stub = data_node_pb2_grpc.DataNodeStub(channel)

                response = stub.GetFile(
                    data_node_pb2.GetFileRequest(
                        filename=filename, 
                        username=block_metadata['Owner']
                    )
                )
                print("File request sent successfully.")
            except Exception as e:
                print(f"Error during gRPC file request: {e}")
                return data_node_pb2.AskForBlockResponse(status=False)

            if not response.file_data:
                print(f"Error: No file data received for file {filename}.")
                return data_node_pb2.AskForBlockResponse(status=False)

            path = PARTITIONS_DIR
            os.makedirs(path, exist_ok=True)
            full_file_path = os.path.join(path, os.path.basename(filename))

            print(f"Saving file to {full_file_path}")
            with open(full_file_path, 'wb') as f:
                f.write(response.file_data)

            print(f"File {filename} saved successfully.")
            return data_node_pb2.AskForBlockResponse(status=True)

        except Exception as e:
            print(f"Unexpected error in AskForBlock: {e}")
            return data_node_pb2.AskForBlockResponse(status=False)

