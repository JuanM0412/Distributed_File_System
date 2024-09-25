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

    

    # SplitFile("/home/sebas/Downloads/test_tel.mp4")

    #JoinBlocks("join_test.mp4", ["/home/sebas/Downloads/test_tel_block_1.mp4", "/home/sebas/Downloads/test_tel_block_2.mp4", "/home/sebas/Downloads/test_tel_block_3.mp4"])

    client = Client(CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT)
    print('Calling Register method...')
    client.Register(username='sebas', password='Test123')
    input('Press Enter to continue...')

    cli = CLI(client)
    cli.start()



    client.MakeDirectory("/test_dir")
    client.MakeDirectory("/test_dir2")
    client.MakeDirectory("/test_dir/inside_test")
    client.MakeDirectory("/test_dir/inside_test/inside_test2")

    client.Put("/test_dir/inside_test", "file1.txt", 1234)
    client.Put("/test_dir/inside_test/inside_test2", "file2.txt", 1234)
    client.Put("/", "file3.txt", 1234)

    client.Rm("/test_dir/inside_test", "file11.txt")

    #client.ListDirectory("/test_dir")

    #client.RemoveDirectory("/test_dir", force=True)

    #client.UploadFile('test.txt')
    #client.DownloadFile('test1.txt')


"""

if __name__ == '__main__':
    client = Client(CLIENT_IP, CLIENT_PORT, SERVER_IP, SERVER_PORT)
    print('Calling Register method...')
    client.Register(username='JuanM04121', password='Test123')
    input('Press Enter to continue...')
    client.UploadFile('/Users/Luisa/Downloads/temp/VID_20231023_120541.mp4')
    #client.DownloadFile('test1.txt')