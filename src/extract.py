#Модуль Extract: получение данных из OpenDota API.

import time
import requests
from .config import API_URL
from .logger import setup_logger

logger = setup_logger()

MAX_RETRIES = 3          # Сколько раз пробовать
RETRY_DELAY = 10         # Пауза между попытками (секунды)


def fetch_hero_stats() -> list:
    logger.info(f"Запрос к OpenDota API: {API_URL}")
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(API_URL, timeout=30)

            if response.status_code >= 500:
                logger.warning(f"Попытка {attempt}/{MAX_RETRIES}: сервер вернул {response.status_code}")

                if attempt < MAX_RETRIES:
                    logger.info(f"Ждём {RETRY_DELAY} секунд и пробуем снова...")
                    time.sleep(RETRY_DELAY)
                    continue

                else:
                    response.raise_for_status()
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"Получено героев: {len(data)}")
            return data
            
        except requests.RequestException as e:
            logger.warning(f"Попытка {attempt}/{MAX_RETRIES}: ошибка соединения — {e}")

            if attempt < MAX_RETRIES:
                logger.info(f"Ждём {RETRY_DELAY} секунд и пробуем снова...")
                time.sleep(RETRY_DELAY)

            else:
                logger.error("Все попытки исчерпаны. Сервер OpenDota недоступен.")
                raise


if __name__ == "__main__":
    data = fetch_hero_stats()
    print(f"\nПервый герой: {data[0]['localized_name']}")
    print(f"Всего героев: {len(data)}")