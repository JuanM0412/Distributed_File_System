import threading, os
from src.client.client import *
from dotenv import load_dotenv


load_dotenv()


if __name__ == '__main__':
    server_ip = os.getenv('SERVER_IP')
    server_port = os.getenv('SERVER_PORT')

    client = Client(os.getenv('DATA_NODE_IP'), os.getenv('DATA_NODE_PORT'))
    client.UploadFile('test.txt')