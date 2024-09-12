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
DOWNLOADS_DIR = os.getenv('DOWNLOADS_DIR')

CHUNK_SIZE = int(os.getenv('CHUNK_SIZE'))