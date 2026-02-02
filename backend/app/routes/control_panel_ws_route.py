import asyncio
from typing import Annotated

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.params import Query
from pydantic import ValidationError

from app import websocket_logger
from app.routes import WssTypeMessage
from app.routes.ws_router import router
from app.schemas.admin_panel_ws_schema import WsPayloadMessage, Notification
from app.schemas.control_panel_ws_schema import ControlPanelWSMessage, AvailableMessageTypes, OutControlPanelWSMessage
from app.services import app_websocket_manager, app_keyboard_controller
from app.services.keyboard_controller.exceptions import ControllerAlreadyRunningException
from app.utils.security.all_instances import store_manager

async def _final_notifier(
    data: ControlPanelWSMessage,
    has_succeed: bool,
    error_msg: str | None = None
) -> None:
    """Fonction interne pour notifier le client et l'admin de la réussite ou non d'une commande"""

    msg = WsPayloadMessage(
        type=WssTypeMessage.COMMAND,
        data=OutControlPanelWSMessage(
            succes=has_succeed,
            data=data if has_succeed else None,
            error=error_msg
        )
    ).model_dump_json()

    tasks = [
        app_websocket_manager.send_data_to_client(msg),  # Plus besoin de is_json=True ou send_json vu qu'on dump en joson directement
        app_websocket_manager.send_data_to_admin(data=msg)
    ]
    await asyncio.gather(*tasks)


async def _execute_command(
    data: ControlPanelWSMessage,
    has_succeed: bool,
    error_msg: str | None = None
) -> tuple[bool, str]:
    """Fonction interne pour exécuter une commande reçue"""
    if data.payload.command is None:
        websocket_logger.warning(f"❌ {error_msg}")
        return False, "Commande vide ou mal formatée"

    else:
        try:
            await app_keyboard_controller.press_key(data.payload.command)
            websocket_logger.debug(f"⌨️ Commande exécutée: {data.payload.command}")
            return has_succeed, error_msg
        except Exception as e:
            websocket_logger.error(f"❌ Erreur lors de l'exécution de la commande: {error_msg}")

            return has_succeed, str(e)

async def _type_string(
    data: ControlPanelWSMessage,
    has_succeed: bool,
    error_msg: str | None = None
) -> tuple[bool, str]:
    """Fonction interne pour taper une chaîne de caractères"""
    if not data.payload or data.payload.text_to_type is None:
        websocket_logger.warning(f"❌ {error_msg}")
        return False, "Texte vide ou mal formaté"
    else:
        try:
            await app_keyboard_controller.type_a_string(data.payload.text_to_type)
            websocket_logger.debug(f"📝 Texte tapé: {len(data.payload.text_to_type)} caractères")
            return has_succeed, error_msg
        except Exception as e:
            websocket_logger.error(f"❌ Erreur lors de la saisie: {error_msg}")
            return has_succeed, str(e)

@router.websocket("/control-panel")
async def control_panel_websocket(websocket: WebSocket, device_token = Annotated[str, Query(...)]):
    """WebSocket route pour le contrôle panel côté client"""

    # Vérification du device_token
    session = store_manager.get_device_token(device_token)
    if not session or session.revoked:
        websocket_logger.warning("❌ Tentative de connexion avec un token invalide")
        await websocket.close(code=1008, reason='Bad device token')
        return

    await app_websocket_manager.connect_client(websocket)
    session.revoke_device_token_session()
    websocket_logger.info("✅ Client connecté au WebSocket control-panel")

    try:
        await app_keyboard_controller.start_controller('Client Control Panel')
    except ControllerAlreadyRunningException as e:
        websocket_logger.warning(f"⚠️ {str(e)}")
        await app_websocket_manager.send_data_to_admin(
            data=WsPayloadMessage(
                    type=WssTypeMessage.NOTIFY, data=Notification(message=str(e))
                ).model_dump(),
            is_json=True
        )
        await app_websocket_manager.disconnect_client()
        return

    websocket_logger.debug("🎮 Contrôleur clavier démarré avec succès")

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = ControlPanelWSMessage.model_validate_json(raw_data)
                websocket_logger.debug(f"📥 Message reçu: {data.message_type}")

            except ValidationError:
                websocket_logger.warning("❌ Erreur de validation JSON: Données de commandes reçu mais mal formatés,"
                                         " Impossible de traiter")
                continue

            has_succeed = True
            error_msg = None

            if data.message_type == AvailableMessageTypes.COMMAND:
                has_succeed, error_msg = await _execute_command(data, has_succeed, error_msg)

            elif data.message_type == AvailableMessageTypes.TYPING:
                has_succeed, error_msg = await _type_string(data, has_succeed, error_msg)

            elif data.message_type == AvailableMessageTypes.DISCONNECT:
                websocket_logger.info("🔌 Déconnexion demandée par le client")
                raise WebSocketDisconnect

            # Pas encore implémenté
            elif data.message_type == AvailableMessageTypes.STATUS_UPDATE:
                websocket_logger.debug("ℹ️ Status update reçu (non implémenté)")
                continue

            #Tache de fond pour optimiser le temps de libération de la boucle
            asyncio.create_task(_final_notifier(data, has_succeed, error_msg))



    except WebSocketDisconnect:
        websocket_logger.info("🔌 Client déconnecté")
        await app_websocket_manager.disconnect_client()
        await app_keyboard_controller.stop_controller()
        await app_websocket_manager.send_data_to_admin(
            data=WsPayloadMessage(
                type=WssTypeMessage.NOTIFY,
                data=Notification(message="Le client s'est déconnecté")
            ).model_dump(),
            is_json=True
        )
    except Exception as e:
        websocket_logger.exception(f"❌ Erreur WebSocket: {e.__class__.__name__}: {e}")
        await app_websocket_manager.disconnect_client()
        await app_keyboard_controller.stop_controller()
        msg = f"Une erreur est survenue dans le control panel client: {e.__class__.__name__}: {e}"
        await app_websocket_manager.send_data_to_admin(
            data=WsPayloadMessage(
                type=WssTypeMessage.NOTIFY,
                data=Notification(message=msg)
            ).model_dump(),
            is_json=True
        )