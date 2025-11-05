# src/attacks/port_scan.py — v15.2.2
import asyncio
import socket
from typing import List, Dict, Any
from src.core.logger import RealTimeLogger
from src.utils.tor_helper import TorClient

COMMON_PORTS = [21, 22, 80, 443, 8080, 8443, 3306, 5432, 6379, 27017, 9200, 11211]

class PortScanModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}
        self.tor = TorClient(self.config, logger)

    async def _scan_port(self, host: str, port: int) -> bool:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=3
            )
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "attack": "port_scan",
            "success": False,
            "open_ports": [],
            "risk": 6
        }

        try:
            from urllib.parse import urlparse
            host = urlparse(target).hostname
            if not host:
                return result

            self.logger.info(f"PORT SCAN → {target}")

            tasks = [self._scan_port(host, port) for port in COMMON_PORTS]
            results = await asyncio.gather(*tasks)

            open_ports = [port for port, open in zip(COMMON_PORTS, results) if open]
            for port in open_ports:
                self.logger.info(f"ПОРТ ОТКРЫТ: {port}")

            result.update({
                "success": bool(open_ports),
                "open_ports": open_ports
            })

            if self.brain and open_ports:
                self.brain.learn("port_scan", target, f"ports:{','.join(map(str, open_ports))}", True)

        except Exception as e:
            self.logger.error(f"PortScan error: {e}")

        return result