
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.services.keyboard_controller.availables import AvailableKeys


class AvailableMessageTypes(str, Enum):
    """Schema pour les types de messages disponibles dans le panneau de contrôle"""

    COMMAND = "command"                 # Envoi de commandes clavier
    DISCONNECT  = "disconnect"          # Notification de déconnexion
    STATUS_UPDATE = "status_update"     # Mise à jour du statut
    TYPING = "typing"                   # Requete de saisie de texte


class PayloadFormat(BaseModel):
    """Schema pour la structure de la charge utile"""

    command: Optional[AvailableKeys] = Field(
        None,
        description="Commande clavier à exécuter, conformementt aux cmd disponible dans AvailableKeys"
    )

    message: Optional[str] = Field(
        None,
        description="Message d'alerte ou de statut"
    )

    text_to_type: Optional[str] = Field(
        None,
        description="Texte à saisir pour le type de message 'typing'"
    )


class ControlPanelWSMessage(BaseModel):
    """Schema principale pour les messages WebSocket du panneau de contrôle"""

    message_type: AvailableMessageTypes = Field(
        ...,
        description="Type de message envoyé depuis le panneau de contrôle"
    )

    payload: Optional[PayloadFormat] = Field(
        None,
        description="Charge utile associée au message"
    )


class OutControlPanelWSMessage(BaseModel):
    """Schéma de sortie des commandes vers le panel admin"""

    succes: bool
    data: Optional[ControlPanelWSMessage]
    error: Optional[str]

    @classmethod
    def success_response(cls, data: ControlPanelWSMessage):
        """
        Methode pour instancier une reponse de succes
        Args:
            data: Données à retourner
        Returns:
            Une instance de OutControlPanelWSMessage
        """
        return cls(succes=True, data=data, error=None)

    # Cette methode permettra de renvoyer les reponse d'erreur directement depuis les classes filles
    @classmethod
    def error_response(cls, error_message: str):
        """
        Methode pour instancier une réponse d'échec
        Args:
            error_message: Le message d'erreur à retourner

        Returns:
            Une instance de OutControlPanelWSMessage
        """
        return cls(succes=False, data=None, error=error_message)