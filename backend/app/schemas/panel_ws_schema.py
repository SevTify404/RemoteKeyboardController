from typing import Union
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.routes import WssTypeMessage


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
  data: Union[ChallengePayload, AuthSuccessPayload]

  class Config:
    # Permet de sérialiser les datetime en ISO format automatiquement
    json_encoders = {
      datetime: lambda v: v.isoformat()
    }