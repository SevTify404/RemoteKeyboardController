from typing import Union

from fastapi import APIRouter

from app import auth_logger
from app.schemas.admin_panel_ws_schema import WsPayloadMessage, AuthSuccessPayload
from app.schemas.auth_schema import VerifyAuthResponse, VerifyAuthRequest
from app.schemas.base_schema import ApiBaseResponse
from app.services import app_websocket_manager
from app.utils.security.all_instances import (
    pin_manager, challenge_manager, device_manager
)
from . import ApiTags, ErrorMessages, WssTypeMessage

router = APIRouter(prefix="/auth", tags=[ApiTags.AUTHENTIFICATION])


@router.post(
  "/verify",
  response_model=ApiBaseResponse[Union[VerifyAuthResponse, str]]
)
async def verify_auth(chall_data: VerifyAuthRequest) -> ApiBaseResponse[Union[VerifyAuthResponse, str]]:
  """Route pour permettre de verifier les authentification(qrcode/pin). c'est vers
  cette route que vous allez envoyer les données"""

  try:
    auth_logger.debug(f"Tentative de vérification - Challenge ID: {bool(chall_data.challenge_id)}, PIN: {bool(chall_data.pin)}")

    if chall_data.challenge_id:
      auth_logger.debug(f"Vérification par Challenge ID: {chall_data.challenge_id}")

      if not challenge_manager.is_valid(chall_data.challenge_id):
        error_msg = f"{ErrorMessages.UNEXIST_CHALLENGE} or {ErrorMessages.CHALLENGE_USED} or {ErrorMessages.CHALLENGE_TIME_OUT}"
        auth_logger.warning(f"Challenge invalide: {chall_data.challenge_id}")
        return ApiBaseResponse.success_response(error_msg)

      challenge_manager.mark_challenge_as_used(chall_data.challenge_id)
      auth_logger.info(f"✅ Challenge validé et marqué comme utilisé: {chall_data.challenge_id}")

    elif chall_data.pin: 
      auth_logger.debug("Vérification par PIN (masqué pour sécurité)")

      if not pin_manager.is_valid_pin(chall_data.pin):
        error_msg = f"{ErrorMessages.INVALID_PIN.value} or {ErrorMessages.BLOCKED_PIN.value} or {ErrorMessages.UNFOUND_PIN.value}"
        auth_logger.warning("Tentative de PIN invalide")
        return ApiBaseResponse.error_response(error_msg)

      pin_obj = pin_manager.get_pin(chall_data.pin)
        
      if not challenge_manager.is_valid(pin_obj.challenge_id):
        error_msg = f"{ErrorMessages.CHALLENGE_TIME_OUT} or {ErrorMessages.CHALLENGE_USED}"
        auth_logger.warning("Challenge associé au PIN invalide")
        return ApiBaseResponse.success_response(error_msg)

      pin_manager.mark_pin_as_used(pin_obj.pin_code)
      auth_logger.info("✅ PIN validé et marqué comme utilisé")

    else:
      auth_logger.warning("Tentative de vérification sans Challenge ID ni PIN")
      return ApiBaseResponse.success_response("Aucune données fournie. Veuillez réessayer")

    # Génération des tokens
    device_token = device_manager.create_device_token()
    session_token = device_manager.create_session_token(device_token.device_id)
    
    auth_logger.info(f"✅ Authentification réussie - Device ID: {device_token.device_id}")

    data = VerifyAuthResponse(
      device_id=device_token.device_id,
      device_token=device_token.token,
      session_token=session_token.token,
      session_expires_at=session_token.expires_at
    )
    
    # Notification WebSocket à l'écran d'attente
    succes_data = AuthSuccessPayload(
      device_id=data.device_id,
      session_expires_at=data.session_expires_at
    )
    
    success_message = WsPayloadMessage(
      type=WssTypeMessage.CHALLENGE_VERIFIED,
      data=succes_data
    )
    
    await app_websocket_manager.send_data_to_waiting(
      data=success_message.model_dump(mode="json"),
      is_json=True
    )
    auth_logger.debug("Notification envoyée au WebSocket d'attente")

    await app_websocket_manager.disconnect_waiting_for_connection()
    auth_logger.debug("WebSocket d'attente déconnecté")

    return ApiBaseResponse.success_response(data)
  
  except Exception as e:
    error_msg = f"Erreur lors de l'authentification: {e.__class__.__name__}: {e}"
    auth_logger.exception(error_msg)
    return ApiBaseResponse.error_response(ErrorMessages.ERROR_MESSAGE)
    
  