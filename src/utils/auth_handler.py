# src/utils/auth_handler.py
from typing import Optional, Dict, Any

class AuthHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def get_headers(self, mode: str = 'unauth', token: Optional[str] = None) -> Dict:
        headers = {'Content-Type': 'application/json'}
        if mode == 'auth':
            token = token or self.config['attacks'].get('csrf', {}).get('auth_token')
            if token:
                headers['Authorization'] = f'Bearer {token}'
        return headers