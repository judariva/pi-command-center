"""Servicio de monitoreo del sistema."""
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
import psutil
import requests

from utils.shell import run_sync, run_async
from utils.formatting import format_bytes, format_uptime

logger = logging.getLogger(__name__)


@dataclass
class SystemStats:
    """Estadísticas del sistema."""
    cpu_percent: float
    memory_used: int
    memory_total: int
    memory_percent: float
    disk_used: int
    disk_total: int
    disk_percent: float
    temperature: float
    uptime_seconds: int
    load_avg: tuple


@dataclass
class ContainerInfo:
    """Información de contenedor Docker."""
    name: str
    status: str
    health: str


@dataclass
class PublicIPInfo:
    """Información de IP pública."""
    ip: str
    country: str
    country_code: str
    city: str
    isp: str


class SystemService:
    """Servicio para monitoreo del sistema."""

    def get_stats(self) -> Optional[SystemStats]:
        """Obtener estadísticas del sistema."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.5)

            # Memoria
            mem = psutil.virtual_memory()

            # Disco
            disk = psutil.disk_usage('/')

            # Temperatura
            temperature = self._get_temperature()

            # Uptime
            uptime = self._get_uptime()

            # Load average
            load_avg = psutil.getloadavg()

            return SystemStats(
                cpu_percent=cpu_percent,
                memory_used=mem.used,
                memory_total=mem.total,
                memory_percent=mem.percent,
                disk_used=disk.used,
                disk_total=disk.total,
                disk_percent=disk.percent,
                temperature=temperature,
                uptime_seconds=uptime,
                load_avg=load_avg
            )
        except Exception as e:
            logger.error(f"Error obteniendo stats del sistema: {e}")
            return None

    def _get_temperature(self) -> float:
        """Obtener temperatura del CPU."""
        try:
            stdout, _, code = run_sync("cat /sys/class/thermal/thermal_zone0/temp")
            if code == 0 and stdout:
                return int(stdout) / 1000.0
        except:
            pass
        return 0.0

    def _get_uptime(self) -> int:
        """Obtener uptime en segundos."""
        try:
            stdout, _, code = run_sync("cat /proc/uptime")
            if code == 0 and stdout:
                return int(float(stdout.split()[0]))
        except:
            pass
        return 0

    def get_containers(self) -> List[ContainerInfo]:
        """Obtener lista de contenedores Docker."""
        containers = []
        try:
            stdout, _, code = run_sync(
                "docker ps -a --format '{{.Names}}|{{.Status}}' 2>/dev/null"
            )
            if code == 0 and stdout:
                for line in stdout.split('\n'):
                    if '|' in line:
                        parts = line.split('|')
                        name = parts[0]
                        status = parts[1] if len(parts) > 1 else "unknown"

                        # Determinar salud
                        health = "unknown"
                        if "(healthy)" in status:
                            health = "healthy"
                        elif "(unhealthy)" in status:
                            health = "unhealthy"
                        elif "Up" in status:
                            health = "running"
                        elif "Exited" in status:
                            health = "stopped"

                        containers.append(ContainerInfo(
                            name=name,
                            status=status,
                            health=health
                        ))
        except Exception as e:
            logger.error(f"Error obteniendo contenedores: {e}")

        return containers

    def get_public_ip(self) -> Optional[PublicIPInfo]:
        """Obtener información de IP pública."""
        try:
            response = requests.get(
                "http://ip-api.com/json/?fields=status,country,countryCode,city,isp,query",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return PublicIPInfo(
                        ip=data.get("query", "N/A"),
                        country=data.get("country", "N/A"),
                        country_code=data.get("countryCode", ""),
                        city=data.get("city", "N/A"),
                        isp=data.get("isp", "N/A")
                    )
        except Exception as e:
            logger.error(f"Error obteniendo IP pública: {e}")
        return None

    async def run_speedtest(self) -> Dict[str, str]:
        """Ejecutar speedtest (async porque tarda)."""
        stdout, stderr, code = await run_async(
            "speedtest-cli --simple 2>/dev/null",
            timeout=90
        )

        if code != 0 or not stdout:
            return {"error": "Speedtest no disponible o timeout"}

        result = {}
        for line in stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip().lower()] = value.strip()

        return result

    def get_country_flag(self, country_code: str) -> str:
        """Convertir código de país a emoji bandera."""
        if not country_code or len(country_code) != 2:
            return "🌍"
        return ''.join(chr(ord(c) + 127397) for c in country_code.upper())

    def format_stats_message(self, stats: SystemStats) -> str:
        """Formatea estadísticas para mensaje."""
        from utils.formatting import get_temp_icon

        temp_icon = get_temp_icon(stats.temperature)
        mem_mb = stats.memory_used // (1024 * 1024)
        mem_total_mb = stats.memory_total // (1024 * 1024)
        disk_gb = stats.disk_used // (1024 ** 3)
        disk_total_gb = stats.disk_total // (1024 ** 3)

        return f"""{temp_icon} *Temperatura:* {stats.temperature:.1f}°C
💻 *CPU:* {stats.cpu_percent:.1f}%
💾 *RAM:* {mem_mb}MB / {mem_total_mb}MB ({stats.memory_percent:.1f}%)
💿 *Disco:* {disk_gb}GB / {disk_total_gb}GB ({stats.disk_percent:.1f}%)
⏱️ *Uptime:* {format_uptime(stats.uptime_seconds)}
📊 *Load:* {stats.load_avg[0]:.2f}, {stats.load_avg[1]:.2f}, {stats.load_avg[2]:.2f}"""
