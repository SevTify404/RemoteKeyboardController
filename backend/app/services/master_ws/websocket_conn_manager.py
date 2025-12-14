from dataclasses import dataclass
from typing import Optional, Any
from fastapi import WebSocket, WebSocketDisconnect

@dataclass
class AvailableWebSocketScopes:
    """Classe pour définir les scopes WebSocket disponibles dans l'application"""
    admin_side: Optional[WebSocket] = None
    client_side: Optional[WebSocket] = None
    waiting_for_connection_side: Optional[WebSocket] = None

    @property
    def is_admin_connect(self) -> bool:
        """Vérifie si le côté admin est connecté"""
        return self.admin_side is not None

    @property
    def is_user_connect(self) -> bool:
        """Vérifie si un client est connecté"""
        return self.client_side is not None

    @property
    def is_waiting_for_connection(self) -> bool:
        """Vérifie si on est en attente d'une connexion"""
        return self.waiting_for_connection_side is not None

    def remove_user_connection(self):
        """Supprime la connexion du client"""
        self.client_side = None

    def remove_admin_connection(self):
        """Supprime la connexion du côté admin"""
        self.admin_side = None

    def remove_waiting_for_connection(self):
        """Supprime la connexion en attente"""
        self.waiting_for_connection_side = None


    def reset(self):
        """Réinitialise toutes les connexions WebSocket"""
        self.admin_side = None
        self.client_side = None
        self.waiting_for_connection_side = None


class AppWebSocketConnectionManager:
    """Classe Sinleton pour gérer les connexions WebSocket dans l'application."""
    _instance = None

    # Singleton pattern implementation
    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppWebSocketConnectionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._scopes = AvailableWebSocketScopes()

    async def connect_admin(self, websocket: WebSocket) -> None:
        """Connecte le côté admin via WebSocket"""
        await websocket.accept()
        self._scopes.admin_side = websocket             # On fait une copie par référence pour une utilisation ultérieure

    async def connect_client(self, websocket: WebSocket) -> None:
        """Connecte un client via WebSocket"""
        await websocket.accept()
        self._scopes.client_side = websocket        # On fait une copie par référence pour une utilisation ultérieure


    async def connect_waiting_for_connection(self, websocket: WebSocket):
        """Connecte le côté en attente de connexion via WebSocket"""
        await websocket.accept()
        self._scopes.waiting_for_connection_side = websocket

    @property
    def client_is_connected(self) -> bool:
        """Vérifie si un client est connecté"""
        return self._scopes.is_user_connect

    @property
    def admin_is_connected(self) -> bool:
        """Vérifie si le côté admin est connecté"""
        return self._scopes.is_admin_connect

    async def disconnect_admin(self, disconnect_reason: str = None) -> None:
        """Déconnecte le côté admin"""
        try:
            await self._scopes.admin_side.close(reason=disconnect_reason)
        except (AttributeError, WebSocketDisconnect):
            pass

        self._scopes.remove_admin_connection()

    async def disconnect_client(self, disconnect_reason: str = None) -> None:
        """Déconnecte le client"""
        try:
            await self._scopes.client_side.close(reason=disconnect_reason)
        except (AttributeError, WebSocketDisconnect):
            pass

        self._scopes.remove_user_connection()

    async def disconnect_waiting_for_connection(self, disconnect_reason: str = None) -> None:
        """La D"""
        try:
            await self._scopes.waiting_for_connection_side.close(reason=disconnect_reason)
        except (AttributeError, WebSocketDisconnect):
            pass

        self._scopes.remove_waiting_for_connection()



    async def _send_data_to_a_websocket(self, data: Any, to_admin: bool, is_json: bool=False) -> None:
        """
        Fonction pour envoyer des données à un websocket précis
        Args:
            data: Les données à envoyer
            to_admin: True si les données doivent etre envoyées au côté admin, False pour le client
            is_json: True si les données doivent etre formattées et envoyées en json

        Returns:
            None
        Raises:
            WebSocketException: Si le websocket ciblé n'est pas/plus connecté
        """

        try:
            if is_json:
                if to_admin:
                    return await self._scopes.admin_side.send_json(data)

                return await self._scopes.client_side.send_json(data)

            else:
                if to_admin:
                    return await self._scopes.admin_side.send_text(data)

                return await self._scopes.client_side.send_text(data)

        except WebSocketDisconnect as e:
            self._scopes.remove_admin_connection()
            raise e
        except AttributeError:
            # L'objet websocket est n'est pas référencé
            raise WebSocketDisconnect(code=1001, reason="Side is not connected")

    async def send_data_to_admin(self, data: Any, is_json: bool=False) -> None:
        """
        Envoie des données au côté admin via WebSocket
        Args:
            data: Les données à envoyer
            is_json: True si les données doivent etre envoyées en json

        Returns:
            None
        Raises:
            WebSocketException: Si l'admin n'est pas/plus connecté
        """
        if self._scopes.is_admin_connect:
            await self._send_data_to_a_websocket(data, to_admin=True, is_json=is_json)
        else:
            raise WebSocketDisconnect(code=1001, reason="Admin side is not connected")

    async def send_data_to_client(self, data: Any, is_json: bool=False) -> None:
        """
        Envoie des données au client via WebSocket
        Args:
            data: Les données à envoyer
            is_json: True si les données doivent etre envoyées en json

        Returns:
            None
        Raises:
            WebSocketException: Si le client n'est pas/plus connecté
        """
        if self._scopes.is_admin_connect:
            await self._send_data_to_a_websocket(data, to_admin=False, is_json=is_json)
        else:
            raise WebSocketDisconnect(code=1001, reason="Admin side is not connected")



app_websocket_connection_manager = AppWebSocketConnectionManager()