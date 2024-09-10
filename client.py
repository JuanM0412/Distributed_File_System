import threading
from src.client.client import *
from dotenv import load_dotenv


load_dotenv()


if __name__ == '__main__':
    client = Client(os.getenv('CLIENT_IP'), os.getenv('CLIENT_PORT'), os.getenv('SERVER_IP'), os.getenv('SERVER_PORT'))
    print('Calling Register method...')
    client.Register(username='JuanM0412', password='Test123')
    input('Press Enter to continue...')
    client.UploadFile('test.txt')