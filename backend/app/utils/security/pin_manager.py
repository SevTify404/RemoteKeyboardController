from datetime import datetime, timedelta
import secrets
import hmac
from uuid import uuid4

from typing import Union
from uuid import UUID

from app.schemas.security_schema import PinSchema


class PinManager:
    """class pour gerer les oepration sur le PIN"""

    def __init__(self, time_to_live: int = 5):
        self.ttl_minutes = time_to_live
        self._pins: dict[UUID, PinSchema] = {}


    def get_pin(self, pin_code: str) -> Union[PinSchema, None]:
      """funct pour lire un PIN generer"""

      for pin in self._pins.values():
        if pin.pin_code == pin_code:
          return pin
        
      return None
    
    
    def create_pin(self, challenge_id: UUID) -> PinSchema:
      """funct pour creer un PIN"""

      created_pin = PinSchema(
        pin_id=uuid4(),
        challenge_id=challenge_id,
        pin_code=f"{secrets.randbelow(1_000_000):06}",
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(minutes=self.ttl_minutes)
      )
      
      self._pins[created_pin.pin_id] = created_pin
      
      return created_pin
      
      
      
    def is_valid_pin(self, given_pin: str) -> bool:
      """funct pr verifer la validiter d'un PIN/et aussi le blocquer si 
      trop de tentative"""

      pin = self.get_pin(given_pin)
      
      if not pin or pin.used or pin.blocked:
        return False
      
      if pin.expires_at < datetime.now():
        return False
      
      if not hmac.compare_digest(given_pin, pin.pin_code):
        pin.attempts += 1
        if pin.attempts > pin.max_attempts:
          pin.blocked = True
        
        return False
      
      return True
    
    
    def mark_pin_as_used(self, pin_code: str) -> None:
      """funct pour marquer un pin comme deja utiliser"""

      pin = self.get_pin(pin_code)

      if pin: 
        pin.used = True
        
      return None
        