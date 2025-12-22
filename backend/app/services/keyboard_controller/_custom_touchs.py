from abc import ABC, abstractmethod
from asyncio import sleep
from dataclasses import dataclass
from typing import Union

from pynput.keyboard import Controller, KeyCode, Key

KeyType = Union[KeyCode, Key]


@dataclass
class KeyboardCombination:
    """
    Représente une combinaison de touches de clavier.

    Attributes:
        keys_to_hold: Liste des touches à maintenir appuyées
        keys_to_press: Liste des touches à presser après (maintenues et relâchées)
    """
    keys_to_hold: list[KeyType]
    keys_to_press: list[KeyType]

    def __post_init__(self):
        """Valide que les listes ne sont pas vides et contiennent des types valides."""
        if not self.keys_to_hold and not self.keys_to_press:
            raise ValueError("Une combinaison doit contenir au moins une touche à maintenir ou à presser")

        for key in self.keys_to_hold:
            if not isinstance(key, (KeyCode, Key)):
                raise TypeError(f"keys_to_hold doit contenir des KeyCode ou Key, reçu: {type(key)}")

        for key in self.keys_to_press:
            if not isinstance(key, (KeyCode, Key)):
                raise TypeError(f"keys_to_press doit contenir des KeyCode ou Key, reçu: {type(key)}")


class KeyboardTouchs(ABC):
    """Classe abstraite représentant une touche de clavier ou une combinaison de touches."""
    _REALASE_DURATION: float = 0.02  # Durée en secondes entre l'appui et le relâchement d'une touche

    def __init__(self, touch: Union[KeyType, KeyboardCombination]):
        self._touch: Union[KeyType, KeyboardCombination] = touch

    @abstractmethod
    async def execute_the_press(self, controller: Controller) -> None:
        """
        Exécute la pression de la touche ou de la combinaison de touches.

        Args:
            controller: L'objet contrôleur clavier courant

        Returns:
            None
        """
        pass


class SingleKeyTouch(KeyboardTouchs):
    """Représente une seule touche de clavier à presser."""

    def __init__(self, touch: KeyType):
        if not isinstance(touch, (KeyCode, Key)):
            raise TypeError("SingleKeyTouch attend une instance de KeyCode ou Key")
        super().__init__(touch)

    async def execute_the_press(self, controller: Controller) -> None:
        """Appuie et relâche une seule touche."""
        controller.press(self._touch)
        await sleep(self._REALASE_DURATION)
        controller.release(self._touch)


class KeyboardCombinationTouch(KeyboardTouchs):
    """
    Représente une combinaison de touches de clavier.

    Permet de maintenir plusieurs touches simultanément et presser d'autres touches après
    """

    def __init__(self, combination: KeyboardCombination):
        if not isinstance(combination, KeyboardCombination):
            raise TypeError("KeyboardCombinationTouch attend une instance de KeyboardCombination")
        super().__init__(combination)

    async def execute_the_press(self, controller: Controller) -> None:
        """
        Exécute une combinaison de touches
        """
        if self._touch.keys_to_hold:
            for key in self._touch.keys_to_hold:
                controller.press(key)
                await sleep(self._REALASE_DURATION)

            try:
                for key in self._touch.keys_to_press:
                    controller.press(key)
                    await sleep(self._REALASE_DURATION)
                    controller.release(key)
                    await sleep(self._REALASE_DURATION)
            finally:
                for key in reversed(self._touch.keys_to_hold):
                    controller.release(key)
                    await sleep(self._REALASE_DURATION)
        else:
            for key in self._touch.keys_to_press:
                controller.press(key)
                await sleep(self._REALASE_DURATION)
                controller.release(key)
                await sleep(self._REALASE_DURATION)

        await sleep(self._REALASE_DURATION)