
from fastapi import APIRouter
from fastapi.params import Depends

from . import ApiTags, ErrorMessages, WssTypeMessage
from app.schemas.utils_schema import IpView
from ..auth.dependencies import local_only
from ..utils.os_funcs import get_lan_ip

router = APIRouter(prefix="/utils", tags=[ApiTags.UTILS])

@router.get("/get-lan-ip", response_model=IpView, dependencies=[Depends(local_only)])
async def recuperer_addresse_ip_locale():
    """Route pour récupérer l'adresse IP locale de l'appareil."""

    return IpView(ip_address=get_lan_ip())