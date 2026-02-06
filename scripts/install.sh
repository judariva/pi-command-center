#!/bin/bash
#
# Pi Command Center - Installation Script
# Run on Raspberry Pi
#

set -e

echo "=================================="
echo " Pi Command Center - Installer"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[X]${NC} $1"; exit 1; }

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "No ejecutar como root. Usa tu usuario normal."
fi

# Check if on Raspberry Pi
if ! grep -q "Raspberry" /proc/cpuinfo 2>/dev/null; then
    warn "No parece ser una Raspberry Pi. Continuando de todos modos..."
fi

log "Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

log "Instalando dependencias del sistema..."
sudo apt install -y \
    python3 python3-pip python3-venv \
    git curl wget \
    nmap arp-scan wakeonlan \
    fail2ban ufw \
    wireguard wireguard-tools \
    ipset iptables

log "Configurando IP estática..."
if ! grep -q "PI_IP_REDACTED" /etc/dhcpcd.conf; then
    cat << 'EOF' | sudo tee -a /etc/dhcpcd.conf

# Static IP for Pi Command Center
interface eth0
static ip_address=PI_IP_REDACTED/24
static routers=192.168.0.1
static domain_name_servers=127.0.0.1 1.1.1.1
EOF
    log "IP estática configurada. Reinicia para aplicar."
else
    log "IP estática ya configurada."
fi

log "Instalando Docker..."
if ! command -v docker &> /dev/null; then
    curl -sSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    log "Docker instalado. Necesitas cerrar sesión y volver a entrar."
else
    log "Docker ya instalado."
fi

log "Configurando SSH Hardening..."
sudo cp configs/sshd_hardening.conf /etc/ssh/sshd_config.d/hardening.conf 2>/dev/null || \
    warn "No se encontró el archivo de configuración SSH"

log "Configurando Fail2ban..."
sudo cp configs/jail.local /etc/fail2ban/jail.local 2>/dev/null || \
    warn "No se encontró el archivo de configuración Fail2ban"
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

log "Configurando UFW..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.0.0/24 to any port 22   # SSH
sudo ufw allow from 192.168.0.0/24 to any port 53   # DNS
sudo ufw allow 67/udp                                 # DHCP
sudo ufw allow from 192.168.0.0/24 to any port 80   # Pi-hole admin
sudo ufw --force enable

log "Creando entorno Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

log "Instalando VPN Manager..."
sudo cp scripts/vpn-manager /usr/local/bin/
sudo chmod +x /usr/local/bin/vpn-manager
sudo touch /etc/pihole/vpn-domains.txt

log "Configurando servicio systemd..."
sudo cp systemd/pibot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pibot

echo ""
echo "=================================="
echo " Instalación completada!"
echo "=================================="
echo ""
echo "Próximos pasos:"
echo "1. Copia .env.example a .env y configura los valores"
echo "2. Configura Docker (Pi-hole + Unbound) en docker/"
echo "3. Configura WireGuard en /etc/wireguard/"
echo "4. Reinicia el sistema: sudo reboot"
echo ""
echo "Después del reinicio:"
echo "  sudo systemctl start pibot"
echo "  sudo journalctl -u pibot -f"
echo ""
