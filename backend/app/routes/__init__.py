from dataclasses import dataclass
from enum import Enum as enum
<<<<<<< HEAD
=======

>>>>>>> 849c251ebeac847e0a8466922a682f4ab0fd3edf


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
<<<<<<< HEAD
    CHALLENGE_TIME_OUT = "CHALLENGE HAS EXPIRED"
    ERROR_MESSAGE = "Erreur interne du serveur. veuillez réessayer."

class WssTypeMessage(str, enum):
    ## message pour type d'action en wss
    CHALLENGE_CREATED = "CHALLENGE_CREATED"
    CHALLENGE_VERIFIED = "CHALLENGE_VERIFIED"
    CHALLENGE_EXPIRED = "CHALLENGE_EXPIRED"

=======
    CHALLENGE_EXPIRED = "CHALLENGE HAS EXPIRED"
    ERROR_MESSAGE = "Erreur interne du serveur. veuillez réessayer."

>>>>>>> 849c251ebeac847e0a8466922a682f4ab0fd3edf
    