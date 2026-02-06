"""Servicio de interacción con Pi-hole API v6."""
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
import requests
from requests.exceptions import RequestException

from config import config

logger = logging.getLogger(__name__)


@dataclass
class PiholeStats:
    """Estadísticas de Pi-hole."""
    total_queries: int = 0
    blocked_queries: int = 0
    percent_blocked: float = 0.0
    domains_on_blocklist: int = 0
    status: str = "unknown"


@dataclass
class TopDomain:
    """Dominio en lista top."""
    domain: str
    count: int


@dataclass
class TopClient:
    """Cliente en lista top."""
    ip: str
    name: str
    count: int


class PiholeService:
    """Servicio para interactuar con Pi-hole API v6."""

    def __init__(self):
        self._session: Optional[str] = None
        self._api_base = config.PIHOLE_API

    def _authenticate(self) -> bool:
        """Autenticarse con la API."""
        try:
            response = requests.post(
                f"{self._api_base}/auth",
                json={"password": config.PIHOLE_PASSWORD},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self._session = data.get("session", {}).get("sid", "")
                return bool(self._session)
        except RequestException as e:
            logger.error(f"Error autenticando con Pi-hole: {e}")
        return False

    def _get_headers(self) -> Dict[str, str]:
        """Devuelve headers con sesión."""
        if not self._session:
            self._authenticate()
        return {"sid": self._session} if self._session else {}

    def _api_get(self, endpoint: str) -> Optional[dict]:
        """GET request a la API."""
        try:
            response = requests.get(
                f"{self._api_base}/{endpoint}",
                headers=self._get_headers(),
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Re-autenticar y reintentar
                if self._authenticate():
                    response = requests.get(
                        f"{self._api_base}/{endpoint}",
                        headers=self._get_headers(),
                        timeout=5
                    )
                    if response.status_code == 200:
                        return response.json()
        except RequestException as e:
            logger.error(f"Error en API Pi-hole ({endpoint}): {e}")
        return None

    def get_stats(self) -> Optional[PiholeStats]:
        """Obtener estadísticas generales."""
        data = self._api_get("stats/summary")
        if not data:
            return None

        queries = data.get("queries", {})
        gravity = data.get("gravity", {})

        total = queries.get("total", 0)
        blocked = queries.get("blocked", 0)

        return PiholeStats(
            total_queries=total,
            blocked_queries=blocked,
            percent_blocked=(blocked / total * 100) if total > 0 else 0,
            domains_on_blocklist=gravity.get("domains_being_blocked", 0),
            status="enabled" if data.get("status") != "disabled" else "disabled"
        )

    def get_top_blocked(self, count: int = 5) -> List[TopDomain]:
        """Obtener top dominios bloqueados."""
        data = self._api_get(f"stats/top_domains?blocked=true&count={count}")
        if not data:
            return []

        domains = data.get("domains", [])
        return [
            TopDomain(domain=d.get("domain", ""), count=d.get("count", 0))
            for d in domains
        ]

    def get_top_permitted(self, count: int = 5) -> List[TopDomain]:
        """Obtener top dominios permitidos."""
        data = self._api_get(f"stats/top_domains?blocked=false&count={count}")
        if not data:
            return []

        domains = data.get("domains", [])
        return [
            TopDomain(domain=d.get("domain", ""), count=d.get("count", 0))
            for d in domains
        ]

    def get_top_clients(self, count: int = 5) -> List[TopClient]:
        """Obtener top clientes."""
        data = self._api_get(f"stats/top_clients?count={count}")
        if not data:
            return []

        clients = data.get("clients", [])
        return [
            TopClient(
                ip=c.get("ip", ""),
                name=c.get("name", "") or c.get("ip", ""),
                count=c.get("count", 0)
            )
            for c in clients
        ]

    def disable(self, seconds: int = 300) -> bool:
        """Deshabilitar Pi-hole por N segundos."""
        try:
            response = requests.post(
                f"{self._api_base}/dns/blocking",
                headers=self._get_headers(),
                json={"blocking": False, "timer": seconds},
                timeout=5
            )
            return response.status_code == 200
        except RequestException as e:
            logger.error(f"Error deshabilitando Pi-hole: {e}")
            return False

    def enable(self) -> bool:
        """Habilitar Pi-hole."""
        try:
            response = requests.post(
                f"{self._api_base}/dns/blocking",
                headers=self._get_headers(),
                json={"blocking": True},
                timeout=5
            )
            return response.status_code == 200
        except RequestException as e:
            logger.error(f"Error habilitando Pi-hole: {e}")
            return False

    def block_domain(self, domain: str) -> bool:
        """Añadir dominio a lista negra."""
        try:
            response = requests.post(
                f"{self._api_base}/domains/deny/exact",
                headers=self._get_headers(),
                json={"domain": domain},
                timeout=5
            )
            return response.status_code in (200, 201)
        except RequestException as e:
            logger.error(f"Error bloqueando dominio: {e}")
            return False

    def allow_domain(self, domain: str) -> bool:
        """Añadir dominio a lista blanca."""
        try:
            response = requests.post(
                f"{self._api_base}/domains/allow/exact",
                headers=self._get_headers(),
                json={"domain": domain},
                timeout=5
            )
            return response.status_code in (200, 201)
        except RequestException as e:
            logger.error(f"Error permitiendo dominio: {e}")
            return False

    def get_status(self) -> Dict[str, any]:
        """Obtener estado general de Pi-hole."""
        stats = self.get_stats()
        if not stats:
            return {"online": False, "error": "No se pudo conectar"}

        return {
            "online": True,
            "blocking": stats.status == "enabled",
            "queries_today": stats.total_queries,
            "blocked_today": stats.blocked_queries,
            "percent_blocked": stats.percent_blocked,
            "domains_blocked": stats.domains_on_blocklist
        }
