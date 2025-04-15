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

class ProcessedDroneStatus(DroneStatus):
    text: Optional[str] = None
    score: Optional[int] = None
    bounding_boxes: Optional[List[List[int]]] = None

class DroneStatusResponse(BaseModel):
    instructions: List[str]
