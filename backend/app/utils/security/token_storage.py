from typing import Dict, Optional
from datetime import UTC, datetime
from app.schemas.security_schema import DeviceTokenSchema, SessionTokenSchema


class DeviceStore:
    """
    stockage static des tokens gerener apres connexion vu qu'on a pas de db
    """

    def __init__(self):
        self._device_tokens: Dict[str, DeviceTokenSchema] = {}
        self._session_tokens: Dict[str, SessionTokenSchema] = {}


    def save_device_token(self, token: DeviceTokenSchema) -> None:
        self._device_tokens[token.token] = token

    def get_device_token(self, token: str) -> Optional[DeviceTokenSchema]:
        return self._device_tokens.get(token)

    def revoke_device_token(self, token: str) -> None:
        if token in self._device_tokens:
            del self._device_tokens[token]



    def save_session_token(self, token: SessionTokenSchema) -> None:
        self._session_tokens[token.token] = token

    def get_session_token(self, token: str) -> Optional[SessionTokenSchema]:
        session = self._session_tokens.get(token)

        if not session:
            return None

        if session.expires_at < datetime.now():
            del self._session_tokens[token]
            return None

        if not session.active:
            return None

        return session

    def revoke_session_token(self, token: str) -> None:
        session = self._session_tokens.get(token)
        if session:
            session.active = False
            del self._session_tokens[token]


    def cleanup_expired_sessions(self) -> None:
        now = datetime.now(UTC)
        expired_tokens = [
            token for token, session in self._session_tokens.items()
            if session.expires_at < now
        ]

        for token in expired_tokens:
            del self._session_tokens[token]
