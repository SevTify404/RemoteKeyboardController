from fastapi import HTTPException, WebSocket

from app.core.config import LOCAL_IP


def local_only(request: WebSocket):
    if request.client.host not in [LOCAL_IP, "127.0.0.1"]:
        raise HTTPException(403, "Local access only")