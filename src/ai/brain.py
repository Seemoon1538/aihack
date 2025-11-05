# src/ai/brain.py — v15.5.2 — ПОЛНЫЙ
import asyncio
import json
import os
from typing import Dict, Any
from src.core.logger import RealTimeLogger

class NeuralBrain:
    def __init__(self, config: Dict):
        self.config = config
        self.memory_file = config.get("ai", {}).get("memory", "ai_brain.json")
        self.memory = self._load_memory()
        self.stats = {"successes": 0, "total": 0}

    def _load_memory(self) -> Dict:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def restore(self):
        self.stats["total"] = sum(len(v) for v in self.memory.values())
        self.stats["successes"] = sum(1 for attacks in self.memory.values() for a in attacks if a.get("success"))

    def learn(self, attack: str, target: str, payload: str, success: bool, data: str = ""):
        key = f"{attack}:{target}"
        if key not in self.memory:
            self.memory[key] = []
        self.memory[key].append({
            "payload": payload,
            "success": success,
            "data": data[:300],
            "timestamp": int(asyncio.get_event_loop().time())
        })
        self.stats["total"] += 1
        if success:
            self.stats["successes"] += 1
        self.save()

    def save(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    def get_stats(self) -> Dict:
        return self.stats

    @staticmethod
    def load(config: Dict) -> 'NeuralBrain':
        return NeuralBrain(config)