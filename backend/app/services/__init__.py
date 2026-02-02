from .keyboard_controller.custom_controller import CustomKeyboardController
from .master_ws.websocket_conn_manager import AppWebSocketConnectionManager

app_websocket_manager = AppWebSocketConnectionManager()
app_keyboard_controller = CustomKeyboardController()

__all__ = [
    "app_websocket_manager",
    "app_keyboard_controller"
]