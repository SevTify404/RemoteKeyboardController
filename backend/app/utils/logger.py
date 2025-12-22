"""
Module de configuration du logging professionnel pour l'application RemoteKeyboardController.

Ce module met en place un système de logging centralizado et optimisé :
- Fichiers de logs avec rotation automatique
- Niveaux de logs configurables
- Format structuré et détaillé
- Filtrage intelligent du terminal
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

# Créer le répertoire des logs s'il n'existe pas
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configuration des fichiers de logs
MAIN_LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "errors.log"
AUTH_LOG_FILE = LOG_DIR / "auth.log"
WEBSOCKET_LOG_FILE = LOG_DIR / "websocket.log"
KEYBOARD_LOG_FILE = LOG_DIR / "keyboard.log"

# Constantes de configuration
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB par fichier
BACKUP_COUNT = 5  # Garder 5 fichiers de sauvegarde
LOG_FORMAT_DETAILED = '%(asctime)s | %(name)-20s | %(levelname)-8s | %(funcName)-20s:%(lineno)-4d | %(message)s'
LOG_FORMAT_SIMPLE = '%(asctime)s | %(levelname)-8s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logger(
    name: str,
    log_file: Path = None,
    level: int = logging.INFO,
    console_level: int = logging.WARNING,
) -> logging.Logger:
    """
    Configure un logger avec handlers pour fichier et console.
    
    Args:
        name: Nom du logger (généralement __name__)
        log_file: Chemin du fichier de log (None = fichier principal)
        level: Niveau de log pour le fichier
        console_level: Niveau de log pour la console
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Éviter les duplicatas si le logger existe déjà
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Handler pour fichier
    if log_file is None:
        log_file = MAIN_LOG_FILE
    
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(LOG_FORMAT_DETAILED, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Handler pour console - SEULEMENT pour les niveaux importants
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(LOG_FORMAT_SIMPLE, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Logger principal de l'application
app_logger = setup_logger(
    'app',
    log_file=MAIN_LOG_FILE,
    level=logging.DEBUG,
    console_level=logging.WARNING,
)

# Logger pour les authentifications
auth_logger = setup_logger(
    'auth',
    log_file=AUTH_LOG_FILE,
    level=logging.DEBUG,
    console_level=logging.WARNING,
)

# Logger pour les WebSockets
websocket_logger = setup_logger(
    'websocket',
    log_file=WEBSOCKET_LOG_FILE,
    level=logging.DEBUG,
    console_level=logging.ERROR,
)

# Logger pour le contrôle clavier
keyboard_logger = setup_logger(
    'keyboard',
    log_file=KEYBOARD_LOG_FILE,
    level=logging.DEBUG,
    console_level=logging.ERROR,
)

# Logger pour les erreurs (tous les niveaux erreur/critique)
error_logger = setup_logger(
    'errors',
    log_file=ERROR_LOG_FILE,
    level=logging.ERROR,
    console_level=logging.ERROR,
)


def get_logger(name: str) -> logging.Logger:
    """
    Obtient ou crée un logger pour un module spécifique.
    
    Args:
        name: Nom du logger (généralement __name__)
        
    Returns:
        Logger configuré
    """
    return logging.getLogger(name)


def log_startup_info():
    """Log les informations de démarrage de l'application."""
    app_logger.info("=" * 80)
    app_logger.info("🚀 RemoteKeyboardController Backend - DÉMARRAGE")
    app_logger.info("=" * 80)
    app_logger.info(f"Répertoire de logs: {LOG_DIR}")
    app_logger.info(f"Heure de démarrage: {datetime.now().strftime(DATE_FORMAT)}")
    app_logger.info("Logs détaillés disponibles dans les fichiers:")
    app_logger.info(f"  - {MAIN_LOG_FILE}")
    app_logger.info(f"  - {ERROR_LOG_FILE}")
    app_logger.info(f"  - {AUTH_LOG_FILE}")
    app_logger.info(f"  - {WEBSOCKET_LOG_FILE}")
    app_logger.info(f"  - {KEYBOARD_LOG_FILE}")
    app_logger.info("=" * 80)


def log_shutdown_info(reason: str = "Arrêt normal"):
    """Log les informations d'arrêt de l'application."""
    app_logger.info("=" * 80)
    app_logger.warning(f"⛔ RemoteKeyboardController Backend - ARRÊT ({reason})")
    app_logger.info(f"Heure d'arrêt: {datetime.now().strftime(DATE_FORMAT)}")
    app_logger.info("=" * 80)

