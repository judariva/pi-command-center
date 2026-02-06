#!/bin/bash
#
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                      PI COMMAND CENTER INSTALLER                          ║
# ║                         One-Command Deploy                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/judariva/pi-command-center/main/install.sh | bash
#
# Or with options:
#   curl -sSL ... | bash -s -- --no-vpn --skip-hardening
#

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================
REPO_URL="https://github.com/judariva/pi-command-center.git"
INSTALL_DIR="$HOME/pi-command-center"
VERSION="1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
    ____  _    ____                                          __
   / __ \(_)  / ____/___  ____ ___  ____ ___  ____ _____  __/ /
  / /_/ / /  / /   / __ \/ __ `__ \/ __ `__ \/ __ `/ __ \/ __  /
 / ____/ /  / /___/ /_/ / / / / / / / / / / / /_/ / / / / /_/ /
/_/   /_/   \____/\____/_/ /_/ /_/_/ /_/ /_/\__,_/_/ /_/\__,_/

         ____            __
        / __ \___  ____  / /____  _____
       / /  / _ \/ __ \/ __/ _ \/ ___/
      / /__/  __/ / / / /_/  __/ /
      \____/\___/_/ /_/\__/\___/_/

EOF
    echo -e "${NC}"
    echo -e "${WHITE}Version ${VERSION} - Privacy-First Home Network Control${NC}"
    echo ""
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_step() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

confirm() {
    local prompt="$1"
    local default="${2:-y}"

    if [[ "$default" == "y" ]]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi

    read -p "$prompt" response
    response=${response:-$default}

    [[ "$response" =~ ^[Yy]$ ]]
}

get_input() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"

    if [[ -n "$default" ]]; then
        read -p "$prompt [$default]: " value
        value=${value:-$default}
    else
        read -p "$prompt: " value
    fi

    eval "$var_name='$value'"
}

get_secret() {
    local prompt="$1"
    local var_name="$2"

    read -sp "$prompt: " value
    echo ""
    eval "$var_name='$value'"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "Do not run this script as root. Run as your normal user."
        exit 1
    fi
}

check_system() {
    log_step "Checking System Requirements"

    # Check OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        log_info "Operating System: $OS"
    else
        log_warn "Could not detect OS"
        OS="Unknown"
    fi

    # Check architecture
    ARCH=$(uname -m)
    log_info "Architecture: $ARCH"

    if [[ "$ARCH" == "armv7l" || "$ARCH" == "aarch64" ]]; then
        log_success "Raspberry Pi detected"
        IS_PI=true
    else
        log_warn "Not a Raspberry Pi - some features may not work"
        IS_PI=false
    fi

    # Check RAM
    TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
    log_info "Total RAM: ${TOTAL_RAM}MB"

    if [[ $TOTAL_RAM -lt 900 ]]; then
        log_warn "Low RAM detected. Performance may be affected."
    fi

    # Check disk space
    FREE_DISK=$(df -m "$HOME" | awk 'NR==2 {print $4}')
    log_info "Free disk space: ${FREE_DISK}MB"

    if [[ $FREE_DISK -lt 2000 ]]; then
        log_error "Insufficient disk space. Need at least 2GB free."
        exit 1
    fi

    log_success "System check passed"
}

detect_network() {
    log_step "Detecting Network Configuration"

    # Get default interface
    DEFAULT_IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
    log_info "Default interface: $DEFAULT_IFACE"

    # Get current IP
    CURRENT_IP=$(ip -4 addr show "$DEFAULT_IFACE" | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -1)
    log_info "Current IP: $CURRENT_IP"

    # Get gateway
    GATEWAY=$(ip route | grep default | awk '{print $3}' | head -1)
    log_info "Gateway: $GATEWAY"

    # Detect network range
    NETWORK_PREFIX=$(echo "$CURRENT_IP" | cut -d. -f1-3)
    NETWORK_RANGE="${NETWORK_PREFIX}.0/24"
    log_info "Network range: $NETWORK_RANGE"

    log_success "Network detected"
}

install_docker() {
    log_step "Installing Docker"

    if command -v docker &> /dev/null; then
        log_success "Docker already installed"
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
        log_info "Docker version: $DOCKER_VERSION"
    else
        log_info "Installing Docker..."
        curl -fsSL https://get.docker.com | sh

        # Add user to docker group
        sudo usermod -aG docker "$USER"
        log_success "Docker installed"
        log_warn "You may need to log out and back in for docker group to take effect"

        NEED_RELOGIN=true
    fi

    # Check docker compose
    if docker compose version &> /dev/null; then
        log_success "Docker Compose available"
    elif command -v docker-compose &> /dev/null; then
        log_success "Docker Compose (standalone) available"
        COMPOSE_CMD="docker-compose"
    else
        log_info "Installing Docker Compose plugin..."
        sudo apt-get update
        sudo apt-get install -y docker-compose-plugin
        log_success "Docker Compose installed"
    fi

    COMPOSE_CMD="${COMPOSE_CMD:-docker compose}"
}

install_dependencies() {
    log_step "Installing System Dependencies"

    sudo apt-get update

    DEPS="git curl wget jq"

    for dep in $DEPS; do
        if command -v "$dep" &> /dev/null; then
            log_success "$dep already installed"
        else
            log_info "Installing $dep..."
            sudo apt-get install -y "$dep"
            log_success "$dep installed"
        fi
    done
}

clone_repository() {
    log_step "Downloading Pi Command Center"

    if [[ -d "$INSTALL_DIR" ]]; then
        log_warn "Installation directory already exists"
        if confirm "Remove and reinstall?"; then
            rm -rf "$INSTALL_DIR"
        else
            log_info "Updating existing installation..."
            cd "$INSTALL_DIR"
            git pull
            return
        fi
    fi

    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    log_success "Repository cloned to $INSTALL_DIR"
}

configure_installation() {
    log_step "Configuration Wizard"

    echo -e "${WHITE}Let's configure your Pi Command Center${NC}"
    echo ""

    # Telegram Bot Token
    echo -e "${CYAN}1. Telegram Bot Configuration${NC}"
    echo "   Create a bot with @BotFather on Telegram to get a token."
    echo "   Guide: https://core.telegram.org/bots#creating-a-new-bot"
    echo ""
    get_secret "Enter your Telegram Bot Token" BOT_TOKEN

    if [[ -z "$BOT_TOKEN" ]]; then
        log_error "Bot token is required"
        exit 1
    fi

    # Authorized Users
    echo ""
    echo -e "${CYAN}2. Authorized Users${NC}"
    echo "   Get your Telegram user ID from @userinfobot"
    echo ""
    get_input "Enter your Telegram User ID" "" USER_ID

    if [[ -z "$USER_ID" ]]; then
        log_error "User ID is required"
        exit 1
    fi

    # Network Configuration
    echo ""
    echo -e "${CYAN}3. Network Configuration${NC}"
    get_input "Static IP for this Pi" "$CURRENT_IP" PI_IP
    get_input "Gateway IP" "$GATEWAY" GATEWAY_IP
    get_input "Network range" "$NETWORK_RANGE" NET_RANGE

    # DHCP Configuration
    echo ""
    echo -e "${CYAN}4. DHCP Configuration${NC}"
    DHCP_START="${NETWORK_PREFIX}.100"
    DHCP_END="${NETWORK_PREFIX}.250"

    if confirm "Enable DHCP server on Pi-hole?" "y"; then
        ENABLE_DHCP="true"
        get_input "DHCP range start" "$DHCP_START" DHCP_START
        get_input "DHCP range end" "$DHCP_END" DHCP_END
        log_warn "Remember to disable DHCP on your router!"
    else
        ENABLE_DHCP="false"
    fi

    # Pi-hole Password
    echo ""
    echo -e "${CYAN}5. Pi-hole Admin Password${NC}"
    get_secret "Enter Pi-hole admin password" PIHOLE_PASS

    if [[ -z "$PIHOLE_PASS" ]]; then
        PIHOLE_PASS=$(openssl rand -base64 12)
        log_info "Generated random password: $PIHOLE_PASS"
    fi

    # Timezone
    echo ""
    echo -e "${CYAN}6. Timezone${NC}"
    CURRENT_TZ=$(timedatectl show --property=Timezone --value 2>/dev/null || echo "Europe/Madrid")
    get_input "Timezone" "$CURRENT_TZ" TIMEZONE

    # VPN Configuration (optional)
    echo ""
    echo -e "${CYAN}7. VPN Configuration (Optional)${NC}"
    if confirm "Configure VPN split routing?" "n"; then
        ENABLE_VPN="true"
        log_info "VPN will be configured. You'll need to add your WireGuard config later."
    else
        ENABLE_VPN="false"
    fi

    log_success "Configuration complete"
}

create_env_file() {
    log_step "Creating Configuration Files"

    cat > "$INSTALL_DIR/.env" << EOF
# ============================================================================
# Pi Command Center Configuration
# Generated on $(date)
# ============================================================================

# Telegram Bot
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
AUTHORIZED_USERS=${USER_ID}

# Network
PI_IP=${PI_IP}
GATEWAY=${GATEWAY_IP}
NETWORK_RANGE=${NET_RANGE}

# DHCP
DHCP_ENABLED=${ENABLE_DHCP}
DHCP_START=${DHCP_START}
DHCP_END=${DHCP_END}

# Pi-hole
PIHOLE_PASSWORD=${PIHOLE_PASS}
PIHOLE_API_URL=http://localhost/admin/api.php

# System
TZ=${TIMEZONE}

# VPN (configure later if enabled)
VPN_ENABLED=${ENABLE_VPN}
EOF

    chmod 600 "$INSTALL_DIR/.env"
    log_success "Configuration saved to $INSTALL_DIR/.env"
}

setup_static_ip() {
    log_step "Configuring Static IP"

    if [[ "$IS_PI" != "true" ]]; then
        log_warn "Skipping static IP configuration (not a Raspberry Pi)"
        return
    fi

    if grep -q "static ip_address=${PI_IP}" /etc/dhcpcd.conf 2>/dev/null; then
        log_success "Static IP already configured"
        return
    fi

    if confirm "Configure static IP ${PI_IP}?" "y"; then
        sudo tee -a /etc/dhcpcd.conf > /dev/null << EOF

# Pi Command Center - Static IP
interface eth0
static ip_address=${PI_IP}/24
static routers=${GATEWAY_IP}
static domain_name_servers=127.0.0.1 1.1.1.1
EOF
        log_success "Static IP configured"
        NEED_REBOOT=true
    fi
}

setup_security() {
    log_step "Configuring Security"

    # SSH Hardening
    if confirm "Apply SSH hardening (disable password auth)?" "y"; then
        sudo tee /etc/ssh/sshd_config.d/pi-command-center.conf > /dev/null << EOF
# Pi Command Center SSH Hardening
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
MaxAuthTries 3
EOF
        sudo systemctl reload ssh 2>/dev/null || sudo systemctl reload sshd 2>/dev/null || true
        log_success "SSH hardening applied"
    fi

    # Fail2ban
    if confirm "Install and configure Fail2ban?" "y"; then
        sudo apt-get install -y fail2ban

        sudo tee /etc/fail2ban/jail.d/pi-command-center.conf > /dev/null << EOF
[sshd]
enabled = true
port = 22
filter = sshd
backend = systemd
maxretry = 3
bantime = 1h
findtime = 10m
ignoreip = 127.0.0.1/8 ${NET_RANGE}
EOF
        sudo systemctl enable fail2ban
        sudo systemctl restart fail2ban
        log_success "Fail2ban configured"
    fi

    # UFW Firewall
    if confirm "Configure UFW firewall?" "y"; then
        sudo apt-get install -y ufw

        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        sudo ufw allow from ${NET_RANGE} to any port 22   # SSH
        sudo ufw allow from ${NET_RANGE} to any port 53   # DNS
        sudo ufw allow 67/udp                              # DHCP
        sudo ufw allow from ${NET_RANGE} to any port 80   # Pi-hole admin
        sudo ufw allow from ${NET_RANGE} to any port 443  # HTTPS

        sudo ufw --force enable
        log_success "UFW firewall configured"
    fi
}

deploy_stack() {
    log_step "Deploying Docker Stack"

    cd "$INSTALL_DIR"

    log_info "Pulling Docker images (this may take a few minutes)..."
    $COMPOSE_CMD pull

    log_info "Starting services..."
    $COMPOSE_CMD up -d

    # Wait for services to be healthy
    log_info "Waiting for services to start..."
    sleep 30

    # Check status
    if $COMPOSE_CMD ps | grep -q "healthy\|running"; then
        log_success "All services started"
    else
        log_warn "Some services may not be running correctly"
        $COMPOSE_CMD ps
    fi
}

print_summary() {
    log_step "Installation Complete!"

    echo -e "${GREEN}"
    cat << EOF
╔═══════════════════════════════════════════════════════════════════════════╗
║                      INSTALLATION SUCCESSFUL!                             ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    echo -e "${WHITE}Your Pi Command Center is ready!${NC}"
    echo ""
    echo -e "${CYAN}Access Points:${NC}"
    echo -e "  • Pi-hole Admin:  ${WHITE}http://${PI_IP}/admin${NC}"
    echo -e "  • Password:       ${WHITE}${PIHOLE_PASS}${NC}"
    echo -e "  • Telegram Bot:   ${WHITE}Open Telegram and message your bot${NC}"
    echo ""
    echo -e "${CYAN}Useful Commands:${NC}"
    echo -e "  • View logs:      ${WHITE}cd $INSTALL_DIR && docker compose logs -f${NC}"
    echo -e "  • Restart:        ${WHITE}cd $INSTALL_DIR && docker compose restart${NC}"
    echo -e "  • Update:         ${WHITE}cd $INSTALL_DIR && docker compose pull && docker compose up -d${NC}"
    echo -e "  • Stop:           ${WHITE}cd $INSTALL_DIR && docker compose down${NC}"
    echo ""

    if [[ "$ENABLE_DHCP" == "true" ]]; then
        echo -e "${YELLOW}⚠️  IMPORTANT: Disable DHCP on your router!${NC}"
        echo -e "   Pi-hole will now serve DHCP on your network."
        echo ""
    fi

    if [[ "$NEED_REBOOT" == "true" ]]; then
        echo -e "${YELLOW}⚠️  A reboot is required to apply network changes.${NC}"
        if confirm "Reboot now?" "y"; then
            sudo reboot
        fi
    fi

    echo -e "${GREEN}Enjoy your privacy-first home network!${NC}"
    echo ""
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    print_banner
    check_root
    check_system
    detect_network
    install_dependencies
    install_docker
    clone_repository
    configure_installation
    create_env_file
    setup_static_ip
    setup_security
    deploy_stack
    print_summary
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-vpn)
            SKIP_VPN=true
            shift
            ;;
        --skip-hardening)
            SKIP_HARDENING=true
            shift
            ;;
        --unattended)
            UNATTENDED=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --no-vpn          Skip VPN configuration"
            echo "  --skip-hardening  Skip security hardening"
            echo "  --unattended      Non-interactive mode (requires env vars)"
            echo "  -h, --help        Show this help"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main
main
