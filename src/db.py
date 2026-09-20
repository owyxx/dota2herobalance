#Модуль для работы с PostgreSQL. Поддерживает подключение как локально, так и из Docker.

import os
import psycopg2
from contextlib import contextmanager
from .logger import setup_logger

logger = setup_logger()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'dota2db'),
    'user': os.getenv('DB_USER', 'dota2'),
    'password': os.getenv('DB_PASSWORD', 'dota2pass'),
}

logger.info(f"Параметры подключения к БД: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, db={DB_CONFIG['database']}")


@contextmanager
def get_connection():
    conn = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Ошибка PostgreSQL: {e}")
        raise

    finally:
        if conn:
            conn.close()