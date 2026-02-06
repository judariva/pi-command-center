"""Handlers de mensajes de texto."""
import logging
import re
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, Application, filters

from config import config
from services import DeviceService, PiholeService, NetworkService
from keyboards import Keyboards
from utils import escape_md

logger = logging.getLogger(__name__)


def is_valid_ip(ip: str) -> bool:
    """Valida formato de IP."""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    parts = ip.split('.')
    return all(0 <= int(p) <= 255 for p in parts)


def is_valid_host(host: str) -> bool:
    """Valida formato de host (IP o dominio)."""
    if is_valid_ip(host):
        return True
    # Dominio
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.?[a-zA-Z]{2,}$'
    return bool(re.match(pattern, host))


def is_authorized(user_id: int) -> bool:
    return user_id in config.AUTHORIZED_USERS


def is_valid_domain(domain: str) -> bool:
    """Valida formato de dominio."""
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensajes de texto."""
    if not is_authorized(update.effective_user.id):
        return

    text = update.message.text.strip()
    device_svc: DeviceService = context.bot_data['device_service']
    pihole_svc: PiholeService = context.bot_data['pihole_service']

    # ─── NOMBRAR DISPOSITIVO ───
    if 'naming_mac' in context.user_data:
        mac = context.user_data.pop('naming_mac')

        if len(text) < 2:
            await update.message.reply_text(
                "❌ El nombre debe tener al menos 2 caracteres",
                reply_markup=Keyboards.back_to_devices()
            )
            return

        if len(text) > 30:
            text = text[:30]

        device = device_svc.add_device(mac=mac, name=text, trusted=True)

        await update.message.reply_text(
            f"✅ *Dispositivo guardado*\n\n"
            f"🏷️ *Nombre:* {device.name}\n"
            f"📱 *MAC:* `{device.mac}`\n"
            f"✅ Marcado como confiable",
            parse_mode="Markdown",
            reply_markup=Keyboards.devices_menu()
        )
        return

    # ─── BLOQUEAR DOMINIO ───
    if context.user_data.get('action') == 'block_domain':
        context.user_data.pop('action')
        domain = text.lower().strip()

        # Quitar http/https si lo incluyó
        domain = re.sub(r'^https?://', '', domain)
        domain = domain.split('/')[0]  # Quitar path

        if not is_valid_domain(domain):
            await update.message.reply_text(
                f"❌ *Dominio inválido*\n\n`{domain}`\n\n_Formato correcto: example.com_",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_pihole()
            )
            return

        success = pihole_svc.block_domain(domain)

        if success:
            await update.message.reply_text(
                f"🚫 *Dominio bloqueado*\n\n`{domain}`\n\n_Añadido a la lista negra_",
                parse_mode="Markdown",
                reply_markup=Keyboards.pihole_menu()
            )
        else:
            await update.message.reply_text(
                f"❌ *Error bloqueando dominio*\n\n`{domain}`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_pihole()
            )
        return

    # ─── PERMITIR DOMINIO ───
    if context.user_data.get('action') == 'allow_domain':
        context.user_data.pop('action')
        domain = text.lower().strip()

        domain = re.sub(r'^https?://', '', domain)
        domain = domain.split('/')[0]

        if not is_valid_domain(domain):
            await update.message.reply_text(
                f"❌ *Dominio inválido*\n\n`{domain}`\n\n_Formato correcto: example.com_",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_pihole()
            )
            return

        success = pihole_svc.allow_domain(domain)

        if success:
            await update.message.reply_text(
                f"✅ *Dominio permitido*\n\n`{domain}`\n\n_Añadido a la lista blanca_",
                parse_mode="Markdown",
                reply_markup=Keyboards.pihole_menu()
            )
        else:
            await update.message.reply_text(
                f"❌ *Error permitiendo dominio*\n\n`{domain}`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_pihole()
            )
        return

    # ─── AÑADIR DOMINIO A VPN ───
    if context.user_data.get('action') == 'vpn_add_domain':
        context.user_data.pop('action')
        domain = text.lower().strip()

        domain = re.sub(r'^https?://', '', domain)
        domain = domain.split('/')[0]

        if not is_valid_domain(domain):
            await update.message.reply_text(
                f"❌ *Dominio inválido*\n\n`{domain}`\n\n_Formato: reddit.com_",
                parse_mode="Markdown",
                reply_markup=Keyboards.vpn_menu()
            )
            return

        from utils.shell import run_async
        stdout, _, code = await run_async(f"sudo /usr/local/bin/vpn-manager add-domain {domain}", timeout=10)

        if code == 0:
            await update.message.reply_text(
                f"✅ *Dominio añadido a VPN*\n\n`{domain}`\n\n_El tráfico a este dominio ahora va por VPN_",
                parse_mode="Markdown",
                reply_markup=Keyboards.vpn_menu()
            )
        else:
            await update.message.reply_text(
                f"❌ *Error añadiendo dominio*\n\n`{domain}`",
                parse_mode="Markdown",
                reply_markup=Keyboards.vpn_menu()
            )
        return

    # ─── BANEAR IP ───
    if context.user_data.get('action') == 'ban_ip':
        context.user_data.pop('action')
        ip = text.strip()

        if not is_valid_ip(ip):
            await update.message.reply_text(
                f"❌ *IP inválida*\n\n`{ip}`\n\n_Formato: 1.2.3.4_",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_security()
            )
            return

        # No banear IPs locales
        if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
            await update.message.reply_text(
                f"⚠️ *No se puede banear IP local*\n\n`{ip}`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_security()
            )
            return

        from utils.shell import run_async
        stdout, stderr, code = await run_async(f"sudo fail2ban-client set sshd banip {ip}", timeout=10)

        if code == 0:
            await update.message.reply_text(
                f"🔒 *IP Baneada*\n\n`{ip}`\n\n_No podrá conectarse a SSH_",
                parse_mode="Markdown",
                reply_markup=Keyboards.security_menu()
            )
        else:
            await update.message.reply_text(
                f"❌ *Error baneando IP*\n\n`{ip}`\n\n_{stderr or 'Error desconocido'}_",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_security()
            )
        return

    # ─── DESBANEAR IP ───
    if context.user_data.get('action') == 'unban_ip':
        context.user_data.pop('action')
        ip = text.strip()

        if not is_valid_ip(ip):
            await update.message.reply_text(
                f"❌ *IP inválida*\n\n`{ip}`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_security()
            )
            return

        from utils.shell import run_async
        stdout, stderr, code = await run_async(f"sudo fail2ban-client set sshd unbanip {ip}", timeout=10)

        if code == 0:
            await update.message.reply_text(
                f"🔓 *IP Desbaneada*\n\n`{ip}`\n\n_Puede volver a conectarse_",
                parse_mode="Markdown",
                reply_markup=Keyboards.security_menu()
            )
        else:
            await update.message.reply_text(
                f"❌ *Error desbaneando IP*\n\n`{ip}`\n\n_{stderr or 'IP no estaba baneada'}_",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_security()
            )
        return

    # ─── DNS LOOKUP ───
    if context.user_data.get('action') == 'dns_lookup':
        context.user_data.pop('action')
        domain = text.lower().strip()
        domain = re.sub(r'^https?://', '', domain)
        domain = domain.split('/')[0]

        if not is_valid_host(domain):
            await update.message.reply_text(
                f"❌ *Dominio/IP inválido*\n\n`{domain}`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_tools()
            )
            return

        msg = await update.message.reply_text(f"🔍 Consultando DNS para `{domain}`...", parse_mode="Markdown")
        net_svc: NetworkService = context.bot_data['network_service']

        try:
            result = await net_svc.dns_lookup(domain)
            lines = [f"🌐 *DNS Lookup: {escape_md(domain)}*\n"]

            if result.get('A'):
                lines.append(f"📍 *IPv4:* `{', '.join(result['A'])}`")
            if result.get('AAAA'):
                lines.append(f"📍 *IPv6:* `{', '.join(result['AAAA'][:2])}`")
            if result.get('MX'):
                mx_list = [f"`{m}`" for m in result['MX'][:3]]
                lines.append(f"📧 *MX:* {', '.join(mx_list)}")
            if result.get('NS'):
                ns_list = [f"`{n}`" for n in result['NS'][:3]]
                lines.append(f"🖥️ *NS:* {', '.join(ns_list)}")
            if result.get('CNAME'):
                lines.append(f"🔗 *CNAME:* `{result['CNAME'][0]}`")
            if result.get('TXT'):
                txt = result['TXT'][0][:100]
                lines.append(f"📝 *TXT:* `{escape_md(txt)}`")

            if len(lines) == 1:
                lines.append("⚠️ Sin registros encontrados")

            await msg.edit_text("\n".join(lines), parse_mode="Markdown", reply_markup=Keyboards.back_to_tools())
        except Exception as e:
            logger.error(f"DNS lookup error: {e}")
            await msg.edit_text(f"❌ Error en DNS lookup: `{escape_md(str(e))}`", parse_mode="Markdown", reply_markup=Keyboards.back_to_tools())
        return

    # ─── TRACEROUTE ───
    if context.user_data.get('action') == 'traceroute':
        context.user_data.pop('action')
        host = text.strip()
        host = re.sub(r'^https?://', '', host)
        host = host.split('/')[0]

        if not is_valid_host(host):
            await update.message.reply_text(
                f"❌ *Host inválido*\n\n`{host}`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_tools()
            )
            return

        msg = await update.message.reply_text(f"🛤️ Traceroute a `{host}`...\n_Esto puede tardar 30-60s_", parse_mode="Markdown")
        net_svc: NetworkService = context.bot_data['network_service']

        try:
            hops = await net_svc.traceroute(host)
            lines = [f"🛤️ *Traceroute: {host}*\n"]

            for hop in hops[:15]:
                if hop['ip'] == '*':
                    lines.append(f"`{hop['hop']:2}` * * *")
                else:
                    rtt = f"{hop['rtt']:.1f}ms" if hop['rtt'] else "?"
                    lines.append(f"`{hop['hop']:2}` {hop['ip']} ({rtt})")

            if len(hops) > 15:
                lines.append(f"_...y {len(hops) - 15} saltos más_")

            await msg.edit_text("\n".join(lines), parse_mode="Markdown", reply_markup=Keyboards.back_to_tools())
        except Exception as e:
            logger.error(f"Traceroute error: {e}")
            await msg.edit_text(f"❌ Error en traceroute", reply_markup=Keyboards.back_to_tools())
        return

    # ─── PORT CHECK (host:puerto) ───
    if context.user_data.get('action') == 'port_check':
        context.user_data.pop('action')

        # Parsear host:puerto
        if ':' not in text:
            await update.message.reply_text(
                "❌ *Formato inválido*\n\nUsa: `host:puerto`\nEjemplo: `google.com:443`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_tools()
            )
            return

        parts = text.rsplit(':', 1)
        host = parts[0].strip()
        try:
            port = int(parts[1].strip())
            if not 1 <= port <= 65535:
                raise ValueError()
        except ValueError:
            await update.message.reply_text(
                "❌ *Puerto inválido*\n\nDebe ser un número entre 1 y 65535",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_tools()
            )
            return

        if not is_valid_host(host):
            await update.message.reply_text(
                f"❌ *Host inválido*\n\n`{host}`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_tools()
            )
            return

        msg = await update.message.reply_text(f"🔌 Verificando `{host}:{port}`...", parse_mode="Markdown")
        net_svc: NetworkService = context.bot_data['network_service']

        try:
            is_open, latency = await net_svc.check_port(host, port)
            if is_open:
                await msg.edit_text(
                    f"✅ *Puerto ABIERTO*\n\n"
                    f"🖥️ Host: `{host}`\n"
                    f"🔌 Puerto: `{port}`\n"
                    f"⏱️ Latencia: `{latency:.0f}ms`",
                    parse_mode="Markdown",
                    reply_markup=Keyboards.back_to_tools()
                )
            else:
                await msg.edit_text(
                    f"❌ *Puerto CERRADO/FILTRADO*\n\n"
                    f"🖥️ Host: `{host}`\n"
                    f"🔌 Puerto: `{port}`",
                    parse_mode="Markdown",
                    reply_markup=Keyboards.back_to_tools()
                )
        except Exception as e:
            logger.error(f"Port check error: {e}")
            await msg.edit_text(f"❌ Error verificando puerto", reply_markup=Keyboards.back_to_tools())
        return

    # ─── PORT SCAN (IP) ───
    if context.user_data.get('action') == 'port_scan':
        context.user_data.pop('action')
        ip = text.strip()

        if not is_valid_ip(ip):
            await update.message.reply_text(
                f"❌ *IP inválida*\n\n`{ip}`\n\nEjemplo: `192.168.0.100`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_tools()
            )
            return

        msg = await update.message.reply_text(f"📡 Escaneando puertos en `{ip}`...\n_Esto puede tardar 1-2 min_", parse_mode="Markdown")
        net_svc: NetworkService = context.bot_data['network_service']

        try:
            ports = await net_svc.scan_device_ports(ip)
            lines = [f"📡 *Scan de puertos: {ip}*\n"]

            if ports:
                for port, service in ports[:20]:
                    lines.append(f"🔓 `{port}/tcp` - {service}")
                if len(ports) > 20:
                    lines.append(f"_...y {len(ports) - 20} más_")
            else:
                lines.append("🔒 No se encontraron puertos abiertos")

            await msg.edit_text("\n".join(lines), parse_mode="Markdown", reply_markup=Keyboards.back_to_tools())
        except Exception as e:
            logger.error(f"Port scan error: {e}")
            await msg.edit_text(f"❌ Error escaneando puertos", reply_markup=Keyboards.back_to_tools())
        return

    # ─── PING ───
    if context.user_data.get('action') == 'ping':
        context.user_data.pop('action')
        host = text.strip()
        host = re.sub(r'^https?://', '', host)
        host = host.split('/')[0]

        if not is_valid_host(host):
            await update.message.reply_text(
                f"❌ *Host inválido*\n\n`{host}`",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_tools()
            )
            return

        msg = await update.message.reply_text(f"🏓 Ping a `{host}`...", parse_mode="Markdown")
        net_svc: NetworkService = context.bot_data['network_service']

        try:
            result = await net_svc.check_connectivity()
            # Hacer ping específico
            from utils.shell import run_async
            output = await run_async(f"ping -c 4 -W 2 {host}")

            if "0% packet loss" in output or "0.0% packet loss" in output:
                # Extraer RTT
                import re as re_mod
                rtt_match = re_mod.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)', output)
                if rtt_match:
                    min_rtt, avg_rtt, max_rtt = rtt_match.groups()
                    await msg.edit_text(
                        f"🏓 *Ping: {escape_md(host)}*\n\n"
                        f"✅ *Host alcanzable*\n"
                        f"⏱️ Min: `{min_rtt}ms`\n"
                        f"⏱️ Avg: `{avg_rtt}ms`\n"
                        f"⏱️ Max: `{max_rtt}ms`",
                        parse_mode="Markdown",
                        reply_markup=Keyboards.back_to_tools()
                    )
                else:
                    await msg.edit_text(f"✅ *{escape_md(host)}* alcanzable", parse_mode="Markdown", reply_markup=Keyboards.back_to_tools())
            elif "100% packet loss" in output:
                await msg.edit_text(
                    f"❌ *{escape_md(host)}* no responde\n\n_100% packet loss_",
                    parse_mode="Markdown",
                    reply_markup=Keyboards.back_to_tools()
                )
            else:
                # Parcial
                loss_match = re_mod.search(r'(\d+)% packet loss', output)
                loss = loss_match.group(1) if loss_match else "?"
                await msg.edit_text(
                    f"⚠️ *{escape_md(host)}* inestable\n\n_Packet loss: {loss}%_",
                    parse_mode="Markdown",
                    reply_markup=Keyboards.back_to_tools()
                )
        except Exception as e:
            logger.error(f"Ping error: {e}")
            await msg.edit_text(
                f"❌ *{escape_md(host)}* no alcanzable",
                parse_mode="Markdown",
                reply_markup=Keyboards.back_to_tools()
            )
        return

    # ─── DEVICE INFO (por MAC o nombre) ───
    if context.user_data.get('action') == 'device_info':
        context.user_data.pop('action')
        query = text.strip().lower()

        net_svc: NetworkService = context.bot_data['network_service']
        devices = await net_svc.scan_all(use_cache=True)

        found = None
        for dev in devices:
            if query in dev.mac.lower() or (dev.hostname and query in dev.hostname.lower()):
                found = dev
                break

        if not found:
            # Buscar en dispositivos guardados
            saved = device_svc.get_device(query.upper().replace('-', ':'))
            if saved:
                await update.message.reply_text(
                    f"📱 *{escape_md(saved.name)}*\n\n"
                    f"📍 MAC: `{saved.mac}`\n"
                    f"{'✅ Confiable' if saved.trusted else '⚠️ No confiable'}\n\n"
                    f"_Dispositivo no online actualmente_",
                    parse_mode="Markdown",
                    reply_markup=Keyboards.back_to_devices()
                )
            else:
                await update.message.reply_text(
                    "❌ Dispositivo no encontrado\n\n_Intenta con MAC completa o nombre exacto_",
                    reply_markup=Keyboards.back_to_devices()
                )
            return

        lines = [f"{found.icon} *{escape_md(found.display_name)}*\n"]
        lines.append(f"📍 IP: `{found.ip}`")
        lines.append(f"🔗 MAC: `{found.mac}`")
        if found.vendor:
            lines.append(f"🏭 Vendor: {escape_md(found.vendor)}")
        if found.hostname:
            lines.append(f"🖥️ Hostname: `{found.hostname}`")
        lines.append(f"📱 Tipo: {found.device_type}")

        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=Keyboards.device_actions(found.mac)
        )
        return

    # ─── MENSAJE NO ESPERADO ───
    # Ignorar o mostrar menú
    await update.message.reply_text(
        "💡 Usa /start para ver el menú principal",
        reply_markup=Keyboards.main_menu()
    )


def setup_message_handlers(app: Application):
    """Registra handlers de mensajes."""
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler
    ))
