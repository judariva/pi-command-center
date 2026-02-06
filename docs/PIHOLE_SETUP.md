# Pi-hole + Unbound Setup

Configure Pi-hole as your network's DNS and DHCP server with Unbound for recursive DNS resolution.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [DHCP Configuration](#dhcp-configuration)
- [Web Admin](#web-admin)
- [Blocklist Management](#blocklist-management)
- [Whitelisting](#whitelisting)
- [Local DNS Records](#local-dns-records)
- [API Key Setup](#api-key-setup)
- [Performance Tuning](#performance-tuning)
- [Backup and Restore](#backup-and-restore)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

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

### DHCP Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Devices not getting IP | Port 67 not exposed | Check Docker port mapping |
| Wrong gateway assigned | DHCP_ROUTER misconfigured | Verify GATEWAY in .env |
| Short lease time | Default 24h | Adjust in Pi-hole admin → DHCP |
| Static leases not working | Need MAC reservation | Use Pi-hole admin → DHCP → Static |
| DHCP conflicts | Router DHCP still active | Disable DHCP on router first |

## Web Admin

Access: `http://<PI_IP>/admin`

### Setting the Admin Password

**Option 1: Via Docker**
```bash
docker exec -it pihole pihole -a -p your_new_password
```

**Option 2: Via Environment Variable**
```bash
# In .env or docker-compose.yml
WEBPASSWORD=your_secure_password
```

**Option 3: Reset Password**
```bash
docker exec -it pihole pihole -a -p
# Will prompt for new password
```

## Blocklist Management

### Adding Blocklists

1. Go to Pi-hole Admin → **Adlists**
2. Add URL and description
3. Click **Add**
4. Run `pihole -g` to update

### Recommended Blocklists

| List | URL | Domains | Description |
|------|-----|---------|-------------|
| Steven Black | `https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts` | ~130K | Unified hosts |
| OISD Basic | `https://dbl.oisd.nl/basic/` | ~70K | Balanced blocking |
| OISD Full | `https://dbl.oisd.nl/` | ~1M+ | Comprehensive |
| Energized | `https://block.energized.pro/basic/formats/hosts.txt` | ~300K | Privacy focused |

### Updating Blocklists

```bash
# Manual update
docker exec -it pihole pihole -g

# Check update status
docker exec -it pihole pihole -g -f

# View current blocklist count
docker exec -it pihole pihole -t
```

### Removing Blocklists

1. Go to Pi-hole Admin → **Adlists**
2. Click the red X next to the list
3. Run `pihole -g` to apply changes

## Whitelisting

### Whitelist a Domain

**Via Web Admin:**
1. Go to **Whitelist** tab
2. Enter domain (e.g., `example.com`)
3. Click **Add**

**Via CLI:**
```bash
# Single domain
docker exec pihole pihole -w example.com

# Wildcard (all subdomains)
docker exec pihole pihole --wild example.com

# Regex whitelist
docker exec pihole pihole --white-regex '.*\.example\.com$'
```

### Common Whitelisting Needs

| Service | Domains to Whitelist |
|---------|---------------------|
| Netflix | `netflix.com`, `nflxvideo.net` |
| Microsoft | `login.microsoftonline.com`, `outlook.office365.com` |
| Apple | `apple.com`, `icloud.com`, `mzstatic.com` |
| Google | `google.com`, `gstatic.com`, `googleapis.com` |
| Amazon | `amazon.com`, `amazonaws.com` |

### Checking Why Something Is Blocked

```bash
# Query logs for domain
docker exec pihole pihole -q blocked-domain.com

# View real-time log
docker exec pihole pihole -t
```

## Local DNS Records

Add local hostname resolution (e.g., `mynas.home` → `192.168.1.50`).

### Via Web Admin

1. Go to **Local DNS** → **DNS Records**
2. Enter domain and IP
3. Click **Add**

### Via Configuration File

Create `/etc/pihole/custom.list`:
```
192.168.1.50 mynas.home
192.168.1.60 printer.home
192.168.1.43 pihole.home pi.home
```

Then restart DNS:
```bash
docker exec pihole pihole restartdns
```

### Local CNAME Records

Go to **Local DNS** → **CNAME Records** to create aliases:
```
www.mynas.home → mynas.home
files.home → mynas.home
```

## API Key Setup

The API key is needed for authenticated operations (enable/disable blocking).

### Generating the API Key

1. Go to Pi-hole Admin → **Settings** → **API/Web Interface**
2. Click **Show API token**
3. Copy the token (it's a SHA-256 hash of your password)

### Using in Bot Configuration

```bash
# .env
PIHOLE_API_KEY=your_api_token_here
```

### API Endpoints

| Endpoint | Auth Required | Description |
|----------|---------------|-------------|
| `?summary` | No | Statistics summary |
| `?enable` | Yes | Enable blocking |
| `?disable=300` | Yes | Disable for 5 minutes |
| `?topItems` | Yes | Top queries/blocked |
| `?getQuerySources` | Yes | Client statistics |

## Performance Tuning

### Unbound Optimization

For Raspberry Pi, optimize memory usage:

```yaml
# unbound.conf additions
server:
    # Reduce memory on Pi 3
    msg-cache-size: 32m
    rrset-cache-size: 64m

    # Aggressive caching
    cache-min-ttl: 3600
    prefetch: yes
    prefetch-key: yes

    # Limit concurrent queries
    num-queries-per-thread: 2048
```

### Pi-hole Database Optimization

```bash
# Vacuum the query database
docker exec pihole sqlite3 /etc/pihole/pihole-FTL.db "VACUUM;"

# Reduce query log retention (default: 365 days)
# In Pi-hole Admin → Settings → Privacy → Query Log: 90 days
```

### Reducing CPU Usage

If DNS queries cause high CPU:

```bash
# Check query rate
docker exec pihole pihole -c -e

# Consider adding delay for heavy clients
# In dnsmasq.d/01-custom.conf:
# limit-port-usage=60
```

## Backup and Restore

### Full Backup

```bash
# Export Pi-hole configuration (teleporter)
curl -X GET "http://localhost/admin/scripts/pi-hole/php/teleporter.php" \
  -o pihole-backup-$(date +%Y%m%d).tar.gz
```

### Via Web Admin

1. Go to **Settings** → **Teleporter**
2. Click **Backup** to download configuration

### Restore from Backup

1. Go to **Settings** → **Teleporter**
2. Upload your backup file
3. Select what to restore
4. Click **Restore**

### Docker Volume Backup

```bash
# Stop containers
docker compose stop

# Backup volumes
tar -czf pihole-volumes-backup.tar.gz \
  -C /var/lib/docker/volumes \
  pibot_pihole_config \
  pibot_pihole_dnsmasq

# Restart
docker compose start
```

### Automated Backups

Add to crontab:
```bash
# Daily backup at 3 AM
0 3 * * * docker exec pihole bash -c "cd /etc/pihole && tar -czf /backup/pihole-$(date +\%Y\%m\%d).tar.gz ."
```

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

# Check Pi-hole is responding
dig pi.hole @<PI_IP>
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| DNS not resolving | Check `docker logs unbound` |
| DHCP not assigning IPs | Verify port 67 is exposed |
| Slow queries | Check Unbound cache settings |
| Ads still showing | Run `pihole -g` to update blocklists |
| Web admin inaccessible | Check port 80 isn't used by another service |

### Diagnostic Commands

```bash
# Check container status
docker compose ps

# View Pi-hole logs
docker logs pihole --tail 50

# View Unbound logs
docker logs unbound --tail 50

# Check DNS chain
docker exec pihole dig google.com @127.0.0.1 +trace

# Verify upstream is Unbound
docker exec pihole cat /etc/pihole/setupVars.conf | grep PIHOLE_DNS

# Check blocking status
docker exec pihole pihole status
```

### Reset to Defaults

```bash
# Clear all custom settings
docker exec pihole pihole -r

# Reset password
docker exec pihole pihole -a -p

# Recreate containers
docker compose down
docker compose up -d
```
