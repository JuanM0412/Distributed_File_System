from src.name_node.name_node import *
from dotenv import load_dotenv
import os


load_dotenv()


if __name__ == '__main__':
    StartServer(os.getenv('SERVER_IP'), os.getenv('SERVER_PORT'))