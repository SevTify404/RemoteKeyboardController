from fastapi import APIRouter

router = APIRouter(prefix="/ws", tags=["WebSocket Routes"])

# Petite fonction inutile (mais utile) pour ajouter les routes websocket à l'objet sinon on aura que des 403
def add_ws_routes():
    pass

add_ws_routes()