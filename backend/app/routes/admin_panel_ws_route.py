from fastapi import WebSocket, WebSocketDisconnect
from fastapi.params import Depends

from app.auth.dependencies import local_only
from app.routes.ws_router import router
from app.services import app_websocket_manager


@router.websocket("/panel", dependencies=[Depends(local_only)])
async def panel_websocket(websocket: WebSocket):
  
  await app_websocket_manager.connect_admin(websocket)

  try:
    while True:
      # On fait rien pour le moment, juste garder la connexion ouverte
      await websocket.receive()
      continue
      
      
  except WebSocketDisconnect:
    await app_websocket_manager.disconnect_admin("Le coté Admin Panel s'est déconnecter")

