from pydantic import BaseModel
from .directory_item import DirectoryItem
from typing import List

class User(BaseModel):
    Username: str
    Password: str
    Directories : List[DirectoryItem] = []
