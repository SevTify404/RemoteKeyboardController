from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.utils.security.token_storage import get


class ChallengeSchema(BaseModel):
  """schema pour valider les données d'un challenge"""

  challenge_id: UUID
  created_at: datetime
  expires_at: datetime
  used: bool = False


class PinSchema(BaseModel):
  """Schema pour valider un PIN generer"""

  pin_id: UUID
  challenge_id: UUID
  pin_code: str
  attempts: int = 0
  max_attempts: int = 3
  created_at: datetime
  expires_at: datetime
  blocked: bool = False
  used: bool = False
  

class DeviceTokenSchema(BaseModel):
  """Schema pour valider les données d'un device"""
  device_id: UUID
  token: str
  created_at: datetime
  expires_at: Optional[datetime]
  revoked: bool = False ## indique une expiration si true

  def revoke_device_token_session(self):
    self.revoked = True
    
  
  
class SessionTokenSchema(BaseModel):
  session_id: UUID
  device_id: UUID
  token: str
  created_at: datetime
  expires_at: Optional[datetime]
  active: bool = False ## indique une expiration si true