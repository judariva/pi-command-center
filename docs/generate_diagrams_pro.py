#!/usr/bin/env python3
"""
Generador de diagramas profesionales para Pi Command Center.
Usa la librería 'diagrams' de mingrammer para diagramas de arquitectura cloud-grade.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users, Client
from diagrams.onprem.compute import Server
from diagrams.onprem.container import Docker
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.security import Vault
from diagrams.generic.network import Router, Firewall, Switch
from diagrams.generic.device import Mobile, Tablet
from diagrams.generic.os import Raspbian
from diagrams.programming.language import Python
from diagrams.saas.chat import Telegram
from diagrams.aws.compute import EC2
from diagrams.custom import Custom
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/diagrams'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Graph attributes for professional look
graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "spline",
    "nodesep": "0.8",
    "ranksep": "1.0",
}

node_attr = {
    "fontsize": "12",
}

edge_attr = {
    "fontsize": "10",
}


def create_network_architecture():
    """Diagrama de arquitectura de red completo."""
    with Diagram(
        "Pi Command Center - Network Architecture",
        filename=f"{OUTPUT_DIR}/network_architecture",
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        # Internet
        internet = Internet("Internet")

        with Cluster("Cloud Services"):
            vpn_server = EC2("VPN Server\n(AWS/DO)")
            telegram = Telegram("Telegram API")

        with Cluster("Home Network - 192.168.0.0/24"):
            router = Router("ISP Router\n192.168.0.1")

            with Cluster("Raspberry Pi 3B+ (PI_IP_REDACTED)"):
                with Cluster("DNS Stack"):
                    pihole = Docker("Pi-hole\nDNS/DHCP")
                    unbound = Docker("Unbound\nRecursive DNS")

                with Cluster("Security"):
                    firewall = Firewall("UFW")
                    fail2ban = Server("Fail2ban")

                with Cluster("VPN"):
                    wireguard = Vault("WireGuard")

                bot = Python("Telegram Bot")

            with Cluster("LAN Devices"):
                devices = [
                    Mobile("Phones"),
                    Tablet("Tablets"),
                    Client("PCs"),
                ]

        # Connections
        internet >> Edge(color="red", style="bold") >> router
        router >> Edge(color="darkgreen") >> pihole
        pihole >> Edge(label="port 5335") >> unbound
        unbound >> Edge(color="blue", style="dashed", label="Root DNS") >> internet

        # VPN tunnel
        wireguard >> Edge(color="purple", style="bold", label="WireGuard Tunnel") >> vpn_server
        vpn_server >> internet

        # Bot
        bot >> Edge(color="deepskyblue", label="Bot API") >> telegram

        # Devices
        for device in devices:
            device >> Edge(label="DNS/DHCP") >> pihole

        # Security
        internet >> Edge(color="red", style="dashed") >> firewall
        firewall >> fail2ban


def create_vpn_split_routing():
    """Diagrama del flujo de VPN Split Routing."""
    with Diagram(
        "VPN Split Routing - Traffic Flow",
        filename=f"{OUTPUT_DIR}/vpn_split_routing",
        outformat="png",
        show=False,
        direction="LR",
        graph_attr={**graph_attr, "rankdir": "LR"},
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        client = Mobile("Client Device")

        with Cluster("Pi-hole DNS"):
            dns = Docker("Pi-hole")
            ipset = Redis("ipset\n(vpn-domains)")

        with Cluster("Routing Decision"):
            iptables = Firewall("iptables\nmangle")

        with Cluster("Destinations"):
            with Cluster("VPN Path (USA)"):
                wg = Vault("WireGuard")
                vpn_out = Internet("VPN Exit\n🇺🇸")

            with Cluster("Direct Path (Spain)"):
                direct = Router("ISP")
                direct_out = Internet("Direct Exit\n🇪🇸")

        # Flow
        client >> Edge(label="DNS Query") >> dns
        dns >> Edge(label="Resolve + ipset") >> ipset
        ipset >> Edge(label="Check membership") >> iptables

        iptables >> Edge(color="purple", style="bold", label="fwmark=51\n(matched)") >> wg
        wg >> vpn_out

        iptables >> Edge(color="green", label="no mark\n(not matched)") >> direct
        direct >> direct_out


def create_security_layers():
    """Diagrama de capas de seguridad."""
    with Diagram(
        "Defense in Depth - Security Layers",
        filename=f"{OUTPUT_DIR}/security_layers",
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        attacker = Users("Attacker")

        with Cluster("Layer 1: Network"):
            ufw = Firewall("UFW Firewall\nPorts: 22, 53, 67, 80")

        with Cluster("Layer 2: Application"):
            fail2ban = Server("Fail2ban\n3 attempts = 1h ban")

        with Cluster("Layer 3: Authentication"):
            ssh = Vault("SSH Hardening\nEd25519 keys only")

        with Cluster("Layer 4: DNS"):
            pihole = Docker("Pi-hole\nMalware blocking")

        with Cluster("Layer 5: Encryption"):
            vpn = Vault("WireGuard VPN\nAll traffic encrypted")

        with Cluster("Protected Zone"):
            home = Client("Home Network")

        # Attack flow (blocked)
        attacker >> Edge(color="red", style="bold") >> ufw
        ufw >> Edge(color="orange", label="filtered") >> fail2ban
        fail2ban >> Edge(color="yellow", label="monitored") >> ssh
        ssh >> Edge(color="green", label="authenticated") >> pihole
        pihole >> Edge(color="blue", label="filtered DNS") >> vpn
        vpn >> Edge(color="darkgreen", style="bold") >> home


def create_bot_architecture():
    """Diagrama de arquitectura del bot."""
    with Diagram(
        "Telegram Bot - Software Architecture",
        filename=f"{OUTPUT_DIR}/bot_architecture",
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        user = Users("User")
        telegram = Telegram("Telegram")

        with Cluster("Bot Application"):
            with Cluster("Presentation Layer"):
                handlers = Python("Handlers\n(commands, callbacks)")
                keyboards = Python("Keyboards\n(inline menus)")

            with Cluster("Business Logic"):
                network_svc = Python("NetworkService")
                pihole_svc = Python("PiholeService")
                system_svc = Python("SystemService")
                device_svc = Python("DeviceService")

            with Cluster("Infrastructure"):
                shell = Python("Shell Utils")
                monitor = Python("Network Monitor")

        with Cluster("External Systems"):
            pihole = Docker("Pi-hole API")
            system = Raspbian("System APIs")
            vpn = Vault("VPN Manager")

        # Connections
        user >> telegram >> handlers
        handlers >> keyboards

        handlers >> network_svc
        handlers >> pihole_svc
        handlers >> system_svc
        handlers >> device_svc

        network_svc >> shell
        pihole_svc >> pihole
        system_svc >> system
        network_svc >> vpn

        monitor >> handlers


def create_data_flow():
    """Diagrama de flujo de datos DNS."""
    with Diagram(
        "DNS Query Flow - Privacy Stack",
        filename=f"{OUTPUT_DIR}/dns_flow",
        outformat="png",
        show=False,
        direction="LR",
        graph_attr={**graph_attr, "rankdir": "LR"},
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        client = Mobile("Client")

        with Cluster("Pi-hole (PI_IP_REDACTED:53)"):
            pihole = Docker("Pi-hole")
            blocklist = Redis("Blocklists\n1M+ domains")

        with Cluster("Decision"):
            check = Server("Ad/Tracker?")

        with Cluster("Unbound (127.0.0.1:5335)"):
            unbound = Docker("Unbound")
            cache = Redis("DNS Cache")

        root = Internet("Root DNS\nServers")

        blocked = Server("0.0.0.0\n(Blocked)")

        # Flow
        client >> Edge(label="1. DNS Query") >> pihole
        pihole >> Edge(label="2. Check blocklist") >> blocklist
        blocklist >> check

        check >> Edge(color="red", label="3a. Blocked") >> blocked
        check >> Edge(color="green", label="3b. Allowed") >> unbound

        unbound >> Edge(label="4. Check cache") >> cache
        cache >> Edge(color="blue", style="dashed", label="5. Recursive\n(if not cached)") >> root


if __name__ == '__main__':
    print("Generando diagramas profesionales...")
    print("=" * 50)

    create_network_architecture()
    print("✓ Network Architecture")

    create_vpn_split_routing()
    print("✓ VPN Split Routing")

    create_security_layers()
    print("✓ Security Layers")

    create_bot_architecture()
    print("✓ Bot Architecture")

    create_data_flow()
    print("✓ DNS Data Flow")

    print("=" * 50)
    print(f"✓ Diagramas guardados en {OUTPUT_DIR}/")
