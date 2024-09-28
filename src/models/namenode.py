from pydantic import BaseModel
from typing import List

class Block(BaseModel):
    Master: str
    Slaves: List[str]

class MetaData(BaseModel):
    Name: str
    SizeMB: float
    Blocks: List[str]
    Owner: str
    