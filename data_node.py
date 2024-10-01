import threading
from src.data_node.data_node import *
from config import SERVER_IP, SERVER_PORT, DATA_NODE_IP, DATA_NODE_PORT, DOWNLOADS_DIR, DATA_NODE_CAPACITY_MB
import socket
 
def get_private_ip():
    hostname = socket.gethostname()
    ip_privada = socket.gethostbyname(hostname)
    return ip_privada
 
if __name__ == '__main__':
    private_ip = get_private_ip()
    data_node = DataNode(
        SERVER_IP,  
        SERVER_PORT,
        private_ip,
        DATA_NODE_PORT,
        DOWNLOADS_DIR,
        DATA_NODE_CAPACITY_MB)
 
    data_node_server_thread = threading.Thread(target=data_node.StartServer)
    data_node_server_thread.daemon = True
    data_node_server_thread.start()
 
    data_node_thread = threading.Thread(target=data_node.Register)
    data_node_thread.daemon = True
    data_node_thread.start()
 
    data_node_server_thread.join()
    data_node_thread.join()
