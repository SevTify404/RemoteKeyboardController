from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from app import websocket_logger
from app.services.master_ws.aliases import SideAlias
from app.services.master_ws.scopes import AvailableWebSocketScopes


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
        websocket_logger.info("✅ Admin panel connecté")

    async def connect_client(self, websocket: WebSocket) -> None:
        """Connecte un client via WebSocket"""
        await websocket.accept()
        self._scopes.client_side = websocket
        websocket_logger.info("✅ Client connecté")

    async def connect_waiting_for_connection(self, websocket: WebSocket):
        """Connecte le côté en attente de connexion via WebSocket"""
        await websocket.accept()
        self._scopes.waiting_for_connection_side = websocket
        websocket_logger.info("✅ Écran d'attente connecté")

    @property
    def client_is_connected(self) -> bool:
        """Vérifie si un client est connecté"""
        return self._scopes.is_client_connected

    @property
    def admin_is_connected(self) -> bool:
        """Vérifie si le côté admin est connecté"""
        return self._scopes.is_admin_connected

    @property
    def is_waiting_for_connection(self) -> bool:
        """Vérifie si une connexion d'authentification est en cours"""
        return self._scopes.is_waiting_for_connection

    async def close_all_connection(self):
        """Ferme toutes les connexions WebSocket de l'app"""
        websocket_logger.info("🔌 Fermeture de toutes les connexions WebSocket")
        await self._close_a_connection(SideAlias.ADMIN_SIDE)
        await self._close_a_connection(SideAlias.WAITING_FOR_CONNECTION_SIDE)
        await self._close_a_connection(SideAlias.CLIENT_SIDE)

        self._scopes.reset()
        websocket_logger.debug("✅ Toutes les connexions fermées et état réinitialisé")


    async def disconnect_admin(self, disconnect_reason: str = None) -> None:
        """Déconnecte le côté admin"""
        websocket_logger.info(f"🔌 Déconnexion admin: {disconnect_reason or 'Sans raison'}")
        await self._close_a_connection(SideAlias.ADMIN_SIDE, disconnect_reason=disconnect_reason)
        self._scopes.remove_admin_connection()

    async def disconnect_client(self, disconnect_reason: str = None) -> None:
        """Déconnecte le client"""
        websocket_logger.info(f"🔌 Déconnexion client: {disconnect_reason or 'Sans raison'}")
        await self._close_a_connection(SideAlias.CLIENT_SIDE, disconnect_reason=disconnect_reason)
        self._scopes.remove_user_connection()

    async def disconnect_waiting_for_connection(self, disconnect_reason: str = None) -> None:
        """Déconnecte l'écran d'attente"""
        websocket_logger.info(f"🔌 Déconnexion écran d'attente: {disconnect_reason or 'Sans raison'}")
        await self._close_a_connection(SideAlias.WAITING_FOR_CONNECTION_SIDE, disconnect_reason=disconnect_reason)
        self._scopes.remove_waiting_for_connection()

    async def send_data_to_admin(self, data: Any, is_json: bool=False) -> None:
        """
        Envoie des données au côté admin via WebSocket
        Args:
            data: Les données à envoyer, un dictionnaire si is_json est True
            is_json: True si les données doivent etre envoyées en json, dans ce cas data doit etre un dico ou un objet serializable

        Returns:
            None
        """

        try:
            return await self._send_data_to_a_websocket(data, target=SideAlias.ADMIN_SIDE, is_json=is_json)
        except WebSocketDisconnect:         # Fallback si l'admin n'est pas connecté on loggue juste un warning avec la data
            websocket_logger.warning(f"⚠️ Admin panel inactif, message perdu : {data}")

    async def send_data_to_client(self, data: Any, is_json: bool=False) -> None:
        """
        Envoie des données au client via WebSocket
        Args:
            data: Les données à envoyer, un dictionnaire si is_json est True
            is_json: True si les données doivent etre envoyées en json ,dans ce cas data doit etre un dico ou un objet serializable

        Returns:
            None
        Raises:
            WebSocketException: Si le client n'est pas/plus connecté
        """

        await self._send_data_to_a_websocket(data, target=SideAlias.CLIENT_SIDE, is_json=is_json)

    async def send_data_to_waiting(self, data: Any, is_json: bool = False) -> None:
        """
        Envoie des données au côté 'waiting_for_connection_side' via WebSocket.
        Args:
            data: Les données à envoyer, un dictionnaire si is_json est True
            is_json: True si les données doivent etre envoyées en json ,dans ce cas data doit etre un dico ou un objet serializable

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

        await self._send_data_to_a_websocket(data, target=SideAlias.ADMIN_SIDE)

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

        await self._send_data_to_a_websocket(data, target=SideAlias.WAITING_FOR_CONNECTION_SIDE)

    async def send_binary_data_to_waiting(self, data: bytes) -> None:
        """
        Envoie des données binaires au côté 'waiting_for_connection_side' via WebSocket.
        Args:
            data: Les données binaires à envoyer.

        Raises:
            WebSocketDisconnect: Si le côté 'waiting' n'est pas/plus connecté.
        """

        await self._send_data_to_a_websocket(data, target=SideAlias.WAITING_FOR_CONNECTION_SIDE)


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
            raise WebSocketDisconnect(code=1001, reason=f"{target.title()} side is not connected")

        try:
            if is_json:
                await websocket.send_json(data)
            elif isinstance(data, str):
                await websocket.send_text(data)
            elif isinstance(data, bytes):
                await websocket.send_bytes(data)
            else:
                raise ValueError("Data must be str, bytes, or JSON-serializable when is_json is True")
        except WebSocketDisconnect as e:
            websocket_logger.debug(f"⚠️ Déconnexion détectée lors de l'envoi vers {target}")
            if target == SideAlias.ADMIN_SIDE:
                self._scopes.remove_admin_connection()
            elif target == SideAlias.CLIENT_SIDE:
                self._scopes.remove_user_connection()
            elif target == SideAlias.WAITING_FOR_CONNECTION_SIDE:
                self._scopes.remove_waiting_for_connection()
            raise e

    async def _close_a_connection(self, target: SideAlias, disconnect_reason: str = None) -> None:
        websocket = None
        if target == SideAlias.ADMIN_SIDE:
            websocket = self._scopes.admin_side
        elif target == SideAlias.CLIENT_SIDE:
            websocket = self._scopes.client_side
        elif target == SideAlias.WAITING_FOR_CONNECTION_SIDE:
            websocket = self._scopes.waiting_for_connection_side

        if websocket is None:
            return None

        try:
            return await websocket.close(reason=disconnect_reason)
        except (WebSocketDisconnect, RuntimeError):
            pass