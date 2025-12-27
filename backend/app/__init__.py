"""
RemoteKeyboardController - Application Backend
Module principal d'initialisation
"""

# Import du système de logging professionnel
from app.utils.logger import (
    app_logger,
    auth_logger,
    websocket_logger,
    keyboard_logger,
    error_logger,
    get_logger,
    log_startup_info,
    log_shutdown_info,
)

# Alias pour compatibilité rétroactive avec le code existant
app_loger = app_logger

__all__ = [
    'app_logger',
    'auth_logger',
    'websocket_logger',
    'keyboard_logger',
    'error_logger',
    'get_logger',
    'log_startup_info',
    'log_shutdown_info',
    'app_loger',  # Compatibilité
]
