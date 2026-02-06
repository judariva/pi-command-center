#!/usr/bin/env python3
"""
🏠 Pi Command Center - Security Edition
Control total de red y seguridad desde Telegram
"""

import asyncio
import subprocess
import logging
import psutil
import requests
import json
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════
BOT_TOKEN = "REDACTED_BOT_TOKEN"
AUTHORIZED_USERS = [REDACTED_USER_ID]
PIHOLE_API = "http://localhost/api"
PIHOLE_PASSWORD = "REDACTED_PASSWORD"
KNOWN_DEVICES_FILE = "/home/judariva/pibot/known_devices.json"
ALERT_CHAT_ID = REDACTED_USER_ID

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# BASE DE DATOS DE DISPOSITIVOS
# ══════════════════════════════════════════════════════════════

def load_known_devices() -> dict:
    try:
        if os.path.exists(KNOWN_DEVICES_FILE):
            with open(KNOWN_DEVICES_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"devices": {}, "trusted": [], "blocked": []}

def save_known_devices(data: dict):
    with open(KNOWN_DEVICES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_device_name(mac: str, db: dict) -> str:
    return db["devices"].get(mac, {}).get("name", "Desconocido")

# ══════════════════════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════════════════════

async def run_cmd_async(cmd: str, timeout: int = 30) -> str:
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return stdout.decode().strip() or stderr.decode().strip()
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except:
            pass
        return "Timeout"
    except Exception as e:
        return f"Error: {e}"

def run_cmd(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"Error: {e}"

def is_authorized(user_id: int) -> bool:
    return user_id in AUTHORIZED_USERS

def get_country_flag(country_code: str) -> str:
    if not country_code or len(country_code) != 2:
        return "🌍"
    return ''.join(chr(ord(c) + 127397) for c in country_code.upper())

def get_public_ip_info() -> dict:
    try:
        r = requests.get("http://ip-api.com/json/?fields=status,country,countryCode,city,isp,query", timeout=5)
        return r.json()
    except:
        return {"status": "fail", "query": "N/A"}

def get_pihole_stats() -> dict:
    try:
        auth_r = requests.post(f"{PIHOLE_API}/auth", json={"password": PIHOLE_PASSWORD}, timeout=5)
        if auth_r.status_code != 200:
            return {"error": "Auth failed"}
        sid = auth_r.json().get("session", {}).get("sid", "")
        headers = {"sid": sid}
        stats_r = requests.get(f"{PIHOLE_API}/stats/summary", headers=headers, timeout=5)
        stats = stats_r.json() if stats_r.status_code == 200 else {}
        top_r = requests.get(f"{PIHOLE_API}/stats/top_domains?blocked=true&count=5", headers=headers, timeout=5)
        top_blocked = top_r.json() if top_r.status_code == 200 else {}
        clients_r = requests.get(f"{PIHOLE_API}/stats/top_clients?count=5", headers=headers, timeout=5)
        top_clients = clients_r.json() if clients_r.status_code == 200 else {}
        return {"stats": stats, "top_blocked": top_blocked, "top_clients": top_clients, "sid": sid}
    except Exception as e:
        return {"error": str(e)}

def get_system_stats() -> dict:
    try:
        temp = "N/A"
        try:
            temp_raw = run_cmd("cat /sys/class/thermal/thermal_zone0/temp")
            temp = f"{int(temp_raw) / 1000:.1f}°C"
        except:
            pass
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        uptime_seconds = int(float(run_cmd("cat /proc/uptime").split()[0]))
        uptime = str(timedelta(seconds=uptime_seconds))
        containers = run_cmd("docker ps --format '{{.Names}}: {{.Status}}' 2>/dev/null")
        return {
            "temp": temp,
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "mem_used": mem.used // (1024**2),
            "mem_total": mem.total // (1024**2),
            "mem_percent": mem.percent,
            "disk_used": disk.used // (1024**3),
            "disk_total": disk.total // (1024**3),
            "disk_percent": disk.percent,
            "uptime": uptime,
            "containers": containers
        }
    except Exception as e:
        return {"error": str(e)}

# ══════════════════════════════════════════════════════════════
# FUNCIONES DE SEGURIDAD
# ══════════════════════════════════════════════════════════════

def scan_network() -> list:
    """Escanea la red y devuelve dispositivos encontrados"""
    try:
        output = run_cmd("sudo arp-scan -l 2>/dev/null | grep -E '^[0-9]'")
        devices = []
        for line in output.split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    devices.append({
                        "ip": parts[0],
                        "mac": parts[1].upper(),
                        "vendor": parts[2] if len(parts) > 2 else "Desconocido"
                    })
        return devices
    except:
        return []

def get_dhcp_devices() -> list:
    """Obtiene dispositivos del DHCP de Pi-hole"""
    try:
        leases = run_cmd("docker exec pihole cat /etc/pihole/dhcp.leases 2>/dev/null")
        devices = []
        for line in leases.strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 4:
                    devices.append({
                        "mac": parts[1].upper(),
                        "ip": parts[2],
                        "hostname": parts[3] if parts[3] != "*" else "Desconocido"
                    })
        return devices
    except:
        return []

def check_internet() -> dict:
    """Verifica conectividad a internet"""
    targets = [
        ("Google DNS", "8.8.8.8"),
        ("Cloudflare", "1.1.1.1"),
        ("Google", "google.com")
    ]
    results = {}
    for name, target in targets:
        ping = run_cmd(f"ping -c 1 -W 2 {target} 2>/dev/null | grep 'time=' | sed 's/.*time=//'")
        results[name] = ping if ping and "ms" in ping else "❌ Sin respuesta"
    return results

# ══════════════════════════════════════════════════════════════
# MENÚS
# ══════════════════════════════════════════════════════════════

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ Seguridad", callback_data="menu_security"),
         InlineKeyboardButton("📊 Pi-hole", callback_data="menu_pihole")],
        [InlineKeyboardButton("🖥️ Sistema", callback_data="menu_system"),
         InlineKeyboardButton("📱 Dispositivos", callback_data="menu_devices")],
        [InlineKeyboardButton("🔄 Refrescar", callback_data="refresh_main")]
    ])

def security_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Escanear Red", callback_data="security_scan")],
        [InlineKeyboardButton("📡 Test Internet", callback_data="security_internet")],
        [InlineKeyboardButton("🆕 Nuevos Dispositivos", callback_data="security_new")],
        [InlineKeyboardButton("🖥️ Wake-on-LAN", callback_data="security_wol")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="menu_main")]
    ])

def pihole_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Estadísticas", callback_data="pihole_stats")],
        [InlineKeyboardButton("🚫 Top Bloqueados", callback_data="pihole_blocked"),
         InlineKeyboardButton("👥 Top Clientes", callback_data="pihole_clients")],
        [InlineKeyboardButton("⏸️ Pausar 5min", callback_data="pihole_pause"),
         InlineKeyboardButton("▶️ Activar", callback_data="pihole_enable")],
        [InlineKeyboardButton("🚫 Bloquear dominio", callback_data="pihole_block_prompt")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="menu_main")]
    ])

def system_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Estado Completo", callback_data="system_full")],
        [InlineKeyboardButton("🐳 Docker", callback_data="system_docker")],
        [InlineKeyboardButton("🔄 Reiniciar Pi-hole", callback_data="system_restart_pihole")],
        [InlineKeyboardButton("📈 Speedtest", callback_data="system_speedtest")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="menu_main")]
    ])

def devices_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Ver Conectados", callback_data="devices_list")],
        [InlineKeyboardButton("✅ Dispositivos Confiables", callback_data="devices_trusted")],
        [InlineKeyboardButton("🏷️ Nombrar Dispositivo", callback_data="devices_name_prompt")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="menu_main")]
    ])

# ══════════════════════════════════════════════════════════════
# HANDLERS
# ══════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔ No autorizado")
        return

    ip_info = get_public_ip_info()
    flag = get_country_flag(ip_info.get("countryCode", ""))
    ph = get_pihole_stats()
    blocked_today = ph.get("stats", {}).get("queries", {}).get("blocked", 0) if "stats" in ph else "N/A"

    # Contar dispositivos
    devices = get_dhcp_devices()

    text = f"""
🏠 *Pi Command Center*
_Security Edition_

{flag} *IP:* `{ip_info.get('query', 'N/A')}`
🛡️ *Bloqueados hoy:* {blocked_today:,}
📱 *Dispositivos:* {len(devices)}

_Selecciona una opción:_
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_authorized(query.from_user.id):
        await query.edit_message_text("⛔ No autorizado")
        return

    data = query.data

    # ─── NAVEGACIÓN ───
    if data == "menu_main" or data == "refresh_main":
        ip_info = get_public_ip_info()
        flag = get_country_flag(ip_info.get("countryCode", ""))
        ph = get_pihole_stats()
        blocked_today = ph.get("stats", {}).get("queries", {}).get("blocked", 0) if "stats" in ph else "N/A"
        devices = get_dhcp_devices()

        text = f"""
🏠 *Pi Command Center*
_Security Edition_

{flag} *IP:* `{ip_info.get('query', 'N/A')}`
🛡️ *Bloqueados hoy:* {blocked_today:,}
📱 *Dispositivos:* {len(devices)}

_Selecciona una opción:_
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

    elif data == "menu_security":
        text = "🛡️ *Panel de Seguridad*\n\n_Monitorea y protege tu red_"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=security_menu_keyboard())

    elif data == "menu_pihole":
        await query.edit_message_text("📊 *Panel Pi-hole*\n\n_Control de bloqueo de anuncios_",
                                      parse_mode="Markdown", reply_markup=pihole_menu_keyboard())

    elif data == "menu_system":
        await query.edit_message_text("🖥️ *Panel Sistema*\n\n_Estado de la Raspberry Pi_",
                                      parse_mode="Markdown", reply_markup=system_menu_keyboard())

    elif data == "menu_devices":
        await query.edit_message_text("📱 *Gestión de Dispositivos*\n\n_Controla quién se conecta_",
                                      parse_mode="Markdown", reply_markup=devices_menu_keyboard())

    # ─── SEGURIDAD ───
    elif data == "security_scan":
        await query.edit_message_text("🔍 *Escaneando red...*\n\n_Esto puede tardar 10-20 segundos_", parse_mode="Markdown")
        devices = scan_network()
        db = load_known_devices()

        if devices:
            text = "🔍 *Dispositivos en la Red*\n\n"
            for d in devices[:15]:  # Limitar a 15
                mac = d['mac']
                name = get_device_name(mac, db)
                trusted = "✅" if mac in db.get("trusted", []) else "❓"
                text += f"{trusted} `{d['ip']}` - {name}\n"
            text += f"\n_Total: {len(devices)} dispositivos_"
        else:
            text = "🔍 *Escaneo completado*\n\n_No se encontraron dispositivos_"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=security_menu_keyboard())

    elif data == "security_internet":
        await query.edit_message_text("📡 *Verificando conexión...*", parse_mode="Markdown")
        results = check_internet()

        text = "📡 *Test de Conectividad*\n\n"
        for name, result in results.items():
            emoji = "✅" if "ms" in result else "❌"
            text += f"{emoji} *{name}:* {result}\n"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=security_menu_keyboard())

    elif data == "security_new":
        devices = scan_network()
        db = load_known_devices()

        new_devices = [d for d in devices if d['mac'] not in db.get("trusted", [])]

        if new_devices:
            text = "🆕 *Dispositivos NO confiables*\n\n"
            for d in new_devices[:10]:
                name = get_device_name(d['mac'], db)
                text += f"❓ `{d['ip']}` - {d['mac']}\n   _{d.get('vendor', 'Desconocido')}_\n\n"
            text += f"_Total: {len(new_devices)} dispositivos sin verificar_\n\n"
            text += "_Usa 'Nombrar Dispositivo' para identificarlos_"
        else:
            text = "✅ *Todos los dispositivos son confiables*\n\n_No hay dispositivos desconocidos_"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=security_menu_keyboard())

    elif data == "security_wol":
        db = load_known_devices()
        trusted = db.get("trusted", [])
        devices_info = db.get("devices", {})

        # Mostrar dispositivos confiables con nombre
        buttons = []
        for mac in trusted[:6]:  # Máx 6 para WoL
            name = devices_info.get(mac, {}).get("name", mac[:8])
            buttons.append([InlineKeyboardButton(f"💻 {name}", callback_data=f"wol_{mac}")])

        buttons.append([InlineKeyboardButton("⬅️ Volver", callback_data="menu_security")])

        if trusted:
            text = "🖥️ *Wake-on-LAN*\n\n_Selecciona un dispositivo para encender:_"
        else:
            text = "🖥️ *Wake-on-LAN*\n\n_No hay dispositivos confiables configurados_\n\nPrimero añade dispositivos desde 'Nombrar Dispositivo'"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("wol_"):
        mac = data[4:]
        await query.edit_message_text(f"📤 *Enviando Wake-on-LAN...*\n\nMAC: `{mac}`", parse_mode="Markdown")
        result = await run_cmd_async(f"wakeonlan {mac}")
        await query.edit_message_text(f"✅ *Magic packet enviado*\n\nMAC: `{mac}`\n\n_El dispositivo debería encenderse en unos segundos_",
                                      parse_mode="Markdown", reply_markup=security_menu_keyboard())

    # ─── DISPOSITIVOS ───
    elif data == "devices_list":
        devices = get_dhcp_devices()
        db = load_known_devices()

        if devices:
            text = "📱 *Dispositivos Conectados*\n\n"
            for d in devices:
                name = get_device_name(d['mac'], db) or d['hostname']
                trusted = "✅" if d['mac'] in db.get("trusted", []) else "❓"
                text += f"{trusted} `{d['ip']}` - {name}\n"
            text += f"\n_Total: {len(devices)} dispositivos_"
        else:
            text = "📱 *Dispositivos Conectados*\n\n_No hay dispositivos_"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=devices_menu_keyboard())

    elif data == "devices_trusted":
        db = load_known_devices()
        trusted = db.get("trusted", [])
        devices_info = db.get("devices", {})

        if trusted:
            text = "✅ *Dispositivos Confiables*\n\n"
            for mac in trusted:
                name = devices_info.get(mac, {}).get("name", "Sin nombre")
                text += f"• {name}\n  `{mac}`\n"
        else:
            text = "✅ *Dispositivos Confiables*\n\n_No hay dispositivos marcados como confiables_\n\nUsa 'Nombrar Dispositivo' para añadir"

        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=devices_menu_keyboard())

    elif data == "devices_name_prompt":
        devices = scan_network()

        buttons = []
        for d in devices[:8]:
            short_mac = d['mac'][-8:]
            buttons.append([InlineKeyboardButton(f"📱 {d['ip']} ({short_mac})", callback_data=f"name_{d['mac']}")])
        buttons.append([InlineKeyboardButton("⬅️ Volver", callback_data="menu_devices")])

        text = "🏷️ *Nombrar Dispositivo*\n\n_Selecciona el dispositivo a nombrar:_"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("name_"):
        mac = data[5:]
        context.user_data['naming_device'] = mac
        await query.edit_message_text(
            f"🏷️ *Nombrar Dispositivo*\n\nMAC: `{mac}`\n\n_Escribe el nombre para este dispositivo:_\n\n(Ej: 'TV Salón', 'PC Gaming', 'iPhone María')",
            parse_mode="Markdown"
        )

    # ─── PIHOLE ───
    elif data == "pihole_stats":
        ph = get_pihole_stats()
        if "error" in ph:
            text = f"❌ Error: {ph['error']}"
        else:
            stats = ph.get("stats", {}).get("queries", {})
            total = stats.get("total", 0)
            blocked = stats.get("blocked", 0)
            percent = (blocked / total * 100) if total > 0 else 0
            text = f"""
📊 *Estadísticas Pi-hole*

📈 *Consultas Hoy:* {total:,}
🚫 *Bloqueadas:* {blocked:,} ({percent:.1f}%)
✅ *Permitidas:* {total - blocked:,}

📋 *Dominios en listas:* {ph.get('stats', {}).get('gravity', {}).get('domains_being_blocked', 'N/A'):,}
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=pihole_menu_keyboard())

    elif data == "pihole_blocked":
        ph = get_pihole_stats()
        if "error" in ph:
            text = f"❌ Error: {ph['error']}"
        else:
            top = ph.get("top_blocked", {}).get("domains", [])
            if top:
                text = "🚫 *Top Dominios Bloqueados*\n\n"
                for i, d in enumerate(top[:5], 1):
                    text += f"{i}. `{d.get('domain', 'N/A')}` ({d.get('count', 0)})\n"
            else:
                text = "🚫 *Top Dominios Bloqueados*\n\n_Sin datos_"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=pihole_menu_keyboard())

    elif data == "pihole_clients":
        ph = get_pihole_stats()
        if "error" in ph:
            text = f"❌ Error: {ph['error']}"
        else:
            clients = ph.get("top_clients", {}).get("clients", [])
            if clients:
                text = "👥 *Top Clientes*\n\n"
                for i, c in enumerate(clients[:5], 1):
                    name = c.get('name', '') or c.get('ip', 'N/A')
                    text += f"{i}. `{name}` ({c.get('count', 0)})\n"
            else:
                text = "👥 *Top Clientes*\n\n_Sin datos_"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=pihole_menu_keyboard())

    elif data == "pihole_pause":
        await run_cmd_async("docker exec pihole pihole disable 300")
        await query.edit_message_text("⏸️ *Pi-hole pausado por 5 minutos*\n\n_Los anuncios se mostrarán temporalmente_",
                                      parse_mode="Markdown", reply_markup=pihole_menu_keyboard())

    elif data == "pihole_enable":
        await run_cmd_async("docker exec pihole pihole enable")
        await query.edit_message_text("▶️ *Pi-hole activado*\n\n_Bloqueo de anuncios activo_",
                                      parse_mode="Markdown", reply_markup=pihole_menu_keyboard())

    elif data == "pihole_block_prompt":
        context.user_data['blocking_domain'] = True
        await query.edit_message_text(
            "🚫 *Bloquear Dominio*\n\n_Escribe el dominio a bloquear:_\n\n(Ej: `tiktok.com`, `facebook.com`)",
            parse_mode="Markdown"
        )

    # ─── SISTEMA ───
    elif data == "system_full":
        sys_stats = get_system_stats()
        if "error" in sys_stats:
            text = f"❌ Error: {sys_stats['error']}"
        else:
            temp_val = float(sys_stats['temp'].replace('°C', '')) if '°C' in sys_stats['temp'] else 0
            temp_emoji = "🔥" if temp_val > 70 else "🌡️" if temp_val > 50 else "❄️"
            text = f"""
🖥️ *Estado del Sistema*

{temp_emoji} *Temperatura:* {sys_stats['temp']}
💻 *CPU:* {sys_stats['cpu_percent']}%
💾 *RAM:* {sys_stats['mem_used']}MB / {sys_stats['mem_total']}MB ({sys_stats['mem_percent']}%)
💿 *Disco:* {sys_stats['disk_used']}GB / {sys_stats['disk_total']}GB ({sys_stats['disk_percent']}%)
⏱️ *Uptime:* {sys_stats['uptime']}
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=system_menu_keyboard())

    elif data == "system_docker":
        sys_stats = get_system_stats()
        containers = sys_stats.get('containers', 'No hay contenedores')
        text = f"🐳 *Contenedores Docker*\n\n```\n{containers}\n```"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=system_menu_keyboard())

    elif data == "system_restart_pihole":
        await query.edit_message_text("🔄 *Reiniciando Pi-hole...*", parse_mode="Markdown")
        await run_cmd_async("docker restart pihole", timeout=60)
        await asyncio.sleep(5)
        await query.edit_message_text("✅ *Pi-hole reiniciado*",
                                      parse_mode="Markdown", reply_markup=system_menu_keyboard())

    elif data == "system_speedtest":
        await query.edit_message_text("📈 *Ejecutando speedtest...*\n\n_30-60 segundos_", parse_mode="Markdown")
        result = await run_cmd_async("speedtest-cli --simple 2>/dev/null || echo 'No disponible'", timeout=90)
        await query.edit_message_text(f"📈 *Speedtest*\n\n```\n{result}\n```",
                                      parse_mode="Markdown", reply_markup=system_menu_keyboard())

# ══════════════════════════════════════════════════════════════
# HANDLER DE MENSAJES DE TEXTO
# ══════════════════════════════════════════════════════════════

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    text = update.message.text.strip()

    # Nombrar dispositivo
    if context.user_data.get('naming_device'):
        mac = context.user_data.pop('naming_device')
        db = load_known_devices()

        if mac not in db["devices"]:
            db["devices"][mac] = {}
        db["devices"][mac]["name"] = text

        if mac not in db["trusted"]:
            db["trusted"].append(mac)

        save_known_devices(db)

        await update.message.reply_text(
            f"✅ *Dispositivo guardado*\n\n🏷️ *Nombre:* {text}\n📱 *MAC:* `{mac}`\n✅ *Marcado como confiable*",
            parse_mode="Markdown",
            reply_markup=devices_menu_keyboard()
        )
        return

    # Bloquear dominio
    if context.user_data.get('blocking_domain'):
        context.user_data.pop('blocking_domain')
        domain = text.lower().strip()

        # Añadir a blacklist de Pi-hole
        result = await run_cmd_async(f"docker exec pihole pihole blacklist {domain}")

        await update.message.reply_text(
            f"🚫 *Dominio bloqueado*\n\n`{domain}`\n\n_Añadido a la lista negra de Pi-hole_",
            parse_mode="Markdown",
            reply_markup=pihole_menu_keyboard()
        )
        return

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    text = """
🏠 *Pi Command Center - Ayuda*

*Comandos:*
/start - Menú principal
/scan - Escaneo rápido de red
/help - Esta ayuda

*Funciones:*
🛡️ Seguridad - Escanear red, detectar intrusos
📊 Pi-hole - Bloqueo de anuncios
🖥️ Sistema - Estado de la Pi
📱 Dispositivos - Gestión de red
"""
    await update.message.reply_text(text, parse_mode="Markdown")

async def quick_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    msg = await update.message.reply_text("🔍 *Escaneando red...*", parse_mode="Markdown")
    devices = scan_network()
    db = load_known_devices()

    new_devices = [d for d in devices if d['mac'] not in db.get("trusted", [])]

    text = f"🔍 *Escaneo Rápido*\n\n"
    text += f"📱 Total: {len(devices)}\n"
    text += f"✅ Confiables: {len(devices) - len(new_devices)}\n"
    text += f"❓ Desconocidos: {len(new_devices)}\n"

    if new_devices:
        text += "\n*Dispositivos nuevos:*\n"
        for d in new_devices[:5]:
            text += f"• `{d['ip']}` - {d.get('vendor', 'N/A')[:20]}\n"

    await msg.edit_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

# ══════════════════════════════════════════════════════════════
# MONITOREO EN BACKGROUND
# ══════════════════════════════════════════════════════════════

async def monitor_network(app):
    """Monitorea la red cada 5 minutos y alerta de dispositivos nuevos"""
    await asyncio.sleep(30)  # Esperar 30s al inicio

    while True:
        try:
            devices = scan_network()
            db = load_known_devices()

            for device in devices:
                mac = device['mac']
                if mac not in db.get("devices", {}) and mac not in db.get("alerted", []):
                    # Nuevo dispositivo detectado!
                    if "alerted" not in db:
                        db["alerted"] = []
                    db["alerted"].append(mac)
                    save_known_devices(db)

                    alert_text = f"""
🚨 *NUEVO DISPOSITIVO DETECTADO*

📍 *IP:* `{device['ip']}`
📱 *MAC:* `{device['mac']}`
�icing *Fabricante:* {device.get('vendor', 'Desconocido')}
⏰ *Hora:* {datetime.now().strftime('%H:%M:%S')}

_Revisa si es un dispositivo autorizado_
"""
                    try:
                        await app.bot.send_message(chat_id=ALERT_CHAT_ID, text=alert_text, parse_mode="Markdown")
                    except Exception as e:
                        logger.error(f"Error enviando alerta: {e}")

            # Verificar temperatura
            try:
                temp_raw = run_cmd("cat /sys/class/thermal/thermal_zone0/temp")
                temp = int(temp_raw) / 1000
                if temp > 75:
                    await app.bot.send_message(
                        chat_id=ALERT_CHAT_ID,
                        text=f"🔥 *ALERTA: Temperatura Alta*\n\nLa Pi está a *{temp:.1f}°C*\n\n_Verifica la ventilación_",
                        parse_mode="Markdown"
                    )
            except:
                pass

        except Exception as e:
            logger.error(f"Error en monitor: {e}")

        await asyncio.sleep(300)  # Cada 5 minutos

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print("🚀 Iniciando Pi Command Center - Security Edition...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("scan", quick_scan))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Iniciar monitor de red en background
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_network(app))

    print("✅ Bot listo!")
    print("🛡️ Monitor de seguridad activo")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
