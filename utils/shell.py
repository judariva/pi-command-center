"""Ejecución segura de comandos shell."""
import asyncio
import subprocess
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


async def run_async(
    cmd: str,
    timeout: int = 30,
    shell: bool = True
) -> Tuple[str, str, int]:
    """
    Ejecuta comando de forma asíncrona.

    Returns:
        Tuple[stdout, stderr, returncode]
    """
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout
        )
        return (
            stdout.decode('utf-8', errors='replace').strip(),
            stderr.decode('utf-8', errors='replace').strip(),
            proc.returncode or 0
        )
    except asyncio.TimeoutError:
        logger.warning(f"Timeout ejecutando: {cmd[:50]}")
        try:
            proc.kill()
        except:
            pass
        return "", "Timeout", -1
    except Exception as e:
        logger.error(f"Error ejecutando {cmd[:50]}: {e}")
        return "", str(e), -1


def run_sync(cmd: str, timeout: int = 10) -> Tuple[str, str, int]:
    """
    Ejecuta comando de forma síncrona.

    Returns:
        Tuple[stdout, stderr, returncode]
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return (
            result.stdout.strip(),
            result.stderr.strip(),
            result.returncode
        )
    except subprocess.TimeoutExpired:
        return "", "Timeout", -1
    except Exception as e:
        return "", str(e), -1
