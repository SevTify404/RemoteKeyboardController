from fastapi import APIRouter

router = APIRouter(prefix="/ws", tags=["WebSocket Routes"])

# Petite fonction inutile (mais utile) pour ajouter les routes websocket à l'objet sinon on aura que des 403
def add_ws_routes():
    from .admin_panel_ws_route import panel_websocket
    from .waiting_ws_route import waiting_connexion
    from .control_panel_ws_route import control_panel_websocket

add_ws_routes()