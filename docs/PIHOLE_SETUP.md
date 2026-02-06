# Pi-hole + Unbound Setup

Configure Pi-hole as your network's DNS and DHCP server with Unbound for recursive DNS resolution.

## Architecture

```
Client → Pi-hole (53) → Unbound (5335) → Root DNS Servers
```

**Why Unbound?**
- No third-party DNS providers (Google, Cloudflare)
- Maximum privacy: queries go directly to root servers
- No external logging of your DNS activity

## Prerequisites

- Docker & Docker Compose installed
- Static IP configured on Raspberry Pi
- Port 53 available (no other DNS server running)

## Docker Deployment

### Environment Variables

```bash
# .env
PIHOLE_PASSWORD=your_secure_password
PI_IP=192.168.1.10
NETWORK_RANGE=192.168.1.0/24
DHCP_START=192.168.1.100
DHCP_END=192.168.1.250
GATEWAY=192.168.1.1
```

### Unbound Configuration

Create `docker/unbound/unbound.conf`:

```yaml
server:
    verbosity: 0
    interface: 0.0.0.0
    port: 5335
    do-ip4: yes
    do-udp: yes
    do-tcp: yes
    do-ip6: no

    # Security
    hide-identity: yes
    hide-version: yes
    harden-glue: yes
    harden-dnssec-stripped: yes

    # Privacy
    qname-minimisation: yes

    # Performance
    num-threads: 2
    msg-cache-size: 64m
    rrset-cache-size: 128m
    cache-min-ttl: 300
    cache-max-ttl: 86400
    prefetch: yes

    # Access control
    access-control: 172.20.0.0/24 allow
    access-control: 127.0.0.0/8 allow
```

## Deploy

```bash
docker compose up -d
```

## DHCP Configuration

When Pi-hole serves as DHCP:

| Setting | Value |
|---------|-------|
| DHCP Range | 192.168.1.100 - 192.168.1.250 |
| Gateway | Your router IP |
| DNS Server | Pi's IP (auto-configured) |
| Lease Time | 24 hours |

**Important**: Disable DHCP on your router when enabling Pi-hole DHCP.

## Verification

```bash
# Test DNS resolution
dig google.com @<PI_IP>

# Test ad blocking (should return 0.0.0.0)
dig ads.google.com @<PI_IP>

# Test Unbound directly
dig google.com @127.0.0.1 -p 5335

# Verify DNSSEC
dig sigok.verteiltesysteme.net @<PI_IP>
```

## Web Admin

Access: `http://<PI_IP>/admin`

## Recommended Blocklists

| List | Description |
|------|-------------|
| Steven Black | Unified hosts with multiple extensions |
| OISD | Comprehensive ad/tracker blocking |

Add via Pi-hole Admin → Adlists → Add.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DNS not resolving | Check `docker logs unbound` |
| DHCP not assigning IPs | Verify port 67 is exposed |
| Slow queries | Check Unbound cache settings |
| Ads showing | Run `pihole -g` to update blocklists |
