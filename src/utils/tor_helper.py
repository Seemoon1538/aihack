
import httpx
import asyncio
from stem import Signal
from stem.control import Controller
from src.core.logger import RealTimeLogger

class TorClient:
    def __init__(self, config: dict, logger: RealTimeLogger):
        self.config = config
        self.logger = logger
        self.proxy = f"socks5h://127.0.0.1:{config['tor'].get('socks_port', 9050)}" if config.get('tor', {}).get('enabled') else None
        self.control_port = config.get('tor', {}).get('control_port', 9051)

    async def renew_identity(self):
        if not self.config.get('tor', {}).get('enabled') or not self.config.get('tor', {}).get('renew_identity'):
            return
        try:
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
            self.logger.info("Tor: новый IP")
            await asyncio.sleep(3)
        except Exception as e:
            self.logger.error(f"Tor renew failed: {e}")

    async def request(self, method: str, url: str, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

        transport = httpx.AsyncHTTPTransport(proxy=self.proxy) if self.proxy else None

        async with httpx.AsyncClient(transport=transport, verify=False, timeout=30) as client:
            resp = await client.request(method, url, headers=headers, **kwargs)
            self.logger.log(f"[{method}] {url} → {resp.status_code}")
            return resp