from src.client.client import Client
from src.cli.cli import CLI
from src.client.manage_blocks import *
from config import CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT
import argparse
from colorama import init, Fore, Style
from pyfiglet import Figlet


"""
def print_welcome_message():
    figlet = Figlet(font='small') 
    message = figlet.renderText('Welcome to HDFS CLI')
    print(Fore.BLUE + Style.BRIGHT + message + Style.RESET_ALL)


def main(username, password):
    client = Client(CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT)
    print('Calling Register method...')
    client.Register(username=username, password=password)

    print_welcome_message()

    cli = CLI(client)
    cli.start()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Client for the file management system.')
    parser.add_argument(
        '--username',
        required=True,
        help='Username for registration')
    parser.add_argument(
        '--password',
        required=True,
        help='Password for registration')

    args = parser.parse_args()

    main(username=args.username, password=args.password)

"""
if __name__ == '__main__':
    client = Client(CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT)
    print('Calling Register method...')
    client.Register(username='luisa', password='123')
    input('Press Enter to continue...')
    #client.UploadFile('/VID_20231023_120541.mp4',r'C:\Users\Luisa\Downloads\temp\VID_20231023_120541.mp4')
    client.DownloadFile('/VID_20231023_120541.mp4')
