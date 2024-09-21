from pydantic import BaseModel
from typing import List


class DataNode(BaseModel):
    Ip: str
    Port: str
    CapacityMB: int
    IsActive: bool
    Blocks: List[str]
