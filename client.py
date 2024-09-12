from src.client.client import *
from config import CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT


if __name__ == '__main__':
    client = Client(CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT)
    print('Calling Register method...')
    client.Register(username='JuanM0412', password='Test123')
    input('Press Enter to continue...')
    client.UploadFile('test.txt')
    client.DownloadFile('test1.txt')