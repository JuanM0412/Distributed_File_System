from pydantic import BaseModel
from typing import List, Optional


class DirectoryItem(BaseModel):
    Name: str
    IsDir: bool
    Contents: List['DirectoryItem'] = []
    FileSize: Optional[int] = None
