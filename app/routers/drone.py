from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends, HTTPException
from app.utils.connection_manager import ConnectionManager
from app.schemas.drone import DroneStatus, DroneStatusResponse, ProcessedDroneStatus
from app.services.database import get_database
from collections import defaultdict, deque
from datetime import datetime, timezone
from app.middleware.drone import verify_token
from bson import Binary
from typing import List
import jwt
from app.services.classification import ClassificationModel

import base64
import os
from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


router = APIRouter(
    prefix="/drone",
    tags=["Drone"]
)


instructions = defaultdict(deque)

db = get_database()
manager = ConnectionManager()
classificationmodel = ClassificationModel()


async def save_drone_status(drone_id, status: dict):
    try:
        status["timestamp"] = datetime.fromtimestamp(status["timestamp"], tz=timezone.utc)
        status["drone_id"] = drone_id

        if "image" in status:
            status["image"] = Binary(status["image"])

        await db["logs"].insert_one(status)
        
    except Exception as e:
        print("Error saving drone status:", e)

@router.websocket("/{drone_id}/ws")
async def websocket_endpoint(websocket: WebSocket, drone_id: str):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=4401)
        return
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        if "exp" in payload:
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            if exp < datetime.now(timezone.utc):
                await websocket.close(code=4401)
                return

        read_drones = payload.get("read_drones", [])
        write_drones = payload.get("write_drones", [])

        if drone_id not in read_drones and drone_id not in write_drones:
            await websocket.close(code=4403)
            return

        can_write = drone_id in write_drones

    except jwt.PyJWTError as e:
        await websocket.close(code=4401)
        return

    await manager.connect(drone_id, websocket)

    try:
        while True:
            instruction = await websocket.receive_text()

            if can_write:
                instructions[drone_id].append(instruction)
    except WebSocketDisconnect:
        manager.disconnect(drone_id, websocket)

@router.post("/{drone_id}/info", response_model=DroneStatusResponse)
async def update_drone_status(status: DroneStatus, background_tasks: BackgroundTasks, drone_id: str):
    if status.image:
        image_bytes = base64.b64decode(status.image)
        result = await classificationmodel.generate(image_bytes)

        status = ProcessedDroneStatus(
            **status.model_dump(),
            text=result["text"],
            score=result["score"],
            bounding_boxes=result["bounding_boxes"]
        )
    
    background_tasks.add_task(manager.send_drone_status, drone_id, status.model_dump(exclude_none=True))
    background_tasks.add_task(save_drone_status, drone_id, status.model_dump(exclude_none=True))

    drone_instructions = []
    instructions_queue = instructions[drone_id]

    while instructions_queue:
        drone_instructions.append(instructions_queue.popleft())

    return {"instructions": drone_instructions}

@router.get("/{drone_id}/info", response_model=List[ProcessedDroneStatus])
async def get_drone_status(drone_id: str, user_info: dict = Depends(verify_token(require_drone=True, access_type="read"))):
    results = await db["logs"].find({"drone_id": drone_id}).sort("timestamp", -1).limit(100).to_list(length=100)
    documents = list(
        results
    )
    
    for document in documents:
        del document["_id"]
        if isinstance(document["timestamp"], datetime):
            document["timestamp"] = int(document["timestamp"].timestamp())

    return documents
