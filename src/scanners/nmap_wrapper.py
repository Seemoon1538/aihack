import subprocess
import json
from typing import Dict, List
from src.core.logger import RealTimeLogger

class NmapWrapper:
    def __init__(self, logger: RealTimeLogger):
        self.logger = logger
        self.nmap_path = 'nmap' 

    def scan_ports(self, target: str, ports: str = '1-1024') -> Dict:
        cmd = [self.nmap_path, '-sV', '-p', ports, target, '-oX', '-']
        self.logger.info(f"Running Nmap: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Nmap failed: {result.stderr}")
            
            import nmap
            nm = nmap.PortScanner()
            nm.scan(target, ports)
            open_ports = []
            for host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    ports = nm[host][proto].keys()
                    for port in ports:
                        if nm[host][proto][port]['state'] == 'open':
                            open_ports.append({
                                'port': port,
                                'service': nm[host][proto][port]['name'],
                                'version': nm[host][proto][port].get('version', 'unknown')
                            })
            return {'open_ports': open_ports, 'host': target}
        except Exception as e:
            self.logger.error(f"Nmap error: {e}")
            return {'error': str(e)}

    def vuln_scan(self, target: str) -> List[Dict]:
        
        cmd = [self.nmap_path, '--script=vuln', target]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        vulns = []  
        for line in result.stdout.splitlines():
            if 'VULNERABLE' in line.upper():
                vulns.append({'vuln': line.strip()})
        return vulns