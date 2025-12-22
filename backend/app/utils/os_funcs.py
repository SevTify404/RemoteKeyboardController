import socket
from enum import Enum
from platform import system


class OperatingSystem(str, Enum):
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"
    UNKNOWN = "unknown"


def detect_os() -> OperatingSystem:
    """Détecte le système d'exploitation courant"""
    sys = system().lower()
    if sys == "linux":
        return OperatingSystem.LINUX
    if sys == "windows":
        return OperatingSystem.WINDOWS
    if sys == "darwin":
        return OperatingSystem.MACOS
    return OperatingSystem.UNKNOWN


def get_lan_ip():
    """Obtient l'adresse IP locale de la machine sur le LAN"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Pas de connexion réelle, juste pour connaître l'interface utilisée
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
