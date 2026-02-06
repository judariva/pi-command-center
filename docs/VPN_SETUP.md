# VPN Split Routing Setup

Configure WireGuard with domain-based split tunneling to route specific traffic through VPN while keeping local traffic direct.

## Table of Contents

- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [WireGuard Key Generation](#wireguard-key-generation)
- [Configuration](#configuration)
- [VPN Manager Script](#vpn-manager-script)
- [Security Considerations](#security-considerations)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Rollback / Uninstall](#rollback--uninstall)

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
4. **Policy Routing**: Marked packets use VPN routing table (table 51820)
5. **Selective Tunneling**: Only marked traffic goes through WireGuard

## Prerequisites

- WireGuard installed on Raspberry Pi
- VPN server with WireGuard configured (your own or provider like Mullvad, PIA)
- Pi-hole running as DNS server
- Root/sudo access

### Installing WireGuard

```bash
# Raspberry Pi OS / Debian
sudo apt update
sudo apt install wireguard wireguard-tools

# Verify installation
wg --version
```

## WireGuard Key Generation

Generate keys for your client (Raspberry Pi):

```bash
# Create directory with secure permissions
sudo mkdir -p /etc/wireguard
cd /etc/wireguard

# Generate private key (keep this secret!)
wg genkey | sudo tee private.key
sudo chmod 600 private.key

# Generate public key from private key
sudo cat private.key | wg pubkey | sudo tee public.key

# View your public key (add this to your VPN server)
cat public.key
```

**Important**: Your public key needs to be added to your VPN server's peer configuration.

## Configuration

### 1. WireGuard Client Config

```ini
# /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <your_private_key_here>
Address = 10.66.66.2/32
Table = off  # CRITICAL: Disable automatic routing

[Peer]
PublicKey = <server_public_key>
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

> **Note**: `Table = off` is essential for split routing. Without it, WireGuard will route ALL traffic through the tunnel.

### 2. Create VPN Domains List

```bash
# /etc/pihole/vpn-domains.txt
netflix.com
reddit.com
spotify.com
hulu.com
```

### 3. Configure dnsmasq ipset

Create or edit `/etc/dnsmasq.d/99-vpn-ipset.conf`:

```bash
# Correct syntax for dnsmasq ipset (one domain per line for clarity)
# Or combine multiple domains on one line separated by /
ipset=/netflix.com/vpn
ipset=/reddit.com/vpn
ipset=/spotify.com/vpn
```

**Alternative: Multiple domains in one line:**
```bash
ipset=/netflix.com/reddit.com/spotify.com/hulu.com/vpn
```

Restart dnsmasq to apply:
```bash
sudo systemctl restart pihole-FTL
# or in Docker:
docker exec pihole pihole restartdns
```

### 4. Setup iptables Rules

```bash
# Create ipset for VPN destinations
sudo ipset create vpn hash:ip

# CRITICAL: Exclude VPN endpoint from VPN routing (prevent routing loop!)
VPN_ENDPOINT_IP=$(dig +short vpn.example.com | head -1)
sudo iptables -t mangle -A PREROUTING -d $VPN_ENDPOINT_IP -j RETURN

# Exclude Telegram IPs (so bot works without VPN)
sudo iptables -t mangle -A PREROUTING -d 149.154.160.0/20 -j RETURN
sudo iptables -t mangle -A PREROUTING -d 91.108.4.0/22 -j RETURN

# Mark packets for VPN destinations
sudo iptables -t mangle -A PREROUTING -m set --match-set vpn dst -j MARK --set-mark 0x1

# NAT for VPN traffic
sudo iptables -t nat -A POSTROUTING -o wg0 -j MASQUERADE
```

### 5. Configure Policy Routing

```bash
# Add routing table (use 51820 - WireGuard default port as ID)
echo "51820 vpn" | sudo tee -a /etc/iproute2/rt_tables

# Add rule for marked packets
sudo ip rule add fwmark 0x1 table 51820 priority 1000

# Add default route via WireGuard interface
sudo ip route add default dev wg0 table 51820
```

### 6. Domain Persistence

Domains are re-added to the ipset automatically when Pi-hole resolves them. However, the ipset itself is cleared on reboot.

**Make ipset persistent:**

Create `/etc/systemd/system/vpn-ipset.service`:
```ini
[Unit]
Description=Create VPN ipset
Before=network-pre.target
Wants=network-pre.target

[Service]
Type=oneshot
ExecStart=/sbin/ipset create vpn hash:ip -exist
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Enable the service:
```bash
sudo systemctl enable vpn-ipset
```

## VPN Manager Script

The included `vpn-manager` script handles all VPN operations:

```bash
# Start VPN in split mode (default)
vpn-manager start

# Switch to full VPN mode (route all traffic)
vpn-manager full

# Switch back to split mode
vpn-manager split

# Add domain to VPN routing
vpn-manager add netflix.com

# Remove domain from VPN routing
vpn-manager remove netflix.com

# Check status
vpn-manager status

# Stop VPN
vpn-manager stop

# Diagnose issues
vpn-manager diagnose
```

## Security Considerations

### What This Setup Does

| Traffic Type | Route | Privacy Level |
|--------------|-------|---------------|
| Domains in vpn-domains.txt | VPN tunnel | High (encrypted, IP hidden) |
| Local network (192.168.x.x) | Direct | N/A (internal) |
| All other traffic | Direct (ISP) | Standard (visible to ISP) |

### Security Implications

**Pros:**
- Streaming services see VPN IP (geo-unlock)
- Selected domains have encrypted tunnel
- Better performance for non-VPN traffic
- Reduces VPN bandwidth usage

**Cons:**
- ISP can see non-VPN traffic patterns
- DNS queries go through Pi-hole (local) then Unbound (recursive) - visible to observers
- If VPN drops, traffic may leak (without kill switch)

### Recommendations

1. **Always exclude VPN endpoint**: Prevents routing loop that breaks connectivity
2. **Exclude Telegram IPs**: Ensures bot works even if VPN is down
3. **Consider DNS over VPN**: For maximum privacy, configure Unbound to query through VPN
4. **Monitor VPN status**: Use the bot or watchdog to detect VPN failures

## Verification

```bash
# Check if WireGuard is up
sudo wg show

# Check if domain resolves and IP is in ipset
dig netflix.com
sudo ipset list vpn

# Verify routing rules
ip rule show
# Should show: 1000:  from all fwmark 0x1 lookup 51820

# Check VPN routing table
ip route show table 51820
# Should show: default dev wg0

# Verify iptables mangle rules
sudo iptables -t mangle -L PREROUTING -v -n

# Test split routing
curl -s ifconfig.me          # Should show ISP IP (direct)
# Then access a VPN domain in browser - should show VPN IP
```

### Testing Split Routing

```bash
# Check what IP Netflix sees
curl -s --resolve api.fast.com:443:$(dig +short api.fast.com) https://api.fast.com/netflix/speedtest/v2 | jq .client.ip

# Or simpler: access Netflix in browser and check IP
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| VPN not connecting | Wrong endpoint/keys | Verify wg0.conf configuration |
| All traffic through VPN | Missing `Table = off` | Add to [Interface] section |
| Domain not routing through VPN | dnsmasq not updated | Restart dnsmasq after config change |
| Connection drops | VPN endpoint in ipset | Ensure endpoint is excluded FIRST |
| Telegram bot fails | Telegram IPs routed to VPN | Add Telegram IP exclusion rules |
| Slow DNS after changes | ipset large/fragmented | `ipset flush vpn` and let it rebuild |

### Diagnostic Commands

```bash
# Check WireGuard status
sudo wg show wg0

# View current ipset entries
sudo ipset list vpn

# Check for routing loops
traceroute 8.8.8.8

# View mangle rules
sudo iptables -t mangle -L -v -n

# Check if fwmark is applied
sudo iptables -t mangle -L PREROUTING -v | grep vpn

# Test DNS resolution for VPN domain
dig netflix.com @localhost
sudo ipset test vpn $(dig +short netflix.com | head -1)
```

## Rollback / Uninstall

### Disable Split Routing (Keep WireGuard)

```bash
# Remove policy routing
sudo ip rule del fwmark 0x1 table 51820

# Remove mangle rules
sudo iptables -t mangle -F PREROUTING

# Remove ipset
sudo ipset destroy vpn

# Remove dnsmasq config
sudo rm /etc/dnsmasq.d/99-vpn-ipset.conf
sudo systemctl restart pihole-FTL
```

### Complete WireGuard Removal

```bash
# Stop and disable WireGuard
sudo wg-quick down wg0
sudo systemctl disable wg-quick@wg0

# Remove configuration
sudo rm -rf /etc/wireguard/

# Remove routing table entry
sudo sed -i '/51820 vpn/d' /etc/iproute2/rt_tables

# Uninstall WireGuard (optional)
sudo apt remove wireguard wireguard-tools
```

### Restore Default Routing

If network is broken after changes:

```bash
# Emergency: flush all custom routing
sudo ip rule flush
sudo ip rule add from all lookup local priority 0
sudo ip rule add from all lookup main priority 32766
sudo ip rule add from all lookup default priority 32767

# Restart networking
sudo systemctl restart networking
```

## Important Notes

- **Always exclude VPN server IP** from VPN routing to prevent routing loops
- **Exclude Telegram IPs** if using the bot (149.154.160.0/20, 91.108.4.0/22)
- The ipset is cleared on reboot; domains are re-added when DNS resolves them
- Use routing table ID **51820** consistently (matches WireGuard default port)
- Monitor VPN health - if tunnel dies, traffic may route incorrectly
