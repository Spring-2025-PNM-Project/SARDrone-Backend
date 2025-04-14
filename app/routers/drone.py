from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.connection_manager import ConnectionManager
from app.schemas.drone import DroneStatus, DroneStatusResponse
from collections import defaultdict, deque


router = APIRouter(
    prefix="/drone",
    tags=["Drone"]
)

manager = ConnectionManager()

instructions = defaultdict(deque)


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
async def update_drone_status(status: DroneStatus):
    await manager.send_drone_status(status.drone_id, status.model_dump(exclude_none=True))

    drone_instructions = []
    instructions_queue = instructions[status.drone_id]

    while instructions_queue:
        drone_instructions.append(instructions_queue.popleft())

    return {"instructions": drone_instructions}