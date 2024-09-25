from src.rpc.data_node import data_node_pb2
from config import MB_IN_BYTES
import os

def GetFileChunks(file_path):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(MB_IN_BYTES)
            if not chunk:
                break
            yield chunk


def SaveChunksToFile(chunks, filename):
    with open(filename, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)


def GetFileSize(file_path):
    size = os.path.getsize(file_path)
    return float(size / MB_IN_BYTES)


def BytesConverter(block_size):
    return block_size * MB_IN_BYTES

