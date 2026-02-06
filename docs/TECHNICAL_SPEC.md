# Technical Specification

## Pi Command Center v1.0

### Document Information

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | Production Ready |
| Last Updated | 2024 |

---

## 1. System Overview

### 1.1 Purpose

Pi Command Center is a self-hosted home network management system that provides:

- **DNS Resolution**: Recursive DNS via Unbound (no third-party DNS providers)
- **Ad Blocking**: Network-wide blocking via Pi-hole (1M+ domains)
- **VPN Routing**: Selective domain-based split tunneling via WireGuard
- **Remote Control**: Telegram bot interface for network management
- **Security Monitoring**: Intrusion detection via Fail2ban

### 1.2 Design Principles

| Principle | Implementation |
|-----------|----------------|
| Privacy First | DNS queries never leave the network |
| Zero Trust | All external access requires authentication |
| Defense in Depth | Multiple security layers (UFW → Fail2ban → SSH keys) |
| Minimal Attack Surface | No exposed ports except DNS (LAN only) |
| Infrastructure as Code | Docker Compose + YAML configuration |

### 1.3 Target Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Device | Raspberry Pi 3B+ | Raspberry Pi 4/5 |
| RAM | 1 GB | 2+ GB |
| Storage | 8 GB SD | 32+ GB SD/SSD |
| Network | 100 Mbps | Gigabit Ethernet |

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           INTERNET                                   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              ┌─────▼─────┐          ┌──────▼──────┐
              │  Telegram │          │ VPN Server  │
              │    API    │          │  (Remote)   │
              └─────┬─────┘          └──────┬──────┘
                    │                       │
┌───────────────────┼───────────────────────┼─────────────────────────┐
│ RASPBERRY PI      │                       │                         │
│ ┌─────────────────┼───────────────────────┼───────────────────────┐ │
│ │ DOCKER          │                       │                       │ │
│ │                 │                       │                       │ │
│ │  ┌──────────────▼────────┐    ┌─────────▼─────────┐            │ │
│ │  │       pibot           │    │    WireGuard      │            │ │
│ │  │  (Telegram Bot)       │    │  (VPN Client)     │            │ │
│ │  │  - python-telegram-bot│    │  - Split Routing  │            │ │
│ │  │  - Host Network Mode  │    │  - fwmark + ipset │            │ │
│ │  └──────────┬────────────┘    └───────────────────┘            │ │
│ │             │                                                   │ │
│ │  ┌──────────▼────────────┐    ┌───────────────────┐            │ │
│ │  │      Pi-hole          │───▶│     Unbound       │            │ │
│ │  │  (DNS + DHCP + Block) │    │ (Recursive DNS)   │            │ │
│ │  │  - 172.20.0.3         │    │  - 172.20.0.2     │            │ │
│ │  │  - Port 53, 80        │    │  - Port 5335      │            │ │
│ │  └──────────┬────────────┘    └─────────┬─────────┘            │ │
│ │             │                           │                       │ │
│ └─────────────┼───────────────────────────┼───────────────────────┘ │
│               │                           │                         │
│  ┌────────────▼────────────┐    ┌─────────▼─────────┐              │
│  │         UFW             │    │   Root DNS        │              │
│  │  (Firewall Rules)       │    │   Servers         │              │
│  └────────────┬────────────┘    └───────────────────┘              │
│               │                                                     │
│  ┌────────────▼────────────┐                                       │
│  │      Fail2ban           │                                       │
│  │  (Intrusion Detection)  │                                       │
│  └─────────────────────────┘                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │     LAN DEVICES       │
                    │  (Phones, PCs, IoT)   │
                    └───────────────────────┘
```

### 2.2 Network Topology

| Network | CIDR | Purpose |
|---------|------|---------|
| LAN | 192.168.1.0/24 | Home network (configurable) |
| Docker DNS | 172.20.0.0/24 | Internal DNS network |
| WireGuard | 10.x.x.x/24 | VPN tunnel (varies) |

### 2.3 Port Mapping

| Port | Protocol | Service | Exposure |
|------|----------|---------|----------|
| 53 | TCP/UDP | Pi-hole DNS | LAN only |
| 67 | UDP | Pi-hole DHCP | LAN only |
| 80 | TCP | Pi-hole Admin | LAN only |
| 22 | TCP | SSH | LAN only |
| 5335 | TCP/UDP | Unbound | Internal only |

---

## 3. Component Specifications

### 3.1 Pi-hole

**Purpose**: DNS server, DHCP server, ad blocker

**Configuration**:
```yaml
Environment Variables:
  PIHOLE_DNS_: "172.20.0.2#5335"  # Upstream = Unbound
  DHCP_ACTIVE: true
  DHCP_START: 192.168.1.100
  DHCP_END: 192.168.1.250
  DHCP_ROUTER: 192.168.1.1
  DNSMASQ_LISTENING: all

Volumes:
  - pihole_config:/etc/pihole
  - pihole_dnsmasq:/etc/dnsmasq.d

Capabilities:
  - NET_ADMIN (required for DHCP)
```

**Blocklists**:
| List | Domains | Purpose |
|------|---------|---------|
| Default | ~300K | Ads, trackers |
| StevenBlack | ~130K | Unified hosts |
| Malware | ~50K | Known malware domains |

### 3.2 Unbound

**Purpose**: Recursive DNS resolver (privacy)

**Why Unbound?**
- Resolves directly with root servers
- No queries sent to Google (8.8.8.8) or Cloudflare (1.1.1.1)
- DNSSEC validation
- Query minimization (RFC 7816)

**Configuration Highlights**:
```yaml
server:
  interface: 0.0.0.0
  port: 5335
  do-ip4: yes
  do-udp: yes
  do-tcp: yes

  # Privacy
  hide-identity: yes
  hide-version: yes
  qname-minimisation: yes

  # Performance
  num-threads: 2
  msg-cache-size: 64m
  rrset-cache-size: 128m
  cache-min-ttl: 300
  cache-max-ttl: 86400
  prefetch: yes
```

### 3.3 Telegram Bot (pibot)

**Purpose**: Remote network management interface

**Technology Stack**:
| Component | Library/Tool |
|-----------|--------------|
| Framework | python-telegram-bot 20.x |
| Async | asyncio |
| HTTP Client | httpx |
| DNS | dnspython |
| Network Scan | scapy, nmap |

**Handler Architecture**:
```
┌─────────────────────────────────────────────┐
│              Telegram Update                │
└─────────────────────┬───────────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│            Authorization Check              │
│         (AUTHORIZED_USERS list)             │
└─────────────────────┬───────────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│              Update Router                  │
├─────────────┬─────────────┬─────────────────┤
│  Commands   │  Callbacks  │   Messages      │
│  /start     │  menu:*     │   IP input      │
│  /status    │  vpn:*      │   Domain input  │
│  /help      │  sec:*      │                 │
└─────────────┴─────────────┴─────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│           Service Layer                     │
├─────────────┬─────────────┬─────────────────┤
│  Pi-hole    │  System     │   Network       │
│  API        │  Commands   │   Scanner       │
└─────────────┴─────────────┴─────────────────┘
```

**Menu Structure**:
```
Main Menu
├── 🔍 Network
│   ├── Public IP
│   ├── Local IPs
│   ├── DNS Test
│   └── Speed Test
├── 🛡️ Pi-hole
│   ├── Status
│   ├── Enable/Disable
│   ├── Statistics
│   └── Top Blocked
├── 🖥️ System
│   ├── Status
│   ├── Temperature
│   ├── Memory
│   └── Reboot
├── 📱 Devices
│   ├── Scan Network
│   ├── Connected
│   └── Wake on LAN
├── 🔐 VPN
│   ├── Status
│   ├── Connect/Disconnect
│   ├── Mode (Split/Full)
│   └── Add Domain
├── 🔒 Security
│   ├── Status
│   ├── Banned IPs
│   ├── Intruders
│   ├── SSH Logs
│   └── Ban/Unban IP
└── 🔧 Tools
    ├── Ping
    ├── DNS Lookup
    ├── Traceroute
    └── Port Check
```

### 3.4 WireGuard VPN

**Purpose**: Encrypted tunnel with selective routing

**Split Routing Implementation**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      TRAFFIC FLOW                               │
└─────────────────────────────────────────────────────────────────┘

1. DNS Query arrives at Pi-hole
   └── Pi-hole resolves → gets IP(s)

2. dnsmasq ipset hook triggers
   └── If domain in vpn-domains.txt → IPs added to ipset "vpn"

3. Packet leaves client
   └── iptables mangle PREROUTING checks ipset
       ├── Match → fwmark 0x1 applied
       └── No match → default routing

4. Policy routing (ip rule)
   └── fwmark 0x1 → lookup table 51820 (WireGuard)
   └── default → main table (direct)

5. Packet routed
   ├── VPN table → wg0 interface → VPN server
   └── Main table → eth0 → router → internet
```

**iptables Rules**:
```bash
# Mark packets destined for VPN IPs
iptables -t mangle -A PREROUTING -m set --match-set vpn dst -j MARK --set-mark 0x1

# Exclude VPN endpoint from VPN routing (critical!)
iptables -t mangle -A PREROUTING -d <VPN_ENDPOINT_IP> -j RETURN

# Exclude Telegram IPs (bot must work without VPN)
iptables -t mangle -A PREROUTING -d 149.154.160.0/20 -j RETURN
iptables -t mangle -A PREROUTING -d 91.108.4.0/22 -j RETURN
```

**Policy Routing**:
```bash
# Create routing table
echo "51820 vpn" >> /etc/iproute2/rt_tables

# Add rule for marked packets
ip rule add fwmark 0x1 table vpn priority 1000

# Add default route via WireGuard
ip route add default dev wg0 table vpn
```

---

## 4. Security Specification

### 4.1 Defense Layers

```
Layer 1: Network (UFW)
├── Default deny incoming
├── Allow SSH from LAN only
├── Allow DNS from LAN only
├── Allow DHCP
└── Allow HTTP (Pi-hole admin) from LAN only

Layer 2: Application (Fail2ban)
├── SSH jail: 3 failures → 1 hour ban
├── Recidive jail: repeat offenders → 1 week ban
└── Telegram alerts on ban

Layer 3: Authentication
├── SSH: Key-only (passwords disabled)
├── SSH: Root login disabled
├── Telegram: User ID whitelist
└── Pi-hole: Password protected admin

Layer 4: Encryption
├── SSH: Ed25519 keys
├── WireGuard: ChaCha20-Poly1305
└── Telegram: TLS 1.3
```

### 4.2 SSH Hardening

```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
AllowUsers <username>
MaxAuthTries 3
LoginGraceTime 30
X11Forwarding no
PermitEmptyPasswords no
```

### 4.3 Fail2ban Configuration

```ini
[sshd]
enabled = true
port = ssh
filter = sshd
backend = systemd
maxretry = 3
findtime = 600
bantime = 3600
action = %(action_mwl)s

[recidive]
enabled = true
filter = recidive
logpath = /var/log/fail2ban.log
bantime = 604800
findtime = 86400
maxretry = 3
```

---

## 5. Deployment

### 5.1 Prerequisites

```bash
# System
- Raspberry Pi OS Lite (64-bit) or Debian/Ubuntu
- Static IP configured
- Internet access

# Software
- Docker 24.x+
- Docker Compose 2.x+
- Python 3.11+ (for local development)
```

### 5.2 Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/judariva/pi-command-center.git
cd pi-command-center

# 2. Configure environment
cp .env.example .env
nano .env

# 3. Deploy stack
docker compose up -d

# 4. Verify deployment
docker compose ps
docker compose logs -f

# 5. Configure router
# - Disable router DHCP
# - OR set Pi as primary DNS
```

### 5.3 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Bot token from @BotFather |
| `AUTHORIZED_USERS` | Yes | - | Comma-separated Telegram user IDs |
| `PIHOLE_PASSWORD` | No | random | Pi-hole admin password |
| `PIHOLE_API_KEY` | No | - | Pi-hole API key (from settings) |
| `NETWORK_RANGE` | No | 192.168.1.0/24 | LAN CIDR for scanning |
| `TZ` | No | UTC | Timezone |
| `DHCP_ENABLED` | No | false | Enable Pi-hole DHCP |
| `DHCP_START` | No | 192.168.1.100 | DHCP range start |
| `DHCP_END` | No | 192.168.1.250 | DHCP range end |
| `GATEWAY` | No | 192.168.1.1 | Router IP |

### 5.4 Health Checks

| Service | Check | Interval | Timeout |
|---------|-------|----------|---------|
| Unbound | `drill @127.0.0.1 -p 5335 cloudflare.com` | 30s | 10s |
| Pi-hole | `dig +short @127.0.0.1 pi.hole` | 30s | 10s |
| pibot | `requests.get('https://api.telegram.org')` | 60s | 15s |

---

## 6. Troubleshooting

### 6.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| DNS not resolving | Unbound not healthy | Check `docker logs unbound` |
| DHCP not working | Missing NET_ADMIN cap | Verify docker-compose capabilities |
| Bot not responding | Wrong token/user ID | Check `.env` configuration |
| VPN not routing | fwmark rules missing | Run `vpn-manager diagnose` |
| High latency | Recursive DNS slow | Check Unbound cache settings |

### 6.2 Diagnostic Commands

```bash
# DNS resolution test
dig google.com @<PI_IP>
dig +trace google.com @<PI_IP>

# Pi-hole blocking test
dig ads.google.com @<PI_IP>  # Should return 0.0.0.0

# Container status
docker compose ps
docker compose logs <service>

# Network connectivity
docker exec pihole ping -c 3 unbound

# VPN routing
ip rule show
ip route show table vpn
iptables -t mangle -L -v
```

---

## 7. Performance

### 7.1 Resource Usage (Idle)

| Resource | Pi 3B+ | Pi 4 (2GB) |
|----------|--------|------------|
| CPU | 5-10% | 2-5% |
| RAM | 400-500 MB | 400-500 MB |
| Disk I/O | Minimal | Minimal |
| Network | <1 Mbps | <1 Mbps |

### 7.2 DNS Performance

| Metric | First Query | Cached |
|--------|-------------|--------|
| Resolution Time | 50-200ms | <5ms |
| Cache Hit Rate | - | 80-90% |

### 7.3 Scaling Limits

| Metric | Limit | Notes |
|--------|-------|-------|
| Devices | 100+ | DHCP lease limit configurable |
| DNS Queries | 10K+/min | Depends on cache |
| Blocked Domains | 1M+ | RAM dependent |
| VPN Domains | 1000+ | ipset limit |

---

## 8. API Reference

### 8.1 Pi-hole API

**Base URL**: `http://localhost/admin/api.php`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `?summary` | GET | Statistics summary |
| `?enable` | GET | Enable blocking |
| `?disable=<seconds>` | GET | Disable for N seconds |
| `?topItems` | GET | Top queries/blocked |
| `?getQuerySources` | GET | Client statistics |

**Authentication**: `&auth=<API_KEY>`

### 8.2 Bot Commands

| Command | Description | Auth Required |
|---------|-------------|---------------|
| `/start` | Show main menu | Yes |
| `/status` | Quick status | Yes |
| `/vpn` | VPN control | Yes |
| `/devices` | Device scan | Yes |
| `/help` | Help message | Yes |

---

## 9. Changelog

### v1.0.0 (Initial Release)

- Pi-hole + Unbound DNS stack
- Telegram bot with full menu system
- VPN split routing (WireGuard)
- Security monitoring (Fail2ban)
- Docker containerization
- One-command installer

---

## 10. References

- [Pi-hole Documentation](https://docs.pi-hole.net/)
- [Unbound Documentation](https://nlnetlabs.nl/documentation/unbound/)
- [WireGuard Documentation](https://www.wireguard.com/)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/)
