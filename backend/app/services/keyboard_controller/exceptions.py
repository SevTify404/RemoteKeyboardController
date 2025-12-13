class TouchNotExistError(Exception):
    """Exception levée lorsque la touche spécifiée n'est pas trouvée dans le mapping."""
    pass

class NoActiveControllerError(Exception):
    """Exception levée lorsqu'aucun contrôleur actif n'est disponible pour effectuer une action."""
    pass

class ControllerAlreadyRunningError(Exception):
    """Exception levée lorsqu'un contrôleur est déjà en cours d'exécution."""
    pass