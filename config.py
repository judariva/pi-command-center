"""Configuración centralizada del bot."""
import os
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Config:
    """Configuración inmutable del bot."""

    # Telegram
    BOT_TOKEN: str = "REDACTED_BOT_TOKEN"
    AUTHORIZED_USERS: tuple = (REDACTED_USER_ID,)
    ALERT_CHAT_ID: int = REDACTED_USER_ID

    # Pi-hole
    PIHOLE_API: str = "http://localhost/api"
    PIHOLE_PASSWORD: str = "REDACTED_PASSWORD"

    # Paths
    DATA_DIR: str = "/home/judariva/pibot/data"
    DEVICES_DB: str = "/home/judariva/pibot/data/devices.json"

    # Network
    LOCAL_NETWORK: str = "192.168.0.0/24"
    PI_IP: str = "PI_IP_REDACTED"

    # Monitoring
    SCAN_INTERVAL: int = 300  # 5 minutos
    TEMP_ALERT_THRESHOLD: float = 75.0

    @classmethod
    def ensure_data_dir(cls):
        """Crea el directorio de datos si no existe."""
        os.makedirs(cls.DATA_DIR, exist_ok=True)


# Singleton
config = Config()
