from enum import Enum


class SideAlias(str, Enum):
    ADMIN_SIDE = "admin"
    CLIENT_SIDE = "client"
    WAITING_FOR_CONNECTION_SIDE = "waiting"
