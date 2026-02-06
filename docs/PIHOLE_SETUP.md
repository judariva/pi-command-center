# Pi-hole + Unbound Setup

Guía completa para configurar Pi-hole con Unbound como DNS recursivo.

## Arquitectura

```
Cliente → Pi-hole (53) → Unbound (5335) → Root DNS Servers
```

**¿Por qué Unbound?**
- No dependes de DNS de terceros (Google, Cloudflare)
- Máxima privacidad: consultas directas a root servers
- Sin logs externos de tu actividad DNS

## Requisitos

- Docker & Docker Compose instalados
- IP estática configurada
- Puerto 53 disponible

## Instalación

### 1. Crear estructura de directorios

```bash
mkdir -p ~/pihole/unbound
cd ~/pihole
```

### 2. Configuración de Unbound

Crear `unbound/unbound.conf`:

```conf
server:
    verbosity: 0
    interface: 127.0.0.1
    port: 5335
    do-ip4: yes
    do-ip6: no
    do-udp: yes
    do-tcp: yes

    # Seguridad
    hide-identity: yes
    hide-version: yes
    harden-glue: yes
    harden-dnssec-stripped: yes
    use-caps-for-id: no

    # Cache
    cache-min-ttl: 3600
    cache-max-ttl: 86400
    prefetch: yes

    # Performance para Pi
    num-threads: 2
    msg-cache-slabs: 2
    rrset-cache-slabs: 2
    infra-cache-slabs: 2
    key-cache-slabs: 2

    # Tamaños de cache (optimizado para 1GB RAM)
    rrset-cache-size: 64m
    msg-cache-size: 32m

    # Root hints
    root-hints: "/opt/unbound/etc/unbound/root.hints"

    # DNSSEC
    auto-trust-anchor-file: "/opt/unbound/etc/unbound/root.key"

    # Acceso
    access-control: 127.0.0.0/8 allow
    access-control: 192.168.0.0/24 allow

    private-address: 192.168.0.0/16
    private-address: 172.16.0.0/12
    private-address: 10.0.0.0/8
```

### 3. Docker Compose

Crear `docker-compose.yml`:

```yaml
version: "3"

services:
  pihole:
    container_name: pihole
    image: pihole/pihole:latest
    network_mode: host
    environment:
      TZ: 'Europe/Madrid'
      WEBPASSWORD: 'tu_password_seguro'
      PIHOLE_DNS_: '127.0.0.1#5335'
      DHCP_ACTIVE: 'true'
      DHCP_START: '192.168.0.100'
      DHCP_END: '192.168.0.250'
      DHCP_ROUTER: '192.168.0.1'
      DHCP_LEASETIME: '24'
      PIHOLE_DOMAIN: 'lan'
      DNSMASQ_LISTENING: 'all'
    volumes:
      - './etc-pihole:/etc/pihole'
      - './etc-dnsmasq.d:/etc/dnsmasq.d'
    cap_add:
      - NET_ADMIN
    restart: unless-stopped
    depends_on:
      - unbound

  unbound:
    container_name: unbound
    image: mvance/unbound:latest
    network_mode: host
    volumes:
      - './unbound:/opt/unbound/etc/unbound'
    restart: unless-stopped
```

### 4. Descargar root hints

```bash
wget https://www.internic.net/domain/named.root -O unbound/root.hints
```

### 5. Iniciar servicios

```bash
docker-compose up -d
```

### 6. Verificar funcionamiento

```bash
# Test Unbound
dig google.com @127.0.0.1 -p 5335

# Test Pi-hole
dig google.com @PI_IP_REDACTED

# Test bloqueo
dig ads.google.com @PI_IP_REDACTED
# Debe devolver 0.0.0.0
```

## Configuración del Router

### Opción A: Pi-hole como DHCP (Recomendado)

1. Deshabilitar DHCP en el router
2. Pi-hole asigna IPs y DNS automáticamente
3. Todos los dispositivos usan Pi-hole

### Opción B: DNS en el Router

1. Mantener DHCP del router
2. Cambiar DNS del router a PI_IP_REDACTED
3. Algunos dispositivos pueden ignorarlo

## Mantenimiento

### Actualizar containers

```bash
cd ~/pihole
docker-compose pull
docker-compose up -d
```

### Actualizar root hints (mensual)

```bash
wget https://www.internic.net/domain/named.root -O ~/pihole/unbound/root.hints
docker restart unbound
```

### Ver logs

```bash
docker logs pihole -f
docker logs unbound -f
```

### Backup

```bash
tar -czf pihole-backup.tar.gz ~/pihole/etc-pihole ~/pihole/etc-dnsmasq.d
```

## Troubleshooting

### Pi-hole no resuelve

```bash
# Verificar Unbound
docker exec unbound drill google.com @127.0.0.1 -p 5335

# Verificar conectividad
docker exec pihole ping -c 3 127.0.0.1
```

### DHCP no asigna IPs

```bash
# Verificar que el router no tiene DHCP activo
# Verificar logs
docker logs pihole | grep -i dhcp
```

### Alto uso de CPU

Reducir cache en unbound.conf:
```conf
rrset-cache-size: 32m
msg-cache-size: 16m
```
