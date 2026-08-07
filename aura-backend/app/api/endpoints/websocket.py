from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.core.config import get_env_settings
from app.services.websocket_manager import ws_manager

router = APIRouter()


@router.websocket("/ws/downloads")
async def websocket_downloads_endpoint(websocket: WebSocket):
    env = get_env_settings()

    # Auth check before accepting the WebSocket handshake.
    if env.auth_enabled:
        token = websocket.query_params.get("token", "")
        if not token or token != env.auth_token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection open and listen for client messages (cancel, ping, etc.)
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
