#!/usr/bin/env python3
"""
Generate high-quality architecture diagrams using Graphviz.
Creates professional SVG and PNG outputs.
"""

import subprocess
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "diagrams"
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# DIAGRAM 1: Network Architecture
# ============================================================================
NETWORK_DIAGRAM = """
digraph G {
    rankdir=TB;
    splines=ortho;
    nodesep=0.8;
    ranksep=1.0;
    bgcolor="white";

    node [
        fontname="Helvetica Neue,Helvetica,Arial,sans-serif"
        fontsize=11
        style="filled,rounded"
        shape=box
        penwidth=2
    ];

    edge [
        fontname="Helvetica Neue,Helvetica,Arial,sans-serif"
        fontsize=9
        penwidth=1.5
    ];

    // Title
    labelloc="t";
    label=<<B><FONT POINT-SIZE="20">Pi Command Center - Network Architecture</FONT></B>>;
    fontname="Helvetica Neue,Helvetica,Arial,sans-serif";

    // Internet
    subgraph cluster_internet {
        label="";
        style=invis;
        internet [
            label=<<B>☁️ INTERNET</B>>
            fillcolor="#e74c3c"
            fontcolor="white"
            shape=ellipse
            width=2
        ];
    }

    // Cloud Services
    subgraph cluster_cloud {
        label=<<B>Cloud Services</B>>;
        style="rounded,filled";
        fillcolor="#f8f9fa";
        color="#dee2e6";

        telegram [
            label=<<B>Telegram API</B><BR/><FONT POINT-SIZE="9">Bot Control</FONT>>
            fillcolor="#0088cc"
            fontcolor="white"
        ];

        vpn_server [
            label=<<B>VPN Server</B><BR/><FONT POINT-SIZE="9">AWS (USA) 🇺🇸</FONT>>
            fillcolor="#9b59b6"
            fontcolor="white"
        ];
    }

    // Router
    router [
        label=<<B>📡 ISP Router</B><BR/><FONT POINT-SIZE="9">192.168.0.1</FONT>>
        fillcolor="#f39c12"
        fontcolor="white"
    ];

    // Raspberry Pi
    subgraph cluster_pi {
        label=<<B>🍓 Raspberry Pi 3B+ (PI_IP_REDACTED)</B>>;
        style="rounded,filled";
        fillcolor="#fce4ec";
        color="#c51a4a";
        penwidth=3;

        subgraph cluster_dns {
            label=<<B>DNS Stack</B>>;
            style="rounded,filled";
            fillcolor="#e8f5e9";
            color="#27ae60";

            pihole [
                label=<<B>Pi-hole</B><BR/><FONT POINT-SIZE="9">DNS + DHCP + Blocking</FONT>>
                fillcolor="#96060c"
                fontcolor="white"
            ];

            unbound [
                label=<<B>Unbound</B><BR/><FONT POINT-SIZE="9">Recursive DNS :5335</FONT>>
                fillcolor="#27ae60"
                fontcolor="white"
            ];
        }

        subgraph cluster_security {
            label=<<B>Security</B>>;
            style="rounded,filled";
            fillcolor="#fff3e0";
            color="#e67e22";

            ufw [
                label=<<B>UFW</B><BR/><FONT POINT-SIZE="9">Firewall</FONT>>
                fillcolor="#e67e22"
                fontcolor="white"
                shape=hexagon
            ];

            fail2ban [
                label=<<B>Fail2ban</B><BR/><FONT POINT-SIZE="9">IDS/IPS</FONT>>
                fillcolor="#d35400"
                fontcolor="white"
                shape=hexagon
            ];
        }

        subgraph cluster_vpn {
            label=<<B>VPN Stack</B>>;
            style="rounded,filled";
            fillcolor="#f3e5f5";
            color="#9b59b6";

            wireguard [
                label=<<B>WireGuard</B><BR/><FONT POINT-SIZE="9">Split Routing</FONT>>
                fillcolor="#9b59b6"
                fontcolor="white"
                shape=diamond
            ];
        }

        pibot [
            label=<<B>🤖 Telegram Bot</B><BR/><FONT POINT-SIZE="9">Python Control Center</FONT>>
            fillcolor="#3498db"
            fontcolor="white"
        ];
    }

    // LAN Devices
    subgraph cluster_lan {
        label=<<B>LAN Devices (192.168.0.100-250)</B>>;
        style="rounded,filled";
        fillcolor="#e3f2fd";
        color="#3498db";

        devices [
            label=<<B>📱 Phones  💻 PCs  📺 TV  🎮 Console</B>>
            fillcolor="#3498db"
            fontcolor="white"
            shape=box3d
        ];
    }

    // Connections
    internet -> router [color="#e74c3c", penwidth=2];
    router -> pihole [label="DNS" color="#27ae60"];
    pihole -> unbound [label=":5335" color="#27ae60"];
    unbound -> internet [label="Root DNS" style=dashed color="#27ae60"];

    wireguard -> vpn_server [label="WireGuard" color="#9b59b6" penwidth=2 style=bold];
    vpn_server -> internet [color="#9b59b6"];

    pibot -> telegram [label="Bot API" color="#0088cc"];

    devices -> pihole [label="DHCP/DNS" color="#3498db" dir=both];

    internet -> ufw [label="Filtered" color="#e74c3c" style=dashed];
    ufw -> fail2ban [style=invis];
}
"""

# ============================================================================
# DIAGRAM 2: VPN Split Routing Flow
# ============================================================================
VPN_FLOW_DIAGRAM = """
digraph G {
    rankdir=LR;
    splines=polyline;
    nodesep=1.0;
    ranksep=1.2;
    bgcolor="white";

    node [
        fontname="Helvetica Neue,Helvetica,Arial,sans-serif"
        fontsize=11
        style="filled,rounded"
        shape=box
        penwidth=2
    ];

    edge [
        fontname="Helvetica Neue,Helvetica,Arial,sans-serif"
        fontsize=10
        penwidth=2
    ];

    labelloc="t";
    label=<<B><FONT POINT-SIZE="20">VPN Split Routing - Traffic Flow</FONT></B>>;

    // Client
    client [
        label=<<B>📱 Client</B><BR/><FONT POINT-SIZE="9">Device</FONT>>
        fillcolor="#3498db"
        fontcolor="white"
    ];

    // Pi-hole
    pihole [
        label=<<B>🛡️ Pi-hole</B><BR/><FONT POINT-SIZE="9">DNS Query</FONT>>
        fillcolor="#96060c"
        fontcolor="white"
    ];

    // Decision
    decision [
        label=<<B>Domain in<BR/>VPN list?</B>>
        shape=diamond
        fillcolor="#f39c12"
        fontcolor="white"
        width=1.5
        height=1.5
    ];

    // Paths
    subgraph cluster_vpn_path {
        label=<<B>VPN Path</B>>;
        style="rounded,filled";
        fillcolor="#f3e5f5";
        color="#9b59b6";

        iptables_vpn [
            label=<<B>iptables</B><BR/><FONT POINT-SIZE="9">fwmark=51</FONT>>
            fillcolor="#9b59b6"
            fontcolor="white"
            shape=hexagon
        ];

        wireguard [
            label=<<B>🔐 WireGuard</B><BR/><FONT POINT-SIZE="9">wg-us tunnel</FONT>>
            fillcolor="#8e44ad"
            fontcolor="white"
        ];

        vpn_exit [
            label=<<B>🇺🇸 USA Exit</B><BR/><FONT POINT-SIZE="9">VPN IP</FONT>>
            fillcolor="#9b59b6"
            fontcolor="white"
            shape=ellipse
        ];
    }

    subgraph cluster_direct_path {
        label=<<B>Direct Path</B>>;
        style="rounded,filled";
        fillcolor="#e8f5e9";
        color="#27ae60";

        iptables_direct [
            label=<<B>iptables</B><BR/><FONT POINT-SIZE="9">no mark</FONT>>
            fillcolor="#27ae60"
            fontcolor="white"
            shape=hexagon
        ];

        isp [
            label=<<B>⚡ ISP Router</B><BR/><FONT POINT-SIZE="9">Direct</FONT>>
            fillcolor="#2ecc71"
            fontcolor="white"
        ];

        direct_exit [
            label=<<B>🇪🇸 Spain Exit</B><BR/><FONT POINT-SIZE="9">Real IP</FONT>>
            fillcolor="#27ae60"
            fontcolor="white"
            shape=ellipse
        ];
    }

    // Internet
    internet [
        label=<<B>🌐 Internet</B>>
        fillcolor="#34495e"
        fontcolor="white"
        shape=ellipse
    ];

    // Connections
    client -> pihole [label="1. DNS Query"];
    pihole -> decision [label="2. Check ipset"];

    decision -> iptables_vpn [label="YES" color="#9b59b6" fontcolor="#9b59b6"];
    iptables_vpn -> wireguard [color="#9b59b6"];
    wireguard -> vpn_exit [color="#9b59b6"];
    vpn_exit -> internet [color="#9b59b6"];

    decision -> iptables_direct [label="NO" color="#27ae60" fontcolor="#27ae60"];
    iptables_direct -> isp [color="#27ae60"];
    isp -> direct_exit [color="#27ae60"];
    direct_exit -> internet [color="#27ae60"];
}
"""

# ============================================================================
# DIAGRAM 3: Security Layers
# ============================================================================
SECURITY_DIAGRAM = """
digraph G {
    rankdir=TB;
    splines=ortho;
    nodesep=0.5;
    ranksep=0.8;
    bgcolor="white";

    node [
        fontname="Helvetica Neue,Helvetica,Arial,sans-serif"
        fontsize=11
        style="filled,rounded"
        shape=box
        penwidth=2
        width=4
    ];

    edge [
        fontname="Helvetica Neue,Helvetica,Arial,sans-serif"
        fontsize=10
        penwidth=2
    ];

    labelloc="t";
    label=<<B><FONT POINT-SIZE="20">Defense in Depth - Security Layers</FONT></B>>;

    // Attacker
    attacker [
        label=<<B>☠️ ATTACKER</B>>
        fillcolor="#e74c3c"
        fontcolor="white"
        shape=ellipse
        width=2
    ];

    // Layer 1
    layer1 [
        label=<<B>Layer 1: UFW Firewall</B><BR/><BR/><FONT POINT-SIZE="9">Only ports 22, 53, 67, 80 open<BR/>Default deny all incoming</FONT>>
        fillcolor="#e67e22"
        fontcolor="white"
    ];

    // Layer 2
    layer2 [
        label=<<B>Layer 2: Fail2ban IDS</B><BR/><BR/><FONT POINT-SIZE="9">3 failed attempts = 1 hour ban<BR/>Automatic IP blocking</FONT>>
        fillcolor="#f39c12"
        fontcolor="white"
    ];

    // Layer 3
    layer3 [
        label=<<B>Layer 3: SSH Hardening</B><BR/><BR/><FONT POINT-SIZE="9">Ed25519 keys only, no passwords<BR/>Root login disabled</FONT>>
        fillcolor="#3498db"
        fontcolor="white"
    ];

    // Layer 4
    layer4 [
        label=<<B>Layer 4: Pi-hole DNS</B><BR/><BR/><FONT POINT-SIZE="9">Blocks malware domains<BR/>1M+ blocked domains</FONT>>
        fillcolor="#27ae60"
        fontcolor="white"
    ];

    // Layer 5
    layer5 [
        label=<<B>Layer 5: VPN Encryption</B><BR/><BR/><FONT POINT-SIZE="9">WireGuard tunnel<BR/>All sensitive traffic encrypted</FONT>>
        fillcolor="#9b59b6"
        fontcolor="white"
    ];

    // Protected
    protected [
        label=<<B>🏠 PROTECTED NETWORK</B>>
        fillcolor="#2ecc71"
        fontcolor="white"
        shape=ellipse
        width=3
    ];

    // Connections
    attacker -> layer1 [label="❌ Blocked" color="#e74c3c"];
    layer1 -> layer2 [label="❌ Banned" color="#e67e22"];
    layer2 -> layer3 [label="❌ Rejected" color="#f39c12"];
    layer3 -> layer4 [label="❌ Filtered" color="#3498db"];
    layer4 -> layer5 [label="🔒 Encrypted" color="#27ae60"];
    layer5 -> protected [label="✅ Safe" color="#2ecc71"];
}
"""

# ============================================================================
# DIAGRAM 4: Bot Architecture
# ============================================================================
BOT_DIAGRAM = """
digraph G {
    rankdir=TB;
    splines=ortho;
    nodesep=0.6;
    ranksep=0.8;
    bgcolor="white";
    compound=true;

    node [
        fontname="Helvetica Neue,Helvetica,Arial,sans-serif"
        fontsize=10
        style="filled,rounded"
        shape=box
        penwidth=1.5
    ];

    edge [
        fontname="Helvetica Neue,Helvetica,Arial,sans-serif"
        fontsize=9
        penwidth=1.5
    ];

    labelloc="t";
    label=<<B><FONT POINT-SIZE="18">Telegram Bot - Software Architecture</FONT></B>>;

    // User
    user [
        label=<<B>👤 User</B>>
        fillcolor="#34495e"
        fontcolor="white"
        shape=ellipse
    ];

    // Telegram
    telegram [
        label=<<B>Telegram</B>>
        fillcolor="#0088cc"
        fontcolor="white"
    ];

    // Bot Application
    subgraph cluster_bot {
        label=<<B>Bot Application</B>>;
        style="rounded,filled";
        fillcolor="#e8f4f8";
        color="#3498db";

        subgraph cluster_handlers {
            label="Handlers";
            style="rounded,filled";
            fillcolor="#d4edda";
            color="#27ae60";

            commands [label="commands.py" fillcolor="#27ae60" fontcolor="white"];
            callbacks [label="callbacks.py" fillcolor="#27ae60" fontcolor="white"];
            messages [label="messages.py" fillcolor="#27ae60" fontcolor="white"];
        }

        subgraph cluster_services {
            label="Services";
            style="rounded,filled";
            fillcolor="#fff3cd";
            color="#f39c12";

            network_svc [label="NetworkService" fillcolor="#f39c12" fontcolor="white"];
            pihole_svc [label="PiholeService" fillcolor="#f39c12" fontcolor="white"];
            system_svc [label="SystemService" fillcolor="#f39c12" fontcolor="white"];
            device_svc [label="DeviceService" fillcolor="#f39c12" fontcolor="white"];
        }

        keyboards [label="Keyboards" fillcolor="#3498db" fontcolor="white"];
        monitor [label="Network Monitor" fillcolor="#9b59b6" fontcolor="white"];
    }

    // External
    subgraph cluster_external {
        label=<<B>External Systems</B>>;
        style="rounded,filled";
        fillcolor="#f8f9fa";
        color="#6c757d";

        pihole_api [label="Pi-hole API" fillcolor="#96060c" fontcolor="white"];
        system_api [label="System APIs" fillcolor="#e74c3c" fontcolor="white"];
        vpn_mgr [label="VPN Manager" fillcolor="#9b59b6" fontcolor="white"];
        docker [label="Docker API" fillcolor="#2496ed" fontcolor="white"];
    }

    // Connections
    user -> telegram;
    telegram -> commands [lhead=cluster_handlers];

    callbacks -> keyboards;
    callbacks -> network_svc [lhead=cluster_services];

    network_svc -> vpn_mgr;
    pihole_svc -> pihole_api;
    system_svc -> system_api;
    system_svc -> docker;

    monitor -> network_svc [style=dashed];
}
"""

def render_diagram(name: str, dot_source: str):
    """Render a diagram to PNG and SVG using graphviz."""
    dot_file = OUTPUT_DIR / f"{name}.dot"
    png_file = OUTPUT_DIR / f"{name}.png"
    svg_file = OUTPUT_DIR / f"{name}.svg"

    # Write DOT file
    dot_file.write_text(dot_source)

    # Render PNG
    subprocess.run(
        ["dot", "-Tpng", "-Gdpi=150", str(dot_file), "-o", str(png_file)],
        check=True
    )

    # Render SVG
    subprocess.run(
        ["dot", "-Tsvg", str(dot_file), "-o", str(svg_file)],
        check=True
    )

    # Clean up DOT file
    dot_file.unlink()

    print(f"✓ {name}.png and {name}.svg generated")


def main():
    print("Generating high-quality diagrams...")
    print("=" * 50)

    render_diagram("network_hq", NETWORK_DIAGRAM)
    render_diagram("vpn_flow_hq", VPN_FLOW_DIAGRAM)
    render_diagram("security_hq", SECURITY_DIAGRAM)
    render_diagram("bot_architecture_hq", BOT_DIAGRAM)

    print("=" * 50)
    print(f"✓ All diagrams saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
