import asyncio
from typing import Annotated

from fastapi.params import Query
from pydantic import ValidationError

from app.routes import WssTypeMessage
from app.routes.ws_router import router
from app.schemas.admin_panel_ws_schema import WsPayloadMessage, Notification

from app.services import app_websocket_manager, app_keyboard_controller
from app.schemas.control_panel_ws_schema import ControlPanelWSMessage, AvailableMessageTypes, OutControlPanelWSMessage
from fastapi import WebSocket, WebSocketDisconnect

from app.services.keyboard_controller.exceptions import ControllerAlreadyRunningException
from app.utils.security.all_instances import store_manager


@router.websocket("/control-panel")
async def control_panel_websocket(websocket: WebSocket, device_token = Annotated[str, Query(...)]):
    """WebSocket route pour le controle panel coté client"""
    #Vérification du device_id

    session = store_manager.get_device_token(device_token)
    if not session or session.revoked:
        await websocket.close(code=1008)
        return

    await app_websocket_manager.connect_client(websocket)

    try:
        await app_keyboard_controller.start_controller('Client Control Panel')
    except ControllerAlreadyRunningException as e:
        await app_websocket_manager.send_data_to_admin(
            data=WsPayloadMessage(
                    type=WssTypeMessage.NOTIFY, data=Notification(message=str(e))
                ).model_dump(),
            is_json=True
        )
        await app_websocket_manager.disconnect_client()
        return

    try:
        while True:
            raw_data = await websocket.receive_text()

            has_succeed = True
            error_msg = None
            data = None
            try:
                data = ControlPanelWSMessage.model_validate_json(raw_data)

            except ValidationError:
                has_succeed = False
                error_msg = "Données de commandes reçu mais mal formatés, Impossible de traiter"


            if data:
                if data.message_type == AvailableMessageTypes.COMMAND:
                    if not data.payload or data.payload.command is None:
                        has_succeed = False
                        error_msg = "Commande vide ou mal formatée"
                    else:
                        try:
                            await app_keyboard_controller.press_key(data.payload.command)
                        except Exception as e:
                            has_succeed = False
                            error_msg = str(e)

                elif data.message_type == AvailableMessageTypes.TYPING:
                    if not data.payload or data.payload.text_to_type is None:
                        has_succeed = False
                        error_msg = "Texte vide ou mal formaté"
                    else:
                        try:
                            await app_keyboard_controller.type_a_string(data.payload.text_to_type)
                        except Exception as e:
                            has_succeed = False
                            error_msg = str(e)

                elif data.message_type == AvailableMessageTypes.DISCONNECT:
                    raise WebSocketDisconnect

                #Pas encore implémenté
                elif data.message_type == AvailableMessageTypes.STATUS_UPDATE:
                    # TODO: Implémenter la mise à jour de statut
                    pass

            msg = WsPayloadMessage(
                    type=WssTypeMessage.COMMAND,
                    data=OutControlPanelWSMessage(
                        succes=has_succeed,
                        data=data if has_succeed else None,
                        error=error_msg
                    )
                ).model_dump()
            tasks = [
                websocket.send_json(msg),
                app_websocket_manager.send_data_to_admin(
                    data=msg,
                    is_json=True
                )
            ]
            await asyncio.gather(*tasks)
    except WebSocketDisconnect:
        await app_websocket_manager.disconnect_client()
        await app_keyboard_controller.stop_controller()
        await app_websocket_manager.send_data_to_admin(
            data=WsPayloadMessage(
                type=WssTypeMessage.NOTIFY,
                data=Notification(message="Le client s'est déconnecté")
            ).model_dump(),
            is_json=True
        )