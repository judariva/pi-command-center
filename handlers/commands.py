"""Handlers de comandos (/start, /scan, etc)."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application

from config import config
from services import NetworkService, PiholeService, SystemService, DeviceService
from keyboards import Keyboards
from utils.formatting import get_device_icon, get_vendor_short

logger = logging.getLogger(__name__)


def is_authorized(user_id: int) -> bool:
    """Verifica si el usuario está autorizado."""
    return user_id in config.AUTHORIZED_USERS


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menú principal."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔ No autorizado")
        return

    # Obtener datos para el dashboard
    system_svc: SystemService = context.bot_data['system_service']
    pihole_svc: PiholeService = context.bot_data['pihole_service']
    network_svc: NetworkService = context.bot_data['network_service']

    # IP pública
    ip_info = system_svc.get_public_ip()
    if ip_info:
        flag = system_svc.get_country_flag(ip_info.country_code)
        ip_text = f"{flag} `{ip_info.ip}`"
    else:
        ip_text = "🌍 No disponible"

    # Pi-hole stats
    pihole_status = pihole_svc.get_status()
    if pihole_status.get("online"):
        blocked = pihole_status.get("blocked_today", 0)
        pihole_text = f"🛡️ {blocked:,} bloqueados"
    else:
        pihole_text = "🛡️ Pi-hole offline"

    # Dispositivos (desde cache o scan rápido)
    devices = network_svc.get_cached_devices()
    device_count = len(devices) if devices else "?"

    text = f"""🏠 *Pi Command Center*

{ip_text}
{pihole_text}
📱 {device_count} dispositivos

_Selecciona una opción:_"""

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=Keyboards.main_menu()
    )


async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /scan - Escaneo rápido de red."""
    if not is_authorized(update.effective_user.id):
        return

    msg = await update.message.reply_text("🔍 Escaneando red...")

    network_svc: NetworkService = context.bot_data['network_service']
    device_svc: DeviceService = context.bot_data['device_service']

    devices = await network_svc.scan_all()

    # Clasificar
    trusted = []
    unknown = []

    for device in devices:
        if device_svc.is_trusted(device.mac):
            trusted.append(device)
        else:
            unknown.append(device)

    lines = [
        f"🔍 *Escaneo de Red*",
        "",
        f"📱 *Total:* {len(devices)}",
        f"✅ *Confiables:* {len(trusted)}",
        f"❓ *Desconocidos:* {len(unknown)}",
    ]

    if unknown:
        lines.append("")
        lines.append("*Dispositivos nuevos:*")
        for d in unknown[:5]:
            icon = get_device_icon(d.vendor, d.hostname)
            name = d.display_name
            lines.append(f"{icon} `{d.ip}` \\- {name}")

    await msg.edit_text(
        "\n".join(lines),
        parse_mode="MarkdownV2",
        reply_markup=Keyboards.main_menu()
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status - Estado rápido del sistema."""
    if not is_authorized(update.effective_user.id):
        return

    system_svc: SystemService = context.bot_data['system_service']

    stats = system_svc.get_stats()
    if not stats:
        await update.message.reply_text("❌ Error obteniendo estado")
        return

    text = f"""🖥️ *Estado del Sistema*

{system_svc.format_stats_message(stats)}"""

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=Keyboards.back_to_main()
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Ayuda."""
    if not is_authorized(update.effective_user.id):
        return

    text = """🏠 *Pi Command Center*

*Comandos:*
/start \\- Menú principal
/scan \\- Escaneo rápido de red
/status \\- Estado del sistema
/help \\- Esta ayuda

*Funciones:*
🔍 *Red* \\- Escanear dispositivos, WoL
📊 *Pi\\-hole* \\- Estadísticas y bloqueos
🖥️ *Sistema* \\- CPU, RAM, Docker
📱 *Dispositivos* \\- Gestión de red"""

    await update.message.reply_text(text, parse_mode="MarkdownV2")


def setup_command_handlers(app: Application):
    """Registra los handlers de comandos."""
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("scan", cmd_scan))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("help", cmd_help))
