from pydantic import BaseModel
from typing import List

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserLogin):
    read_drones: List[str]
    write_drones: List[str]
