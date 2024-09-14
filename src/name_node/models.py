from pydantic import BaseModel
from typing import List

class DataNode(BaseModel):
    Ip: str
    Port: str 
    CapacityMB: int
    IsActive: bool

class User(BaseModel):
    Username: str
    Password: str

