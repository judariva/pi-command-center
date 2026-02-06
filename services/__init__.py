"""Servicios del bot."""
from services.network import NetworkService
from services.pihole import PiholeService
from services.system import SystemService
from services.devices import DeviceService

__all__ = ['NetworkService', 'PiholeService', 'SystemService', 'DeviceService']
