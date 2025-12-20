
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

from app.services.keyboard_controller.availables import AvailableKeys


class AvailableMessageTypes(str, Enum):
    """Schema pour les types de messages disponibles dans le panneau de contrôle"""

    COMMAND = "command"                 # Envoi de commandes clavier
    ALERT = "alert"                     # Envoi d'alertes
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