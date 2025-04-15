from pydantic import BaseModel
from typing import List

class User(BaseModel):
    username: str
    password: str
    read_drones: List[str]
    write_drones: List[str]
