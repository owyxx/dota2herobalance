#Настройка логирования для ETL-пайплайна. Логи пишутся и в консоль, и в файл.

import logging
import os
from .config import LOGS_DIR, LOG_FILE


def setup_logger(name: str = "dota2_etl") -> logging.Logger:
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger