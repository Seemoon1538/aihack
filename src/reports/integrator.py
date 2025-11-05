import requests
import json
from typing import Dict
from src.core.logger import RealTimeLogger

class Integrator:
    def __init__(self, config: Dict, logger: RealTimeLogger):
        self.config = config
        self.logger = logger
        self.burp_proxy = {'http': f"http://{config['integrations']['burp_proxy']}", 'https': f"http://{config['integrations']['burp_proxy']}"}
        self.zap_url = config['integrations']['zap_api']

    def send_to_burp(self, report_data: Dict):
        """Proxy traffic through Burp for passive scan"""
        session = requests.Session()
        session.proxies = self.burp_proxy
        # Example: Send a request to trigger scan
        resp = session.get(report_data['target'])
        self.logger.info(f"Proxied through Burp: {resp.status_code}")
        # Burp API: If Burp has REST API enabled, POST /scan
        try:
            burp_api = "http://127.0.0.1:8080"  # Assume
            requests.post(f"{burp_api}/v0.1/scan", json=report_data)
        except:
            self.logger.warning("Burp API not available; using proxy only.")

    def send_to_zap(self, report_data: Dict):
        """ZAP API integration"""
        headers = {'Accept': 'application/json'}
        # Start spider/scan
        spider_id = requests.post(f"{self.zap_url}/spider/scan", json={'url': report_data['target']}, headers=headers).json()['scan']
        # Wait for completion (poll)
        import time
        while True:
            status = requests.get(f"{self.zap_url}/spider/status/{spider_id}", headers=headers).json()['status']
            if status == '100':
                break
            time.sleep(5)
        # Get alerts
        alerts = requests.get(f"{self.zap_url}/core/getAlerts", params={'baseurl': report_data['target']}, headers=headers).json()
        report_data['zap_alerts'] = alerts
        self.logger.info(f"ZAP scan complete: {len(alerts)} alerts")
        return report_data