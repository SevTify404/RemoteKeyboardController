import secrets
from datetime import datetime, timedelta
from uuid import uuid4, UUID

from app.schemas.security_schema import DeviceTokenSchema, SessionTokenSchema
from app.utils.security.token_storage import DeviceStore


class DeviceTokenManager:
  
  def __init__(self, tokens_store: DeviceStore):
    self._store = tokens_store
    self._ttl_minutes = timedelta(hours=1)


  def create_device_token(self) -> DeviceTokenSchema:
    """funct pour creer un jeton de token pour identifier un device(PC/Tel)"""

    dev_token = DeviceTokenSchema(
      device_id=uuid4(),
      token=secrets.token_urlsafe(32),
      created_at=datetime.now(),
      expires_at=datetime.now() + self._ttl_minutes,
    )


    self._store.save_device_token(dev_token)
    return dev_token


  def create_session_token(self, device_id: UUID) -> SessionTokenSchema:
    """funct pour creer un jeton de token pour identifier un device(PC/Tel)"""

    sess_token = SessionTokenSchema(
      session_id=uuid4(),
      device_id=device_id,
      token=secrets.token_urlsafe(32),
      created_at=datetime.now(),
      expires_at=datetime.now() + self._ttl_minutes
    )
    
    self._store.save_session_token(sess_token)

    return sess_token