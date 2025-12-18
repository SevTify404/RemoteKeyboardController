from .pin_manager import PinManager
from .challenge_manager import ChallengeManager
from .device_manager import DeviceTokenManager
from .token_storage import DeviceStore

pin_manager = PinManager()
challenge_manager = ChallengeManager()
store_manager = DeviceStore()
device_manager = DeviceTokenManager(store_manager)