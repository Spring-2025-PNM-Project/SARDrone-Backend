from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from app.utils.connection_manager import ConnectionManager
from app.schemas.drone import DroneStatus, DroneStatusResponse
from app.services.database import get_database
from collections import defaultdict, deque
from datetime import datetime, timezone

router = APIRouter(
    prefix="/drone",
    tags=["Drone"]
)

manager = ConnectionManager()

instructions = defaultdict(deque)

db = get_database()

async def save_drone_status(status: dict):
    try:

        status["created_at"] = datetime.now(timezone.utc)    
        db["logs"].insert_one(status)
        
    except Exception as e:
        print("Error saving drone status:", e)

@router.websocket("/ws/{drone_id}")
async def websocket_endpoint(websocket: WebSocket, drone_id: str):
    await manager.connect(drone_id, websocket)

    try:
        while True:
            instruction = await websocket.receive_text()
            instructions[drone_id].append(instruction)
    except WebSocketDisconnect:
        manager.disconnect(drone_id, websocket)

@router.post("/status", response_model=DroneStatusResponse)
async def update_drone_status(status: DroneStatus, background_tasks: BackgroundTasks):
    await manager.send_drone_status(status.drone_id, status.model_dump(exclude_none=True))

    background_tasks.add_task(save_drone_status, status.model_dump(exclude_none=True))

    drone_instructions = []
    instructions_queue = instructions[status.drone_id]

    while instructions_queue:
        drone_instructions.append(instructions_queue.popleft())

    print(f"Returning instructions for drone {status.drone_id}: {drone_instructions}")
    return {"instructions": drone_instructions}