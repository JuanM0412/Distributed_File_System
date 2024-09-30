class FileManager:
    def __init__(self, username, users_collection):
        self.username = username
        self.users_collection = users_collection

    def MakeDirectory(self, path: str):
        if self.username is None:
            print("Username is not set. Please register first")
            return

        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return

        directories = user_data['Directories']
        parts = path.strip('/').split('/')
        current_dir = self.FindDirectory(directories, "/")

        if current_dir is None:
            print("Root directory not found")
            return

        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                if not any(item['Name'] == part and item['IsDir']
                           for item in current_dir['Contents']):
                    current_dir['Contents'].append({
                        "Name": part,
                        "IsDir": True,
                        "Contents": []
                    })
                    print(f"Directory {path} created successfully.")
                else:
                    print(f"Directory {path} already exists.")
                break
            else:
                next_dir = next(
                    (item for item in current_dir['Contents'] if item['Name'] == part and item['IsDir']),
                    None)
                if next_dir is None:
                    next_dir = {
                        "Name": part,
                        "IsDir": True,
                        "Contents": []
                    }
                    current_dir['Contents'].append(next_dir)
                current_dir = next_dir

        self.users_collection.update_one(
            {"Username": self.username},
            {"$set": {"Directories": directories}}
        )

    def FindDirectory(self, directories, path):
        if path == '/':
            return next(
                (item for item in directories if item["Name"] == "/"), None)

        parts = path.strip('/').split('/')
        current_dir = next(
            (item for item in directories if item["Name"] == "/"), None)

        for part in parts:
            if current_dir is None:
                return None
            current_dir = next(
                (item for item in current_dir["Contents"] if item["IsDir"] and item["Name"] == part),
                None)

        return current_dir

    def RemoveDirectory(self, path: str, force: bool = False):
        if self.username is None:
            print("Username is not set. Please register first")
            return

        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return

        directories = user_data['Directories']
        parts = path.strip('/').split('/')

        if len(parts) == 1 and parts[0] == '':
            print("Cannot remove root directory")
            return

        parent_path = '/' + '/'.join(parts[:-1])
        dir_to_remove = parts[-1]

        parent_dir = self.FindDirectory(directories, parent_path)
        if parent_dir is None:
            print(f"Parent directory {parent_path} not found")
            return

        dir_index = next(
            (i for i,
             item in enumerate(
                 parent_dir['Contents']) if item['Name'] == dir_to_remove and item['IsDir']),
            None)

        if dir_index is None:
            print(f"Directory {path} not found")
            return

        dir_to_remove = parent_dir['Contents'][dir_index]

        del parent_dir['Contents'][dir_index]
        print(f"Directory {path} removed successfully")

        self.users_collection.update_one(
            {"Username": self.username},
            {"$set": {"Directories": directories}}
        )

    def ListDirectory(self, path: str):
        if self.username is None:
            print("Username is not set. Please register first")
            return

        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return

        directories = user_data['Directories']
        dir_to_list = self.FindDirectory(directories, path)

        if dir_to_list is None:
            print(f"Directory {path} not found")
            return

        print(f"Contents of {path}:")

        BLUE = '\033[94m'
        WHITE = '\033[97m'
        RESET = '\033[0m'

        for item in dir_to_list['Contents']:
            if item['IsDir']:
                print(f"{BLUE}{item['Name']}/{RESET}")
            else:
                print(f"{WHITE}{item['Name']}{RESET}")

    def DirectoryExists(self, path):
        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return False

        result = self.FindDirectory(user_data['Directories'], path)
        return result is not None

    def Put(self, path: str, file_name: str, file_size: int = 0):
        filename = file_name.replace('\\', '/').split('/')[-1]
        filename = "/" + filename
        print("Path in put:", path)
        print("File name in put:", filename)
        if self.username is None:
            print("Username is not set. Please register first")
            return

        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return

        directories = user_data['Directories']
        current_dir = self.FindDirectory(directories, path)

        if current_dir is None:
            print(f"Directory {path} not found")
            return

        if any(item['Name'] == filename and not item['IsDir']
               for item in current_dir['Contents']):
            print(f"File {filename} already exists in {path}")
            return

        current_dir['Contents'].append({
            "Name": filename,
            "IsDir": False,
            "Contents": None,
            "FileSize": file_size
        })

        self.users_collection.update_one(
            {"Username": self.username},
            {"$set": {"Directories": directories}}
        )

        print(f"File {filename} added to {path} successfully")

    def Rm(self, path: str, file_name: str):
        if self.username is None:
            print("Username is not set. Please register first")
            return

        user_data = self.users_collection.find_one({"Username": self.username})
        if not user_data:
            print("User not found")
            return

        directories = user_data['Directories']
        current_dir = self.FindDirectory(directories, path)

        if current_dir is None:
            print(f"Directory {path} not found")
            return

        file_index = next(
            (i for i,
             item in enumerate(
                 current_dir['Contents']) if item['Name'] == file_name and not item['IsDir']),
            None)

        if file_index is None:
            print(f"File {file_name} not found in {path}")
            return

        del current_dir['Contents'][file_index]
        print(f"File {file_name} removed from {path} successfully")

        self.users_collection.update_one(
            {"Username": self.username},
            {"$set": {"Directories": directories}}
        )
