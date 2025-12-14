from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any
from fastapi import WebSocket, WebSocketDisconnect

@dataclass
class AvailableWebSocketScopes:
    """Classe pour définir les scopes WebSocket disponibles dans l'application"""
    admin_side: Optional[WebSocket] = None
    client_side: Optional[WebSocket] = None
    waiting_for_connection_side: Optional[WebSocket] = None

    @property
    def is_admin_connected(self) -> bool:
        """Vérifie si le côté admin est connecté"""
        return self.admin_side is not None

    @property
    def is_client_connected(self) -> bool:
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

class SideAlias(str, Enum):
    ADMIN_SIDE = "admin"
    CLIENT_SIDE = "client"
    WAITING_FOR_CONNECTION_SIDE = "waiting"

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
        return self._scopes.is_client_connected

    @property
    def admin_is_connected(self) -> bool:
        """Vérifie si le côté admin est connecté"""
        return self._scopes.is_admin_connected

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



    async def _send_data_to_a_websocket(self, data: Any, target: SideAlias, is_json: bool = False) -> None:
        """
        Fonction générique pour envoyer des données à un websocket précis.
        Args:
            data: Les données à envoyer
            target: Le côté cible
            is_json: True si les données doivent être envoyées en jsno

        Raises:
            WebSocketDisconnect: Si le websocket ciblé n'est pas/plus connecté.
        """
        websocket = None
        if target == SideAlias.ADMIN_SIDE:
            websocket = self._scopes.admin_side
        elif target == SideAlias.CLIENT_SIDE:
            websocket = self._scopes.client_side
        elif target == SideAlias.WAITING_FOR_CONNECTION_SIDE:
            websocket = self._scopes.waiting_for_connection_side

        if websocket is None:
            raise WebSocketDisconnect(code=1001, reason=f"{target.capitalize()} side is not connected")

        try:
            if is_json:
                await websocket.send_json(data)
            else:
                await websocket.send_text(data)
        except WebSocketDisconnect as e:
            if target == SideAlias.ADMIN_SIDE:
                self._scopes.remove_admin_connection()
            elif target == SideAlias.CLIENT_SIDE:
                self._scopes.remove_user_connection()
            elif target == SideAlias.WAITING_FOR_CONNECTION_SIDE:
                self._scopes.remove_waiting_for_connection()
            raise e

    async def send_data_to_admin(self, data: Any, is_json: bool=False) -> None:
        """
        Envoie des données au côté admin via WebSocket
        Args:
            data: Les données à envoyer, un dictionnaire si is_json est True
            is_json: True si les données doivent etre envoyées en json, dans ce cas data doit etre un dico

        Returns:
            None
        Raises:
            WebSocketException: Si l'admin n'est pas/plus connecté
        """
        if self._scopes.is_admin_connected:
            await self._send_data_to_a_websocket(data, target=SideAlias.ADMIN_SIDE, is_json=is_json)
        else:
            raise WebSocketDisconnect(code=1001, reason="Admin side is not connected")

    async def send_data_to_client(self, data: Any, is_json: bool=False) -> None:
        """
        Envoie des données au client via WebSocket
        Args:
            data: Les données à envoyer, un dictionnaire si is_json est True
            is_json: True si les données doivent etre envoyées en json,dans ce cas data doit etre un dico

        Returns:
            None
        Raises:
            WebSocketException: Si le client n'est pas/plus connecté
        """
        if self._scopes.is_client_connected:
            await self._send_data_to_a_websocket(data, target=SideAlias.CLIENT_SIDE, is_json=is_json)
        else:
            raise WebSocketDisconnect(code=1001, reason="Admin side is not connected")

    async def send_data_to_waiting(self, data: Any, is_json: bool = False) -> None:
        """
        Envoie des données au côté 'waiting_for_connection_side' via WebSocket.
        Args:
            data: Les données à envoyer.
            is_json: True si les données doivent être envoyées en json.

        Raises:
            WebSocketDisconnect: Si le côté 'waiting' n'est pas/plus connecté.
        """
        await self._send_data_to_a_websocket(data, target=SideAlias.WAITING_FOR_CONNECTION_SIDE, is_json=is_json)

    async def send_binary_data_to_admin(self, data: bytes) -> None:
        """
        Envoie des données binaires au côté admin via WebSocket
        Args:
            data: Les données binaires à envoyer

        Returns:
            None
        Raises:
            WebSocketException: Si l'admin n'est pas/plus connecté
        """
        if self._scopes.is_admin_connected:
            await self._send_data_to_a_websocket(data, target=SideAlias.ADMIN_SIDE)
        else:
            raise WebSocketDisconnect(code=1001, reason="Admin side is not connected")

    async def send_binary_data_to_client(self, data: bytes) -> None:
        """
        Envoie des données binaires au client via WebSocket
        Args:
            data: Les données binaires à envoyer

        Returns:
            None
        Raises:
            WebSocketException: Si le client n'est pas/plus connecté
        """
        if self._scopes.is_client_connected:
            await self._send_data_to_a_websocket(data, target=SideAlias.WAITING_FOR_CONNECTION_SIDE)
        else:
            raise WebSocketDisconnect(code=1001, reason="Client side is not connected")

    async def send_binary_data_to_waiting(self, data: bytes) -> None:
        """
        Envoie des données binaires au côté 'waiting_for_connection_side' via WebSocket.
        Args:
            data: Les données binaires à envoyer.

        Raises:
            WebSocketDisconnect: Si le côté 'waiting' n'est pas/plus connecté.
        """
        await self._send_data_to_a_websocket(data, target=SideAlias.WAITING_FOR_CONNECTION_SIDE)


app_websocket_connection_manager = AppWebSocketConnectionManager()