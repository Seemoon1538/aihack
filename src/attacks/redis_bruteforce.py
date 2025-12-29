
import asyncio
import redis.asyncio as redis
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class RedisBruteforceModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "redis_bruteforce", "success": False, "risk": 8}

        host = options['context']['target'].split('/')[2].split(':')[0]
        port = 6379

        self.logger.info(f"REDIS BRUTEFORCE → {host}:{port}")

        try:
            r = await redis.Redis(host=host, port=port, socket_timeout=3)
            await r.ping()
            result.update({
                "success": True,
                "vulnerable_payload": "no_auth",
                "data_leaked": {"status": "unauthenticated"}
            })
            self.logger.breach("REDIS: NO AUTH")
            if self.brain:
                self.brain.learn("redis_bruteforce", target, "no_auth", True)
            await r.close()
            return result
        except:
            return result