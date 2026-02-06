#!/usr/bin/env python3
"""
Pi Command Center v2.0
Bot de Telegram para control de red y Raspberry Pi
Refactorizado con best practices
"""
import asyncio
import logging
import sys

from telegram.ext import Application

from config import config
from services import NetworkService, PiholeService, SystemService, DeviceService
from handlers import setup_command_handlers, setup_callback_handlers, setup_message_handlers
from monitor import NetworkMonitor

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Reducir ruido de httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


async def post_init(app: Application):
    """Inicialización post-arranque."""
    # Iniciar monitor de red
    monitor: NetworkMonitor = app.bot_data['monitor']
    await monitor.start()
    logger.info("Monitor de red iniciado")


async def post_shutdown(app: Application):
    """Limpieza al apagar."""
    monitor: NetworkMonitor = app.bot_data.get('monitor')
    if monitor:
        await monitor.stop()
    logger.info("Bot apagado correctamente")


def main():
    """Punto de entrada principal."""
    logger.info("=" * 50)
    logger.info("Pi Command Center v2.0")
    logger.info("=" * 50)

    # Asegurar directorio de datos
    config.ensure_data_dir()

    # Crear servicios (singleton-like)
    network_service = NetworkService()
    pihole_service = PiholeService()
    system_service = SystemService()
    device_service = DeviceService()

    logger.info("Servicios inicializados")

    # Crear aplicación
    app = Application.builder().token(config.BOT_TOKEN).build()

    # Almacenar servicios en bot_data para acceso global
    app.bot_data['network_service'] = network_service
    app.bot_data['pihole_service'] = pihole_service
    app.bot_data['system_service'] = system_service
    app.bot_data['device_service'] = device_service

    # Crear monitor de red
    monitor = NetworkMonitor(
        app=app,
        network_service=network_service,
        system_service=system_service,
        device_service=device_service
    )
    app.bot_data['monitor'] = monitor

    # Registrar handlers
    setup_command_handlers(app)
    setup_callback_handlers(app)
    setup_message_handlers(app)

    logger.info("Handlers registrados")

    # Hooks de ciclo de vida
    app.post_init = post_init
    app.post_shutdown = post_shutdown

    # Arrancar bot
    logger.info("Iniciando bot...")
    logger.info(f"Usuarios autorizados: {config.AUTHORIZED_USERS}")

    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Interrupción de teclado")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
