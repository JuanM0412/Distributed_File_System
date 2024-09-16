from src.rpc.name_node import name_node_pb2_grpc, name_node_pb2
import grpc
import json
from concurrent import futures
from src.models.datanode import DataNode
from src.models.user import User
from config.db import database


class Server(name_node_pb2_grpc.NameNodeServiceServicer):
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def Register(self, request, context):
        # Extract the info about the dataNode.
        ip = request.ip
        port = request.port
        capacity_MB = request.capacity_MB

        # Instance of the model
        data_node_info = DataNode(
            Ip=ip,
            Port=port,
            CapacityMB=capacity_MB,
            IsActive=True,
            Blocks=[])
        print('data:', data_node_info.model_dump())

        # Add the dataNode in the DB
        print('After insert')
        data_node = database.dataNodes.insert_one(data_node_info.model_dump())
        print('data_node:', data_node.inserted_id)
        return name_node_pb2.RegisterResponse(id=str(data_node.inserted_id))

    def GetDataNodesForUpload(self, request, context):
        file = request.file
        data_nodes = list(database.dataNodes.find())

        response = name_node_pb2.DataNodesResponse()
        for data_node in data_nodes:
            data_node_info = name_node_pb2.DataNodeInfo(
                id=str(
                    data_node['_id']), ip=str(
                    data_node['ip']), port=str(
                    data_node['port']), capacity_MB=data_node['storage'])
            response.nodes.append(data_node_info)
            # This break will be in this for while we realize how choose in
            # which datanodes we are going to save a file. For the same reason
            # I asked for the filename. In this way, we are going to add the
            # files just in the first data_node, then it will be different
            break

        return response

    def GetDataNodesForDownload(self, request, context):
        file = request.file
        username = request.username
        data_nodes = list(database.dataNodes.find())

        response = name_node_pb2.DataNodesResponse()
        for data_node in data_nodes:
            data_node_info = name_node_pb2.DataNodeInfo(
                id=str(
                    data_node['_id']), ip=str(
                    data_node['ip']), port=str(
                    data_node['port']), capacity_MB=data_node['storage'])
            response.nodes.append(data_node_info)
            # This break will be in this for while we realize how choose in
            # which datanodes we are going to save a file. For the same reason
            # I asked for the filename. In this way, we are going to add the
            # files just in the first data_node, then it will be different
            break

        return response

    def AddUser(self, request, context):
        # Extract the info about the user.
        username = request.username
        password = request.password

        print('AddUser method')

        check_unique_name = database.users.find_one({'Username': username})
        if check_unique_name:
            return name_node_pb2.AddUserResponse(status='Name unavailable')

        # Instance of the model
        user_info = User(Username=username, Password=password)
        print('user:', user_info.model_dump())

        # Add the dataNode in the DB
        database.users.insert_one(user_info.model_dump())
        return name_node_pb2.AddUserResponse(
            status='User created successfully')

    def ValidateUser(self, request, context):
        # Extract the info about the user.
        username = request.username
        password = request.password

        # Validate that exist
        user = database.users.find_one(
            {'username': username, 'password': password})

        if user:
            return name_node_pb2.ValidateUserResponse(
                status='User logged successfully')
        else:
            return name_node_pb2.ValidateUserResponse(
                status='Invalid username or password')


def StartServer(ip: str, port: int):
    print('Server is running')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    name_node_pb2_grpc.add_NameNodeServiceServicer_to_server(
        Server(ip=ip, port=port), server)
    server.add_insecure_port(f'{ip}:{port}')
    server.start()
    server.wait_for_termination()
