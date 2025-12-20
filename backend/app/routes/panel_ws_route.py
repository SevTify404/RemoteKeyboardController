import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from app.routes import WssTypeMessage
from app.routes.ws_router import router
from app.services import app_websocket_manager
from app.schemas.panel_ws_schema import ChallengePayload, WsPayloadMessage
from app.utils.security.all_instances import (
  pin_manager, challenge_manager, 
)


## schedulers pour rafraichir le changement sur PC
async def rotation_loop():
  """Tâche de fond pour rafraîchir le QR/PIN toutes les 5 min"""
  while app_websocket_manager.admin_is_connected:
    try:
      
      challenge = challenge_manager.create_challenge()
      pin = pin_manager.create_pin(challenge.challenge_id)

      challenge_payload = ChallengePayload(
        challenge_id=challenge.challenge_id,
        pin=pin.pin_code,
        expires_at=challenge.expires_at
      )
      
      message = WsPayloadMessage(
        type=WssTypeMessage.CHALLENGE_CREATED,
        data=challenge_payload
      )
      
      await app_websocket_manager.send_data_to_admin(
        message.model_dump(mode="json"), 
        is_json=True
      )
      
    except Exception as e:
      print(f"Exception {e.__class__.__name__}: {e}")

    await asyncio.sleep(300)


@router.websocket("/ws/panel")
async def panel_websocket(websocket: WebSocket):
  
  await app_websocket_manager.connect_admin(websocket)

  ## creation de la tache asynchrone
  refresh_task = asyncio.create_task(rotation_loop())

  try:
    while True:
      
      await websocket.receive_json()
      
  except WebSocketDisconnect:
    refresh_task.cancel()
    await app_websocket_manager.disconnect_admin("Le coté Admin Panel s'est déconnecter") 

