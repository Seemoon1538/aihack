
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List
from src.core.logger import RealTimeLogger

class VulnPredictor(nn.Module):
    def __init__(self, input_size: int = 15, hidden: int = 128, num_classes: int = 7):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden, batch_first=True)
        self.fc = nn.Linear(hidden, num_classes)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        _, (hn, _) = self.lstm(x)
        return self.softmax(self.fc(hn[-1]))

class Predictor:
    CLASSES = ['xss', 'csrf', 'sqli', 'rce', 'ssrf', 'open_port', 'waf']

    def __init__(self, config: Dict, logger: RealTimeLogger):
        self.config = config
        self.logger = logger
        self.model = VulnPredictor()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self._load_model()

    def _load_model(self):
        path = self.config['ai'].get('predictor_model', 'ai/model_vuln.pth')
        try:
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            self.logger.info("Предиктор загружен.")
        except:
            self.logger.warning("Модель не найдена — случайные веса.")

    def extract_features(self, response_text: str, status_code: int, url: str) -> List[float]:
        text = response_text.lower()
        return [
            len(response_text),
            response_text.count('<script'),
            response_text.count('alert('),
            response_text.count('union select'),
            response_text.count('error'),
            response_text.count('sql'),
            response_text.count('cf-ray'),
            response_text.count('onerror'),
            status_code / 1000,
            len(url),
            'onion' in url,
            'admin' in url,
            'login' in url,
            'api' in url,
            'json' in response_text
        ]

    def predict(self, features: List[float]) -> Dict[str, float]:
        x = torch.tensor([features], dtype=torch.float32).unsqueeze(1).to(self.device)
        probs = self.model(x).detach().cpu().numpy()[0]
        return {cls: float(p) for cls, p in zip(self.CLASSES, probs)}

    def train(self, features: List[float], label_idx: int):
        x = torch.tensor([features], dtype=torch.float32).unsqueeze(1).to(self.device)
        y = torch.tensor([label_idx], dtype=torch.long).to(self.device)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()
        for _ in range(10):
            out = self.model(x)
            loss = criterion(out, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        torch.save(self.model.state_dict(), self.config['ai']['predictor_model'])