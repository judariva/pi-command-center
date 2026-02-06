"""Handlers de callbacks (botones inline)."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, Application

from config import config
from services import NetworkService, PiholeService, SystemService, DeviceService
from keyboards import Keyboards
from utils.shell import run_async
from utils.formatting import get_device_icon, get_vendor_short, truncate, escape_md

logger = logging.getLogger(__name__)


def is_authorized(user_id: int) -> bool:
    return user_id in config.AUTHORIZED_USERS


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal de callbacks."""
    query = update.callback_query
    await query.answer()

    if not is_authorized(query.from_user.id):
        await query.edit_message_text("⛔ No autorizado")
        return

    data = query.data

    # Obtener servicios
    network_svc: NetworkService = context.bot_data['network_service']
    pihole_svc: PiholeService = context.bot_data['pihole_service']
    system_svc: SystemService = context.bot_data['system_service']
    device_svc: DeviceService = context.bot_data['device_service']

    # ═══════════════════════════════════════════════════════════
    # NAVEGACIÓN DE MENÚS
    # ═══════════════════════════════════════════════════════════

    if data == "menu:main" or data == "action:refresh_main":
        # === DASHBOARD EN TIEMPO REAL ===

        # IP Pública
        ip_info = system_svc.get_public_ip()
        if ip_info:
            flag = system_svc.get_country_flag(ip_info.country_code)
            ip_line = f"{flag}  `{ip_info.ip}`"
        else:
            ip_line = "🌐  Sin conexión"

        # Pi-hole
        pihole_status = pihole_svc.get_status()
        if pihole_status.get("online"):
            blocked = pihole_status.get("blocked_today", 0)
            enabled = pihole_status.get("enabled", True)
            pihole_line = f"{'🛡' if enabled else '⏸'}  {blocked:,} anuncios bloqueados"
        else:
            pihole_line = "🛡  Pi-hole offline"

        # Dispositivos
        devices = network_svc.get_cached_devices()
        device_count = len(devices) if devices else 0
        untrusted = len([d for d in (devices or []) if not device_svc.is_trusted(d.mac)])
        if untrusted > 0:
            device_line = f"📱  {device_count} online  ·  ⚠️ {untrusted} nuevos"
        else:
            device_line = f"📱  {device_count} dispositivos online"

        # VPN con detalle
        vpn_out, _, _ = await run_async("sudo /usr/local/bin/vpn-manager status 2>/dev/null", timeout=5)
        vpn_state = "down"
        vpn_ip = ""
        for line in (vpn_out.strip().split('\n') if vpn_out else []):
            if line.startswith("vpn:"): vpn_state = line.split(":")[1]
            if line.startswith("ip:"): vpn_ip = line.split(":")[1]

        if vpn_state == "active":
            vpn_line = f"🔐  VPN activa  ·  🇺🇸 {vpn_ip}"
        elif vpn_state == "stale":
            vpn_line = "🔐  VPN reconectando..."
        else:
            vpn_line = "🔓  VPN desactivada"

        # Sistema
        stats = system_svc.get_stats()
        if stats:
            temp = stats.temperature
            cpu = stats.cpu_percent
            temp_warn = " ⚠️" if temp > 65 else ""
            sys_line = f"🖥  {cpu:.0f}% CPU  ·  {temp:.0f}°C{temp_warn}"
        else:
            sys_line = "🖥  Sin datos"

        text = f"""*CENTRO DE CONTROL*

{ip_line}
{pihole_line}
{device_line}
{vpn_line}
{sys_line}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.main_menu())

    elif data == "menu:network":
        devices = network_svc.get_cached_devices()
        online = len(devices) if devices else 0
        untrusted = len([d for d in (devices or []) if not device_svc.is_trusted(d.mac)])

        results = await network_svc.check_connectivity()
        all_ok = all(r["ok"] for r in results.values())

        status_icon = "🟢" if all_ok else "🔴"
        alert_text = f"⚠️ {untrusted} dispositivos nuevos" if untrusted > 0 else "✓ Red segura"

        text = f"""*RED & SEGURIDAD*

{status_icon}  {online} dispositivos conectados
{alert_text}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.network_menu())

    elif data == "menu:pihole":
        stats = pihole_svc.get_stats()
        status = pihole_svc.get_status()

        if stats and status.get("online"):
            enabled = status.get("enabled", True)
            percent = stats.percent_blocked
            status_text = "Protección activa" if enabled else "En pausa"
            status_icon = "🟢" if enabled else "⏸"

            text = f"""*PI-HOLE DNS*

{status_icon}  {status_text}

📊  {stats.total_queries:,} consultas hoy
🚫  {stats.blocked_queries:,} bloqueadas ({percent:.1f}%)
📋  {stats.domains_on_blocklist:,} en lista negra"""
        else:
            text = """*PI-HOLE DNS*

🔴  Servicio no disponible

Verifica el contenedor Docker."""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.pihole_menu())

    elif data == "menu:system":
        stats = system_svc.get_stats()
        containers = system_svc.get_containers()

        if stats:
            cpu = stats.cpu_percent
            ram = stats.memory_percent
            temp = stats.temperature
            disk = stats.disk_percent

            temp_icon = "🔴" if temp > 70 else "🟡" if temp > 60 else "🟢"
            running = len([c for c in containers if c.health in ["running", "healthy"]])
            total = len(containers)

            text = f"""*SISTEMA*

{temp_icon}  {temp:.0f}°C

💻  CPU {cpu:.0f}%
🧠  RAM {ram:.0f}%
💾  Disco {disk:.0f}%
🐳  Docker {running}/{total}
⏱  {stats.uptime}"""
        else:
            text = """*SISTEMA*

🔴  Sin conexión

No se pudo obtener el estado."""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.system_menu())

    elif data == "menu:devices":
        devices = network_svc.get_cached_devices() or []
        trusted_list = device_svc.get_trusted_devices()

        online = len(devices)
        trusted = len([d for d in devices if device_svc.is_trusted(d.mac)])
        untrusted = online - trusted

        if untrusted > 0:
            status_line = f"⚠️  {untrusted} sin verificar"
        elif online == 0:
            status_line = "📡  Escanea para detectar"
        else:
            status_line = "✓  Todos verificados"

        text = f"""*DISPOSITIVOS*

🟢  {online} online
✓  {trusted} verificados
{status_line}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.devices_menu())

    # ═══════════════════════════════════════════════════════════
    # RED Y SEGURIDAD
    # ═══════════════════════════════════════════════════════════

    elif data == "net:scan":
        await query.edit_message_text("🔍 *Escaneando red...*\n\n_10-20 segundos_", parse_mode="Markdown")

        devices = await network_svc.scan_all()

        if not devices:
            await query.edit_message_text(
                "🔍 *Escaneo completado*\n\n_No se encontraron dispositivos_",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_network()
            )
            return

        lines = ["🔍 *Dispositivos en Red*", ""]

        for d in devices[:12]:
            icon = get_device_icon(d.vendor, d.hostname)
            name = device_svc.get_device_name(d.mac)
            if not name:
                name = d.display_name
            trusted = "✅" if device_svc.is_trusted(d.mac) else "❓"

            lines.append(f"{trusted}{icon} `{d.ip}` {escape_md(name)}")

        lines.append(f"\n_Total: {len(devices)} dispositivos_")

        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_network()
        )

    elif data == "net:connectivity":
        await query.edit_message_text("📡 *Verificando conexión...*", parse_mode="Markdown")

        results = await network_svc.check_connectivity()

        lines = ["📡 *Test de Conectividad*", ""]

        for name, result in results.items():
            emoji = "✅" if result["ok"] else "❌"
            latency = result["latency"] or "timeout"
            lines.append(f"{emoji} *{name}:* {latency}")

        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_network()
        )

    elif data == "net:new_devices":
        await query.edit_message_text("🔍 *Buscando dispositivos nuevos...*", parse_mode="Markdown")

        devices = await network_svc.scan_all()

        # Filtrar no confiables
        unknown = [d for d in devices if not device_svc.is_trusted(d.mac)]

        if not unknown:
            await query.edit_message_text(
                "✅ *Todos los dispositivos son confiables*\n\n_No hay dispositivos desconocidos_",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_network()
            )
            return

        lines = ["🆕 *Dispositivos Desconocidos*", ""]

        for d in unknown[:8]:
            icon = get_device_icon(d.vendor, d.hostname)
            vendor = get_vendor_short(d.vendor)
            lines.append(f"{icon} `{d.ip}`")
            lines.append(f"   MAC: `{d.mac}`")
            lines.append(f"   {escape_md(vendor)}")
            lines.append("")

        lines.append(f"_Total: {len(unknown)} sin verificar_")
        lines.append("_Usa 'Nombrar Dispositivo' para identificarlos_")

        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_network()
        )

    elif data == "net:wol_menu":
        trusted = device_svc.get_trusted_devices()
        devices = [(d.mac, d.name or d.mac[:8]) for d in trusted if d.name]

        if not devices:
            text = "⚡ *Wake-on-LAN*\n\n_No hay dispositivos configurados_\n\nPrimero nombra dispositivos como confiables."
        else:
            text = "⚡ *Wake-on-LAN*\n\n_Selecciona dispositivo a encender:_"

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=Keyboards.wol_devices(devices)
        )

    elif data.startswith("wol:send:"):
        mac = data.split(":")[2]
        await query.edit_message_text(f"📤 *Enviando Magic Packet...*\n\nMAC: `{mac}`", parse_mode="Markdown")

        await run_async(f"wakeonlan {mac}")

        await query.edit_message_text(
            f"✅ *Magic Packet enviado*\n\nMAC: `{mac}`\n\n_El dispositivo debería encenderse en segundos_",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_network()
        )

    # ═══════════════════════════════════════════════════════════
    # PI-HOLE
    # ═══════════════════════════════════════════════════════════

    elif data == "pihole:stats":
        stats = pihole_svc.get_stats()

        if not stats:
            await query.edit_message_text(
                "❌ *Error conectando con Pi-hole*",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_pihole()
            )
            return

        percent = stats.percent_blocked

        text = f"""📊 *Estadísticas Pi-hole*

📈 *Consultas hoy:* {stats.total_queries:,}
🚫 *Bloqueadas:* {stats.blocked_queries:,} ({percent:.1f}%)
✅ *Permitidas:* {stats.total_queries - stats.blocked_queries:,}

📋 *Dominios en listas:* {stats.domains_on_blocklist:,}
🔒 *Estado:* {stats.status}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_pihole())

    elif data == "pihole:top_blocked":
        domains = pihole_svc.get_top_blocked(5)

        if not domains:
            text = "🚫 *Top Bloqueados*\n\n_Sin datos_"
        else:
            lines = ["🚫 *Top Dominios Bloqueados*", ""]
            for i, d in enumerate(domains, 1):
                domain = truncate(d.domain, 30)
                lines.append(f"{i}. `{domain}`")
                lines.append(f"   {d.count:,} bloqueos")
            text = "\n".join(lines)

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_pihole())

    elif data == "pihole:top_clients":
        clients = pihole_svc.get_top_clients(5)

        if not clients:
            text = "👥 *Top Clientes*\n\n_Sin datos_"
        else:
            lines = ["👥 *Top Clientes*", ""]
            for i, c in enumerate(clients, 1):
                name = device_svc.get_device_name(c.ip) or c.name
                lines.append(f"{i}. {escape_md(name)}")
                lines.append(f"   `{c.ip}` ({c.count:,} consultas)")
            text = "\n".join(lines)

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_pihole())

    elif data == "pihole:disable":
        success = pihole_svc.disable(300)
        if success:
            text = "⏸️ *Pi-hole pausado 5 minutos*\n\n_Los anuncios se mostrarán temporalmente_"
        else:
            text = "❌ *Error pausando Pi-hole*"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_pihole())

    elif data == "pihole:enable":
        success = pihole_svc.enable()
        if success:
            text = "▶️ *Pi-hole activado*\n\n_Bloqueo de anuncios activo_"
        else:
            text = "❌ *Error activando Pi-hole*"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_pihole())

    elif data == "pihole:block_prompt":
        context.user_data['action'] = 'block_domain'
        await query.edit_message_text(
            "🚫 *Bloquear Dominio*\n\n_Escribe el dominio a bloquear:_\n\nEjemplo: `facebook.com`",
            parse_mode="Markdown"
        )

    elif data == "pihole:allow_prompt":
        context.user_data['action'] = 'allow_domain'
        await query.edit_message_text(
            "✅ *Permitir Dominio*\n\n_Escribe el dominio a permitir:_\n\nEjemplo: `teams.microsoft.com`",
            parse_mode="Markdown"
        )

    # ═══════════════════════════════════════════════════════════
    # SISTEMA
    # ═══════════════════════════════════════════════════════════

    elif data == "sys:stats":
        stats = system_svc.get_stats()

        if not stats:
            await query.edit_message_text(
                "❌ *Error obteniendo estado*",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_system()
            )
            return

        text = f"""🖥️ *Estado del Sistema*

{system_svc.format_stats_message(stats)}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_system())

    elif data == "sys:docker":
        containers = system_svc.get_containers()

        if not containers:
            text = "🐳 *Contenedores Docker*\n\n_No hay contenedores_"
        else:
            lines = ["🐳 *Contenedores Docker*", ""]
            for c in containers:
                if c.health == "healthy":
                    emoji = "✅"
                elif c.health == "running":
                    emoji = "🟢"
                elif c.health == "unhealthy":
                    emoji = "🔴"
                else:
                    emoji = "⚪"

                lines.append(f"{emoji} *{c.name}*")
                lines.append(f"   {c.status}")
            text = "\n".join(lines)

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_system())

    elif data == "sys:speedtest":
        await query.edit_message_text("📈 *Ejecutando Speedtest...*\n\n_30-60 segundos_", parse_mode="Markdown")

        result = await system_svc.run_speedtest()

        if "error" in result:
            text = f"❌ *Speedtest*\n\n{result['error']}"
        else:
            text = f"""📈 *Speedtest*

⬇️ *Download:* {result.get('download', 'N/A')}
⬆️ *Upload:* {result.get('upload', 'N/A')}
📡 *Ping:* {result.get('ping', 'N/A')}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_system())

    elif data == "sys:restart_pihole":
        await query.edit_message_text("🔄 *Reiniciando Pi-hole...*", parse_mode="Markdown")

        await run_async("docker restart pihole", timeout=60)

        await query.edit_message_text(
            "✅ *Pi-hole reiniciado*",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_system()
        )

    # ═══════════════════════════════════════════════════════════
    # DISPOSITIVOS
    # ═══════════════════════════════════════════════════════════

    elif data == "dev:list":
        devices = await network_svc.scan_all(use_cache=True)

        if not devices:
            await query.edit_message_text(
                "📱 *Dispositivos*\n\n_No hay dispositivos conectados_",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_devices()
            )
            return

        lines = ["📱 *Dispositivos Conectados*", ""]

        for d in devices[:15]:
            icon = get_device_icon(d.vendor, d.hostname)
            name = device_svc.get_device_name(d.mac) or d.display_name
            trusted = "✅" if device_svc.is_trusted(d.mac) else "❓"
            lines.append(f"{trusted}{icon} `{d.ip}` {escape_md(name)}")

        lines.append(f"\n_Total: {len(devices)}_")

        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_devices()
        )

    elif data == "dev:trusted":
        trusted = device_svc.get_trusted_devices()

        if not trusted:
            text = "✅ *Dispositivos Confiables*\n\n_No hay dispositivos marcados_\n\nUsa 'Nombrar Dispositivo' para añadir"
        else:
            lines = ["✅ *Dispositivos Confiables*", ""]
            for d in trusted:
                lines.append(f"• *{d.name}*")
                lines.append(f"  `{d.mac}`")
            text = "\n".join(lines)

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_devices())

    elif data == "dev:name_prompt":
        await query.edit_message_text("🔍 *Buscando dispositivos...*", parse_mode="Markdown")

        devices = await network_svc.scan_all()

        if not devices:
            await query.edit_message_text(
                "❌ *No hay dispositivos*",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_devices()
            )
            return

        device_list = [(d.mac, d.display_name, d.ip) for d in devices[:8]]

        await query.edit_message_text(
            "🏷️ *Nombrar Dispositivo*\n\n_Selecciona el dispositivo:_",
            parse_mode="Markdown",
            reply_markup=Keyboards.device_selection(device_list, "dev:name")
        )

    elif data.startswith("dev:name:"):
        mac = data.split(":")[2]
        context.user_data['naming_mac'] = mac
        await query.edit_message_text(
            f"🏷️ *Nombrar Dispositivo*\n\nMAC: `{mac}`\n\n_Escribe el nombre:_\n\nEjemplo: TV Salón, iPhone María",
            parse_mode="Markdown"
        )

    elif data == "dev:clear_alerts":
        device_svc.clear_alerts()
        await query.edit_message_text(
            "✅ *Alertas limpiadas*\n\n_Se volverá a alertar de dispositivos nuevos_",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_devices()
        )

    elif data == "dev:offline":
        offline = network_svc.get_offline_devices()
        if not offline:
            text = "📴 *Dispositivos Offline*\n\n_Todos los dispositivos conocidos están online_"
        else:
            lines = ["📴 *Dispositivos Offline*", ""]
            for d in offline[:10]:
                name = device_svc.get_device_name(d.mac) or d.display_name
                lines.append(f"• {escape_md(name)}")
                lines.append(f"  `{d.ip}` - {escape_md(d.vendor or 'Desconocido')}")
            lines.append(f"\n_Total: {len(offline)} offline_")
            text = "\n".join(lines)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_devices())

    elif data == "dev:info_prompt":
        devices = network_svc.get_online_devices()
        if not devices:
            await query.edit_message_text(
                "📱 *Info Dispositivo*\n\n_No hay dispositivos online_\n\nEjecuta un escaneo primero.",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_devices()
            )
            return
        device_list = [(d.mac, d.display_name, d.ip) for d in devices[:8]]
        await query.edit_message_text(
            "🔍 *Info Dispositivo*\n\nSelecciona para ver detalles:",
            parse_mode="Markdown",
            reply_markup=Keyboards.device_selection(device_list, "dev:info")
        )

    elif data.startswith("dev:info:"):
        mac = data.split(":")[2]
        device = network_svc.get_device_by_mac(mac)
        if not device:
            await query.edit_message_text(
                "❌ *Dispositivo no encontrado*\n\nPuede que se haya desconectado.\nEjecuta un nuevo escaneo.",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_devices()
            )
            return

        known = device_svc.get_device(mac)
        name = known.name if known else device.display_name
        trusted_icon = "✅" if (known and known.trusted) else "❓"
        trusted_text = "Dispositivo verificado" if (known and known.trusted) else "Sin verificar"

        text = f"""📱 *{escape_md(name)}*

━━━━━━━━━━━━━━━━━━━━
*Información de Red*
━━━━━━━━━━━━━━━━━━━━
📍 IP: `{device.ip}`
📱 MAC: `{device.mac}`
🏭 Fabricante: {escape_md(device.vendor or 'Desconocido')}
🖥️ Tipo: {escape_md(device.device_type)}

━━━━━━━━━━━━━━━━━━━━
*Estado*
━━━━━━━━━━━━━━━━━━━━
{trusted_icon} {trusted_text}
📊 Visto {device.times_seen} veces
🕐 Primera vez: {device.first_seen.strftime('%d/%m %H:%M')}
🕐 Última vez: {device.last_seen.strftime('%d/%m %H:%M')}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.device_actions(mac))

    elif data.startswith("dev:ports:"):
        mac = data.split(":")[2]
        device = network_svc.get_device_by_mac(mac)
        if not device:
            await query.edit_message_text("❌ Dispositivo no encontrado", parse_mode="Markdown", reply_markup=Keyboards.back_to_devices())
            return

        await query.edit_message_text(f"🔌 *Escaneando puertos de {device.ip}...*\n\n_30-60 segundos_", parse_mode="Markdown")

        ports = await network_svc.scan_device_ports(device.ip)

        if ports:
            lines = [f"🔌 *Puertos abiertos: {device.ip}*", ""]
            for port, service in ports:
                lines.append(f"• *{port}* - {service}")
            text = "\n".join(lines)
        else:
            text = f"🔌 *{device.ip}*\n\n_No se encontraron puertos abiertos_"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_devices())

    elif data.startswith("dev:trust:"):
        mac = data.split(":")[2]
        device_svc.set_trusted(mac, True)
        await query.edit_message_text(
            "✅ *Dispositivo Verificado*\n\nMarcado como confiable.\nNo recibirás alertas sobre él.",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_devices()
        )

    elif data.startswith("dev:untrust:"):
        mac = data.split(":")[2]
        device_svc.set_trusted(mac, False)
        await query.edit_message_text(
            "⚠️ *Dispositivo No Verificado*\n\nMarcado como no confiable.\nRecibirás alertas si se conecta.",
            parse_mode="Markdown",
            reply_markup=Keyboards.back_to_devices()
        )

    # ═══════════════════════════════════════════════════════════
    # HERRAMIENTAS DE RED
    # ═══════════════════════════════════════════════════════════

    elif data == "menu:tools":
        # Tests rápidos
        dns_out, _, dns_code = await run_async("dig +short google.com @127.0.0.1 -p 5335 2>/dev/null | head -1", timeout=3)
        gw_out, _, _ = await run_async(f"ping -c 1 -W 1 {config.GATEWAY} 2>/dev/null | grep time= | awk -F'time=' '{{print $2}}'", timeout=3)
        inet_out, _, _ = await run_async("ping -c 1 -W 2 8.8.8.8 2>/dev/null | grep time= | awk -F'time=' '{print $2}'", timeout=4)

        dns_ok = "🟢" if dns_out and dns_code == 0 else "🔴"
        gw_ok = "🟢" if gw_out else "🔴"
        inet_ok = "🟢" if inet_out else "🔴"

        gw_ms = gw_out.strip() if gw_out else "timeout"
        inet_ms = inet_out.strip() if inet_out else "timeout"

        text = f"""*HERRAMIENTAS*

{dns_ok}  DNS Unbound
{gw_ok}  Gateway {gw_ms}
{inet_ok}  Internet {inet_ms}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.tools_menu())

    elif data == "tools:dns_prompt":
        context.user_data['action'] = 'dns_lookup'
        await query.edit_message_text(
            "🌐 *DNS Lookup*\n\n_Escribe el dominio:_\n\nEjemplo: `google.com`",
            parse_mode="Markdown"
        )

    elif data == "tools:trace_prompt":
        context.user_data['action'] = 'traceroute'
        await query.edit_message_text(
            "🛤️ *Traceroute*\n\n_Escribe el host o IP:_\n\nEjemplo: `google.com` o `8.8.8.8`",
            parse_mode="Markdown"
        )

    elif data == "tools:port_prompt":
        context.user_data['action'] = 'port_check'
        await query.edit_message_text(
            "🔌 *Port Check*\n\n_Escribe host:puerto_\n\nEjemplo: `google.com:443`",
            parse_mode="Markdown"
        )

    elif data == "tools:portscan_prompt":
        context.user_data['action'] = 'port_scan'
        await query.edit_message_text(
            f"📡 *Port Scan*\n\n_Escribe la IP:_\n\nEjemplo: `{config.GATEWAY}`",
            parse_mode="Markdown"
        )

    elif data == "tools:ping_prompt":
        context.user_data['action'] = 'ping'
        await query.edit_message_text(
            "🏓 *Ping*\n\n_Escribe el host o IP:_\n\nEjemplo: `google.com`",
            parse_mode="Markdown"
        )

    # ═══════════════════════════════════════════════════════════
    # RED AVANZADA
    # ═══════════════════════════════════════════════════════════

    elif data == "net:deep_scan":
        await query.edit_message_text("🔬 *Escaneo Profundo*\n\n_Detectando OS y servicios..._\n_Esto puede tardar 2-3 minutos_", parse_mode="Markdown")

        devices = await network_svc.scan_all(deep=True)

        if not devices:
            await query.edit_message_text("🔬 *Escaneo completado*\n\n_No se encontraron dispositivos_", parse_mode="Markdown", reply_markup=Keyboards.back_to_network())
            return

        lines = ["🔬 *Escaneo Profundo*", ""]
        for d in devices[:10]:
            icon = d.icon
            name = device_svc.get_device_name(d.mac) or d.display_name
            os_info = f" ({escape_md(d.os_guess)})" if d.os_guess else ""
            lines.append(f"{icon} `{d.ip}` {escape_md(name)}{os_info}")

        lines.append(f"\n_Total: {len(devices)} dispositivos_")

        await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=Keyboards.back_to_network())

    elif data == "net:stats":
        stats = network_svc.get_statistics()

        by_type_lines = []
        for t, count in sorted(stats['by_type'].items(), key=lambda x: -x[1])[:5]:
            by_type_lines.append(f"  • {escape_md(t)}: {count}")

        by_vendor_lines = []
        for v, count in sorted(stats['by_vendor'].items(), key=lambda x: -x[1])[:5]:
            by_vendor_lines.append(f"  • {escape_md(v)}: {count}")

        text = f"""📊 *Estadísticas de Red*

📱 *Total conocidos:* {stats['total_known']}
🟢 *Online:* {stats['online']}
🔴 *Offline:* {stats['offline']}

*Por tipo:*
{chr(10).join(by_type_lines) if by_type_lines else '  _Sin datos_'}

*Por fabricante:*
{chr(10).join(by_vendor_lines) if by_vendor_lines else '  _Sin datos_'}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_network())

    # ═══════════════════════════════════════════════════════════
    # SISTEMA AVANZADO
    # ═══════════════════════════════════════════════════════════

    elif data == "sys:restart_unbound":
        await query.edit_message_text("🔄 *Reiniciando Unbound...*", parse_mode="Markdown")
        await run_async("docker restart unbound", timeout=60)
        await query.edit_message_text("✅ *Unbound reiniciado*", parse_mode="Markdown", reply_markup=Keyboards.back_to_system())

    elif data == "sys:pihole_logs":
        stdout, _, _ = await run_async("docker logs pihole --tail 15 2>&1", timeout=10)
        text = f"📋 *Logs Pi-hole*\n\n```\n{stdout[:1500] if stdout else 'Sin logs'}\n```"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_system())

    elif data == "pihole:top_permitted":
        domains = pihole_svc.get_top_permitted(5)
        if not domains:
            text = "✅ *Top Permitidos*\n\n_Sin datos_"
        else:
            lines = ["✅ *Top Dominios Permitidos*", ""]
            for i, d in enumerate(domains, 1):
                domain = truncate(d.domain, 30)
                lines.append(f"{i}. `{domain}`")
                lines.append(f"   {d.count:,} consultas")
            text = "\n".join(lines)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_pihole())

    # ═══════════════════════════════════════════════════════════
    # VPN SPLIT ROUTING
    # ═══════════════════════════════════════════════════════════

    elif data == "menu:vpn":
        # Estado completo desde el script
        stdout, _, _ = await run_async("sudo /usr/local/bin/vpn-manager status", timeout=10)

        vpn_state = "down"
        domains = "0"
        vpn_ip = "N/A"
        mode = "split"

        for line in (stdout.strip().split('\n') if stdout else []):
            if line.startswith("vpn:"): vpn_state = line.split(":")[1]
            elif line.startswith("domains:"): domains = line.split(":")[1]
            elif line.startswith("ip:"): vpn_ip = line.split(":")[1]
            elif line.startswith("mode:"): mode = line.split(":")[1]

        # IP directa
        direct_ip, _, _ = await run_async("curl -s --max-time 3 ifconfig.co", timeout=5)
        direct = direct_ip.strip() if direct_ip else "N/A"

        if vpn_state == "active":
            if mode == "all":
                text = f"""*VPN ACTIVA*  🟢

🔒  *Modo: Protección Total*

Todo tu tráfico sale por USA.
Vodafone no ve tu actividad.

*Tu conexión:*
🇺🇸  Salida: `{vpn_ip}`
📋  Todo el tráfico protegido

_Netflix/HBO verán IP de USA_"""
            else:
                text = f"""*VPN ACTIVA*  🟢

🔀  *Modo: Split Routing*

Solo dominios seleccionados
pasan por VPN.

*Tu conexión:*
🇺🇸  VPN: `{vpn_ip}`
🇪🇸  Directa: `{direct}`
📋  {domains} dominios protegidos

_Streaming rápido + privacidad_"""

        elif vpn_state == "stale":
            text = f"""*VPN INESTABLE*  🟡

El túnel perdió sincronización.

*Estado:*
🇺🇸  Última IP: `{vpn_ip}`
⚠️  Handshake expirado

*Solución:*
Pulsa "Encender" para reconectar."""

        else:
            text = f"""*VPN APAGADA*  🔴

Sin protección VPN activa.

*Tu conexión:*
🇪🇸  IP: `{direct}`
👁  Vodafone ve tu tráfico

*Recomendación:*
Activa la VPN para protegerte."""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.vpn_menu())

    elif data == "vpn:status":
        stdout, _, _ = await run_async("sudo /usr/local/bin/vpn-manager status", timeout=10)
        wg_out, _, _ = await run_async("sudo wg show wg-us 2>/dev/null", timeout=5)

        vpn_state = "down"
        vpn_ip = "N/A"
        domains = "0"
        mode = "split"

        for line in (stdout.strip().split('\n') if stdout else []):
            if line.startswith("vpn:"): vpn_state = line.split(":")[1]
            elif line.startswith("domains:"): domains = line.split(":")[1]
            elif line.startswith("ip:"): vpn_ip = line.split(":")[1]
            elif line.startswith("mode:"): mode = line.split(":")[1]

        rx = tx = ""
        handshake = ""
        if wg_out:
            for wg_line in wg_out.split('\n'):
                if 'transfer' in wg_line and ':' in wg_line:
                    parts = wg_line.split(':', 1)[1].strip()
                    if 'received' in parts and 'sent' in parts:
                        rx = parts.split('received')[0].strip()
                        tx = parts.split(',')[1].replace('sent', '').strip()
                elif 'latest handshake' in wg_line and ':' in wg_line:
                    handshake = wg_line.split(':', 1)[1].strip()

        direct_ip, _, _ = await run_async("curl -s --max-time 3 ifconfig.co", timeout=5)
        direct = direct_ip.strip() if direct_ip else "N/A"

        mode_text = "Todo VPN" if mode == "all" else "Split"

        if vpn_state == "active":
            status_icon = "🟢"
            status_text = "Conectada"
        elif vpn_state == "stale":
            status_icon = "🟡"
            status_text = "Inestable"
        else:
            status_icon = "🔴"
            status_text = "Desconectada"

        text = f"""*ESTADO VPN*

{status_icon}  {status_text}  ·  {mode_text}

*Túnel WireGuard*
🤝  Handshake: {handshake or 'N/A'}
⬇️  Recibido: {rx or 'N/A'}
⬆️  Enviado: {tx or 'N/A'}

*Direcciones IP*
🇺🇸  VPN: `{vpn_ip}`
🇪🇸  Directa: `{direct}`

📋  {domains} dominios en lista"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.vpn_menu())

    elif data == "vpn:split":
        await query.edit_message_text("⏳ Configurando...", parse_mode="Markdown")
        stdout, _, _ = await run_async("sudo /usr/local/bin/vpn-manager split-mode", timeout=10)

        # Obtener estado actual
        status_out, _, _ = await run_async("sudo /usr/local/bin/vpn-manager status", timeout=5)
        domains = "0"
        for line in (status_out.strip().split('\n') if status_out else []):
            if line.startswith("domains:"): domains = line.split(":")[1]

        text = f"""*MODO SPLIT*  ✓

Configuración aplicada.

*Routing activo:*
🔒  {domains} dominios → USA
⚡  Resto → Conexión directa

Streaming sin límites.
Privacidad donde importa."""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.vpn_menu())

    elif data == "vpn:all":
        await query.edit_message_text("⏳ Activando protección total...", parse_mode="Markdown")
        stdout, stderr, code = await run_async("sudo /usr/local/bin/vpn-manager all-vpn", timeout=10)

        if stdout and "error:" in stdout.lower():
            text = """*ERROR*  ❌

VPN no conectada.

Primero pulsa "Encender VPN"
y espera a que esté 🟢"""
        else:
            # Obtener IP para confirmar
            vpn_ip, _, _ = await run_async("curl -s --max-time 5 ipinfo.io/ip", timeout=8)
            ip = vpn_ip.strip() if vpn_ip else "USA"

            text = f"""*MODO TODO VPN*  ✓

Protección total activada.

*Tu conexión:*
🇺🇸  Todo sale por `{ip}`
👁  ISP no ve tu actividad

⚠️  Velocidad reducida."""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.vpn_menu())

    elif data == "vpn:add_prompt":
        context.user_data['action'] = 'vpn_add_domain'
        await query.edit_message_text(
            """*AÑADIR DOMINIO*

Escribe el dominio a proteger.
Saldrá por VPN (USA).

Ejemplo: `reddit.com`""",
            parse_mode="Markdown"
        )

    elif data == "vpn:list":
        stdout, _, _ = await run_async("sudo /usr/local/bin/vpn-manager list-domains", timeout=10)
        domains = [d.strip() for d in stdout.strip().split('\n') if d.strip()] if stdout else []

        if domains:
            lines = [f"*DOMINIOS PROTEGIDOS*  ({len(domains)})\n"]
            for d in domains[:12]:
                lines.append(f"🔒  `{d}`")
            if len(domains) > 12:
                lines.append(f"\n_+{len(domains) - 12} más_")
            text = "\n".join(lines)
        else:
            text = """*DOMINIOS PROTEGIDOS*

Lista vacía.

Usa "Añadir" para proteger
dominios con la VPN."""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.vpn_menu())

    elif data == "vpn:myip":
        await query.edit_message_text("⏳ Consultando...", parse_mode="Markdown")

        vpn_ip, _, _ = await run_async("curl -s --max-time 8 ipinfo.io/ip", timeout=12)
        direct_ip, _, _ = await run_async("curl -s --max-time 8 ifconfig.co", timeout=12)

        vpn = vpn_ip.strip() if vpn_ip else "Error"
        direct = direct_ip.strip() if direct_ip else "Error"

        if vpn != direct and vpn != "Error" and direct != "Error":
            status = "✓  Split funcionando"
        elif vpn == direct and vpn != "Error":
            status = "⚠️  Sin split activo"
        else:
            status = "❌  Error de conexión"

        text = f"""*TEST DE IP*

🇺🇸  VPN: `{vpn}`
🇪🇸  Directa: `{direct}`

{status}"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.vpn_menu())

    elif data == "vpn:up":
        await query.edit_message_text("⏳ Conectando...", parse_mode="Markdown")
        stdout, _, code = await run_async("sudo /usr/local/bin/vpn-manager vpn-up", timeout=15)

        # Esperar y verificar
        await run_async("sleep 2", timeout=5)
        status_out, _, _ = await run_async("sudo /usr/local/bin/vpn-manager status", timeout=5)

        vpn_ip = "N/A"
        for line in (status_out.strip().split('\n') if status_out else []):
            if line.startswith("ip:"): vpn_ip = line.split(":")[1]

        if code == 0:
            text = f"""*VPN CONECTADA*  ✓

Túnel WireGuard activo.

🇺🇸  IP: `{vpn_ip}`
📍  Servidor: AWS Lightsail"""
        else:
            text = """*ERROR*  ❌

No se pudo conectar.
Verifica la configuración."""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.vpn_menu())

    elif data == "vpn:down":
        await query.edit_message_text("⏳ Desconectando...", parse_mode="Markdown")
        stdout, _, _ = await run_async("sudo /usr/local/bin/vpn-manager vpn-down", timeout=15)

        direct_ip, _, _ = await run_async("curl -s --max-time 3 ifconfig.co", timeout=5)
        direct = direct_ip.strip() if direct_ip else "N/A"

        text = f"""*VPN APAGADA*  ✓

Túnel cerrado.

🇪🇸  IP: `{direct}`
⚠️  Sin protección VPN"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.vpn_menu())

    # ═══════════════════════════════════════════════════════════
    # SEGURIDAD
    # ═══════════════════════════════════════════════════════════

    elif data == "menu:security":
        # Estado general de seguridad
        f2b_out, _, f2b_code = await run_async("sudo fail2ban-client status sshd 2>/dev/null", timeout=5)
        ssh_out, _, _ = await run_async("journalctl -u ssh --since '1 hour ago' --no-pager 2>/dev/null | grep -c 'Failed password' || echo 0", timeout=5)
        banned_out, _, _ = await run_async("sudo fail2ban-client status sshd 2>/dev/null | grep 'Banned IP' | awk -F: '{print $2}' | xargs | wc -w", timeout=5)

        f2b_active = "🟢" if f2b_code == 0 else "🔴"
        ssh_fails = ssh_out.strip() if ssh_out else "0"
        banned_count = banned_out.strip() if banned_out else "0"

        # SSH config
        ssh_pw, _, _ = await run_async("grep -E '^PasswordAuthentication' /etc/ssh/sshd_config.d/*.conf 2>/dev/null | head -1 | awk '{print $2}'", timeout=3)
        ssh_secure = "🟢" if ssh_pw and "no" in ssh_pw.lower() else "🟡"

        text = f"""*SEGURIDAD*

{f2b_active}  Fail2ban activo
{ssh_secure}  SSH sin contraseña
🔒  {banned_count} IPs baneadas
⚠️  {ssh_fails} intentos fallidos (1h)"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.security_menu())

    elif data == "sec:status":
        await query.edit_message_text("🔍 *Analizando seguridad...*", parse_mode="Markdown")

        # Fail2ban
        f2b_out, _, f2b_code = await run_async("sudo fail2ban-client status 2>/dev/null", timeout=5)
        f2b_status = "✅ Activo" if f2b_code == 0 else "❌ Inactivo"

        # SSH config
        ssh_pw, _, _ = await run_async("grep -E '^PasswordAuthentication' /etc/ssh/sshd_config.d/*.conf 2>/dev/null | head -1", timeout=3)
        ssh_root, _, _ = await run_async("grep -E '^PermitRootLogin' /etc/ssh/sshd_config.d/*.conf 2>/dev/null | head -1", timeout=3)

        ssh_pw_status = "✅ Deshabilitado" if ssh_pw and "no" in ssh_pw.lower() else "⚠️ Habilitado"
        ssh_root_status = "✅ Deshabilitado" if ssh_root and "no" in ssh_root.lower() else "⚠️ Habilitado"

        # Firewall
        ufw_out, _, ufw_code = await run_async("sudo ufw status 2>/dev/null | head -1", timeout=5)
        ufw_status = "✅ Activo" if ufw_out and "active" in ufw_out.lower() else "⚠️ Inactivo"

        # Últimos accesos
        last_login, _, _ = await run_async("last -n 3 --time-format short 2>/dev/null | head -3", timeout=5)

        text = f"""*AUDITORÍA DE SEGURIDAD*

*Protecciones*
🛡  Fail2ban: {f2b_status}
🔥  Firewall: {ufw_status}

*SSH Hardening*
🔑  Contraseña: {ssh_pw_status}
👤  Root login: {ssh_root_status}

*Últimos accesos*
```
{last_login.strip() if last_login else 'Sin datos'}
```"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_security())

    elif data == "sec:banned":
        stdout, _, code = await run_async("sudo fail2ban-client status sshd 2>/dev/null", timeout=10)

        if code != 0:
            text = "🚫 *IPs Baneadas*\n\n_Fail2ban no disponible_"
        else:
            # Extraer IPs baneadas
            banned_line = ""
            for line in stdout.split('\n'):
                if 'Banned IP' in line:
                    banned_line = line.split(':')[-1].strip()
                    break

            if banned_line:
                ips = banned_line.split()
                lines = ["🚫 *IPs Baneadas*", ""]
                for ip in ips[:10]:
                    lines.append(f"• `{ip}`")
                lines.append(f"\n_Total: {len(ips)}_")
                text = "\n".join(lines)
            else:
                text = "🚫 *IPs Baneadas*\n\n✅ No hay IPs baneadas\n\n_Tu red está tranquila_"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_security())

    elif data == "sec:intruders":
        await query.edit_message_text("🔍 *Buscando intentos de intrusión...*", parse_mode="Markdown")

        # Intentos fallidos recientes
        stdout, _, _ = await run_async(
            "journalctl -u ssh --since '24 hours ago' --no-pager 2>/dev/null | grep 'Failed password' | tail -10",
            timeout=15
        )

        if stdout and stdout.strip():
            lines = ["👁️ *Intentos de Intrusión (24h)*", ""]

            for attempt in stdout.strip().split('\n')[:8]:
                # Extraer IP y usuario
                if 'from' in attempt:
                    parts = attempt.split('from')
                    if len(parts) > 1:
                        ip_part = parts[1].strip().split()[0]
                        user_part = attempt.split('for')[-1].split('from')[0].strip() if 'for' in attempt else "?"
                        time_part = ' '.join(attempt.split()[:3])
                        lines.append(f"⚠️ `{ip_part}`")
                        lines.append(f"   Usuario: {user_part}")
                        lines.append(f"   {time_part}")
                        lines.append("")

            text = "\n".join(lines)
        else:
            text = """👁️ *Intentos de Intrusión*

✅ Sin intentos en 24 horas

_Tu sistema está seguro_"""

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_security())

    elif data == "sec:ssh_logs":
        stdout, _, _ = await run_async(
            "journalctl -u ssh --since '1 hour ago' --no-pager 2>/dev/null | tail -15",
            timeout=10
        )

        if stdout and stdout.strip():
            # Limpiar y truncar
            log_text = stdout.strip()[:1200]
            text = f"📋 *Logs SSH (1h)*\n\n```\n{log_text}\n```"
        else:
            text = "📋 *Logs SSH*\n\n_Sin actividad reciente_"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=Keyboards.back_to_security())

    elif data == "sec:unban_prompt":
        # Mostrar IPs baneadas para desbanear
        stdout, _, code = await run_async("sudo fail2ban-client status sshd 2>/dev/null", timeout=10)

        banned_ips = []
        if code == 0:
            for line in stdout.split('\n'):
                if 'Banned IP' in line:
                    banned_line = line.split(':')[-1].strip()
                    banned_ips = banned_line.split()
                    break

        if not banned_ips:
            await query.edit_message_text(
                "🔓 *Desbanear IP*\n\n_No hay IPs baneadas_",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_security()
            )
            return

        context.user_data['action'] = 'unban_ip'
        lines = ["🔓 *Desbanear IP*\n", "_Escribe la IP a desbanear:_\n", "*IPs baneadas:*"]
        for ip in banned_ips[:5]:
            lines.append(f"• `{ip}`")

        await query.edit_message_text("\n".join(lines), parse_mode="Markdown")

    elif data == "sec:ban_prompt":
        context.user_data['action'] = 'ban_ip'
        await query.edit_message_text(
            "🔒 *Banear IP*\n\n_Escribe la IP a banear:_\n\nEjemplo: `1.2.3.4`\n\n⚠️ No te banees a ti mismo",
            parse_mode="Markdown"
        )


def setup_callback_handlers(app: Application):
    """Registra el handler de callbacks."""
    app.add_handler(CallbackQueryHandler(callback_handler))
