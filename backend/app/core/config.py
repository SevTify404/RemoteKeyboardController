import os

from dotenv import load_dotenv

load_dotenv()  ## Permet de charger les configs depuis le fichier .env

# Environnement courant, on doit définir à LOCAL si on est en local et à PRODUCTION si on est sur le serveur
ENVIRONMENT: str= os.getenv("ENVIRONMENT")

# Clé secrete pour hashage et autres
SECRET_KEY: str = os.getenv("SECRET_KEY")
REFRESH_TOKEN_SECRET_KEY: str = os.getenv("REFRESH_TOKEN_SECRET_KEY", "refresh-cles-secrete")

# Algorithme de hashage qu'on va utiliser
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

# Minutes par défauts après lequel les tokens JWT s'expirent
ACCESS_TOKEN_EXPIRES_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", 240))
REFRESH_TOKEN_EXPIRES_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_MINUTES", 7 * 24 * 60))

## les IDs des cookies
ACCESS_IDENTIFIER: str = os.getenv("ACCESS_IDENTIFIER", "access_token")
REFRESH_IDENTIFIER: str = os.getenv("REFRESH_IDENTIFIER", "refresh_token")
