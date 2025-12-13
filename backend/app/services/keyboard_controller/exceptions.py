class TouchNotExistException(Exception):
    """Exception levée lorsque la touche spécifiée n'est pas trouvée dans le mapping."""
    pass

class NoActiveControllerException(Exception):
    """Exception levée lorsqu'aucun contrôleur actif n'est disponible pour effectuer une action."""
    pass

class ControllerAlreadyRunningException(Exception):
    """Exception levée lorsqu'un contrôleur est déjà en cours d'exécution."""
    pass