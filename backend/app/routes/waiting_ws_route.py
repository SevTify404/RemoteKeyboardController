import asyncio
import logging
import traceback
from app.routes import WssTypeMessage
from app.schemas.admin_panel_ws_schema import ChallengePayload, WsPayloadMessage
from .ws_router import router
from app.services import app_websocket_manager
from app.utils.security.all_instances import (
  pin_manager, challenge_manager, 
)

from fastapi import WebSocket, WebSocketDisconnect


## schedulers pour rafraichir le changement sur PC
async def rotation_loop():
  """Tâche de fond pour rafraîchir le QR/PIN toutes les 5 min"""
  while app_websocket_manager.is_waiting_for_connection:
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
      
      await app_websocket_manager.send_data_to_waiting(
        message.model_dump(mode="json"), 
        is_json=True
      )
      
    except Exception as e:
      print(f"Exception {e.__class__.__name__}: {e}")
      logging.exception("Une erreur s'est produite")
      traceback.print_exc()

    await asyncio.sleep(300)


@router.websocket(
  "/ws/waiting"
)
async def waiting_connexion(websocket: WebSocket):
  
  await app_websocket_manager.connect_waiting_for_connection(websocket)

  ## creation de la tache asynchrone
  refresh_task = asyncio.create_task(rotation_loop())

  try: 
    
    while True:
      
      await websocket.receive_json()
      
  except WebSocketDisconnect:
    await app_websocket_manager.disconnect_waiting_for_connection("La connexion n'a pu etre établie")
    refresh_task.cancel()