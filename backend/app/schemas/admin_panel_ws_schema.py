from typing import Any, Self, Union, Optional
from pydantic import BaseModel, model_validator
from uuid import UUID
from datetime import datetime

from app.routes import WssTypeMessage
from app.schemas.control_panel_ws_schema import ControlPanelWSMessage
from app.services.keyboard_controller.availables import AvailableKeys


class ChallengePayload(BaseModel):
  """schema pour valider la creation d'un challenge en ws"""

  challenge_id: UUID
  pin: str
  expires_at: datetime


class AuthSuccessPayload(BaseModel):
  """schema pour valider un succes d'authentification"""

  device_id: UUID
  session_expires_at: datetime


class WsPayloadMessage(BaseModel):
  """schema pour valider les données JSON qui seront envoyer par ws"""

  type: WssTypeMessage
  data: Union[ChallengePayload, AuthSuccessPayload, ControlPanelWSMessage]

  
  def is_related_to_authentification(self) -> bool:
    """Verifie si les infos recu concerne l'authetification"""

    auth_types = [
      WssTypeMessage.CHALLENGE_CREATED,
      WssTypeMessage.CHALLENGE_VERIFIED
    ]

    return self.type in auth_types

  
  def is_related_to_pptCommand(self) -> bool:
    """Verifie si les données recu concerne les commandes PPT"""
    
    return self.type == WssTypeMessage.PPT_COMMAND


  @property
  def command_action(self) -> Optional[AvailableKeys]:
    """Return l'action que le client veut faire ex: UP, DOWN, etc"""

    if isinstance(self.data, ControlPanelWSMessage):
      return self.data.action
    
    return None

  
  @property
  def command_value(self) -> Any:
    """Return l'action que le client veut faire ex: UP, DOWN, etc"""

    if isinstance(self.data, ControlPanelWSMessage):
      return self.data.value
    
    return None
  
  
  @model_validator(mode='after')
  def verify_type_matching_data(self) -> Self:
    """Comme ici certains data dependent de type, il faut s'assurer que le type de WssPayload
    match avec la data egalement envoyer. ce decorateur s'execute automatiquement a 
    chaque instance de cette classe"""

    if self.is_related_to_authentification() and not isinstance(self.data, ChallengePayload):
      raise ValueError(f"{WssTypeMessage.CHALLENGE_CREATED} doit etre une correspondre a ChallengePayload")

    if self.is_related_to_pptCommand() and not isinstance(self.data, ControlPanelWSMessage):
      raise ValueError(f"{WssTypeMessage.PPT_COMMAND} doit etre une correspondre a CommandPayload")

    return self


  class Config:
    # Permet de sérialiser les datetime en ISO format automatiquement
    json_encoders = {
      datetime: lambda v: v.isoformat(),
      UUID: lambda v: str(v)
    }
    
