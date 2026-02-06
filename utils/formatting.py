"""Formateo de mensajes para Telegram."""
import re
from datetime import timedelta
from typing import Optional


def escape_md(text: str) -> str:
    """
    Escapa caracteres especiales para Markdown V1 de Telegram.
    Solo escapa dentro del texto, no en código.
    """
    if not text:
        return ""
    # Caracteres que necesitan escape en Markdown
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    result = text
    for char in special_chars:
        result = result.replace(char, f'\\{char}')
    return result


def escape_md_v2(text: str) -> str:
    """Escapa para MarkdownV2 (más estricto)."""
    if not text:
        return ""
    special = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(special)}])', r'\\\1', text)


def format_mac(mac: str) -> str:
    """Formatea MAC address de forma consistente."""
    if not mac:
        return "00:00:00:00:00:00"
    # Normalizar: quitar separadores, uppercase, reformatear
    clean = mac.upper().replace(':', '').replace('-', '').replace('.', '')
    if len(clean) != 12:
        return mac.upper()
    return ':'.join(clean[i:i+2] for i in range(0, 12, 2))


def format_bytes(bytes_val: int) -> str:
    """Formatea bytes a unidad legible."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(bytes_val) < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"


def format_uptime(seconds: int) -> str:
    """Formatea segundos a formato legible."""
    if seconds < 0:
        return "N/A"

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or not parts:
        parts.append(f"{minutes}m")

    return " ".join(parts)


def format_percentage(value: float, decimals: int = 1) -> str:
    """Formatea porcentaje."""
    return f"{value:.{decimals}f}%"


def truncate(text: str, max_len: int = 20, suffix: str = "...") -> str:
    """Trunca texto si excede longitud máxima."""
    if not text or len(text) <= max_len:
        return text or ""
    return text[:max_len - len(suffix)] + suffix


def get_vendor_short(vendor: str) -> str:
    """Extrae nombre corto del fabricante."""
    if not vendor:
        return "Desconocido"

    # Mapeo de fabricantes conocidos
    known = {
        'apple': 'Apple',
        'samsung': 'Samsung',
        'huawei': 'Huawei',
        'xiaomi': 'Xiaomi',
        'google': 'Google',
        'amazon': 'Amazon',
        'intel': 'Intel',
        'realtek': 'Realtek',
        'tp-link': 'TP-Link',
        'asus': 'ASUS',
        'raspberry': 'Raspberry Pi',
        'espressif': 'ESP/IoT',
        'tuya': 'Tuya/Smart',
        'shenzhen': 'Generico CN',
        'hon hai': 'Foxconn',
        'liteon': 'LiteOn',
        'murata': 'Murata',
        'broadcom': 'Broadcom',
        'qualcomm': 'Qualcomm',
        'microsoft': 'Microsoft',
        'sony': 'Sony',
        'lg': 'LG',
        'dell': 'Dell',
        'hewlett': 'HP',
        'lenovo': 'Lenovo',
    }

    vendor_lower = vendor.lower()
    for key, name in known.items():
        if key in vendor_lower:
            return name

    # Si no se reconoce, devolver primeras 2 palabras
    words = vendor.split()[:2]
    return ' '.join(words) if words else "Desconocido"


def get_device_icon(vendor: str, hostname: str = "") -> str:
    """Devuelve emoji según tipo de dispositivo."""
    text = f"{vendor} {hostname}".lower()

    if any(x in text for x in ['iphone', 'ipad', 'apple', 'mac']):
        return "🍎"
    if any(x in text for x in ['samsung', 'galaxy', 'android']):
        return "📱"
    if any(x in text for x in ['tv', 'television', 'chromecast', 'roku', 'fire']):
        return "📺"
    if any(x in text for x in ['laptop', 'notebook', 'macbook']):
        return "💻"
    if any(x in text for x in ['desktop', 'pc', 'computer']):
        return "🖥️"
    if any(x in text for x in ['printer', 'print']):
        return "🖨️"
    if any(x in text for x in ['camera', 'cam', 'ring', 'nest']):
        return "📷"
    if any(x in text for x in ['echo', 'alexa', 'homepod', 'speaker']):
        return "🔊"
    if any(x in text for x in ['router', 'gateway', 'vodafone']):
        return "📡"
    if any(x in text for x in ['raspberry', 'pi']):
        return "🍓"
    if any(x in text for x in ['esp', 'tuya', 'smart', 'iot', 'sensor']):
        return "🏠"
    if any(x in text for x in ['playstation', 'xbox', 'nintendo', 'gaming']):
        return "🎮"

    return "📶"


def get_temp_icon(temp: float) -> str:
    """Devuelve emoji según temperatura."""
    if temp >= 80:
        return "🔥"
    if temp >= 70:
        return "🌡️"
    if temp >= 60:
        return "☀️"
    if temp >= 40:
        return "🌤️"
    return "❄️"
