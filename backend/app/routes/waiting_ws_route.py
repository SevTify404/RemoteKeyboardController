import asyncio

from fastapi.params import Depends

from app.routes import WssTypeMessage
from app.schemas.admin_panel_ws_schema import ChallengePayload, WsPayloadMessage
from .ws_router import router
from app.services import app_websocket_manager
from app.utils.security.all_instances import (
  pin_manager, challenge_manager, 
)

from fastapi import WebSocket, WebSocketDisconnect

from ..auth.dependencies import local_only
from .. import websocket_logger


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
      
      websocket_logger.debug(f"✅ Nouveau challenge généré et envoyé")

    except Exception as e:
      websocket_logger.exception(f"❌ Erreur lors de la génération du challenge: {e.__class__.__name__}: {e}")

    await asyncio.sleep(300)

@router.websocket("/waiting", dependencies=[Depends(local_only)])
async def waiting_connexion(websocket: WebSocket):
  """WebSocket pour les connexions en attente d'authentification (local uniquement)"""

  await app_websocket_manager.connect_waiting_for_connection(websocket)
  websocket_logger.info("✅ Connexion d'attente établie (waiting)")

  # Création de la tâche asynchrone de rafraîchissement
  refresh_task = asyncio.create_task(rotation_loop())
  websocket_logger.debug("🔄 Boucle de rafraîchissement des challenges démarrée")

  try: 
    while True:
      await websocket.receive_json()
      
  except WebSocketDisconnect:
    websocket_logger.info("🔌 Connexion d'attente fermée")
    await app_websocket_manager.disconnect_waiting_for_connection("La connexion n'a pu etre établie")
    refresh_task.cancel()
    websocket_logger.debug("🛑 Boucle de rafraîchissement arrêtée")
