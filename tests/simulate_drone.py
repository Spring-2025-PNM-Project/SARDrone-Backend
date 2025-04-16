import asyncio
import base64
import json
import requests
import threading
import time
import uvicorn
import websockets

from app.main import app


drone_id = "1"
drone_status = {
    "location": {"latitude": 1, "longitude": 1, "altitude": 5},
    "timestamp": 0,
    "status": "online"
}


# Drone behavior simulation
async def simulate_drone():
    # Simulate drone status updates
    i = 0

    while 1:
        i += 1
        drone_status["timestamp"] = int(time.time())

        response = requests.post(f"http://localhost:8001/drone/{drone_id}/info", json=drone_status).json()
        status_for_logging = drone_status.copy()
        if "image" in status_for_logging:
            status_for_logging["image"] = status_for_logging["image"][:10]
        print(f"[Drone] Sent Data: {status_for_logging}")

        # if instructions are present, print them
        for instruction in response["instructions"]:
            print(f"[Drone] Recieved Instruction: {instruction}")

            if instruction == "takeoff":
                drone_status["status"] = "flying"

                file_path = "tests/images/droneimage1.jpg"
                with open(file_path, "rb") as f:
                    image_bytes = f.read()
                    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
                drone_status["image"] = encoded_image
            elif instruction == "shutdown":
                drone_status["status"] = "shutdown"
                del drone_status["image"]

        await asyncio.sleep(1)
    
# Frontend behavior simulation
async def simulate_frontend():
    # Initially fetch any existing drone staus messages
    response = requests.get(f"http://localhost:8001/drone/{drone_id}/info")
    print(f"[Frontend] Initial Data: {len(response.json())} messages received")

    websocket_url = f"ws://localhost:8001/drone/{drone_id}/ws"

    async with websockets.connect(websocket_url) as websocket:
        # Simulate sending a takeoff command
        async def send_takeoff():
            await asyncio.sleep(1)
            await websocket.send("takeoff")
            print("[Frontend] Sent: takeoff")
        
        # Simulate sending a shutdown command
        async def send_shutdown():
            await asyncio.sleep(18)
            await websocket.send("shutdown")
            print("[Frontend] Sent: shutdown")

        asyncio.create_task(send_takeoff())
        asyncio.create_task(send_shutdown())

        # Recieve new status messages from backend
        while True:
            message = await websocket.recv()
            message = json.loads(message)
            if "image" in message:
                message["image"] = message["image"][:10]
            print(f"[Frontend] Received: {message}")

def start_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8001)

async def start_tasks():
    tasks = [
        simulate_drone(),
        simulate_frontend(),
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Start FastAPI in the background
    threading.Thread(target=start_fastapi, daemon=True).start()
    time.sleep(1)

    asyncio.run(start_tasks())
