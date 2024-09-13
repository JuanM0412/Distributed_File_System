from src.rpc.data_node import data_node_pb2
from config import CHUNK_SIZE
import os


def GetFileChunks(file_path):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield data_node_pb2.Chunk(buffer=chunk)


def SaveChunksToFile(chunks, filename):
    with open(filename, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)


def GetFileSize(file_path):
    size = os.path.getsize(file_path)
    return float(size / CHUNK_SIZE) # CHUNK_SIZE is 1024*1024 bytes = 1MB