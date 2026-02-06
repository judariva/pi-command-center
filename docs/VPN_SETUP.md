# VPN Split Routing Setup

Configure WireGuard with domain-based split tunneling to route specific traffic through VPN while keeping local traffic direct.

## Architecture

```
                    ┌─────────────────┐
                    │   VPN Server    │
                    │  (Remote Host)  │
                    └────────▲────────┘
                             │ WireGuard Tunnel
                             │
┌─────────────────────────────────────────────────────────┐
│                    RASPBERRY PI                          │
│                                                          │
│  ┌─────────┐    ┌─────────┐    ┌───────────────────┐   │
│  │ Pi-hole │───▶│  ipset  │───▶│  iptables mangle  │   │
│  │  (DNS)  │    │ (domain │    │     (fwmark)      │   │
│  │         │    │   IPs)  │    │                   │   │
│  └─────────┘    └─────────┘    └─────────┬─────────┘   │
│                                           │             │
│                    ┌──────────────────────┼─────────┐   │
│                    │                      │         │   │
│                    ▼                      ▼         │   │
│            ┌──────────────┐      ┌──────────────┐   │   │
│            │  VPN Table   │      │  Main Table  │   │   │
│            │ (marked pkts)│      │  (default)   │   │   │
│            └──────┬───────┘      └──────┬───────┘   │   │
│                   │                     │           │   │
│                   ▼                     ▼           │   │
│            ┌──────────────┐      ┌──────────────┐   │   │
│            │   wg0        │      │    eth0      │   │   │
│            │  (VPN iface) │      │ (LAN iface)  │   │   │
│            └──────────────┘      └──────────────┘   │   │
└─────────────────────────────────────────────────────────┘
                   │                      │
                   ▼                      ▼
            Internet (VPN)         Internet (Direct)
```

## How It Works

1. **DNS Resolution**: Pi-hole resolves domain names
2. **IP Collection**: dnsmasq ipset directive adds resolved IPs to an ipset
3. **Packet Marking**: iptables mangle table marks packets destined for ipset IPs
4. **Policy Routing**: Marked packets use VPN routing table
5. **Selective Tunneling**: Only marked traffic goes through WireGuard

## Prerequisites

- WireGuard installed on Raspberry Pi
- VPN server with WireGuard configured
- Pi-hole running as DNS server

## Configuration

### 1. WireGuard Client Config

```ini
# /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <client_private_key>
Address = 10.66.66.2/32
Table = off  # Disable automatic routing

[Peer]
PublicKey = <server_public_key>
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

### 2. Create VPN Domains List

```bash
# /etc/pihole/vpn-domains.txt
netflix.com
reddit.com
spotify.com
```

### 3. Configure dnsmasq ipset

```bash
# /etc/dnsmasq.d/99-vpn-ipset.conf
ipset=/netflix.com/reddit.com/spotify.com/vpn
```

### 4. Setup iptables Rules

```bash
# Create ipset
ipset create vpn hash:ip

# Mark packets for VPN destinations
iptables -t mangle -A PREROUTING -m set --match-set vpn dst -j MARK --set-mark 0x1

# Exclude VPN endpoint from marking (critical!)
iptables -t mangle -I PREROUTING -d <VPN_SERVER_IP> -j RETURN
```

### 5. Configure Policy Routing

```bash
# Add routing table
echo "100 vpn" >> /etc/iproute2/rt_tables

# Add rule for marked packets
ip rule add fwmark 0x1 table vpn priority 1000

# Add default route via WireGuard
ip route add default dev wg0 table vpn
```

## VPN Manager Script

The included `vpn-manager` script handles all VPN operations:

```bash
# Start VPN in split mode
vpn-manager start

# Switch to full VPN mode (route all traffic)
vpn-manager full

# Switch back to split mode
vpn-manager split

# Add domain to VPN routing
vpn-manager add netflix.com

# Check status
vpn-manager status

# Stop VPN
vpn-manager stop
```

## Verification

```bash
# Check if domain resolves and IP is in ipset
dig netflix.com
ipset list vpn

# Verify routing
ip rule show
ip route show table vpn

# Test split routing
curl -s ifconfig.me          # Should show your ISP IP
curl -s --resolve netflix.com:443:<netflix_ip> https://netflix.com  # Through VPN
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| VPN not connecting | Check endpoint IP and firewall rules |
| All traffic through VPN | Verify `Table = off` in wg0.conf |
| Domain not routing through VPN | Restart dnsmasq after adding to ipset |
| Connection drops | Check VPN endpoint exclusion rule |

## Important Notes

- Always exclude VPN server IP from VPN routing
- Exclude Telegram IPs if using the bot (149.154.160.0/20, 91.108.4.0/22)
- The ipset is cleared on reboot; domains are re-added on DNS resolution
