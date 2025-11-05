import pytest
import torch
from src.ai.evolution import EvolutionEngine, SimpleRLModel
from src.core.config_loader import ConfigLoader

@pytest.fixture
def config():
    return {'ai': {'evolution': {'generations': 10, 'mutation_rate': 0.1, 'reward_threshold': 0.5}}}

def test_model_forward(config):
    model = SimpleRLModel()
    x = torch.tensor([[1.0]*10])
    out = model(x)
    assert out.shape == (1, 5)
    assert torch.allclose(out.sum(dim=1), torch.tensor([1.0]))

@pytest.mark.asyncio
async def test_evolve_generation(config):
    engine = EvolutionEngine(config['ai']['evolution'])
    target = 'http://test.com'
    success = await engine.evolve_generation(target)
    assert len(engine.population) == 100  # Unchanged size
    assert isinstance(success, bool)