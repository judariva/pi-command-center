"""Definición de teclados inline mejorados."""
from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Keyboards:
    """Clase con todos los teclados del bot."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Menú principal."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔍 Red", callback_data="menu:network"),
                InlineKeyboardButton("🛡 Pi-hole", callback_data="menu:pihole")
            ],
            [
                InlineKeyboardButton("🖥️ Sistema", callback_data="menu:system"),
                InlineKeyboardButton("📱 Dispositivos", callback_data="menu:devices")
            ],
            [
                InlineKeyboardButton("🔐 VPN", callback_data="menu:vpn"),
                InlineKeyboardButton("🔒 Seguridad", callback_data="menu:security")
            ],
            [
                InlineKeyboardButton("🔧 Herramientas", callback_data="menu:tools")
            ],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="action:refresh_main")
            ]
        ])

    @staticmethod
    def network_menu() -> InlineKeyboardMarkup:
        """Menú de red y seguridad."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Escaneo Rápido", callback_data="net:scan")],
            [InlineKeyboardButton("🔬 Escaneo Profundo (nmap)", callback_data="net:deep_scan")],
            [InlineKeyboardButton("📡 Test Conexión", callback_data="net:connectivity")],
            [InlineKeyboardButton("📊 Estadísticas Red", callback_data="net:stats")],
            [InlineKeyboardButton("🆕 Nuevos (24h)", callback_data="net:new_devices")],
            [InlineKeyboardButton("⚡ Wake-on-LAN", callback_data="net:wol_menu")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu:main")]
        ])

    @staticmethod
    def tools_menu() -> InlineKeyboardMarkup:
        """Menú de herramientas de red."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 DNS Lookup", callback_data="tools:dns_prompt")],
            [InlineKeyboardButton("🛤️ Traceroute", callback_data="tools:trace_prompt")],
            [InlineKeyboardButton("🔌 Port Check", callback_data="tools:port_prompt")],
            [InlineKeyboardButton("📡 Scan Puertos IP", callback_data="tools:portscan_prompt")],
            [InlineKeyboardButton("🏓 Ping", callback_data="tools:ping_prompt")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu:main")]
        ])

    @staticmethod
    def pihole_menu() -> InlineKeyboardMarkup:
        """Menú de Pi-hole."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📈 Estadísticas", callback_data="pihole:stats")],
            [
                InlineKeyboardButton("🚫 Bloqueados", callback_data="pihole:top_blocked"),
                InlineKeyboardButton("✅ Permitidos", callback_data="pihole:top_permitted")
            ],
            [InlineKeyboardButton("👥 Top Clientes", callback_data="pihole:top_clients")],
            [
                InlineKeyboardButton("⏸️ Pausar 5m", callback_data="pihole:disable"),
                InlineKeyboardButton("▶️ Activar", callback_data="pihole:enable")
            ],
            [
                InlineKeyboardButton("🚫 Bloquear", callback_data="pihole:block_prompt"),
                InlineKeyboardButton("✅ Permitir", callback_data="pihole:allow_prompt")
            ],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu:main")]
        ])

    @staticmethod
    def system_menu() -> InlineKeyboardMarkup:
        """Menú del sistema."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Estado Completo", callback_data="sys:stats")],
            [InlineKeyboardButton("🐳 Contenedores", callback_data="sys:docker")],
            [InlineKeyboardButton("📈 Speedtest", callback_data="sys:speedtest")],
            [
                InlineKeyboardButton("🔄 Restart Pi-hole", callback_data="sys:restart_pihole"),
                InlineKeyboardButton("🔄 Restart Unbound", callback_data="sys:restart_unbound")
            ],
            [InlineKeyboardButton("📋 Logs Pi-hole", callback_data="sys:pihole_logs")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu:main")]
        ])

    @staticmethod
    def devices_menu() -> InlineKeyboardMarkup:
        """Menú de dispositivos."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Todos Online", callback_data="dev:list")],
            [InlineKeyboardButton("📴 Offline", callback_data="dev:offline")],
            [InlineKeyboardButton("✅ Confiables", callback_data="dev:trusted")],
            [InlineKeyboardButton("🏷️ Nombrar", callback_data="dev:name_prompt")],
            [InlineKeyboardButton("🔍 Info Dispositivo", callback_data="dev:info_prompt")],
            [InlineKeyboardButton("🗑️ Limpiar Alertas", callback_data="dev:clear_alerts")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu:main")]
        ])

    @staticmethod
    def vpn_menu() -> InlineKeyboardMarkup:
        """Menú de VPN Split Routing."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Estado", callback_data="vpn:status")],
            [
                InlineKeyboardButton("🔀 Modo Split", callback_data="vpn:split"),
                InlineKeyboardButton("🔒 Todo VPN", callback_data="vpn:all")
            ],
            [InlineKeyboardButton("➕ Añadir Dominio", callback_data="vpn:add_prompt")],
            [InlineKeyboardButton("📋 Ver Dominios", callback_data="vpn:list")],
            [InlineKeyboardButton("🌍 Mi IP", callback_data="vpn:myip")],
            [
                InlineKeyboardButton("🟢 Activar", callback_data="vpn:up"),
                InlineKeyboardButton("🔴 Apagar", callback_data="vpn:down")
            ],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu:main")]
        ])

    @staticmethod
    def security_menu() -> InlineKeyboardMarkup:
        """Menú de seguridad."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡️ Estado General", callback_data="sec:status")],
            [InlineKeyboardButton("🚫 IPs Baneadas", callback_data="sec:banned")],
            [InlineKeyboardButton("👁️ Intrusos Detectados", callback_data="sec:intruders")],
            [InlineKeyboardButton("📋 Logs SSH", callback_data="sec:ssh_logs")],
            [
                InlineKeyboardButton("🔓 Desbanear IP", callback_data="sec:unban_prompt"),
                InlineKeyboardButton("🔒 Banear IP", callback_data="sec:ban_prompt")
            ],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu:main")]
        ])

    @staticmethod
    def back_to_security() -> InlineKeyboardMarkup:
        return Keyboards.back_to("security")

    @staticmethod
    def family_menu() -> InlineKeyboardMarkup:
        """Menú simplificado para familia."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ¿Internet funciona?", callback_data="family:check")],
            [InlineKeyboardButton("🎬 Modo Películas", callback_data="family:movies")],
            [InlineKeyboardButton("📚 Modo Estudio", callback_data="family:study")],
            [InlineKeyboardButton("📱 ¿Quién está conectado?", callback_data="family:who")],
            [InlineKeyboardButton("🆘 Reportar problema", callback_data="family:help")]
        ])

    @staticmethod
    def back_to_vpn() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu:vpn")]
        ])

    @staticmethod
    def back_to(menu: str) -> InlineKeyboardMarkup:
        """Botón genérico de volver."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Volver", callback_data=f"menu:{menu}")]
        ])

    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        return Keyboards.back_to("main")

    @staticmethod
    def back_to_network() -> InlineKeyboardMarkup:
        return Keyboards.back_to("network")

    @staticmethod
    def back_to_pihole() -> InlineKeyboardMarkup:
        return Keyboards.back_to("pihole")

    @staticmethod
    def back_to_system() -> InlineKeyboardMarkup:
        return Keyboards.back_to("system")

    @staticmethod
    def back_to_devices() -> InlineKeyboardMarkup:
        return Keyboards.back_to("devices")

    @staticmethod
    def back_to_tools() -> InlineKeyboardMarkup:
        return Keyboards.back_to("tools")

    @staticmethod
    def device_selection(devices: list, prefix: str = "select") -> InlineKeyboardMarkup:
        """Teclado para seleccionar dispositivo."""
        buttons = []
        for mac, name, ip in devices[:8]:
            display = f"{name}" if name else ip
            buttons.append([
                InlineKeyboardButton(
                    f"📱 {display}",
                    callback_data=f"{prefix}:{mac}"
                )
            ])
        buttons.append([InlineKeyboardButton("⬅️ Cancelar", callback_data="menu:main")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def wol_devices(devices: list) -> InlineKeyboardMarkup:
        """Teclado para Wake-on-LAN."""
        buttons = []
        for mac, name in devices[:6]:
            buttons.append([
                InlineKeyboardButton(
                    f"💻 {name}",
                    callback_data=f"wol:send:{mac}"
                )
            ])
        if not devices:
            buttons.append([
                InlineKeyboardButton(
                    "⚠️ No hay dispositivos",
                    callback_data="menu:devices"
                )
            ])
        buttons.append([InlineKeyboardButton("⬅️ Volver", callback_data="menu:network")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def device_actions(mac: str) -> InlineKeyboardMarkup:
        """Acciones para un dispositivo específico."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔌 Scan Puertos", callback_data=f"dev:ports:{mac}")],
            [InlineKeyboardButton("⚡ Wake-on-LAN", callback_data=f"wol:send:{mac}")],
            [
                InlineKeyboardButton("✅ Confiar", callback_data=f"dev:trust:{mac}"),
                InlineKeyboardButton("❌ Desconfiar", callback_data=f"dev:untrust:{mac}")
            ],
            [InlineKeyboardButton("⬅️ Volver", callback_data="menu:devices")]
        ])

    @staticmethod
    def confirm_action(action: str, cancel: str = "menu:main") -> InlineKeyboardMarkup:
        """Teclado de confirmación."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm:{action}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=cancel)
            ]
        ])

    @staticmethod
    def quick_actions() -> InlineKeyboardMarkup:
        """Acciones rápidas desde dashboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔍", callback_data="net:scan"),
                InlineKeyboardButton("📊", callback_data="pihole:stats"),
                InlineKeyboardButton("🖥️", callback_data="sys:stats"),
                InlineKeyboardButton("🔄", callback_data="action:refresh_main")
            ]
        ])
