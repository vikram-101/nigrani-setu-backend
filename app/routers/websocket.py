from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.security import decode_access_token
from app.ws_manager import manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/dashboard")
async def dashboard_socket(websocket: WebSocket, token: str = Query(...)):
    """
    The Department Dashboard opens this once on load:
      new WebSocket(`wss://<api-host>/ws/dashboard?token=<jwt>`)
    Every time an inspector submits a report (or an alert is raised), every
    connected dashboard gets pushed the new data instantly — no polling.
    """
    payload = decode_access_token(token)
    if payload is None or payload.get("role") not in ("admin", "department"):
        await websocket.close(code=4401)
        return

    await manager.connect(websocket)
    try:
        while True:
            # We don't expect messages from the client, but this keeps the
            # connection alive and lets us detect a clean disconnect.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
