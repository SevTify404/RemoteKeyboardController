import os

from dotenv import load_dotenv

from app.utils.os_funcs import detect_os, get_lan_ip

load_dotenv()  ## Permet de charger les configs depuis le fichier .env

# Type de système d'exploitation
OS_TYPE = detect_os()

# Adresse IP locale de la machine
LOCAL_IP: str = get_lan_ip()

# Environnement courant, on doit définir à LOCAL si on est en local et à PRODUCTION si on est sur le serveur
ENVIRONMENT: str= os.getenv("ENVIRONMENT", "LOCAL")