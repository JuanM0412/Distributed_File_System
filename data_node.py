import threading, os
from src.data_node.data_node import *
from dotenv import load_dotenv


load_dotenv()


if __name__ == '__main__':
    server_ip = os.getenv('SERVER_IP')
    server_port = os.getenv('SERVER_PORT')

    data_node = DataNode(server_ip, server_port, os.getenv('DATA_NODE_IP'), os.getenv('DATA_NODE_PORT'), os.getenv("DOWNLOADS_DIR"))
    
    data_node.start_server()