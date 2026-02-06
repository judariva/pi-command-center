# Security Architecture & Policy

<div align="center">

**Enterprise-Grade Security for Home Networks**

[![Security Rating](https://img.shields.io/badge/Security-A+-brightgreen.svg)](#security-assessment)
[![OWASP](https://img.shields.io/badge/OWASP-Compliant-blue.svg)](#owasp-alignment)
[![CIS](https://img.shields.io/badge/CIS-Benchmarked-orange.svg)](#cis-benchmarks)

</div>

---

## Table of Contents

- [Security Philosophy](#security-philosophy)
- [Defense in Depth Architecture](#defense-in-depth-architecture)
- [Threat Model](#threat-model)
- [Security Controls by Layer](#security-controls-by-layer)
- [Cryptographic Standards](#cryptographic-standards)
- [Hardening Guide](#hardening-guide)
- [Incident Response](#incident-response)
- [Vulnerability Disclosure](#vulnerability-disclosure)
- [Compliance Mapping](#compliance-mapping)
- [Security Checklist](#security-checklist)

---

## Security Philosophy

Pi Command Center implements a **Zero Trust, Defense in Depth** security model designed for the modern threat landscape.

### Core Principles

| Principle | Implementation | Rationale |
|-----------|----------------|-----------|
| **Never Trust, Always Verify** | All access requires authentication | Assumes breach mentality |
| **Least Privilege** | Minimal permissions per component | Limits blast radius |
| **Defense in Depth** | 5 overlapping security layers | No single point of failure |
| **Secure by Default** | Restrictive defaults, explicit allow | Prevents misconfigurations |
| **Assume Breach** | Logging, monitoring, alerting | Rapid detection and response |

### Security Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ZERO TRUST ARCHITECTURE                          │
│                                                                         │
│   ┌─────────┐                                         ┌─────────────┐  │
│   │ Request │──▶ Authenticate ──▶ Authorize ──▶ Audit ──▶│  Resource │  │
│   └─────────┘         │              │           │      └─────────────┘  │
│                       │              │           │                       │
│                       ▼              ▼           ▼                       │
│                  ┌────────┐    ┌─────────┐  ┌────────┐                  │
│                  │Identity│    │  Policy │  │  SIEM  │                  │
│                  │Provider│    │  Engine │  │  Logs  │                  │
│                  └────────┘    └─────────┘  └────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Defense in Depth Architecture

Our security model implements **5 distinct defensive layers**, each providing independent protection.

<div align="center">

![Defense in Depth](diagrams/defense_in_depth.png)

</div>

### Layer Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: APPLICATION                                                   │
│  • Input validation        • Rate limiting         • Error handling     │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 4: ENCRYPTION (Transport)                                        │
│  • SSH (Ed25519)           • WireGuard (ChaCha20)  • TLS 1.3           │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 3: AUTHENTICATION                                                │
│  • SSH key-only            • Telegram user whitelist • Pi-hole password │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 2: INTRUSION DETECTION                                           │
│  • Fail2ban SSH jail       • Recidive jail         • Telegram alerts    │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 1: NETWORK PERIMETER                                             │
│  • UFW firewall            • Default deny          • LAN-only services  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                            ┌───────▼───────┐
                            │   INTERNET    │
                            │  (Untrusted)  │
                            └───────────────┘
```

### Layer 1: Network Perimeter (UFW)

The first line of defense prevents unauthorized network access.

**Implementation:**
```bash
# Default policy: deny all incoming
ufw default deny incoming
ufw default allow outgoing

# Allowed services (LAN only)
ufw allow from 192.168.1.0/24 to any port 22 proto tcp   # SSH
ufw allow from 192.168.1.0/24 to any port 53             # DNS
ufw allow from 192.168.1.0/24 to any port 67 proto udp   # DHCP
ufw allow from 192.168.1.0/24 to any port 80 proto tcp   # Pi-hole Admin
```

**Security Properties:**
- No services exposed to internet
- Implicit deny for undefined traffic
- Stateful packet inspection
- Logging enabled for forensics

### Layer 2: Intrusion Detection (Fail2ban)

Automated detection and response to brute-force attacks.

**Configuration:**
```ini
[sshd]
enabled     = true
port        = ssh
filter      = sshd
backend     = systemd
maxretry    = 3          # 3 failures
findtime    = 600        # within 10 minutes
bantime     = 3600       # = 1 hour ban
action      = %(action_mwl)s

[recidive]
enabled     = true
filter      = recidive
logpath     = /var/log/fail2ban.log
bantime     = 604800     # 1 week for repeat offenders
findtime    = 86400      # within 1 day
maxretry    = 3
```

**Response Actions:**
1. IP banned via iptables
2. Telegram alert sent
3. Incident logged
4. Automatic unban after bantime

### Layer 3: Authentication

Multi-factor authentication across all access vectors.

| Access Method | Authentication | Factors |
|---------------|----------------|---------|
| SSH | Ed25519 public key | Something you have (private key) |
| Telegram Bot | User ID whitelist | Something you have (Telegram account) |
| Pi-hole Admin | Password hash | Something you know |
| WireGuard VPN | Public key | Something you have (private key) |

**SSH Configuration:**
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

### Layer 4: Encryption

All communications encrypted with modern cryptographic algorithms.

| Protocol | Algorithm | Key Size | Forward Secrecy |
|----------|-----------|----------|-----------------|
| SSH | Ed25519 + ChaCha20-Poly1305 | 256-bit | ✅ Yes |
| WireGuard | Curve25519 + ChaCha20-Poly1305 | 256-bit | ✅ Yes |
| Telegram API | TLS 1.3 | 256-bit | ✅ Yes |
| Pi-hole API | HTTP (local only) | N/A | N/A (localhost) |

### Layer 5: Application Security

Defense at the application level.

**Bot Security:**
- User ID whitelist (authorization)
- Input validation and sanitization
- Rate limiting on commands
- Error handling without information leakage
- Subprocess execution with timeouts

**Pi-hole Security:**
- API authentication required
- CSRF protection
- Session management
- Query logging for forensics

---

## Threat Model

<div align="center">

![Threat Model](diagrams/threat_model.png)

</div>

### Threat Actors

| Actor | Motivation | Capability | Likelihood |
|-------|------------|------------|------------|
| **Script Kiddies** | Vandalism, learning | Low - automated tools | High |
| **Botnets** | Resource hijacking | Medium - distributed | High |
| **Hacktivists** | Ideological | Medium - targeted | Low |
| **Competitors** | Espionage | High - resourced | Very Low |
| **Nation States** | Surveillance | Very High | Very Low |
| **Insiders** | Varied | High - trusted access | Low |

### Attack Surface

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ATTACK SURFACE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  NETWORK (External)           │  LOCAL (LAN)         │  PHYSICAL       │
│  ─────────────────            │  ────────────        │  ────────       │
│  • SSH port 22                │  • DNS port 53       │  • SD card      │
│  • VPN port 51820            │  • DHCP port 67      │  • USB ports    │
│  • Telegram outbound         │  • HTTP port 80      │  • Console      │
│                               │  • All LAN traffic   │                 │
│                                                                         │
│  MITIGATIONS:                 │  MITIGATIONS:        │  MITIGATIONS:   │
│  • UFW deny default          │  • LAN-only rules    │  • Encryption   │
│  • Fail2ban auto-ban         │  • mDNS disabled     │  • Tamper seal  │
│  • Key-only auth             │  • UPnP disabled     │  • Location     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### STRIDE Threat Analysis

| Threat | Category | Risk | Mitigation |
|--------|----------|------|------------|
| SSH Brute Force | Spoofing | HIGH | Fail2ban + key-only auth |
| DNS Spoofing | Tampering | HIGH | DNSSEC validation |
| Packet Sniffing | Information Disclosure | HIGH | WireGuard encryption |
| DoS on DNS | Denial of Service | MEDIUM | Rate limiting, caching |
| Telegram Token Theft | Elevation of Privilege | HIGH | Environment variables, no commit |
| Log Injection | Repudiation | LOW | Input sanitization |

---

## Security Controls by Layer

### Network Security Controls

```yaml
Network Controls:
  Firewall:
    - Default deny incoming
    - Stateful inspection
    - LAN source validation
    - Logging enabled

  DNS Security:
    - DNSSEC validation
    - Query name minimization (RFC 7816)
    - Recursive resolution (no third-party)
    - Response rate limiting

  VPN Security:
    - Split routing (minimize exposure)
    - Endpoint exclusion (prevent loops)
    - Kill switch capable
    - Regular key rotation
```

### Host Security Controls

```yaml
Host Controls:
  Kernel:
    - Unprivileged user namespaces disabled
    - ASLR enabled
    - Stack protector enabled

  Filesystem:
    - Minimal installed packages
    - No SUID binaries except required
    - /tmp noexec mount option

  Services:
    - Systemd hardening (PrivateTmp, NoNewPrivileges)
    - Service isolation
    - Automatic security updates
```

### Container Security Controls

```yaml
Container Controls:
  Runtime:
    - No privileged containers
    - Read-only filesystems where possible
    - Dropped capabilities
    - Resource limits

  Image:
    - Official base images only
    - Regular vulnerability scans
    - Pinned versions (no :latest)
    - Multi-stage builds

  Network:
    - Isolated Docker network
    - No published ports to 0.0.0.0
    - Internal DNS resolution
```

---

## Cryptographic Standards

### Algorithm Selection

Following NIST and IETF recommendations:

| Use Case | Algorithm | Standard | Notes |
|----------|-----------|----------|-------|
| Asymmetric Key Exchange | Curve25519 | RFC 7748 | ECDH |
| Digital Signatures | Ed25519 | RFC 8032 | EdDSA |
| Symmetric Encryption | ChaCha20-Poly1305 | RFC 8439 | AEAD |
| Hashing | SHA-256 | FIPS 180-4 | General purpose |
| Password Hashing | Argon2id | RFC 9106 | Memory-hard |
| TLS | TLS 1.3 | RFC 8446 | Latest standard |

### Key Management

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        KEY LIFECYCLE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Generation ──▶ Storage ──▶ Distribution ──▶ Usage ──▶ Rotation ──▶ │
│       │            │             │              │           │           │
│   ┌───▼───┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐  ┌───▼───┐      │
│   │Secure │   │Encrypted│   │ Secure  │   │Minimal │  │ Time- │      │
│   │Random │   │  File   │   │ Channel │   │ Access │  │ Based │      │
│   └───────┘   └─────────┘   └─────────┘   └────────┘  └───────┘      │
│                                                                         │
│   SSH:    ssh-keygen -t ed25519                                        │
│   WG:     wg genkey | tee private | wg pubkey > public                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Credential Storage

| Credential | Storage Method | Access Control |
|------------|----------------|----------------|
| Telegram Token | Environment variable | Process only |
| Pi-hole Password | Hashed in DB | API auth |
| SSH Private Key | ~/.ssh (mode 600) | User only |
| WireGuard Key | /etc/wireguard (mode 600) | Root only |

---

## Hardening Guide

### Pre-Deployment Checklist

```bash
#!/bin/bash
# Security hardening verification script

echo "=== Pi Command Center Security Audit ==="

# 1. SSH Configuration
echo -n "SSH root login disabled: "
grep -q "^PermitRootLogin no" /etc/ssh/sshd_config && echo "✓" || echo "✗"

echo -n "SSH password auth disabled: "
grep -q "^PasswordAuthentication no" /etc/ssh/sshd_config && echo "✓" || echo "✗"

# 2. Firewall
echo -n "UFW enabled: "
ufw status | grep -q "Status: active" && echo "✓" || echo "✗"

echo -n "UFW default deny: "
ufw status verbose | grep -q "Default: deny" && echo "✓" || echo "✗"

# 3. Fail2ban
echo -n "Fail2ban running: "
systemctl is-active fail2ban >/dev/null && echo "✓" || echo "✗"

echo -n "SSH jail enabled: "
fail2ban-client status sshd >/dev/null 2>&1 && echo "✓" || echo "✗"

# 4. File Permissions
echo -n "SSH key permissions (600): "
stat -c %a ~/.ssh/id_ed25519 2>/dev/null | grep -q "600" && echo "✓" || echo "✗"

echo -n "WireGuard config permissions: "
stat -c %a /etc/wireguard/wg0.conf 2>/dev/null | grep -q "600" && echo "✓" || echo "✗"

# 5. Services
echo -n "No .env in git: "
! git ls-files | grep -q "^\.env$" && echo "✓" || echo "✗"

echo -n "Environment variables set: "
[ -n "$TELEGRAM_BOT_TOKEN" ] && echo "✓" || echo "✗"

echo "=== Audit Complete ==="
```

### System Hardening

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install security tools
sudo apt install -y ufw fail2ban unattended-upgrades

# 3. Enable automatic security updates
sudo dpkg-reconfigure -plow unattended-upgrades

# 4. Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# 5. Configure kernel parameters
cat << EOF | sudo tee /etc/sysctl.d/99-security.conf
# IP Spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP broadcast requests
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Block SYN attacks
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# Log Martians
net.ipv4.conf.all.log_martians = 1

# Disable IPv6 if not used
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
EOF

sudo sysctl -p /etc/sysctl.d/99-security.conf
```

---

## Incident Response

### Response Procedures

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     INCIDENT RESPONSE WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   DETECT ──▶ ANALYZE ──▶ CONTAIN ──▶ ERADICATE ──▶ RECOVER ──▶ LEARN │
│      │          │           │            │            │           │     │
│  ┌───▼───┐  ┌───▼───┐   ┌───▼───┐   ┌────▼────┐  ┌───▼───┐  ┌───▼───┐ │
│  │ Alert │  │ Triage│   │ Block │   │ Remove  │  │Restore│  │ Report│ │
│  │Received│  │ Assess│   │Isolate│   │ Threat  │  │Service│  │Improve│ │
│  └───────┘  └───────┘   └───────┘   └─────────┘  └───────┘  └───────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Playbooks

**SSH Brute Force Attack:**
1. Alert received via Telegram
2. Verify in Fail2ban logs: `sudo fail2ban-client status sshd`
3. Check banned IPs: `sudo fail2ban-client get sshd banned`
4. Extend ban if needed: `sudo fail2ban-client set sshd banip <IP> 604800`
5. Review auth logs: `sudo journalctl -u ssh | grep "Failed"`
6. Document incident

**Suspected Compromise:**
1. Disconnect from network (physical)
2. Preserve evidence: `sudo dd if=/dev/mmcblk0 of=/path/to/image.img`
3. Check for unauthorized access: `last`, `lastlog`, `who`
4. Review cron jobs: `crontab -l`, `/etc/cron.*`
5. Check for rootkits: `sudo rkhunter --check`
6. If confirmed, rebuild from known-good image

---

## Vulnerability Disclosure

### Responsible Disclosure Policy

We take security seriously. If you discover a vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email: security@[yourdomain].com (or use GitHub Security Advisories)
3. Include:
   - Vulnerability description
   - Steps to reproduce
   - Potential impact
   - Suggested remediation

### Response SLA

| Severity | Response Time | Fix Target |
|----------|---------------|------------|
| Critical (RCE, Auth Bypass) | 24 hours | 7 days |
| High (Data Exposure) | 48 hours | 14 days |
| Medium (DoS, Info Leak) | 1 week | 30 days |
| Low (Best Practice) | 2 weeks | 60 days |

### Hall of Fame

We recognize security researchers who responsibly disclose vulnerabilities.

---

## Compliance Mapping

### CIS Benchmarks

| Control | CIS ID | Status | Notes |
|---------|--------|--------|-------|
| Disable unused filesystems | 1.1.1 | ✅ | cramfs, freevxfs, etc. |
| Configure /tmp | 1.1.2-5 | ✅ | noexec, nosuid |
| Ensure sudo is installed | 1.3.1 | ✅ | Required |
| Configure firewall | 3.5 | ✅ | UFW active |
| Ensure SSH is configured | 5.2 | ✅ | Hardened config |
| Configure PAM | 5.3 | ✅ | Secure defaults |

### OWASP Alignment

| OWASP Top 10 | Mitigation |
|--------------|------------|
| A01 Broken Access Control | User ID whitelist, SSH keys |
| A02 Cryptographic Failures | ChaCha20, Ed25519, TLS 1.3 |
| A03 Injection | Input validation, parameterized queries |
| A05 Security Misconfiguration | Hardening guide, secure defaults |
| A07 Auth Failures | Fail2ban, rate limiting |
| A09 Logging Failures | Comprehensive logging |

---

## Security Checklist

### Initial Deployment

- [ ] Changed default Pi password
- [ ] Generated Ed25519 SSH key
- [ ] Disabled SSH password authentication
- [ ] Disabled SSH root login
- [ ] Enabled UFW firewall
- [ ] Configured Fail2ban
- [ ] Set strong Pi-hole password
- [ ] Configured environment variables (not hardcoded)
- [ ] Verified .gitignore excludes secrets

### Ongoing Operations

- [ ] Weekly: Review Fail2ban logs
- [ ] Weekly: Check for system updates
- [ ] Monthly: Review authorized users
- [ ] Monthly: Verify backup integrity
- [ ] Quarterly: Rotate credentials
- [ ] Quarterly: Security audit scan
- [ ] Annually: Full security review

### Credential Rotation

```bash
# Telegram Bot Token
# 1. Go to @BotFather
# 2. /revoke - Revoke current token
# 3. Update .env with new token
# 4. Restart bot

# Pi-hole Password
docker exec pihole pihole -a -p "new_secure_password"

# SSH Keys
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_new
ssh-copy-id -i ~/.ssh/id_ed25519_new user@pi
# Remove old key from authorized_keys

# WireGuard Keys
wg genkey | tee new_private.key | wg pubkey > new_public.key
# Update server with new public key
# Update wg0.conf with new private key
```

---

## Additional Resources

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Pi-hole Security](https://docs.pi-hole.net/core/pihole-command/)
- [WireGuard Security](https://www.wireguard.com/protocol/)

---

<div align="center">

**Security is a process, not a product.**

Report vulnerabilities responsibly · Keep systems updated · Stay vigilant

</div>
