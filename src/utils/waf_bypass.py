# zrc/utils/waf_bypass.py — v15.1
import random
import time
from typing import Dict, List

WAF_SIGNATURES = {
    "cloudflare": ["cf-ray", "checking your browser"],
    "akamai": ["reference #"],
    "sucuri": ["sucuri"],
    "aws_waf": ["awswaf"]
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

class WAFBypass:
    def __init__(self, config: dict):
        self.config = config
        self.delay = config['waf_bypass'].get('delay', 1.5)

    def detect(self, text: str) -> str:
        text = text.lower()
        for waf, signs in WAF_SIGNATURES.items():
            if any(s in text for s in signs):
                return waf
        return "unknown"

    def get_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }
        for h in self.config['waf_bypass'].get('headers', []):
            k, v = h.split(": ", 1)
            headers[k] = v
        return headers

    def delay(self):
        time.sleep(random.uniform(0.5, self.delay))