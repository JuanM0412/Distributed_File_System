from pydantic import BaseModel
from typing import List

class DirectoryItem(BaseModel):
    Name: str
    IsDir: bool
    Contents: List['DirectoryItem'] = []