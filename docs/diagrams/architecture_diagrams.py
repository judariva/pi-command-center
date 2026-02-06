#!/usr/bin/env python3
"""
Pi Command Center - Enterprise Architecture Diagrams
Generates professional technical diagrams using mingrammer/diagrams library.

Usage:
    python3 architecture_diagrams.py

Output:
    - defense_in_depth.png - Multi-layer security architecture
    - network_flow.png - Complete traffic flow diagram
    - threat_model.png - Threat landscape and mitigations
    - dns_architecture.png - DNS resolution chain
    - vpn_split_routing.png - VPN routing decision flow
    - system_components.png - Service interaction diagram
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.security import Vault
from diagrams.onprem.client import Users, Client
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.monitoring import Grafana
from diagrams.onprem.container import Docker
from diagrams.generic.network import Firewall, Router, Switch
from diagrams.generic.device import Mobile, Tablet
from diagrams.generic.os import Raspbian
from diagrams.generic.storage import Storage
from diagrams.programming.language import Python
from diagrams.saas.chat import Telegram
from diagrams.aws.network import VPC
from diagrams.custom import Custom
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Graph attributes for professional look
GRAPH_ATTR = {
    "fontsize": "16",
    "fontname": "Helvetica Neue",
    "bgcolor": "white",
    "pad": "0.5",
    "nodesep": "0.8",
    "ranksep": "1.0",
}

NODE_ATTR = {
    "fontsize": "12",
    "fontname": "Helvetica Neue",
}

EDGE_ATTR = {
    "fontsize": "10",
    "fontname": "Helvetica Neue",
}


def create_defense_in_depth():
    """
    Defense in Depth Architecture
    Shows all 5 security layers with specific controls at each layer.
    """
    with Diagram(
        "Defense in Depth Architecture",
        filename="defense_in_depth",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        internet = Internet("Internet\n(Untrusted)")

        with Cluster("Layer 1: Network Perimeter"):
            with Cluster("UFW Firewall"):
                fw = Firewall("iptables/nftables")
                fw_rules = Server("Rules:\n• Default DENY\n• Allow 22,53,67,80\n• LAN only")

        with Cluster("Layer 2: Intrusion Detection"):
            with Cluster("Fail2ban"):
                ids = Server("Log Monitor")
                jail = Storage("SSH Jail\n3 failures = 1hr ban")
                recidive = Storage("Recidive\nRepeat = 1 week")

        with Cluster("Layer 3: Authentication"):
            with Cluster("Multi-Factor"):
                ssh_auth = Vault("SSH Keys\nEd25519 only")
                tg_auth = Vault("Telegram\nUser ID whitelist")
                pihole_auth = Vault("Pi-hole\nPassword hash")

        with Cluster("Layer 4: Encryption"):
            with Cluster("Transport Security"):
                ssh_enc = Server("SSH\nChaCha20")
                wg_enc = Server("WireGuard\nChaCha20-Poly1305")
                tls = Server("TLS 1.3\nTelegram API")

        with Cluster("Layer 5: Application"):
            with Cluster("Raspberry Pi"):
                pihole = Docker("Pi-hole")
                unbound = Docker("Unbound")
                bot = Docker("Telegram Bot")

        # Flow with attack indicators
        internet >> Edge(color="red", style="bold", label="Attacks") >> fw
        fw >> Edge(color="orange", label="Filtered") >> ids
        ids >> Edge(color="yellow", label="Monitored") >> ssh_auth
        ssh_auth >> Edge(color="blue", label="Encrypted") >> ssh_enc
        ssh_enc >> Edge(color="green", label="Authorized") >> pihole


def create_network_flow():
    """
    Complete Network Traffic Flow
    Shows how different types of traffic flow through the system.
    """
    with Diagram(
        "Network Traffic Flow",
        filename="network_flow",
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        with Cluster("LAN Devices"):
            laptop = Client("Laptop")
            phone = Mobile("Phone")
            iot = Server("IoT")

        with Cluster("Raspberry Pi - Pi Command Center"):
            with Cluster("DNS Stack"):
                pihole = Docker("Pi-hole\n:53")
                unbound = Docker("Unbound\n:5335")

            with Cluster("VPN Stack"):
                ipset = Server("ipset\n(domain IPs)")
                mangle = Firewall("iptables\nmangle")
                wg = Server("WireGuard\nwg0")

            with Cluster("Security Stack"):
                ufw = Firewall("UFW")
                f2b = Server("Fail2ban")

            with Cluster("Control"):
                bot = Python("Telegram Bot")

        with Cluster("Internet"):
            internet_direct = Internet("Direct\n(ISP)")
            internet_vpn = Internet("VPN Exit\n(Encrypted)")
            telegram_api = Telegram("Telegram\nAPI")
            root_dns = Server("Root DNS\nServers")

        # DNS Flow (Blue)
        laptop >> Edge(color="blue", label="DNS query") >> pihole
        pihole >> Edge(color="blue", label="Recursive") >> unbound
        unbound >> Edge(color="blue", label="DNSSEC") >> root_dns

        # VPN Domain Flow (Purple)
        pihole >> Edge(color="purple", style="dashed", label="ipset hook") >> ipset
        ipset >> Edge(color="purple") >> mangle
        mangle >> Edge(color="purple", label="fwmark 0x1") >> wg
        wg >> Edge(color="purple", label="Encrypted tunnel") >> internet_vpn

        # Direct Flow (Green)
        laptop >> Edge(color="green", label="Non-VPN traffic") >> internet_direct

        # Bot Control Flow (Orange)
        bot >> Edge(color="orange") >> telegram_api


def create_dns_architecture():
    """
    DNS Resolution Architecture
    Detailed view of the DNS chain with privacy features.
    """
    with Diagram(
        "Privacy-First DNS Architecture",
        filename="dns_architecture",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        client = Client("LAN Client\n192.168.1.x")

        with Cluster("Pi-hole - DNS Server"):
            pihole_recv = Server("DNS Receiver\n:53 UDP/TCP")
            blocklist = Storage("Blocklists\n~1M domains")
            cache_ph = Storage("Query Cache")
            ftl = Server("FTL Engine\n(dnsmasq)")

            with Cluster("dnsmasq Extensions"):
                ipset_hook = Server("ipset Hook\nVPN domains")
                local_dns = Storage("Local DNS\ncustom.list")

        with Cluster("Unbound - Recursive Resolver"):
            unbound_recv = Server("Receiver\n:5335")
            cache_ub = Storage("Response Cache\n64MB")
            validator = Vault("DNSSEC\nValidator")
            qmin = Server("QNAME\nMinimization")

        with Cluster("Root DNS Infrastructure"):
            root = Server("Root Servers\n(a-m.root-servers.net)")
            tld = Server("TLD Servers\n(.com, .org, etc)")
            auth = Server("Authoritative\nServers")

        blocked = Server("Blocked Response\n0.0.0.0")

        # Query flow
        client >> Edge(label="1. Query") >> pihole_recv
        pihole_recv >> Edge(label="2. Check blocklist") >> blocklist
        blocklist >> Edge(color="red", style="dashed", label="Blocked") >> blocked
        blocklist >> Edge(label="3. Not blocked") >> ftl
        ftl >> Edge(label="4. Check cache") >> cache_ph
        ftl >> Edge(label="5. Forward") >> unbound_recv

        # Unbound resolution
        unbound_recv >> Edge(label="6. Check cache") >> cache_ub
        cache_ub >> Edge(label="7. Recursive") >> qmin
        qmin >> Edge(label="8. Query root") >> root
        root >> Edge(label="9. Referral") >> tld
        tld >> Edge(label="10. Referral") >> auth
        auth >> Edge(color="green", label="11. Response") >> validator
        validator >> Edge(label="12. Validated") >> client


def create_vpn_split_routing():
    """
    VPN Split Routing Decision Flow
    Shows how traffic routing decisions are made.
    """
    with Diagram(
        "VPN Split Routing Architecture",
        filename="vpn_split_routing",
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        with Cluster("Traffic Sources"):
            clients = Client("LAN Clients")

        with Cluster("Decision Engine"):
            with Cluster("Pi-hole DNS"):
                dns = Server("DNS Query")
                domains = Storage("vpn-domains.txt\nnetflix.com\nreddit.com")

            with Cluster("Linux Netfilter"):
                ipset = Storage("ipset 'vpn'\nhash:ip")
                mangle = Firewall("PREROUTING\nmangle table")
                mark = Server("MARK\n0x1")

            with Cluster("Policy Routing"):
                rules = Server("ip rule\nfwmark 0x1 → table 51820")
                table_vpn = Storage("Table 51820\ndefault via wg0")
                table_main = Storage("Table main\ndefault via eth0")

        with Cluster("Interfaces"):
            wg0 = Server("wg0\nWireGuard")
            eth0 = Router("eth0\nEthernet")

        with Cluster("Destinations"):
            vpn_exit = Internet("VPN Server\n(Encrypted)")
            isp = Internet("ISP Gateway\n(Direct)")

        # DNS triggers ipset
        clients >> dns
        dns >> Edge(label="Domain match?") >> domains
        domains >> Edge(color="purple", label="Add IP") >> ipset

        # Packet marking
        clients >> Edge(label="Packet") >> mangle
        mangle >> Edge(label="Check ipset") >> ipset
        ipset >> Edge(color="purple", label="Match") >> mark

        # Routing decision
        mark >> rules
        rules >> Edge(color="purple", label="Marked") >> table_vpn
        rules >> Edge(color="green", label="Unmarked") >> table_main

        table_vpn >> wg0 >> vpn_exit
        table_main >> eth0 >> isp


def create_threat_model():
    """
    Threat Model Overview
    Shows attack vectors and mitigations.
    """
    with Diagram(
        "Threat Model & Mitigations",
        filename="threat_model",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        with Cluster("Threat Actors", graph_attr={"bgcolor": "#ffebee"}):
            attacker = Users("External\nAttacker")
            bot_net = Server("Botnet\nScanner")
            insider = Users("Malicious\nInsider")

        with Cluster("Attack Vectors", graph_attr={"bgcolor": "#fff3e0"}):
            brute_force = Server("SSH\nBrute Force")
            dns_spoof = Server("DNS\nSpoofing")
            mitm = Server("Man-in-the\nMiddle")
            unauth = Server("Unauthorized\nBot Access")

        with Cluster("Mitigations", graph_attr={"bgcolor": "#e8f5e9"}):
            with Cluster("Network Controls"):
                fw = Firewall("UFW\nDefault Deny")
                f2b = Server("Fail2ban\nAuto-ban")

            with Cluster("Crypto Controls"):
                keys = Vault("SSH Keys\nNo Passwords")
                wg = Vault("WireGuard\nE2E Encryption")
                dnssec = Vault("DNSSEC\nValidation")

            with Cluster("Access Controls"):
                whitelist = Vault("User ID\nWhitelist")
                priv = Server("Least\nPrivilege")

        with Cluster("Protected Assets", graph_attr={"bgcolor": "#e3f2fd"}):
            dns_service = Docker("DNS Service")
            network = Router("Home Network")
            data = Storage("Query Logs")

        # Attack paths and mitigations
        attacker >> brute_force >> Edge(color="red", style="dashed") >> fw
        fw >> Edge(color="green", label="Blocked") >> f2b

        bot_net >> dns_spoof >> Edge(color="red", style="dashed") >> dnssec
        dnssec >> Edge(color="green", label="Validated") >> dns_service

        attacker >> mitm >> Edge(color="red", style="dashed") >> wg
        wg >> Edge(color="green", label="Encrypted") >> network

        insider >> unauth >> Edge(color="red", style="dashed") >> whitelist
        whitelist >> Edge(color="green", label="Denied") >> priv


def create_system_components():
    """
    System Component Interaction
    Shows all services and their communication.
    """
    with Diagram(
        "System Components & Interactions",
        filename="system_components",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        with Cluster("External"):
            internet = Internet("Internet")
            telegram = Telegram("Telegram API")
            vpn_server = Server("VPN Server")

        with Cluster("Raspberry Pi", graph_attr={"bgcolor": "#f5f5f5"}):
            with Cluster("Docker Network (172.20.0.0/24)"):
                with Cluster("DNS Services"):
                    pihole = Docker("Pi-hole\n172.20.0.3:53")
                    unbound = Docker("Unbound\n172.20.0.2:5335")

                with Cluster("Bot Service"):
                    bot = Python("pibot\nHost Network")

            with Cluster("Host Services"):
                wg = Server("WireGuard\nwg0 interface")
                ufw = Firewall("UFW\nFirewall")
                f2b = Server("Fail2ban\nIDS")
                systemd = Server("systemd\nService Manager")

            with Cluster("Storage"):
                pihole_db = Storage("/etc/pihole/\nConfig + FTL DB")
                bot_data = Storage("/home/*/pibot/data/\nDevice DB")
                logs = Storage("/var/log/\nSystem Logs")

        with Cluster("LAN"):
            router = Router("Router\n192.168.1.1")
            devices = Client("Clients\n192.168.1.x")

        # Service interactions
        devices >> Edge(label="DNS :53") >> pihole
        pihole >> Edge(label=":5335") >> unbound
        unbound >> Edge(label="Recursive") >> internet

        bot >> Edge(label="HTTPS") >> telegram
        bot >> Edge(label="API") >> pihole
        bot >> Edge(label="subprocess") >> wg
        bot >> Edge(label="subprocess") >> f2b

        wg >> Edge(label="UDP :51820") >> vpn_server

        devices >> Edge(label="Gateway") >> router >> internet


def main():
    """Generate all architecture diagrams."""
    print("=" * 60)
    print("  Pi Command Center - Architecture Diagram Generator")
    print("=" * 60)

    diagrams = [
        ("Defense in Depth", create_defense_in_depth),
        ("Network Flow", create_network_flow),
        ("DNS Architecture", create_dns_architecture),
        ("VPN Split Routing", create_vpn_split_routing),
        ("Threat Model", create_threat_model),
        ("System Components", create_system_components),
    ]

    for name, func in diagrams:
        print(f"\n🔧 Generating: {name}")
        try:
            func()
            print(f"   ✓ Complete")
        except Exception as e:
            print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("  ✓ All diagrams generated")
    print("=" * 60)


if __name__ == "__main__":
    main()
