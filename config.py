"""Configuración centralizada del bot usando variables de entorno."""
import os
import sys
from dataclasses import dataclass
from typing import Tuple
from pathlib import Path

# Load .env file if present (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not required in production


def _get_required_env(name: str) -> str:
    """Get a required environment variable or exit with error."""
    value = os.environ.get(name)
    if not value:
        print(f"❌ ERROR: Required environment variable {name} is not set.")
        print(f"   Please set it in your .env file or environment.")
        print(f"   See .env.example for reference.")
        sys.exit(1)
    return value


def _get_authorized_users() -> Tuple[int, ...]:
    """Parse comma-separated user IDs from environment."""
    users_str = _get_required_env("AUTHORIZED_USERS")
    try:
        return tuple(int(uid.strip()) for uid in users_str.split(",") if uid.strip())
    except ValueError as e:
        print(f"❌ ERROR: Invalid AUTHORIZED_USERS format: {users_str}")
        print(f"   Expected comma-separated integers (e.g., 123456789,987654321)")
        sys.exit(1)


@dataclass(frozen=True)
class Config:
    """Configuración inmutable del bot basada en variables de entorno."""

    # Telegram - Required
    BOT_TOKEN: str = ""
    AUTHORIZED_USERS: Tuple[int, ...] = ()
    ALERT_CHAT_ID: int = 0

    # Pi-hole - Optional with defaults
    PIHOLE_API: str = ""
    PIHOLE_PASSWORD: str = ""

    # Paths - Optional with defaults
    DATA_DIR: str = ""
    DEVICES_DB: str = ""

    # Network - Optional with defaults
    LOCAL_NETWORK: str = ""
    PI_IP: str = ""
    GATEWAY: str = ""

    # Monitoring - Optional with defaults
    SCAN_INTERVAL: int = 300
    TEMP_ALERT_THRESHOLD: float = 75.0

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        # Get base data directory
        data_dir = os.getenv("DATA_DIR", "/home/judariva/pibot/data")

        # Get authorized users (required)
        authorized_users = _get_authorized_users()

        # Alert chat defaults to first authorized user if not specified
        alert_chat_id = int(os.getenv("ALERT_CHAT_ID", str(authorized_users[0])))

        # Network defaults
        network_range = os.getenv("NETWORK_RANGE", "192.168.1.0/24")
        gateway = os.getenv("GATEWAY", "192.168.1.1")
        pi_ip = os.getenv("PI_IP", "")

        # If PI_IP not set, try to derive from network range
        if not pi_ip:
            # Default: use .43 in the network range
            base = network_range.rsplit(".", 2)[0]
            pi_ip = f"{base}.43"

        return cls(
            BOT_TOKEN=_get_required_env("TELEGRAM_BOT_TOKEN"),
            AUTHORIZED_USERS=authorized_users,
            ALERT_CHAT_ID=alert_chat_id,
            PIHOLE_API=os.getenv("PIHOLE_API_URL", "http://localhost/api"),
            PIHOLE_PASSWORD=os.getenv("PIHOLE_PASSWORD", ""),
            DATA_DIR=data_dir,
            DEVICES_DB=os.getenv("DEVICES_DB", f"{data_dir}/devices.json"),
            LOCAL_NETWORK=network_range,
            PI_IP=pi_ip,
            GATEWAY=gateway,
            SCAN_INTERVAL=int(os.getenv("SCAN_INTERVAL", "300")),
            TEMP_ALERT_THRESHOLD=float(os.getenv("TEMP_ALERT_THRESHOLD", "75.0")),
        )

    @classmethod
    def ensure_data_dir(cls):
        """Crea el directorio de datos si no existe."""
        Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)


# Create singleton from environment
config = Config.from_env()
