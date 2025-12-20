from dataclasses import dataclass
from enum import Enum

from pynput.keyboard import Key, KeyCode

from app.services.keyboard_controller._custom_touchs import KeyboardTouchs, SingleKeyTouch, KeyboardCombination, \
    KeyboardCombinationTouch


class AvailableKeys(str, Enum):
    UP_KEY="UP"
    DOWN_KEY="DOWN"
    LEFT_KEY="LEFT"
    RIGHT_KEY="RIGHT"
    ENTER_KEY="ENTER"
    MUTE_KEY="MUTE"
    VOLUME_UP_KEY="VOLUME_UP"
    VOLUME_DOWN_KEY="VOLUME_DOWN"


    # Les combos
    COPY = "COPY"
    PASTE = "PASTE"
    SELECT_ALL = "SELECT_ALL"
    ALT_TAB = "ALT_TAB"
    START_PRESENTATION = "START_PRESENTATION"
    END_PRESENTATION = "END_PRESENTATION"

@dataclass
class KeysImplementations:
    UP_KEY = SingleKeyTouch(Key.up)
    DOWN_KEY = SingleKeyTouch(Key.down)
    LEFT_KEY = SingleKeyTouch(Key.left)
    RIGHT_KEY = SingleKeyTouch(Key.right)
    ENTER_KEY = SingleKeyTouch(Key.enter)
    MUTE_KEY = SingleKeyTouch(Key.media_volume_mute)
    VOLUME_UP_KEY = SingleKeyTouch(Key.media_volume_up)
    VOLUME_DOWN_KEY = SingleKeyTouch(Key.media_volume_down)

    #Les combos
    COPY = KeyboardCombinationTouch(
        KeyboardCombination(
            keys_to_hold=[Key.ctrl],
            keys_to_press=[KeyCode(char='c')]
        )
    )

    PASTE = KeyboardCombinationTouch(
        KeyboardCombination(
            keys_to_hold=[Key.ctrl],
            keys_to_press=[KeyCode(char='v')]
        )
    )

    SELECT_ALL = KeyboardCombinationTouch(
        KeyboardCombination(
            keys_to_hold=[Key.ctrl],
            keys_to_press=[KeyCode(char='a')]
        )
    )

    ALT_TAB = KeyboardCombinationTouch(
        KeyboardCombination(
            keys_to_hold=[Key.alt],
            keys_to_press=[Key.tab]
        )
    )

    START_PRESENTATION = KeyboardCombinationTouch(
        KeyboardCombination(
            keys_to_hold=[Key.f5],
            keys_to_press=[]
        )
    )

    END_PRESENTATION = KeyboardCombinationTouch(
        KeyboardCombination(
            keys_to_hold=[Key.esc],
            keys_to_press=[]
        )
    )



key_map :  dict[AvailableKeys, KeyboardTouchs] = {
    AvailableKeys.UP_KEY : KeysImplementations.UP_KEY,
    AvailableKeys.DOWN_KEY : KeysImplementations.DOWN_KEY,
    AvailableKeys.LEFT_KEY : KeysImplementations.LEFT_KEY,
    AvailableKeys.RIGHT_KEY : KeysImplementations.RIGHT_KEY,
    AvailableKeys.ENTER_KEY : KeysImplementations.ENTER_KEY,
    AvailableKeys.MUTE_KEY : KeysImplementations.MUTE_KEY,
    AvailableKeys.VOLUME_UP_KEY : KeysImplementations.VOLUME_UP_KEY,
    AvailableKeys.VOLUME_DOWN_KEY : KeysImplementations.VOLUME_DOWN_KEY,

    # Les combos
    AvailableKeys.COPY: KeysImplementations.COPY,
    AvailableKeys.PASTE: KeysImplementations.PASTE,
    AvailableKeys.SELECT_ALL: KeysImplementations.SELECT_ALL,
    AvailableKeys.ALT_TAB: KeysImplementations.ALT_TAB,
    AvailableKeys.START_PRESENTATION: KeysImplementations.START_PRESENTATION,
    AvailableKeys.END_PRESENTATION: KeysImplementations.END_PRESENTATION,

}