import threading, os
from src.client.client import *
from dotenv import load_dotenv
from config.env import SERVER_IP, SERVER_PORT


load_dotenv()


if __name__ == '__main__':
    #client = Client(os.getenv('DATA_NODE_IP'), os.getenv('DATA_NODE_PORT'))
    #client.UploadFile('test.txt')
    client = Client(SERVER_IP, SERVER_PORT)
    print('Calling Register method...')
    client.Register(username='JuanM0412', password='Test123')