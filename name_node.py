from src.name_node.name_node import *
from config.env import SERVER_IP, SERVER_PORT


if __name__ == '__main__':
    serve(SERVER_IP, SERVER_PORT)