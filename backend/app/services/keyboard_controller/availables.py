from dataclasses import dataclass
from enum import Enum

from pynput.keyboard import Key

from app.services.keyboard_controller._custom_touchs import KeyboardTouchs, SingleKeyTouch


class AvailableKeys(str, Enum):
    UP_KEY="UP"
    DOWN_KEY="DOWN"
    LEFT_KEY="LEFT"
    RIGHT_KEY="RIGHT"
    ENTER_KEY="ENTER"
    MUTE_KEY="MUTE"
    VOLUME_UP_KEY="VOLUME_UP"
    VOLUME_DOWN_KEY="VOLUME_DOWN"

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


key_map :  dict[AvailableKeys, KeyboardTouchs] = {
    AvailableKeys.UP_KEY : KeysImplementations.UP_KEY,
    AvailableKeys.DOWN_KEY : KeysImplementations.DOWN_KEY,
    AvailableKeys.LEFT_KEY : KeysImplementations.LEFT_KEY,
    AvailableKeys.RIGHT_KEY : KeysImplementations.RIGHT_KEY,
    AvailableKeys.ENTER_KEY : KeysImplementations.ENTER_KEY,
    AvailableKeys.MUTE_KEY : KeysImplementations.MUTE_KEY,
    AvailableKeys.VOLUME_UP_KEY : KeysImplementations.VOLUME_UP_KEY,
    AvailableKeys.VOLUME_DOWN_KEY : KeysImplementations.VOLUME_DOWN_KEY
}