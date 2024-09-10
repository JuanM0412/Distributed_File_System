import threading, os
from src.data_node.data_node import *
from dotenv import load_dotenv


load_dotenv()


if __name__ == '__main__':
    data_node = DataNode(os.getenv('SERVER_IP'), os.getenv('SERVER_PORT'), os.getenv('DATA_NODE_IP'), os.getenv('DATA_NODE_PORT'), os.getenv('DOWNLOADS_DIR'))
    
    data_node_server_thread = threading.Thread(target=data_node.StartServer)
    data_node_server_thread.daemon = True
    data_node_server_thread.start()

    data_node_thread = threading.Thread(target=data_node.Register)
    data_node_thread.daemon = True
    data_node_thread.start()

    data_node_server_thread.join()
    data_node_thread.join()