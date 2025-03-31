from pydantic import BaseModel
from typing import List

class DroneStatus(BaseModel):
    drone_id: str
    latitude: float
    longitude: float
    altitude: float
    status: str

class DroneStatusResponse(BaseModel):
    instructions: List[str]
