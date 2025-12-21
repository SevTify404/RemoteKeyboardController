from asyncio import Lock
from typing import Optional
from pynput.keyboard import Controller
from app.services.keyboard_controller import exceptions
from app.services.keyboard_controller._custom_touchs import KeyboardTouchs
from app.services.keyboard_controller.availables import AvailableKeys, key_map
from app.main import app_loger

class CustomKeyboardController:
    """Classe singleton personnalisé pour controler le clavier par rapport à l'app dans son ensemble."""

    def __init__(self):
        self._keys: dict[AvailableKeys, KeyboardTouchs] = key_map
        self._is_a_controller_running: bool = False
        self._active_controller: Optional[Controller] = None
        self._current_client_alias: Optional[str] = None

        self._state_lock = Lock()  # Lock pour proteger l'état du contrôleur (thread safing)



    @property
    def current_client_alias(self) -> Optional[str]:
        """Retourne le nom du client actuellement connecté."""
        return self._current_client_alias

    async def _verify_controller_running(self) -> Controller:
        """Vérifie que le contrôleur est actif et retourne l'instance."""
        if not self._is_a_controller_running or self._active_controller is None:
            raise exceptions.NoActiveControllerException("Aucun contrôleur actif pour presser une touche")
        return self._active_controller

    async def start_controller(self, client_alias: str) -> bool:
        """
        Démarre un nouveau contrôleur de clavier pour le client spécifié.
        Args:
            client_alias: Le nom du client qui demande le contrôle du clavier.

        Returns:
            bool: True si le contrôleur a été démarré avec succès, une exception sinon.

        Raises:
            ControllerAlreadyRunningException: Si un autre contrôleur est déjà en cours d'exécution.
        """
        async with self._state_lock:
            if self._is_a_controller_running:
                msg = f"Un autre client ({self._current_client_alias}) contrôle déjà le clavier"
                app_loger.warning(msg)
                raise exceptions.ControllerAlreadyRunningException(msg)

            self._active_controller = Controller()

            self._is_a_controller_running = True

            self._current_client_alias = client_alias

        app_loger.info(f"Le client '{client_alias}' a démarré le contrôle du clavier.")
        return True

    async def stop_controller(self) -> None:
        """
        Arrête le contrôleur de clavier actif.
        """
        async with self._state_lock:
            if not self._is_a_controller_running:
                app_loger.warning("Aucun client actif à arrêter.")
                return
            self._active_controller = None
            self._is_a_controller_running = False
            stopped_client = self._current_client_alias
            self._current_client_alias = None

        app_loger.info(f"Client '{stopped_client}' déconnecté du controle du clavier.")

    async def press_key(self, key_name: AvailableKeys) -> None:
        """
        Simule la pression d'une touche du clavier définie dans AvailableKeys en thread safe
        Args:
            key_name: Le nom de la touche à presser (parmi AvailableKeys)

        Raises:
            NoActiveControllerException: Si aucun contrôleur n'est actif.
            KeyError: Si la touche spécifiée n'existe pas.
        """

        async with self._state_lock:
            controller = await self._verify_controller_running()

            if key_name not in self._keys:
                raise exceptions.TouchNotExistException(f"La touche '{key_name}' n'existe pas dans les touches définies.")

            key_to_press = self._keys[key_name]
            client_alias = self._current_client_alias

        await key_to_press.execute_the_press(controller=controller)
        app_loger.info(f"Touche '{key_name}' pressée par le client '{client_alias}'.")

    async def type_a_string(self, char: str) -> None:
        """
        Simule la tape d'une touche alphanumérique du clavier.
        Args:
            char: Le caractère alphanumérique à taper.

        Raises:
            NoActiveControllerException: Si aucun contrôleur n'est actif.
        """
        async with self._state_lock:
            controller = await self._verify_controller_running()
            client_alias = self._current_client_alias

        try:
            controller.type(char)
        except self._active_controller.InvalidCharacterException as e:
            app_loger.info(f"Le caractère '{char}' n'est pas valide pour la saisie : {e}")
            return

        app_loger.info(f"Touche alphanumérique '{char}' pressée par le client '{client_alias}'.")