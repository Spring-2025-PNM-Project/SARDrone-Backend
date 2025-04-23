import asyncio
import base64
import requests
import time
import os
import random 
from PIL import Image
import io

from app.main import app


drone_id = "1"
drone_status = {
    "location": {"latitude": 37.3352, "longitude": -121.8811, "altitude": 5},
    "timestamp": 0,
    "status": "online"
}


yes_human_folder = "images/yes_human"
no_human_folder = "images/no_human"

images = [os.path.join(yes_human_folder, f) for f in os.listdir(yes_human_folder)]
images.extend([os.path.join(no_human_folder, f) for f in os.listdir(no_human_folder)])

# Drone behavior simulation
async def simulate_drone():
    # Simulate drone status updates
    i = 0

    while 1:
        i += 1
        drone_status["timestamp"] = int(time.time())

        response = requests.post(f"https://api.meritdrone.site/drone/{drone_id}/info", json=drone_status)

        response = response.json()
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
                
                file_path = random.choice(images)

                with Image.open(file_path) as img:
                    # Resize to max 640px width (keep aspect ratio)
                    img.thumbnail((640, 640))

                    # Save to a bytes buffer in JPEG format with reduced quality
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=70)  # quality 0-100
                    buffer.seek(0)

                    # Encode to base64
                    encoded_image = base64.b64encode(buffer.read()).decode("utf-8")



                drone_status["image"] = encoded_image
            elif instruction == "shutdown":
                drone_status["status"] = "shutdown"
                del drone_status["image"]

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(simulate_drone())
