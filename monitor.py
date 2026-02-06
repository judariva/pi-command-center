"""Monitor de red en background."""
import asyncio
import logging
from datetime import datetime
from telegram.ext import Application

from config import config
from services import NetworkService, SystemService, DeviceService
from utils.formatting import get_device_icon, get_vendor_short

logger = logging.getLogger(__name__)


class NetworkMonitor:
    """Monitor de red que corre en background."""

    def __init__(
        self,
        app: Application,
        network_service: NetworkService,
        system_service: SystemService,
        device_service: DeviceService
    ):
        self.app = app
        self.network_svc = network_service
        self.system_svc = system_service
        self.device_svc = device_service
        self._running = False
        self._task = None

    async def start(self):
        """Inicia el monitor."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("Monitor de red iniciado")

    async def stop(self):
        """Detiene el monitor."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Monitor de red detenido")

    async def _monitor_loop(self):
        """Loop principal del monitor."""
        # Esperar 60s antes del primer escaneo
        await asyncio.sleep(60)

        while self._running:
            try:
                await self._check_network()
                await self._check_temperature()
            except Exception as e:
                logger.error(f"Error en monitor: {e}")

            # Esperar intervalo configurado
            await asyncio.sleep(config.SCAN_INTERVAL)

    async def _check_network(self):
        """Verifica dispositivos nuevos en la red."""
        try:
            devices = await self.network_svc.scan_all()

            for device in devices:
                mac = device.mac

                # Skip si ya conocemos o ya alertamos
                if self.device_svc.is_known(mac):
                    self.device_svc.update_last_seen(mac)
                    continue

                if self.device_svc.was_alerted(mac):
                    continue

                # Nuevo dispositivo - alertar
                self.device_svc.mark_alerted(mac)

                icon = get_device_icon(device.vendor, device.hostname)
                vendor = get_vendor_short(device.vendor)
                now = datetime.now().strftime("%H:%M:%S")

                message = (
                    f"🚨 *NUEVO DISPOSITIVO*\n\n"
                    f"{icon} Dispositivo desconocido conectado\n\n"
                    f"📍 *IP:* `{device.ip}`\n"
                    f"📱 *MAC:* `{device.mac}`\n"
                    f"🏭 *Fabricante:* {vendor}\n"
                    f"⏰ *Hora:* {now}\n\n"
                    f"_Usa /start > Dispositivos para identificarlo_"
                )

                await self._send_alert(message)

        except Exception as e:
            logger.error(f"Error verificando red: {e}")

    async def _check_temperature(self):
        """Verifica temperatura del sistema."""
        try:
            stats = self.system_svc.get_stats()
            if not stats:
                return

            if stats.temperature >= config.TEMP_ALERT_THRESHOLD:
                message = (
                    f"🔥 *ALERTA: Temperatura Alta*\n\n"
                    f"La Raspberry Pi esta a *{stats.temperature:.1f}C*\n\n"
                    f"_Verifica la ventilacion del dispositivo_"
                )

                await self._send_alert(message)

        except Exception as e:
            logger.error(f"Error verificando temperatura: {e}")

    async def _send_alert(self, message: str):
        """Envia alerta a Telegram."""
        try:
            await self.app.bot.send_message(
                chat_id=config.ALERT_CHAT_ID,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error enviando alerta: {e}")
