from src.rpc.data_node import data_node_pb2
from config import MB_IN_BYTES
import os

def GetFileChunks(file_path):
    print("File path in UTILS:", file_path)
    chunks = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read()
            if not chunk:
                break
            chunks.append(chunk)
    return chunks


def SaveChunksToFile(chunks, filename):
    with open(filename, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)


def GetFileSize(file_path):
    size = os.path.getsize(file_path)
    return float(size / MB_IN_BYTES)


def BytesConverter(block_size):
    return block_size * MB_IN_BYTES

