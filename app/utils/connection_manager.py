import base64
from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, drone_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[drone_id].append(websocket)

    def disconnect(self, drone_id: str, websocket: WebSocket):
        if websocket in self.active_connections[drone_id]:
            self.active_connections[drone_id].remove(websocket)
            if not self.active_connections[drone_id]:
                del self.active_connections[drone_id]

    async def send_drone_status(self, drone_id: str, data: dict):
        if isinstance(data.get("image"), bytes):
            data["image"] = data["image"].decode("utf-8")

        connections = self.active_connections.get(drone_id, [])
        for websocket in connections:
            try:
                await websocket.send_json(data)
            except Exception as e:
                print('Error sending message:', e)
                self.disconnect(drone_id, websocket)
