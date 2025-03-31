from fastapi import APIRouter

from app.schemas.drone import DroneStatus, DroneStatusResponse


router = APIRouter(
    prefix="/drone",
    tags=["Drone"]
)


@router.post("/status", response_model=DroneStatusResponse)
async def update_drone_status(status: DroneStatus):
    return {"message": "Drone status updated successfully", "instructions": ["take off"]}
