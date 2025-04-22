import asyncio
import base64
import requests
import time

from app.main import app


drone_id = "1"
drone_status = {
    "location": {"latitude": 37.3352, "longitude": -121.8811, "altitude": 5},
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

        response = requests.post(f"https://api.meritdrone.site/drone/{drone_id}/info", json=drone_status).json()
        status_for_logging = drone_status.copy()
        if "image" in status_for_logging:
            status_for_logging["image"] = status_for_logging["image"][:10]
        print(f"[Drone] Sent Data: {status_for_logging}")

        # if instructions are present, print them
        response["instructions"]=["takeoff"]
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


if __name__ == "__main__":
    asyncio.run(simulate_drone())
