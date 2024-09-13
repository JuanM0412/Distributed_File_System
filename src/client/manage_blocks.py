from config import MB_SIZE


def SplitFile(file_path: str, block_size: int = MB_SIZE):
    """
        SplitFile('/home/juan/Downloads/video.mp4', 128 * 1024 * 1024) this is an example of how to use this function, where 128 * 1024 * 1024 is 128MB.
    """

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


def JoinBlocks(output_file, blocks_list):
    """
        JoinBlocks('/home/juan/Downloads/archivo_original.mp4', ['/home/juan/Downloads/video_block_1.mp4', '/home/juan/Downloads/video_block_2.mp4', '/home/juan/Downloads/video_block_3.mp4']) this is an example of how to use this function.
    """
    with open(output_file, 'wb') as file:
        for block in blocks_list:
            with open(block, 'rb') as block_file:
                file.write(block_file.read())