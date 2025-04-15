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
        drone_status["timestamp"] = i

        response = requests.post(f"http://localhost:8001/drone/{drone_id}/status", json=drone_status).json()
        print(f"[Drone] Sent Data: {json.dumps(drone_status)}")

        # if instructions are present, print them
        for instruction in response["instructions"]:
            print(f"[Drone] Recieved Instruction: {instruction}")

            if instruction == "takeoff":
                drone_status["status"] = "flying"
                fake_bytes = b"Hello, drone!"
                encoded = base64.b64encode(fake_bytes).decode("utf-8")
                drone_status["image"] = encoded
                drone_status["text"] = "There is a human"
                drone_status["humanDetected"] = True
            elif instruction == "shutdown":
                drone_status["status"] = "shutdown"
                del drone_status["image"]
                del drone_status["text"]
                del drone_status["humanDetected"]

        await asyncio.sleep(1)
    
# Frontend behavior simulation
async def simulate_frontend():
    # Initially fetch any existing drone staus messages
    # (WIP)
    # response = requests.get(f"http://localhost:8001/drone/{drone_id}/status")

    websocket_url = f"ws://localhost:8001/drone/{drone_id}/ws"

    async with websockets.connect(websocket_url) as websocket:
        # Simulate sending a takeoff command
        async def send_takeoff():
            await asyncio.sleep(6)
            await websocket.send("takeoff")
            print("[Frontend] Sent: takeoff")
        
        # Simulate sending a shutdown command
        async def send_shutdown():
            await asyncio.sleep(12)
            await websocket.send("shutdown")
            print("[Frontend] Sent: shutdown")

        asyncio.create_task(send_takeoff())
        asyncio.create_task(send_shutdown())

        # Recieve new status messages from backend
        while True:
            message = await websocket.recv()
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
