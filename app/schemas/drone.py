from pydantic import BaseModel
from typing import List, Optional


class Location(BaseModel):
    latitude: float
    longitude: float
    altitude: float

class DroneStatus(BaseModel):
    location: Location
    timestamp: int
    status: str
    image: Optional[bytes] = None
    text: Optional[str] = None
    humanDetected: Optional[bool] = None

class DroneStatusResponse(BaseModel):
    instructions: List[str]
