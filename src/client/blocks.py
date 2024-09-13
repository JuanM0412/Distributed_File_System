import os


def SplitFile(file_path: str, block_size: int):
    with open(file_path, 'rb') as file:
        block_number = 1
        
        while True:
            data = file.read(block_size)
            
            if not data:
                break
            
            split_name = file_path.split('.')
            file_name = split_name[0]
            file_extension = split_name[1]
            block_name = f'{file_name}_block_{block_number}.{file_extension}'
            
            with open(block_name, 'wb') as fragmento:
                fragmento.write(data)
            
            print(f'Block {block_number} was created: {block_name}')
            
            block_number += 1