import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.active_connections.remove(conn)

    async def handle_connection(self, websocket: WebSocket) -> None:
        await self.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                await self._handle_message(msg, websocket)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def _handle_message(
        self, msg: dict[str, Any], websocket: WebSocket
    ) -> None:
        msg_type = msg.get("type")
        if msg_type == "play_clip":
            pass
        elif msg_type == "stop_clip":
            pass
        elif msg_type == "dtmf":
            pass


manager = ConnectionManager()
