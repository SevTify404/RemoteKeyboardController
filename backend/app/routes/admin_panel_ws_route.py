from fastapi import WebSocket, WebSocketDisconnect
from fastapi.params import Depends

from app.auth.dependencies import local_only
from app.routes.ws_router import router
from app.services import app_websocket_manager
from app.schemas.admin_panel_ws_schema import WsPayloadMessage


@router.websocket("/panel", dependencies=[Depends(local_only)])
async def panel_websocket(websocket: WebSocket):
  
  await app_websocket_manager.connect_admin(websocket)

  try:
    while True:
      
      msg: WsPayloadMessage = await websocket.receive_json()

      if msg.is_related_to_pptCommand():
        app_websocket_manager.send_data_to_client(f"L'admin a traité l'action: {msg.command_action}")
      
      
  except WebSocketDisconnect:
    await app_websocket_manager.disconnect_admin("Le coté Admin Panel s'est déconnecter")

