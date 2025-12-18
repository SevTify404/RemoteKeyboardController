from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ChallengeResponse(BaseModel):
    """Schema pour envoyer les infos pour qrcode/pin au front"""

    challenge_id: UUID
    pin_code: str
    expires_at: datetime
    
    
class VerifyAuthRequest(BaseModel):
    """Schema pour verifier les infos lors du scan qrcode/saisie pin
    ici le PIN/challenge_id est optionnel si on veut s'authentifier par qrcode/PIN"""

    challenge_id: Optional[UUID]
    pin: Optional[str]
    
    
class VerifyAuthResponse(BaseModel):
    """Schema pour valider les données apres un succes de verification"""

    device_id: UUID
    device_token: str
    session_token: str
    session_expires_at: Optional[datetime]


