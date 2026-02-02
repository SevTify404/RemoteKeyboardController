from typing import Optional

from pydantic import BaseModel, Field


class IpView(BaseModel):
    """Schema pour la réponse de l'API get ip"""

    ip_address: Optional[str] = Field(None, description="Adresse IP locale de l'appareil")


