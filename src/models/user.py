from pydantic import BaseModel

class User(BaseModel):
    Username: str
    Password: str
