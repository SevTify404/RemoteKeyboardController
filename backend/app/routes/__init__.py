from dataclasses import dataclass
from enum import Enum as enum



@dataclass
class ApiTags:
    AUTHENTIFICATION: str = "Authentification"
    
    
class ErrorMessages(str, enum):
    """Enum pour des messages de retour"""    

    CHALLENGE_USED = "CHALLENGE IS USED"
    UNEXIST_CHALLENGE = "CHALLENGE NOT FOUND"
    INVALID_PIN = "INVALID PIN"
    UNFOUND_PIN = "PIN NOT FOUND"
    BLOCKED_PIN = "PIN BLOCKED DUE TO MAX ATTEMPTS"
    CHALLENGE_EXPIRED = "CHALLENGE HAS EXPIRED"
    ERROR_MESSAGE = "Erreur interne du serveur. veuillez réessayer."

    