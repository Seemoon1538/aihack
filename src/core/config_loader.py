# zrc/core/config_loader.py — v15.1
import yaml
import os
from typing import Dict, Any
from pathlib import Path

class ConfigLoader:
    @staticmethod
    def load(config_path: str = 'config.yaml') -> Dict[str, Any]:
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Конфиг не найден: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        # === ОБЯЗАТЕЛЬНЫЕ ===
        required = ['global', 'target', 'attacks', 'ai']
        for key in required:
            if key not in config:
                raise ValueError(f"Отсутствует секция: {key}")

        # === ДЕФОЛТЫ ===
        defaults = {
            'global': {'log_level': 'INFO', 'max_threads': 50, 'timeout': 30},
            'attacks': {'dump_db': True, 'evolve_ai': True, 'report': {'json': True, 'md': True, 'html': True, 'pdf': True}},
            'tor': {'enabled': False, 'socks_port': 9050, 'control_port': 9051, 'renew_identity': True},
            'waf_bypass': {'enabled': True, 'delay': 1.5, 'user_agents': 'rotating'}
        }

        for section, vals in defaults.items():
            config.setdefault(section, {})
            if isinstance(vals, dict):
                for k, v in vals.items():
                    config[section].setdefault(k, v)

        return config