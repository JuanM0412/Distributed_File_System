import os
from src.client.client import Client


class CLI:
    def __init__(self, client: Client):
        self.client = client
        self.current_path = "/"

    def start(self):
        while True:

            command = input(
                f'{self.client.username}{self.current_path} > ').strip()

            if command:
                parts = command.split()
                cmd = parts[0]
                args = parts[1:]

                if cmd == 'exit':
                    print("Exiting CLI...")
                    break
                elif cmd == 'cd':
                    self.cd(args)
                elif cmd == 'ls':
                    self.ls(args)
                elif cmd == 'mkdir':
                    self.mkdir(args)
                elif cmd == 'rm':
                    self.rm(args)
                elif cmd == 'put':
                    self.put(args)
                elif cmd == 'clear':
                    self.clear()
                elif cmd == 'get':
                    self.get(args)
                else:
                    print(f"Command '{cmd}' not found.")

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def cd(self, args):
        if len(args) != 1:
            print("Usage: cd <directory>")
            return

        new_dir = args[0]

        if new_dir == "..":
            if self.current_path != "/":
                self.current_path = "/".join(
                    self.current_path.rstrip('/').split('/')[:-1]) or "/"
            return

        if new_dir.startswith('/'):
            new_path = new_dir
        else:
            new_path = os.path.join(
                self.current_path,
                new_dir).replace(
                '//',
                '/')

        if not self.client.GetFileManager().DirectoryExists(new_path):
            print(f"Directory {new_path} does not exist.")
        else:
            self.current_path = new_path

    def ls(self, args):
        path = self.current_path if len(args) == 0 else args[0]
        self.client.GetFileManager().ListDirectory(path)

    def mkdir(self, args):
        if len(args) != 1:
            print("Usage: mkdir <directory_name>")
            return
        dir_name = args[0]
        self.client.GetFileManager().MakeDirectory(os.path.join(self.current_path, dir_name))

    def rm(self, args):
        if len(args) != 2:
            print("Usage: rm <directory/file> <name>")
            return
        path = args[0]
        file_name = args[1]
        virtual_path = os.path.join(self.current_path, file_name)
        if path == 'dir':
            force = False
            if (len(args) == 3):
                force = bool(args[3].split('=')[1])
            files = self.client.GetFileManager().ListFiles(file_name)
            self.client.DeleteFiles(files)
            self.client.GetFileManager().RemoveDirectory(file_name, force)
        else:
            print("Deleting file...")
            self.client.DeleteFile(file_name)
            self.client.GetFileManager().Rm(self.current_path, virtual_path)

    def put(self, args):
        if len(args) != 1:
            print("Usage: put <file_name>")
            return
        file_name = args[0]
        file = os.path.basename(file_name)
        virtual_path = os.path.join(self.current_path, file)
        print("Uploading file...")
        self.client.UploadFile(virtual_path, file_name)
        self.client.GetFileManager().Put(
            self.current_path,
            virtual_path,
            os.path.getsize(file_name))

    def get(self, args):
        if len(args) != 1:
            print("Usage: get <file_name>")
            return
        file_name = args[0]
        print("Downloading file...")
        self.client.DownloadFile(file_name)

    def list_files(self, args):
        if len(args) != 1:
            print("Usage: list_files <directory>")
            return
        path = args[0]
        files = self.client.GetFileManager().ListFiles(path)
        if files:
            print(f"Files in {path}:")
            for file in files:
                print(file)
        else:
            print(f"No files found in {path}")
