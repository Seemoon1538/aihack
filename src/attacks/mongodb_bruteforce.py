# src/attacks/mongodb_bruteforce.py — v15.3
import asyncio
from pymongo import MongoClient
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class MongoDBBruteforceModule:
    def __init__(self, logger: RealTimeLogger, brain=None, config: Dict = None):
        self.logger = logger
        self.brain = brain
        self.config = config or {}

    async def attack(self, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
        result = {"attack": "mongodb_bruteforce", "success": False, "risk": 8}

        host = options['context']['target'].split('/')[2].split(':')[0]
        port = 27017

        self.logger.info(f"MONGODB BRUTEFORCE → {host}:{port}")

        try:
            client = await asyncio.to_thread(MongoClient, host, port, serverSelectionTimeoutMS=3000)
            await asyncio.to_thread(client.admin.command, 'ping')
            result.update({
                "success": True,
                "vulnerable_payload": "no_auth",
                "data_leaked": {"status": "unauthenticated"}
            })
            self.logger.breach("MONGODB: NO AUTH")
            if self.brain:
                self.brain.learn("mongodb_bruteforce", target, "no_auth", True)
            client.close()
            return result
        except:
            return result