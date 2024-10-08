from src.name_node.name_node import StartServer
from config import SERVER_IP, SERVER_PORT


if __name__ == '__main__':
    StartServer(SERVER_IP, SERVER_PORT)
