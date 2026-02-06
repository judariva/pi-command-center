#!/usr/bin/env python3
"""
Generador de diagramas de arquitectura para Pi Command Center.
Genera diagramas de red, arquitectura y flujos del sistema.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np
import os

# Configuración global
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/diagrams'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_network_diagram():
    """Genera el diagrama de red del hogar."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Diagrama de Red - Pi Command Center', fontsize=16, fontweight='bold', pad=20)

    # Colores
    colors = {
        'internet': '#E74C3C',
        'router': '#F39C12',
        'raspberry': '#27AE60',
        'devices': '#3498DB',
        'vpn': '#9B59B6',
        'docker': '#2980B9'
    }

    # Internet Cloud
    cloud = mpatches.FancyBboxPatch((5.5, 8.5), 3, 1.2, boxstyle="round,pad=0.1",
                                     facecolor=colors['internet'], edgecolor='black', linewidth=2)
    ax.add_patch(cloud)
    ax.text(7, 9.1, '☁️ INTERNET', ha='center', va='center', fontsize=12, fontweight='bold', color='white')

    # Router Vodafone
    router = mpatches.FancyBboxPatch((5.5, 6.2), 3, 1.2, boxstyle="round,pad=0.1",
                                      facecolor=colors['router'], edgecolor='black', linewidth=2)
    ax.add_patch(router)
    ax.text(7, 6.8, '📡 Router Vodafone', ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(7, 6.4, '192.168.0.1', ha='center', va='center', fontsize=9, style='italic')

    # Raspberry Pi (Centro)
    pi_box = mpatches.FancyBboxPatch((5, 3.5), 4, 2, boxstyle="round,pad=0.1",
                                      facecolor=colors['raspberry'], edgecolor='black', linewidth=3)
    ax.add_patch(pi_box)
    ax.text(7, 5.1, '🍓 Raspberry Pi 3B+', ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    ax.text(7, 4.7, 'PI_IP_REDACTED', ha='center', va='center', fontsize=10, color='white')
    ax.text(7, 4.3, 'Pi-hole + Unbound + VPN', ha='center', va='center', fontsize=9, color='white')
    ax.text(7, 3.9, 'Telegram Bot + Fail2ban', ha='center', va='center', fontsize=9, color='white')

    # VPN Server (AWS)
    vpn_box = mpatches.FancyBboxPatch((11, 6.2), 2.5, 1.2, boxstyle="round,pad=0.1",
                                       facecolor=colors['vpn'], edgecolor='black', linewidth=2)
    ax.add_patch(vpn_box)
    ax.text(12.25, 6.8, '🔐 VPN Server', ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    ax.text(12.25, 6.4, 'AWS (USA)', ha='center', va='center', fontsize=9, color='white')

    # Dispositivos
    devices = [
        ('📱 Móviles', 1, 4.5),
        ('💻 PCs', 1, 3.5),
        ('📺 Smart TV', 1, 2.5),
        ('🎮 Consolas', 1, 1.5),
    ]

    for name, x, y in devices:
        dev_box = mpatches.FancyBboxPatch((x-0.3, y-0.4), 2.2, 0.8, boxstyle="round,pad=0.05",
                                           facecolor=colors['devices'], edgecolor='black', linewidth=1)
        ax.add_patch(dev_box)
        ax.text(x+0.8, y, name, ha='center', va='center', fontsize=9, color='white')

    # Telegram Cloud
    tg_box = mpatches.FancyBboxPatch((11, 3.8), 2.5, 1, boxstyle="round,pad=0.1",
                                      facecolor='#0088CC', edgecolor='black', linewidth=2)
    ax.add_patch(tg_box)
    ax.text(12.25, 4.3, '✈️ Telegram', ha='center', va='center', fontsize=10, fontweight='bold', color='white')

    # Flechas de conexión
    arrow_style = "Simple,tail_width=0.5,head_width=4,head_length=8"

    # Internet -> Router
    ax.annotate('', xy=(7, 7.4), xytext=(7, 8.5),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))

    # Router -> Pi
    ax.annotate('', xy=(7, 5.5), xytext=(7, 6.2),
                arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    ax.text(7.3, 5.85, 'DHCP/DNS', fontsize=8, style='italic')

    # Devices -> Pi (DNS queries)
    ax.annotate('', xy=(5, 4), xytext=(3.2, 3.5),
                arrowprops=dict(arrowstyle='->', color=colors['devices'], lw=1.5, ls='--'))
    ax.text(3.8, 4, 'DNS', fontsize=8, color=colors['devices'])

    # Pi -> VPN (tunnel)
    ax.annotate('', xy=(11, 6.8), xytext=(9, 5),
                arrowprops=dict(arrowstyle='<->', color=colors['vpn'], lw=2))
    ax.text(10.3, 5.8, 'WireGuard', fontsize=8, color=colors['vpn'], fontweight='bold')

    # Pi -> Telegram
    ax.annotate('', xy=(11, 4.3), xytext=(9, 4.3),
                arrowprops=dict(arrowstyle='<->', color='#0088CC', lw=1.5))
    ax.text(10, 4.6, 'Bot API', fontsize=8, color='#0088CC')

    # Leyenda
    legend_elements = [
        mpatches.Patch(facecolor=colors['internet'], label='Internet'),
        mpatches.Patch(facecolor=colors['router'], label='Router ISP'),
        mpatches.Patch(facecolor=colors['raspberry'], label='Raspberry Pi'),
        mpatches.Patch(facecolor=colors['devices'], label='Dispositivos LAN'),
        mpatches.Patch(facecolor=colors['vpn'], label='VPN Server'),
        mpatches.Patch(facecolor='#0088CC', label='Telegram'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    # Info box
    info_text = """Red: 192.168.0.0/24
DHCP Range: 100-250
DNS: Pi-hole → Unbound
VPN: Split Routing"""
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.5, 8.5, info_text, fontsize=9, verticalalignment='top', bbox=props)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/network_diagram.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"✓ Diagrama de red guardado en {OUTPUT_DIR}/network_diagram.png")


def create_architecture_diagram():
    """Genera el diagrama de arquitectura del software."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Arquitectura del Sistema - Pi Command Center', fontsize=16, fontweight='bold', pad=20)

    colors = {
        'telegram': '#0088CC',
        'bot': '#27AE60',
        'handlers': '#3498DB',
        'services': '#E74C3C',
        'infra': '#9B59B6',
        'external': '#F39C12'
    }

    # === CAPA TELEGRAM ===
    tg_box = mpatches.FancyBboxPatch((0.5, 10), 13, 1.5, boxstyle="round,pad=0.1",
                                      facecolor=colors['telegram'], edgecolor='black', linewidth=2, alpha=0.3)
    ax.add_patch(tg_box)
    ax.text(7, 11.2, 'TELEGRAM API', ha='center', va='center', fontsize=12, fontweight='bold')

    # User
    ax.add_patch(Circle((2, 10.75), 0.4, facecolor='white', edgecolor='black', linewidth=2))
    ax.text(2, 10.75, '👤', ha='center', va='center', fontsize=14)
    ax.text(2, 10.1, 'Usuario', ha='center', fontsize=9)

    # Bot Token
    ax.add_patch(mpatches.FancyBboxPatch((5, 10.3), 4, 0.8, boxstyle="round,pad=0.05",
                                          facecolor='white', edgecolor='black'))
    ax.text(7, 10.7, '🤖 python-telegram-bot', ha='center', fontsize=10)

    # === CAPA BOT (main.py) ===
    bot_box = mpatches.FancyBboxPatch((0.5, 7.8), 13, 1.8, boxstyle="round,pad=0.1",
                                       facecolor=colors['bot'], edgecolor='black', linewidth=2, alpha=0.3)
    ax.add_patch(bot_box)
    ax.text(7, 9.3, 'BOT CORE', ha='center', va='center', fontsize=12, fontweight='bold', color='white')

    components = [('main.py', 2.5), ('config.py', 5.5), ('monitor.py', 8.5), ('keyboards/', 11.5)]
    for name, x in components:
        ax.add_patch(mpatches.FancyBboxPatch((x-1, 8), 2, 0.7, boxstyle="round,pad=0.03",
                                              facecolor='white', edgecolor='black'))
        ax.text(x, 8.35, name, ha='center', fontsize=9)

    # === CAPA HANDLERS ===
    handlers_box = mpatches.FancyBboxPatch((0.5, 5.5), 13, 1.8, boxstyle="round,pad=0.1",
                                            facecolor=colors['handlers'], edgecolor='black', linewidth=2, alpha=0.3)
    ax.add_patch(handlers_box)
    ax.text(7, 7, 'HANDLERS', ha='center', va='center', fontsize=12, fontweight='bold', color='white')

    handlers = [('commands.py', 2), ('callbacks.py', 5.5), ('messages.py', 9), ('menus.py', 12)]
    for name, x in handlers:
        ax.add_patch(mpatches.FancyBboxPatch((x-1.2, 5.7), 2.4, 0.8, boxstyle="round,pad=0.03",
                                              facecolor='white', edgecolor='black'))
        ax.text(x, 6.1, name, ha='center', fontsize=9)

    # === CAPA SERVICES ===
    services_box = mpatches.FancyBboxPatch((0.5, 3), 13, 2, boxstyle="round,pad=0.1",
                                            facecolor=colors['services'], edgecolor='black', linewidth=2, alpha=0.3)
    ax.add_patch(services_box)
    ax.text(7, 4.7, 'SERVICES', ha='center', va='center', fontsize=12, fontweight='bold', color='white')

    services = [
        ('NetworkService', 'network.py', 1.8),
        ('PiholeService', 'pihole.py', 5),
        ('SystemService', 'system.py', 8.2),
        ('DeviceService', 'devices.py', 11.5)
    ]
    for svc_name, file_name, x in services:
        ax.add_patch(mpatches.FancyBboxPatch((x-1.3, 3.2), 2.6, 1.2, boxstyle="round,pad=0.03",
                                              facecolor='white', edgecolor='black'))
        ax.text(x, 3.95, svc_name, ha='center', fontsize=9, fontweight='bold')
        ax.text(x, 3.5, file_name, ha='center', fontsize=8, style='italic')

    # === CAPA INFRAESTRUCTURA ===
    infra_box = mpatches.FancyBboxPatch((0.5, 0.5), 13, 2, boxstyle="round,pad=0.1",
                                         facecolor=colors['infra'], edgecolor='black', linewidth=2, alpha=0.3)
    ax.add_patch(infra_box)
    ax.text(7, 2.2, 'INFRASTRUCTURE', ha='center', va='center', fontsize=12, fontweight='bold', color='white')

    infra = [
        ('🛡️ Pi-hole', 'DNS/DHCP', 1.8),
        ('🔄 Unbound', 'Recursive DNS', 4.5),
        ('🔐 WireGuard', 'VPN Tunnel', 7.2),
        ('🚫 Fail2ban', 'IDS/IPS', 10),
        ('🔥 UFW', 'Firewall', 12.5)
    ]
    for name, desc, x in infra:
        ax.add_patch(mpatches.FancyBboxPatch((x-1.1, 0.7), 2.2, 1, boxstyle="round,pad=0.03",
                                              facecolor='white', edgecolor='black'))
        ax.text(x, 1.35, name, ha='center', fontsize=9)
        ax.text(x, 0.95, desc, ha='center', fontsize=7, style='italic')

    # Flechas entre capas
    for y_start, y_end in [(10, 9.3), (7.8, 7), (5.5, 4.7), (3, 2.2)]:
        ax.annotate('', xy=(7, y_end+0.3), xytext=(7, y_start),
                    arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/architecture_diagram.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"✓ Diagrama de arquitectura guardado en {OUTPUT_DIR}/architecture_diagram.png")


def create_vpn_flow_diagram():
    """Genera el diagrama de flujo del VPN Split Routing."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('VPN Split Routing - Flujo de Tráfico', fontsize=16, fontweight='bold', pad=20)

    colors = {
        'client': '#3498DB',
        'pihole': '#27AE60',
        'decision': '#F39C12',
        'vpn': '#9B59B6',
        'direct': '#E74C3C',
        'internet': '#2C3E50'
    }

    # Cliente
    ax.add_patch(mpatches.FancyBboxPatch((0.5, 4), 2, 1.5, boxstyle="round,pad=0.1",
                                          facecolor=colors['client'], edgecolor='black', linewidth=2))
    ax.text(1.5, 4.75, '📱 Cliente', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # Pi-hole DNS
    ax.add_patch(mpatches.FancyBboxPatch((3.5, 4), 2.5, 1.5, boxstyle="round,pad=0.1",
                                          facecolor=colors['pihole'], edgecolor='black', linewidth=2))
    ax.text(4.75, 5, '🛡️ Pi-hole', ha='center', fontsize=11, fontweight='bold', color='white')
    ax.text(4.75, 4.5, 'DNS Query', ha='center', fontsize=9, color='white')

    # Decision Diamond (ipset check)
    diamond_x, diamond_y = 7.5, 4.75
    diamond = plt.Polygon([[diamond_x, diamond_y+1], [diamond_x+1.2, diamond_y],
                           [diamond_x, diamond_y-1], [diamond_x-1.2, diamond_y]],
                          facecolor=colors['decision'], edgecolor='black', linewidth=2)
    ax.add_patch(diamond)
    ax.text(diamond_x, diamond_y, '¿En\nipset?', ha='center', va='center', fontsize=9, fontweight='bold')

    # VPN Path
    ax.add_patch(mpatches.FancyBboxPatch((9.5, 6.5), 2.5, 1.5, boxstyle="round,pad=0.1",
                                          facecolor=colors['vpn'], edgecolor='black', linewidth=2))
    ax.text(10.75, 7.5, '🔐 WireGuard', ha='center', fontsize=10, fontweight='bold', color='white')
    ax.text(10.75, 7, 'Túnel VPN', ha='center', fontsize=9, color='white')

    # Direct Path
    ax.add_patch(mpatches.FancyBboxPatch((9.5, 2), 2.5, 1.5, boxstyle="round,pad=0.1",
                                          facecolor=colors['direct'], edgecolor='black', linewidth=2))
    ax.text(10.75, 3, '⚡ Directo', ha='center', fontsize=10, fontweight='bold', color='white')
    ax.text(10.75, 2.5, 'Sin VPN', ha='center', fontsize=9, color='white')

    # Internet
    ax.add_patch(mpatches.FancyBboxPatch((12.5, 4), 1.3, 1.5, boxstyle="round,pad=0.1",
                                          facecolor=colors['internet'], edgecolor='black', linewidth=2))
    ax.text(13.15, 4.75, '🌐', ha='center', fontsize=20, color='white')

    # Arrows
    # Cliente -> Pi-hole
    ax.annotate('', xy=(3.5, 4.75), xytext=(2.5, 4.75),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))

    # Pi-hole -> Decision
    ax.annotate('', xy=(6.3, 4.75), xytext=(6, 4.75),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))

    # Decision -> VPN (SÍ)
    ax.annotate('', xy=(9.5, 7.25), xytext=(8.2, 5.5),
                arrowprops=dict(arrowstyle='->', color=colors['vpn'], lw=2))
    ax.text(8.5, 6.5, 'SÍ', fontsize=10, fontweight='bold', color=colors['vpn'])

    # Decision -> Direct (NO)
    ax.annotate('', xy=(9.5, 2.75), xytext=(8.2, 4),
                arrowprops=dict(arrowstyle='->', color=colors['direct'], lw=2))
    ax.text(8.5, 3.2, 'NO', fontsize=10, fontweight='bold', color=colors['direct'])

    # VPN -> Internet
    ax.annotate('', xy=(12.5, 5), xytext=(12, 7),
                arrowprops=dict(arrowstyle='->', color=colors['vpn'], lw=2))

    # Direct -> Internet
    ax.annotate('', xy=(12.5, 4.5), xytext=(12, 3),
                arrowprops=dict(arrowstyle='->', color=colors['direct'], lw=2))

    # Info boxes
    vpn_domains = """Dominios VPN (ipset):
• netflix.com
• hbomax.com
• reddit.com
• openai.com
• *.torrent sites"""
    props = dict(boxstyle='round', facecolor='#E8DAEF', alpha=0.9)
    ax.text(0.5, 8, vpn_domains, fontsize=9, verticalalignment='top', bbox=props)

    direct_info = """Tráfico Directo:
• Navegación normal
• Servicios locales
• Streaming España
• Gaming (baja latencia)"""
    props2 = dict(boxstyle='round', facecolor='#FADBD8', alpha=0.9)
    ax.text(0.5, 1.8, direct_info, fontsize=9, verticalalignment='top', bbox=props2)

    # Technical details
    tech_info = """Implementación:
iptables -t mangle + fwmark
ip rule + ip route table
ipset hash:ip + dnsmasq"""
    props3 = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
    ax.text(10, 0.8, tech_info, fontsize=8, verticalalignment='top', bbox=props3)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/vpn_flow_diagram.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"✓ Diagrama de VPN guardado en {OUTPUT_DIR}/vpn_flow_diagram.png")


def create_security_diagram():
    """Genera el diagrama de capas de seguridad."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Capas de Seguridad - Defense in Depth', fontsize=16, fontweight='bold', pad=20)

    # Capas concéntricas (de fuera hacia dentro)
    layers = [
        (6, 5, 5.5, '#E74C3C', 'INTERNET\n(Amenazas)', 0.2),
        (6, 5, 4.5, '#F39C12', 'UFW Firewall\nPuertos: 22, 53, 67, 80', 0.3),
        (6, 5, 3.5, '#9B59B6', 'Fail2ban\nIDS/IPS SSH', 0.4),
        (6, 5, 2.5, '#3498DB', 'SSH Hardening\nKey-only, No root', 0.5),
        (6, 5, 1.5, '#27AE60', 'Pi-hole\nDNS Filtering', 0.6),
        (6, 5, 0.8, '#2ECC71', '🏠 RED LOCAL\n192.168.0.0/24', 0.9),
    ]

    for x, y, radius, color, label, alpha in layers:
        circle = plt.Circle((x, y), radius, facecolor=color, edgecolor='black',
                            linewidth=2, alpha=alpha)
        ax.add_patch(circle)

    # Labels (positioned outside circles)
    ax.text(6, 9.2, '🌐 INTERNET', ha='center', fontsize=12, fontweight='bold')
    ax.text(11, 8, '🔥 UFW', ha='left', fontsize=10, fontweight='bold', color='#F39C12')
    ax.text(11, 7.3, 'Ports: 22,53,67,80', ha='left', fontsize=8)

    ax.text(11, 6.2, '🚫 Fail2ban', ha='left', fontsize=10, fontweight='bold', color='#9B59B6')
    ax.text(11, 5.5, 'Ban after 3 fails', ha='left', fontsize=8)

    ax.text(11, 4.4, '🔑 SSH', ha='left', fontsize=10, fontweight='bold', color='#3498DB')
    ax.text(11, 3.7, 'Ed25519 keys only', ha='left', fontsize=8)

    ax.text(11, 2.6, '🛡️ Pi-hole', ha='left', fontsize=10, fontweight='bold', color='#27AE60')
    ax.text(11, 1.9, 'Ad/Malware block', ha='left', fontsize=8)

    ax.text(6, 5, '🏠', ha='center', va='center', fontsize=30)

    # Attack arrows (blocked)
    attacks = [
        (1, 8, 4, 6.5, 'Brute Force SSH'),
        (1, 2, 4, 3.5, 'Port Scan'),
        (11, 8, 8, 6.5, 'Malware DNS'),
    ]

    for x1, y1, x2, y2, label in attacks:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2, ls='--'))
        ax.text(x1, y1+0.3, label, fontsize=8, color='red')
        ax.text(x2-0.3, y2, '❌', fontsize=14)

    # Legend
    legend_text = """Defensa en Profundidad:
1. UFW bloquea puertos no autorizados
2. Fail2ban detecta y banea ataques SSH
3. SSH solo acepta claves Ed25519
4. Pi-hole bloquea dominios maliciosos
5. VPN cifra tráfico sensible"""
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
    ax.text(0.3, 3.5, legend_text, fontsize=9, verticalalignment='top', bbox=props)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/security_layers.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"✓ Diagrama de seguridad guardado en {OUTPUT_DIR}/security_layers.png")


def create_bot_menu_diagram():
    """Genera el diagrama de estructura del menú del bot."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Estructura del Menú - Telegram Bot', fontsize=16, fontweight='bold', pad=20)

    # Main menu (center top)
    ax.add_patch(mpatches.FancyBboxPatch((5.5, 8.5), 3, 1, boxstyle="round,pad=0.1",
                                          facecolor='#2C3E50', edgecolor='black', linewidth=2))
    ax.text(7, 9, '🏠 MENÚ PRINCIPAL', ha='center', va='center', fontsize=11, fontweight='bold', color='white')

    # Submenus
    menus = [
        ('🔍 Red', '#3498DB', 1, 6, [
            'Escaneo Rápido',
            'Escaneo Profundo',
            'Test Conexión',
            'Wake-on-LAN'
        ]),
        ('🛡 Pi-hole', '#27AE60', 4, 6, [
            'Estadísticas',
            'Top Bloqueados',
            'Pausar/Activar',
            'Bloquear/Permitir'
        ]),
        ('🖥️ Sistema', '#E74C3C', 7, 6, [
            'Estado CPU/RAM',
            'Docker Status',
            'Speedtest',
            'Logs'
        ]),
        ('📱 Dispositivos', '#F39C12', 10, 6, [
            'Listar Online',
            'Offline',
            'Nombrar',
            'Trust/Untrust'
        ]),
        ('🔐 VPN', '#9B59B6', 2.5, 3, [
            'Estado',
            'Modo Split/All',
            'Añadir Dominio',
            'Ver Lista'
        ]),
        ('🔒 Seguridad', '#1ABC9C', 7, 3, [
            'Auditoría',
            'IPs Baneadas',
            'Intrusos',
            'Ban/Unban'
        ]),
        ('🔧 Herramientas', '#E67E22', 11.5, 3, [
            'DNS Lookup',
            'Traceroute',
            'Port Check',
            'Ping'
        ]),
    ]

    for name, color, x, y, items in menus:
        # Menu box
        height = 0.3 * len(items) + 0.8
        ax.add_patch(mpatches.FancyBboxPatch((x-1.2, y-height+0.5), 2.4, height,
                                              boxstyle="round,pad=0.05",
                                              facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.8))
        ax.text(x, y+0.2, name, ha='center', va='center', fontsize=10, fontweight='bold', color='white')

        # Items
        for i, item in enumerate(items):
            ax.text(x, y - 0.3 - (i * 0.3), f'• {item}', ha='center', fontsize=8, color='white')

        # Arrow from main menu
        ax.annotate('', xy=(x, y+0.5), xytext=(7, 8.5),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=1, connectionstyle='arc3,rad=0.1'))

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/bot_menu_structure.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"✓ Diagrama de menú guardado en {OUTPUT_DIR}/bot_menu_structure.png")


if __name__ == '__main__':
    print("Generando diagramas...")
    print("=" * 50)
    create_network_diagram()
    create_architecture_diagram()
    create_vpn_flow_diagram()
    create_security_diagram()
    create_bot_menu_diagram()
    print("=" * 50)
    print(f"✓ Todos los diagramas guardados en {OUTPUT_DIR}/")
