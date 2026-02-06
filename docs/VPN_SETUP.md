# VPN Split Routing Setup

Guía completa para configurar WireGuard con enrutamiento selectivo.

## Arquitectura

```
                    ┌─────────────────┐
                    │  VPN Server     │
                    │  (AWS/DO/etc)   │
                    │  IP: X.X.X.X    │
                    └────────▲────────┘
                             │ WireGuard
                             │ (wg-us)
┌─────────────────────────────────────────────────────┐
│                 Raspberry Pi                         │
│                                                      │
│  ┌─────────┐    ┌─────────┐    ┌─────────────────┐ │
│  │ Pi-hole │───▶│ ipset   │───▶│ iptables mangle │ │
│  │  (DNS)  │    │ (lista) │    │    (fwmark)     │ │
│  └─────────┘    └─────────┘    └────────┬────────┘ │
│                                          │          │
│                    ┌─────────────────────┼──────┐   │
│                    │                     │      │   │
│                    ▼                     ▼      │   │
│            ┌──────────────┐     ┌────────────┐  │   │
│            │ Tabla VPN    │     │ Tabla main │  │   │
│            │ (fwmark=51)  │     │ (default)  │  │   │
│            └──────────────┘     └────────────┘  │   │
│                    │                     │      │   │
│                    ▼                     ▼      │   │
│            ┌──────────────┐     ┌────────────┐  │   │
│            │   wg-us      │     │    eth0    │  │   │
│            │  (10.66.66.2)│     │(192.168.x) │  │   │
│            └──────────────┘     └────────────┘  │   │
└─────────────────────────────────────────────────────┘
                    │                     │
                    ▼                     ▼
              Internet (VPN)       Internet (ISP)
```

## Requisitos

### En el servidor VPN (AWS/DigitalOcean/etc)

```bash
# Instalar WireGuard
apt update && apt install wireguard -y

# Generar claves
wg genkey | tee /etc/wireguard/server_private.key | wg pubkey > /etc/wireguard/server_public.key

# Crear configuración
cat > /etc/wireguard/wg0.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/server_private.key)
Address = 10.66.66.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# Raspberry Pi
PublicKey = <PI_PUBLIC_KEY>
AllowedIPs = 10.66.66.2/32
EOF

# Habilitar IP forwarding
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Iniciar WireGuard
wg-quick up wg0
systemctl enable wg-quick@wg0
```

### En la Raspberry Pi

```bash
# Instalar WireGuard
apt update && apt install wireguard wireguard-tools -y

# Generar claves
wg genkey | tee /etc/wireguard/pi_private.key | wg pubkey > /etc/wireguard/pi_public.key
```

## Instalación del VPN Manager

### 1. Copiar el script

```bash
sudo cp scripts/vpn-manager /usr/local/bin/
sudo chmod +x /usr/local/bin/vpn-manager
```

### 2. Crear archivo de dominios

```bash
sudo touch /etc/pihole/vpn-domains.txt
```

### 3. Configuración de WireGuard

Crear `/etc/wireguard/wg-us.conf`:

```ini
[Interface]
PrivateKey = <PI_PRIVATE_KEY>
Address = 10.66.66.2/24

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = X.X.X.X:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

## Uso del VPN Manager

### Comandos disponibles

```bash
# Estado del sistema
sudo vpn-manager status

# Levantar/bajar VPN
sudo vpn-manager vpn-up
sudo vpn-manager vpn-down

# Modos de routing
sudo vpn-manager split-mode    # Solo dominios en lista
sudo vpn-manager all-vpn       # Todo por VPN

# Gestión de dominios
sudo vpn-manager add-domain netflix.com
sudo vpn-manager remove-domain netflix.com
sudo vpn-manager list-domains
```

### Salida del comando status

```
vpn:active
mode:split
domains:15
ip:3.235.240.175
```

## Cómo funciona el Split Routing

### 1. Resolución DNS (Pi-hole + dnsmasq)

Cuando Pi-hole resuelve un dominio en la lista:
```bash
# En /etc/dnsmasq.d/07-vpn-domains.conf
ipset=/netflix.com/vpn-domains
```

Las IPs resueltas se añaden automáticamente al ipset.

### 2. Marcado de paquetes (iptables mangle)

```bash
# Marcar paquetes hacia IPs en el ipset
iptables -t mangle -A OUTPUT -m set --match-set vpn-domains dst -j MARK --set-mark 51
iptables -t mangle -A PREROUTING -m set --match-set vpn-domains dst -j MARK --set-mark 51
```

### 3. Policy Routing

```bash
# Tabla de rutas para VPN
ip route add default dev wg-us table 51

# Regla: paquetes marcados usan tabla 51
ip rule add fwmark 51 table 51
```

## Modo Todo VPN

Cuando se activa "Todo VPN":

```bash
# Redirigir TODO el tráfico excepto red local
iptables -t mangle -A OUTPUT ! -d 192.168.0.0/24 -j MARK --set-mark 51
iptables -t mangle -A PREROUTING ! -d 192.168.0.0/24 -j MARK --set-mark 51
```

## Exclusiones Críticas

El VPN Manager siempre excluye:

1. **VPN Endpoint**: Para que el túnel no se enrute por sí mismo
2. **Telegram**: Para que el bot siga funcionando
3. **Red Local**: 192.168.0.0/24

```bash
# Ejemplos de exclusiones
iptables -t mangle -A OUTPUT -d 3.235.240.175 -j RETURN      # VPN endpoint
iptables -t mangle -A OUTPUT -d 149.154.160.0/20 -j RETURN   # Telegram
```

## Watchdog

El servicio de watchdog verifica cada 30 segundos:

```bash
# /etc/systemd/system/vpn-watchdog.timer
[Timer]
OnBootSec=60
OnUnitActiveSec=30
```

Si la VPN se cae, automáticamente:
1. Detecta que el handshake expiró (>180s)
2. Cambia a modo split
3. Intenta reconectar

## Troubleshooting

### VPN conectada pero sin tráfico

```bash
# Verificar rutas
ip route show table 51

# Verificar marca
iptables -t mangle -L -v -n

# Verificar ipset
ipset list vpn-domains
```

### Red muerta después de activar Todo VPN

```bash
# Emergencia: limpiar reglas
sudo vpn-manager split-mode

# O manualmente:
sudo iptables -t mangle -F
```

### Telegram no funciona con VPN

Verificar exclusiones de Telegram:
```bash
sudo iptables-save | grep 149.154
```

### Comprobar qué IP sale

```bash
# Debe mostrar IP del VPN
curl ipinfo.io/ip

# O la web completa
curl ipinfo.io
```

## Dominios Recomendados

```
# Streaming USA
netflix.com
hbomax.com
hulu.com
disneyplus.com

# Privacidad
reddit.com
twitter.com

# IA
openai.com
anthropic.com

# Torrents (legal disclaimer)
# Añade los que necesites
```

## Seguridad

- Las claves privadas deben tener permisos 600
- El archivo de configuración debe tener permisos 600
- Solo root puede ejecutar vpn-manager (sudo)
