# src/reports/generator.py
import json
import os
from datetime import datetime
from typing import Dict, Any
from weasyprint import HTML
from jinja2 import Environment, select_autoescape

class ReportGenerator:
    """
    Генератор отчётов: PDF (weasyprint), JSON, HTML, Markdown
    v2.2 — БЕЗ wkhtmltopdf
    """
    def __init__(self, result: Dict[str, Any], config: Dict[str, Any]):
        self.result = result
        self.config = config
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _get_html_template(self) -> str:
        return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>AIPentest v2.2 — NEUROHACK</title>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: 'DejaVu Sans', Arial, sans-serif; margin: 0; padding: 20px; background: #f9f9f9; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        h1 { color: #d32f2f; font-size: 28px; margin-bottom: 10px; text-align: center; }
        h2 { color: #1976d2; border-bottom: 2px solid #eee; padding-bottom: 8px; }
        .success { color: #2e7d32; font-weight: bold; background: #e8f5e9; padding: 10px; border-radius: 6px; margin: 10px 0; }
        .warning { color: #f57c00; font-weight: bold; background: #fff3e0; padding: 10px; border-radius: 6px; margin: 10px 0; }
        .error { color: #c62828; font-weight: bold; background: #ffebee; padding: 10px; border-radius: 6px; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f5f5f5; font-weight: 600; }
        .footer { margin-top: 40px; font-size: 12px; color: #777; text-align: center; }
    </style>
</head>
<body>
<div class="container">
    <h1>AIPentest v2.2 — NEUROHACK</h1>
    <p><strong>Дата:</strong> {{ timestamp }}</p>
    <p><strong>Атака:</strong> {{ result.attack }}</p>
    <p><strong>Цель:</strong> {{ result.get('target', 'N/A') }}</p>

    {% if result.success %}
        <p class="success">УСПЕХ: Атака выполнена</p>
    {% else %}
        <p class="warning">ПРОВАЛ: Уязвимостей не найдено</p>
    {% endif %}

    {% if result.get('secrets') %}
        <h2>НАЙДЕННЫЕ СЕКРЕТЫ</h2>
        <ul>
        {% for secret in result.secrets %}
            <li class="error">{{ secret }}</li>
        {% endfor %}
        </ul>
    {% endif %}

    <h2>ДЕТАЛИ</h2>
    <table>
        <tr><th>Параметр</th><th>Значение</th></tr>
        {% for k, v in result.items() if k not in ['attack', 'success', 'secrets', 'recommendations', 'target'] %}
        <tr><td>{{ k }}</td><td>{{ v }}</td></tr>
        {% endfor %}
    </table>

    <h2>РЕКОМЕНДАЦИИ</h2>
    <ul>
    {% for rec in result.recommendations %}
        <li>{{ rec }}</li>
    {% endfor %}
    </ul>

    <div class="footer">
        AIPentest v2.2 — Самообучающийся AI-пентест агент | weasyprint
    </div>
</div>
</body>
</html>
        """

    def save_pdf(self, filepath: str):
        try:
            env = Environment(autoescape=select_autoescape())
            template = env.from_string(self._get_html_template())
            html_content = template.render(result=self.result, timestamp=self.timestamp)
            HTML(string=html_content).write_pdf(filepath)
            print(f"[green]PDF создан: {filepath}[/green]")
        except Exception as e:
            print(f"[red]PDF ошибка: {e}[/red]")

    def save_json(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.result, f, indent=2, ensure_ascii=False)
        print(f"[green]JSON создан: {filepath}[/green]")

    def save_html(self, filepath: str):
        env = Environment(autoescape=select_autoescape())
        template = env.from_string(self._get_html_template())
        html_content = template.render(result=self.result, timestamp=self.timestamp)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[green]HTML создан: {filepath}[/green]")

    def save_markdown(self, filepath: str):
        md_content = f"""
# AIPentest v2.2 — NEUROHACK

**Дата:** {self.timestamp}  
**Атака:** {self.result['attack']}  
**Цель:** {self.result.get('target', 'N/A')}

{'**УСПЕХ**: Атака выполнена' if self.result['success'] else '**ПРОВАЛ**: Уязвимостей не найдено'}

{'## НАЙДЕННЫЕ СЕКРЕТЫ' if self.result.get('secrets') else ''}
{''.join(f'- **{s}**' for s in self.result.get('secrets', []))}

## ДЕТАЛИ
| Параметр | Значение |
|----------|----------|
{''.join(f'| {k} | {v} |' for k, v in self.result.items() if k not in ['attack', 'success', 'secrets', 'recommendations', 'target'])}

## РЕКОМЕНДАЦИИ
{''.join(f'- {r}' for r in self.result['recommendations'])}
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content.strip())
        print(f"[green]MD создан: {filepath}[/green]")