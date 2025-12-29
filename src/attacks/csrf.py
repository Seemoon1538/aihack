
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class CSRFModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "csrf", "success": False, "risk": 8}

        request = options.get('request')
        if not request:
            return result

        try:
            resp = await request('GET', target)
            if resp and "csrf" not in resp.text.lower() and "token" not in resp.text.lower():
                result.update({
                    "success": True,
                    "vulnerable_payload": "no_csrf_token",
                    "data_leaked": {"html": resp.text[:500]}
                })
                self.logger.breach("CSRF: нет токена")
                if self.brain:
                    self.brain.learn("csrf", target, "no_token", True)
        except:
            pass

        return result