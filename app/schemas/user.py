from pydantic import BaseModel
from typing import List, Literal, Union

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserLogin):
    read_drones: List[str]
    write_drones: List[str]


class LoginResponse(BaseModel):
    status: Literal["success"]
    token: str

class UserResponse(BaseModel):
    username: str
    read_drones: List[str]
    write_drones: List[str]
