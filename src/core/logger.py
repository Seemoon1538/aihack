
import logging
import sys
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.highlighter import ReprHighlighter
from pathlib import Path

console = Console()

class RealTimeLogger:
    """
    Нейронный логер v10.1
    → Rich в консоль
    → Полный лог в logs/attack_*.log
    → Уровни: DEBUG, INFO, WARNING, ERROR, CRITICAL
    → Авто-папка logs/
    """
    def __init__(self, level: str = 'INFO', log_file: Optional[str] = None):
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.highlighter = ReprHighlighter()
        
       
        rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=True,
            show_path=False,
            rich_tracebacks=True,
            markup=True,
            tracebacks_show_locals=True
        )
        rich_handler.setFormatter(logging.Formatter('%(message)s', datefmt='%H:%M:%S'))
        
       
        self.logger = logging.getLogger('NeuralHunter')
        self.logger.setLevel(self.level)
        self.logger.handlers.clear()  # Чистим дубли
        self.logger.addHandler(rich_handler)
        
         
        if log_file or True:  
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = log_file or f"attack_{timestamp}.log"
            file_handler = logging.FileHandler(log_dir / filename, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(file_handler)
            self.log_file = log_dir / filename
        
        self.info("[bold magenta]НЕЙРОННЫЙ ЛОГЕР v10.1 АКТИВИРОВАН[/bold magenta]")

    def log(self, message: str, level: str = 'INFO'):
        lvl = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(lvl, self.highlighter(message))

    def debug(self, message: str):    self.log(message, 'DEBUG')
    def info(self, message: str):     self.log(message, 'INFO')
    def warning(self, message: str):  self.log(message, 'WARNING')
    def error(self, message: str):    self.log(message, 'ERROR')
    def critical(self, message: str): self.log(message, 'CRITICAL')

    def success(self, message: str):
        self.log(f"[bold green]УСПЕХ: {message}[/bold green]", 'INFO')

    def breach(self, message: str):
        self.log(f"[bold red]БРЕШЬ: {message}[/bold red]", 'CRITICAL')

    def ai(self, message: str):
        self.log(f"[bold cyan]ИИ: {message}[/bold cyan]", 'INFO')

    def print_table(self, data: list, headers: list, title: str = "Neural Autopsy"):
        from rich.table import Table
        table = Table(title=title, show_header=True, header_style="bold magenta")
        for h in headers:
            table.add_column(h, style="cyan")
        for row in data:
            table.add_row(*[str(cell) for cell in row])
        console.print(table)