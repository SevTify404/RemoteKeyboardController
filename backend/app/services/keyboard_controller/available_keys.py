from enum import Enum


class AvailableKeyboardKeys(str, Enum):
    UP_KEY="UP"
    DOWN_KEY="DOWN"
    LEFT_KEY="LEFT"
    RIGHT_KEY="RIGHT"
    ENTER_KEY="ENTER"
    MUTE_KEY="MUTE"
    VOLUME_UP_KEY="VOLUME_UP"
    VOLUME_DOWN_KEY="VOLUME_DOWN"