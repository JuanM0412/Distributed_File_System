from pydantic import BaseModel


class DataNode(BaseModel):
    ip: str
    port: int 
    storage: int
    

class User(BaseModel):
    username: str
    password: str