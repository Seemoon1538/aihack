import schedule
import time
import asyncio
from typing import Callable

class AIPScheduler:
    def __init__(self, pause_hours: int = 1):
        self.pause_hours = pause_hours
        self.jobs = []

    def add_job(self, job: Callable, interval_hours: int):
        schedule.every(interval_hours).hours.do(lambda: asyncio.create_task(job()))

    def run_forever(self):
        while True:
            schedule.run_pending()
            time.sleep(self.pause_hours * 3600)  # Pause

# Usage in evolution.py: scheduler = AIPScheduler(config['ai']['training']['pause_hours'])
# scheduler.add_job(evolve_generation, 1)
# scheduler.run_forever()