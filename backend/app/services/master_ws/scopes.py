from dataclasses import dataclass
from typing import Optional

from fastapi import WebSocket


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
