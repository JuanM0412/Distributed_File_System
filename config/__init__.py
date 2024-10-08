from dotenv import load_dotenv
import os


load_dotenv()


MONGO_CLIENT = os.getenv('MONGO_CLIENT')
DB_NAME = os.getenv('DB_NAME')

CLIENT_IP = os.getenv('CLIENT_IP')
CLIENT_PORT = os.getenv('CLIENT_PORT')

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = os.getenv('SERVER_PORT')

DATA_NODE_IP = os.getenv('DATA_NODE_IP')
DATA_NODE_PORT = os.getenv('DATA_NODE_PORT')
DATA_NODE_CAPACITY_MB = float(os.getenv('DATA_NODE_CAPACITY_MB'))

PARTITIONS_DIR = os.getenv('PARTITIONS_DIR')
DOWNLOADS_DIR = os.getenv('DOWNLOADS_DIR')

MB_IN_BYTES = int(os.getenv('MB_IN_BYTES'))
SIZE_BLOCK = int(os.getenv('SIZE_BLOCK'))
