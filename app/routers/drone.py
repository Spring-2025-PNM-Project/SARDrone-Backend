from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from app.utils.connection_manager import ConnectionManager
from app.schemas.drone import DroneStatus, DroneStatusResponse
from app.services.database import get_database
from collections import defaultdict, deque
from datetime import datetime, timezone
from bson import Binary

router = APIRouter(
    prefix="/drone",
    tags=["Drone"]
)

manager = ConnectionManager()

instructions = defaultdict(deque)

db = get_database()

async def save_drone_status(drone_id, status: dict):
    try:
        status["timestamp"] = datetime.fromtimestamp(status["timestamp"], tz=timezone.utc)
        status["drone_id"] = drone_id

        if "image" in status:
            status["image"] = Binary(status["image"])
            
        db["logs"].insert_one(status)
        
    except Exception as e:
        print("Error saving drone status:", e)

@router.websocket("/{drone_id}/ws")
async def websocket_endpoint(websocket: WebSocket, drone_id: str):
    await manager.connect(drone_id, websocket)

    try:
        while True:
            instruction = await websocket.receive_text()
            instructions[drone_id].append(instruction)
    except WebSocketDisconnect:
        manager.disconnect(drone_id, websocket)

@router.post("/{drone_id}/status", response_model=DroneStatusResponse)
async def update_drone_status(status: DroneStatus, background_tasks: BackgroundTasks, drone_id: str):
    background_tasks.add_task(manager.send_drone_status, drone_id, status.model_dump(exclude_none=True))
    background_tasks.add_task(save_drone_status, drone_id, status.model_dump(exclude_none=True))

    drone_instructions = []
    instructions_queue = instructions[drone_id]

    while instructions_queue:
        drone_instructions.append(instructions_queue.popleft())

    return {"instructions": drone_instructions}
 
@router.get("/{drone_id}/status")
async def get_drone_status(drone_id: str):
        logs = list(
            db["logs"]
            .find({"drone_id": drone_id})
            .sort("timestamp", -1)  
            .limit(100)
        )
        
        for log in logs:
            log["_id"] = str(log["_id"])  

        return logs