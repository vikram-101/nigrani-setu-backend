from fastapi import WebSocket
from typing import List
import json


class ConnectionManager:
    """
    Keeps track of every Department Dashboard currently connected via
    WebSocket. When a new report or alert is created, `broadcast` pushes it
    to all of them instantly — this is what makes the dashboard "real-time"
    instead of something that only updates on page refresh.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event_type: str, payload: dict):
        message = json.dumps({"event": event_type, "data": payload})
        stale = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


manager = ConnectionManager()
