import grpc
from concurrent import futures
from src.proto import nameNode_pb2, nameNode_pb2_grpc
from .models import DataNode, User
from config.db import database


class Server(nameNode_pb2_grpc.nameNodeServiceServicer):
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port


    def Register(self, request, context):
        # Extract the info about the dataNode.
        ip = request.ip
        port = request.port
        storage = request.storage

        # Instance of the model
        data_node_info = DataNode(ip=ip, port=port, storage=storage)
        print('data:', data_node_info.model_dump())

        # Add the dataNode in the DB
        print('After insert')
        data_node = database.dataNodes.insert_one(data_node_info.model_dump())
        print('data_node:', data_node.inserted_id)
        return nameNode_pb2.RegisterResponse(id=str(data_node.inserted_id))
    

    def GetDataNodes(self, request, context):
        file = request.file
        data_nodes = list(database.dataNodes.find())

        response = nameNode_pb2.GetDataNodes()
        for data_node in data_nodes:
            data_node_info = nameNode_pb2.DataNodeInfo(id=data_node['id'], ip=data_node['ip'], port=data_node['port'], storage=data_node['storage'])
            response.nodes.append(data_node_info)
            #This break will be in this for while we realize how choose in which datanodes we are going to save a file. For the same reason I asked for the filename. In this way, we are going to add the files just in the first data_node, then it will be different
            break 
        return response
    

    def AddUser(self, request, context):
        # Extract the info about the user.
        username = request.username
        password = request.password

        check_unique_name = database.users.find_one({"username": username})
        if check_unique_name:
            return nameNode_pb2.AddUserResponse(status="Name unavailable")
        
        # Instance of the model
        user_info = User(username, password)

        # Add the dataNode in the DB
        database.users.insert_one(user_info.dict())
        return nameNode_pb2.AddUserResponse(status="User created successfully")
    

    def ValidateUser(self, request, context):
        # Extract the info about the user.
        username = request.username
        password = request.password

        # Validate that exist
        user = database.users.find_one({"username": username, "password": password})

        if user:
            return nameNode_pb2.AddUserResponse(status="User logged successfully")
        else:
            return nameNode_pb2.AddUserResponse(status="Invalid username or password")


def serve(ip: str, port: int):
    print('Server is running')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nameNode_pb2_grpc.add_nameNodeServiceServicer_to_server(Server(ip=ip, port=port), server)
    server.add_insecure_port(f'{ip}:{port}')
    server.start()
    server.wait_for_termination()