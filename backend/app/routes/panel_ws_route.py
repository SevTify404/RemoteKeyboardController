from fastapi import WebSocket, WebSocketDisconnect
from app.routes.ws_router import router
from app.services import app_websocket_manager


@router.websocket("/ws/panel")
async def panel_websocket(websocket: WebSocket):
  
  await app_websocket_manager.connect_admin(websocket)
  try:
    while True:
      
      await websocket.receive_json()
      
  except WebSocketDisconnect:
    await app_websocket_manager.disconnect_admin("Le coté Admin Panel s;est déconnecter")

