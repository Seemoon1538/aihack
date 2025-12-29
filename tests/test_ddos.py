import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src.attacks.ddos import DDoSModule
from src.core.config_loader import ConfigLoader

@pytest.fixture
def config():
    return ConfigLoader.load('config.yaml')  

@pytest.fixture
def logger():
    class MockLogger:
        def info(self, msg): pass
        def error(self, msg): pass
    return MockLogger()

@pytest.mark.asyncio
async def test_ddos_attack(config, logger):
    module = DDoSModule(config, logger)
    options = {'load': '50%'}
    with patch('src.attacks.ddos.send') as mock_send:
        result = await module.attack('http://test.com', options)
        assert result['success'] is not None
        mock_send.assert_called()

@pytest.mark.asyncio
async def test_verify_downtime(config, logger):
    module = DDoSModule(config, logger)
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 1  
        success = await module._verify_downtime('http://test.com')
        assert success is True