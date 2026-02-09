"""
Настройка логирования для проекта.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "jobpulse") -> logging.Logger:
    """Настроить и вернуть логгер.

    Args:
        name: Имя логгера

    Returns:
        Настроенный экземпляр логгера
    """
    # Создаём папку для логов
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Формат времени для имени файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"jobpulse_{timestamp}.log"

    # Создаём логгер
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Удаляем существующие обработчики (чтобы избежать дублирования)
    logger.handlers.clear()

    # Форматтер для консоли
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )

    # Форматтер для файла (более подробный)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Обработчик для консоли (только INFO и выше)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Обработчик для файла (все уровни)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Добавляем обработчики
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Глобальный экземпляр логгера
logger = setup_logger()
