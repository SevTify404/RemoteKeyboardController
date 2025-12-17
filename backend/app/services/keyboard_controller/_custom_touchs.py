from dataclasses import dataclass
from typing import Union
from asyncio import sleep
from pynput.keyboard import Controller, KeyCode, Key
from abc import ABC, abstractmethod
@dataclass
class CombinaisonTouch:
    a_maintenir: KeyCode

    apres_maintien: list[KeyCode]

class KeyboardTouchs(ABC):
    """Classe abstraite représentant une touche de clavier ou une combinaison de touches."""
    _REALASE_DURATION: float = 0.02  # Durée en secondes entre l'appui et le relâchement d'une touche

    def __init__(self, touch: Union[KeyCode, Key, CombinaisonTouch]):

        self._touch: KeyCode | Key | CombinaisonTouch = touch

    @abstractmethod
    async def execute_the_press(self, controller: Controller) -> None:
        """
        Fonction pour vraiment appuyer la touche ou la combinaison de touche
        Args:
            controller: L'objet clavier courant

        Returns:
            Rien du tout
        """

        pass

class SingleKeyTouch(KeyboardTouchs):

    def __init__(self, touch: Union[KeyCode, Key]):
        if not isinstance(touch, (KeyCode, Key)):
            raise TypeError("SingleKeyTouch attend une instance de KeyCode ou Key")
        super().__init__(touch)

    async def execute_the_press(self, controller: Controller) -> None:

        controller.press(self._touch)
        await sleep(self._REALASE_DURATION)
        controller.release(self._touch)

class CombinationKeyTouch(KeyboardTouchs):

    def __init__(self, touch: CombinaisonTouch):
        if not isinstance(touch, CombinaisonTouch):
            raise TypeError("CombinationKeyTouch attend une instance de CombinaisonTouch")
        super().__init__(touch)


    async def execute_the_press(self, controller: Controller) -> None:

        with controller.pressed(self._touch.a_maintenir):
            for key in self._touch.apres_maintien:
                controller.press(key)
                await sleep(self._REALASE_DURATION)
                controller.release(key)
                await sleep(self._REALASE_DURATION)

        await sleep(self._REALASE_DURATION)