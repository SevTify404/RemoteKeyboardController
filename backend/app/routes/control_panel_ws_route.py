from pydantic import ValidationError

from app.routes.ws_router import router

from app.services import app_websocket_manager, app_keyboard_controller
from app.schemas.control_panel_ws_schema import ControlPanelWSMessage, AvailableMessageTypes
from fastapi import WebSocket, WebSocketDisconnect

#TODO: Ajouter la gestion des erreurs et des logs notament pour les cas de WebSocketDisconnect
@router.websocket("/ws/control-panel")
async def control_panel_websocket(websocket: WebSocket):
    """WebSocket route pour le controle panel coté client"""

    await app_websocket_manager.connect_client(websocket)
    # TODO: Ajjuster cete logique avec un try...catch
    app_keyboard_controller.start_controller('Client Control Panel')

    try:
        while True:
            raw_data = await websocket.receive_json()

            try:
                data = ControlPanelWSMessage.model_validate_json(raw_data)
            except ValidationError:
                continue

            else:
                if data.message_type == AvailableMessageTypes.COMMAND:
                    await app_keyboard_controller.press_key(data.payload.command)
                    await app_websocket_manager.send_data_to_admin(data.model_dump_json(), is_json=True)
                    continue

                elif data.message_type == AvailableMessageTypes.TYPING:
                    await app_keyboard_controller.type_a_string(data.payload.text_to_type)
                    await app_websocket_manager.send_data_to_admin(data.model_dump_json(), is_json=True)
                    continue

                elif data.message_type == AvailableMessageTypes.ALERT:
                    pass
                    continue

                elif data.message_type == AvailableMessageTypes.DISCONNECT:
                    await app_websocket_manager.disconnect_client("Le coté Control Panel a demandé la déconnexion")
                    await app_websocket_manager.send_data_to_admin("Le coté Control Panel Client s'est déconnecter")
                    break

                elif data.message_type == AvailableMessageTypes.STATUS_UPDATE:
                    pass
                    continue

    except WebSocketDisconnect:
        await app_websocket_manager.disconnect_client("Le coté Control Panel Client s'est déconnecter")
        await app_websocket_manager.send_data_to_admin("Le coté Control Panel Client s'est déconnecter")