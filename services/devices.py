"""Servicio de gestión de dispositivos conocidos."""
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set

from config import config
from utils.formatting import format_mac

logger = logging.getLogger(__name__)


@dataclass
class KnownDevice:
    """Dispositivo conocido en la base de datos."""
    mac: str
    name: str
    trusted: bool = False
    first_seen: str = ""
    last_seen: str = ""
    notes: str = ""

    def __post_init__(self):
        self.mac = format_mac(self.mac)
        if not self.first_seen:
            self.first_seen = datetime.now().isoformat()


class DeviceService:
    """Servicio para gestionar dispositivos conocidos."""

    def __init__(self):
        self._db_path = config.DEVICES_DB
        self._devices: Dict[str, KnownDevice] = {}
        self._alerted: Set[str] = set()
        self._load()

    def _load(self):
        """Cargar base de datos desde archivo."""
        config.ensure_data_dir()

        if not os.path.exists(self._db_path):
            self._save()
            return

        try:
            with open(self._db_path, 'r') as f:
                data = json.load(f)

            # Cargar dispositivos
            for mac, device_data in data.get("devices", {}).items():
                self._devices[format_mac(mac)] = KnownDevice(
                    mac=mac,
                    name=device_data.get("name", ""),
                    trusted=device_data.get("trusted", False),
                    first_seen=device_data.get("first_seen", ""),
                    last_seen=device_data.get("last_seen", ""),
                    notes=device_data.get("notes", "")
                )

            # Cargar dispositivos ya alertados
            self._alerted = set(format_mac(m) for m in data.get("alerted", []))

        except Exception as e:
            logger.error(f"Error cargando base de datos: {e}")

    def _save(self):
        """Guardar base de datos a archivo."""
        config.ensure_data_dir()

        data = {
            "devices": {
                mac: asdict(device)
                for mac, device in self._devices.items()
            },
            "alerted": list(self._alerted),
            "updated": datetime.now().isoformat()
        }

        try:
            with open(self._db_path, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando base de datos: {e}")

    def get_device(self, mac: str) -> Optional[KnownDevice]:
        """Obtener dispositivo por MAC."""
        return self._devices.get(format_mac(mac))

    def get_device_name(self, mac: str) -> str:
        """Obtener nombre de dispositivo o string vacío."""
        device = self.get_device(mac)
        return device.name if device else ""

    def is_trusted(self, mac: str) -> bool:
        """Verificar si dispositivo es confiable."""
        device = self.get_device(mac)
        return device.trusted if device else False

    def is_known(self, mac: str) -> bool:
        """Verificar si dispositivo está en la base de datos."""
        return format_mac(mac) in self._devices

    def was_alerted(self, mac: str) -> bool:
        """Verificar si ya se alertó sobre este dispositivo."""
        return format_mac(mac) in self._alerted

    def mark_alerted(self, mac: str):
        """Marcar dispositivo como alertado."""
        self._alerted.add(format_mac(mac))
        self._save()

    def add_device(
        self,
        mac: str,
        name: str,
        trusted: bool = True,
        notes: str = ""
    ) -> KnownDevice:
        """Añadir o actualizar dispositivo."""
        mac = format_mac(mac)

        if mac in self._devices:
            device = self._devices[mac]
            device.name = name
            device.trusted = trusted
            device.last_seen = datetime.now().isoformat()
            if notes:
                device.notes = notes
        else:
            device = KnownDevice(
                mac=mac,
                name=name,
                trusted=trusted,
                notes=notes
            )
            self._devices[mac] = device

        self._save()
        return device

    def remove_device(self, mac: str) -> bool:
        """Eliminar dispositivo de la base de datos."""
        mac = format_mac(mac)
        if mac in self._devices:
            del self._devices[mac]
            self._alerted.discard(mac)
            self._save()
            return True
        return False

    def set_trusted(self, mac: str, trusted: bool) -> bool:
        """Establecer estado de confianza."""
        mac = format_mac(mac)
        if mac in self._devices:
            self._devices[mac].trusted = trusted
            self._save()
            return True
        return False

    def update_last_seen(self, mac: str):
        """Actualizar última vez visto."""
        mac = format_mac(mac)
        if mac in self._devices:
            self._devices[mac].last_seen = datetime.now().isoformat()
            self._save()

    def get_all_devices(self) -> List[KnownDevice]:
        """Obtener todos los dispositivos."""
        return list(self._devices.values())

    def get_trusted_devices(self) -> List[KnownDevice]:
        """Obtener solo dispositivos confiables."""
        return [d for d in self._devices.values() if d.trusted]

    def get_untrusted_devices(self) -> List[KnownDevice]:
        """Obtener dispositivos no confiables."""
        return [d for d in self._devices.values() if not d.trusted]

    def clear_alerts(self):
        """Limpiar lista de alertas."""
        self._alerted.clear()
        self._save()

    def get_stats(self) -> Dict[str, int]:
        """Obtener estadísticas de dispositivos."""
        return {
            "total": len(self._devices),
            "trusted": len([d for d in self._devices.values() if d.trusted]),
            "untrusted": len([d for d in self._devices.values() if not d.trusted]),
            "alerted": len(self._alerted)
        }
