<div align="center">

<img src="docs/diagrams/logo.png" alt="Pi Command Center" width="120"/>

# Pi Command Center

Transform your Raspberry Pi into a privacy-first home network control center

<img src="docs/diagrams/hero_banner.png" alt="Hero" width="100%"/>

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](docker-compose.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](requirements.txt)
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)](#changelog)

[Installation](#installation) · [Features](#features) · [Architecture](#architecture) · [Documentation](#documentation) · [Getting Help](#getting-help)

</div>

---

## Overview

Pi Command Center provides complete control over your home network's DNS, security, and privacy. Deploy with one command on any Raspberry Pi.

| Capability | Implementation |
|------------|----------------|
| DNS Resolution | Unbound recursive resolver (no third-party DNS) |
| Ad Blocking | Pi-hole with 1M+ blocked domains |
| VPN Routing | WireGuard with domain-based split tunneling |
| Remote Control | Telegram bot interface |
| Security | UFW firewall + Fail2ban intrusion detection |

---

## Privacy & Security

**Your data stays yours.** Pi Command Center is designed with privacy as the core principle:

- **No third-party DNS**: All DNS queries resolve recursively through Unbound directly to root servers. Google, Cloudflare, and other DNS providers never see your queries.
- **Local control**: Everything runs on your hardware. No cloud dependencies, no external services.
- **Encrypted remote access**: Telegram bot uses end-to-end encryption. No ports exposed to the internet.
- **Defense in depth**: Multiple security layers protect your network (firewall → intrusion detection → key-based SSH).

---

## Installation

### Quick Start

```bash
curl -sSL https://raw.githubusercontent.com/judariva/pi-command-center/main/install.sh | bash
```

### Manual Installation

```bash
git clone https://github.com/judariva/pi-command-center.git
cd pi-command-center
cp .env.example .env
# Configure your settings in .env
docker compose up -d
```

### Requirements

- Raspberry Pi 3B+ or newer (ARM64)
- Docker and Docker Compose
- Telegram bot token from [@BotFather](https://t.me/BotFather)

### Getting Your Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Choose a name (e.g., "My Pi Bot") and username (must end in `bot`)
4. Copy the token provided (looks like `123456789:ABCdefGHI...`)
5. Add the token to your `.env` file

### Getting Your Telegram User ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Send any message
3. Copy your numeric ID (e.g., `123456789`)
4. Add it to `AUTHORIZED_USERS` in your `.env` file

---

## Features

### Private DNS

All DNS queries are resolved recursively through Unbound. Your browsing data never touches Google, Cloudflare, or any third-party DNS provider.

### Network-Wide Ad Blocking

Pi-hole blocks ads and trackers for every device on your network. No client-side configuration required.

### Smart VPN Routing

<div align="center">
<img src="docs/diagrams/vpn_routing.png" alt="VPN Split Routing" width="700"/>
</div>

Route specific domains through VPN while keeping local traffic fast:

```
netflix.com     → VPN (geo-unlock)
reddit.com      → VPN (privacy)
google.com      → Direct (speed)
local services  → Direct (no latency)
```

### Security Monitoring

<div align="center">
<img src="docs/diagrams/security_shield.png" alt="Security Layers" width="300"/>
</div>

- Automatic IP banning after failed SSH attempts
- Real-time intrusion alerts via Telegram
- Key-only SSH authentication

---

## Architecture

<div align="center">
<img src="docs/diagrams/architecture_hero.png" alt="Architecture" width="700"/>
</div>

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    RASPBERRY PI                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Pi-hole   │→ │   Unbound   │→ │  Root Servers   │ │
│  │  DNS/DHCP   │  │  Recursive  │  │                 │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  WireGuard  │  │   Fail2ban  │  │       UFW       │ │
│  │     VPN     │  │     IDS     │  │    Firewall     │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐│
│  │              Telegram Bot (pibot)                   ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Docker Stack

| Service | Port | Purpose |
|---------|------|---------|
| `unbound` | 5335 | Recursive DNS resolver |
| `pihole` | 53, 80 | DNS server + ad blocking + DHCP |
| `pibot` | - | Telegram control interface |

---

## Configuration

All settings are managed through environment variables:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_token_here
AUTHORIZED_USERS=123456789

# Optional
NETWORK_RANGE=192.168.1.0/24
PIHOLE_PASSWORD=your_password
TZ=UTC
```

See [.env.example](.env.example) for all available options.

---

## Documentation

### Core Documentation

| Document | Description |
|----------|-------------|
| [Technical Specification](docs/TECHNICAL_SPEC.md) | Complete system architecture |
| [Pi-hole Setup](docs/PIHOLE_SETUP.md) | DNS, DHCP, and ad-blocking configuration |
| [VPN Setup](docs/VPN_SETUP.md) | WireGuard split routing |
| [Security Architecture](docs/SECURITY.md) | Defense in depth, threat model, hardening |

### Project Planning

| Document | Description |
|----------|-------------|
| [Roadmap](ROADMAP.md) | Feature roadmap v1.0 → v2.0 |
| [Contributing](CONTRIBUTING.md) | Contribution guidelines |

### Architecture Diagrams (Python/Graphviz)

| Diagram | Description |
|---------|-------------|
| [Defense in Depth](docs/diagrams/defense_in_depth.png) | 5-layer security architecture |
| [Network Flow](docs/diagrams/network_flow.png) | Traffic flow through system |
| [DNS Architecture](docs/diagrams/dns_architecture.png) | Privacy-first DNS resolution chain |
| [Threat Model](docs/diagrams/threat_model.png) | Attack vectors and mitigations |
| [System Components](docs/diagrams/system_components.png) | Service interaction diagram |

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu |
| `/status` | System status |
| `/devices` | Network scan |
| `/vpn` | VPN control |

---

## Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| Bot not responding | Check `TELEGRAM_BOT_TOKEN` in `.env` |
| DNS not working | Run `docker logs unbound` |
| Ads still showing | Run `docker exec pihole pihole -g` |
| VPN not connecting | Verify WireGuard keys and endpoint |
| Container won't start | Check `docker compose logs <service>` |

For detailed troubleshooting, see the [Technical Specification](docs/TECHNICAL_SPEC.md#troubleshooting).

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/judariva/pi-command-center/issues)
- **Discussions**: [GitHub Discussions](https://github.com/judariva/pi-command-center/discussions)
- **Documentation**: See the [docs/](docs/) folder

Before opening an issue, please:
1. Check existing issues for your problem
2. Include relevant logs (`docker compose logs`)
3. Describe your setup (Pi model, OS version)

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## Changelog

### v1.0.0
- Initial release
- Pi-hole + Unbound DNS stack
- Telegram bot with full menu system
- VPN split routing (WireGuard)
- Security monitoring (Fail2ban)

---

## License

MIT License. See [LICENSE](LICENSE) for details.
