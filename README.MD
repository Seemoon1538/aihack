# AIHACK v15.7 — AI-Powered Penetration Testing Framework

> **21 атака | ИИ-обучение | Автоматический отчёт | Proof-of-Concept**  
> **Разработчик:** [Твоё Имя] — Tech Lead | AI | Pentest | Blockchain  
> **GitHub:** [github.com/Seemoon1538/aihack](https://github.com/Seemoon1538/aihack)

---

## Что это?

**AIHACK** — это **автономный ИИ-пентестер**, который:
- Сканирует цель
- Атакует 16+ векторами
- **Учится** на успешных атаках
- Генерирует **профессиональный отчёт** с PoC

> **Цель:** автоматизировать рутинные проверки безопасности с помощью ИИ.

---



## Возможности

| Функция | Статус |
|--------|--------|
| Port Scanning | 12+ портов |
| SQL Injection | 5+ пейлоадов |
| XSS | Reflected |
| RCE | Command injection |
| Brute-force | MySQL, Redis, SSH, FTP |
| Token Hunter | JS + HTML |
| DDoS (тестовый) | |
| **AI Brain** | Учится, сохраняет |
| **Отчёт** | JSON + Markdown + `curl` PoC |

---

## Установка

```bash
git clone https://github.com/Seemoon1538/aihack.git
cd aihack
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt



python main.py \
  --config config.yaml \
  --target "http://dvwa.local/FUZZ" \
  --lhost "192.168.1.100" \
  --lport 4444
