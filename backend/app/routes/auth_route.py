import traceback
from fastapi import APIRouter
from . import ApiTags, ErrorMessages, WssTypeMessage
from typing import Union
from app.schemas.base_schema import ApiBaseResponse
from app.schemas.auth_schema import VerifyAuthResponse, VerifyAuthRequest, ChallengeResponse
from app.services.master_ws.websocket_conn_manager import app_websocket_connection_manager
from app.utils.security.all_instances import (
  pin_manager, challenge_manager, device_manager
)


router = APIRouter("/auth", ApiTags.AUTHENTIFICATION)


@router.get(
  "/challenge",
  response_model=ApiBaseResponse[Union[ChallengeResponse, str]]
)
def create_challenge() -> ApiBaseResponse[Union[ChallengeResponse, str]]:
  """Route pour creer un challenge. Vous allez recevoir le id du 
  challenge(utiliser ca pour le qrcode) et aussi le pin a afficher pour alternative"""

  try:
    
    challenge = challenge_manager.create_challenge()
    pin = pin_manager.create_pin(challenge.challenge_id)
    
    data = ChallengeResponse(
      challenge_id=challenge.challenge_id,
      pin_code=pin,
      expires_at=challenge.expires_at
    )
    
    return ApiBaseResponse.success_response(data)

  except Exception as e:
    traceback.print_exc()
    print(f"Exception {e.__class__.__name__}: {e}")
    return ApiBaseResponse.error_response(ErrorMessages.ERROR_MESSAGE)


@router.post(
  "/verify",
  response_model=ApiBaseResponse[Union[VerifyAuthResponse, str]]
)
async def verify_auth(chall_data: VerifyAuthRequest) -> ApiBaseResponse[Union[VerifyAuthResponse, str]]:
  """Route pour permettre de verifier les authentification(qrcode/pin). c'est vers 
  cette route que vous allez envoyer les données"""
  
  try:
    
    if chall_data.challenge_id:
      
      if not challenge_manager.is_valid(chall_data.challenge_id):
        return ApiBaseResponse.success_response(
          f"{ErrorMessages.UNEXIST_CHALLENGE} or {ErrorMessages.CHALLENGE_USED} or {ErrorMessages.CHALLENGE_TIME_OUT}"
        )
        
      challenge_manager.mark_challenge_as_used(chall_data.challenge_id)
      
    elif chall_data.pin: 
      
      if not pin_manager.is_valid_pin(chall_data.pin):
        return ApiBaseResponse.success_response(
          f"{ErrorMessages.INVALID_PIN} or {ErrorMessages.BLOCKED_PIN} or {ErrorMessages.UNFOUND_PIN}"
        )
        
      pin_obj = pin_manager.get_pin(chall_data.pin)
        
      if not challenge_manager.is_valid(pin_obj.challenge_id):
        return ApiBaseResponse.success_response(
          f"{ErrorMessages.CHALLENGE_TIME_OUT} or {ErrorMessages.CHALLENGE_USED}"
        )  
      
      pin_manager.mark_pin_as_used(pin_obj.pin_code)
      
    else:
      return ApiBaseResponse.success_response(
        f"Aucune données fournie. Veuillez réessayer"
      ) 

    device_token = device_manager.create_device_token()
    session_token = device_manager.create_session_token(device_token.device_id)
    
    data = VerifyAuthResponse(
      device_id=device_token.device_id,
      device_token=device_token.token,
      session_token=session_token.token,
      session_expires_at=session_token.expires_at
    )
    
    await app_websocket_connection_manager.send_data_to_admin(
      {
       "type": WssTypeMessage.CHALLENGE_VERIFIED,
       "payload": {
         "device_id": str(data.device_id)
       }
      },
      is_json=True
    )
    
    return ApiBaseResponse.success_response(data)
  
  except Exception as e:
    traceback.print_exc()
    print(f"Exception {e.__class__.__name__}: {e}")
    return ApiBaseResponse.error_response(ErrorMessages.ERROR_MESSAGE)
    
  