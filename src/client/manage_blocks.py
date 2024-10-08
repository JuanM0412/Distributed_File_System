from config import SIZE_BLOCK
from utils.utils import BytesConverter


def SplitFile(file_path: str):
    block_size = BytesConverter(SIZE_BLOCK)
    block_names = []

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
            block_names.append(block_name)

            with open(block_name, 'wb') as block:
                block.write(data)

            block_number += 1

    return block_names


def JoinBlocks(output_file: str, blocks_list: list):
    with open(output_file, 'wb') as file:
        for block in blocks_list:
            with open(block, 'rb') as block_file:
                file.write(block_file.read())
