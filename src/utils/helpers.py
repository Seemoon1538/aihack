# src/utils/helpers.py
import shutil
import subprocess
import os
import socket
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.core.logger import RealTimeLogger

# Глобальный логгер
logger = RealTimeLogger('INFO')

class Helpers:
    """
    Вспомогательные функции: Tor, Hydra, sqlmap, IP, retries.
    """

    @staticmethod
    def get_target_ip(target: str) -> str:
        """
        Извлекает IP из URL или .onion
        """
        try:
            host = target.split('//')[-1].split('/')[0].split(':')[0]
            if host.endswith('.onion'):
                return host  # Tor сам разберётся
            return socket.gethostbyname(host)
        except Exception as e:
            raise ValueError(f"Не удалось получить IP для {target}: {e}")

    @staticmethod
    def init_tor_session() -> requests.Session:
        """
        Инициализирует сессию через Tor (для Onion).
        """
        try:
            from torrequest import TorRequest
            tr = TorRequest()
            tr.reset_identity()
            logger.log("Tor session initialized")
            return tr.session
        except ImportError:
            logger.log("torrequest not installed, falling back to requests")
            session = requests.Session()
            retry_strategy = Retry(total=3, backoff_factor=1)
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            return session

    @staticmethod
    def run_hydra(target: str, service: str = 'http-post-form', creds_file: str = None):
        """
        Запускает Hydra для brute-force.
        """
        if not shutil.which('hydra'):
            logger.log("Hydra не найдена в PATH. Установите: https://github.com/vanhauser-thc/thc-hydra")
            return None

        cmd = [
            'hydra',
            '-l', creds_file or 'admin',
            '-P', creds_file or 'passlist.txt',
            target,
            service
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            logger.log(f"Hydra result: {result.stdout}")
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.log("Hydra timeout")
            return None

    @staticmethod
    def run_sqlmap(target: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Запускает sqlmap с токеном, POST-данными, фразой и игнором 401.
        """
        if options is None:
            options = {}

        sqlmap_dir = 'sqlmap'
        if not os.path.exists(sqlmap_dir):
            logger.log("sqlmap не найден в папке sqlmap/ — выполните: git clone https://github.com/sqlmapproject/sqlmap.git sqlmap")
            return "ERROR: sqlmap not found"

        cmd = [
            'python', f'{sqlmap_dir}/sqlmap.py',
            '-u', target,
            '--batch',
            '--risk=3',
            '--level=5',
            '--random-agent',
            '--threads=5',
            '--ignore-code=401',
            '--force-ssl',
            '--flush-session'
        ]

        if options.get('auth_token'):
            cmd.extend(['--header', f'Authorization: Bearer {options["auth_token"]}'])

        if options.get('data'):
            cmd.extend(['--data', options['data']])
        else:
            cmd.extend(['--data', 'id=1'])

        if options.get('secret_phrase'):
            cmd.extend(['--string', options['secret_phrase']])

        try:
            logger.log(f"SQLMAP CMD: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            output = result.stdout + "\n" + result.stderr
            logger.log(f"sqlmap завершён: {len(output)} символов")
            return output
        except subprocess.TimeoutExpired:
            error = "sqlmap: таймаут (10 минут)"
            logger.log(error)
            return error
        except Exception as e:
            error = f"sqlmap ошибка: {e}"
            logger.log(error)
            return error

    @staticmethod
    def create_session_with_retries() -> requests.Session:
        """
        Создаёт сессию с повторными попытками.
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session