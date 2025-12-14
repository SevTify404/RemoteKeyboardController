from typing import Optional
from pynput.keyboard import Controller, Key, KeyCode
from logging import getLogger
from asyncio import sleep
from app.services.keyboard_controller import exceptions
from app.services.keyboard_controller.available_keys import AvailableKeyboardKeys

logger = getLogger(__name__)

class CustomKeyboardController:
    """Classe singleton personnalisé pour controler le clavier par rapport à l'app dans son ensemble."""

    def __init__(self):
        self._keys: dict[str, KeyCode] = {
            AvailableKeyboardKeys.UP_KEY: Key.up,
            AvailableKeyboardKeys.DOWN_KEY: Key.down,
            AvailableKeyboardKeys.LEFT_KEY: Key.left,
            AvailableKeyboardKeys.RIGHT_KEY: Key.right,
            AvailableKeyboardKeys.ENTER_KEY: Key.enter,
            AvailableKeyboardKeys.MUTE_KEY: Key.media_volume_mute,
            AvailableKeyboardKeys.VOLUME_UP_KEY: Key.media_volume_up,
            AvailableKeyboardKeys.VOLUME_DOWN_KEY: Key.media_volume_down
        }
        self._is_a_controller_running: bool = False
        self._active_controller: Optional[Controller] = None
        self._current_client_alias: Optional[str] = None
        self.REALASE_DURATION: float = 0.01

    @property
    def is_a_controller_running(self) -> bool:
        """Indique si un controleur est actuellement actif."""
        return self._is_a_controller_running

    @property
    def current_client_alias(self) -> Optional[str]:
        """Retourne le nom du client actuellement connecté."""
        return self._current_client_alias

    def start_controller(self, client_alias: str) -> bool:
        """
        Démarre un nouveau contrôleur de clavier pour le client spécifié.
        Args:
            client_alias: Le nom du client qui demande le contrôle du clavier.

        Returns:
            bool: True si le contrôleur a été démarré avec succès, une exception sinon.

        Raises:
            ControllerAlreadyRunningException: Si un autre contrôleur est déjà en cours d'exécution.
        """
        if self._is_a_controller_running:
            raise exceptions.ControllerAlreadyRunningException(
                f"Un autre client ({self._current_client_alias}) contrôle déjà le clavier"
            )

        self._active_controller = Controller()

        self._is_a_controller_running = True

        self._current_client_alias = client_alias

        logger.info(f"Le client '{client_alias}' a démarré le contrôle du clavier.")

        return True

    def stop_controller(self) -> None:
        """
        Arrête le contrôleur de clavier actif.
        """
        if not self._is_a_controller_running:
            logger.warning("Aucun client actif à arrêter.")
            return

        self._active_controller = None
        self._is_a_controller_running = False
        self._current_client_alias = None

        logger.info(f"Client '{self._current_client_alias}' déconnecté du controle du clavier.")

    async def press_special_key(self, key_name: AvailableKeyboardKeys) -> None:
        """
        Simule la pression d'une touche du clavier.
        Args:
            key_name: Le nom de la touche à presser (doit être dans self._keys).

        Raises:
            NoActiveControllerException: Si aucun contrôleur n'est actif.
            KeyError: Si la touche spécifiée n'existe pas.
        """
        if not self._is_a_controller_running or self._active_controller is None:
            raise exceptions.NoActiveControllerException("Aucun contrôleur actif pour presser une touche.")

        if key_name not in self._keys:
            raise exceptions.TouchNotExistException(f"La touche '{key_name}' n'existe pas dans les touches définies.")

        key_to_press = self._keys[key_name]

        self._active_controller.press(key_to_press)

        await sleep(self.REALASE_DURATION)

        self._active_controller.release(key_to_press)


        logger.info(f"Touche '{key_name}' pressée par le client '{self._current_client_alias}'.")

    def press_alphanumeric_key(self, char: str) -> None:
        """
        Simule la pression d'une touche alphanumérique du clavier.
        Args:
            char: Le caractère alphanumérique à presser.

        Raises:
            NoActiveControllerException: Si aucun contrôleur n'est actif.
        """
        if not self._is_a_controller_running or self._active_controller is None:
            raise exceptions.NoActiveControllerException("Aucun contrôleur actif pour presser une touche.")

        try:
            self._active_controller.type(char)
        except self._active_controller.InvalidCharacterException as e:
            logger.info(f"Le caractère '{char}' n'est pas valide pour la saisie : {e}")
            return

        logger.info(f"Touche alphanumérique '{char}' pressée par le client '{self._current_client_alias}'.")

app_keyboard_controller = CustomKeyboardController()