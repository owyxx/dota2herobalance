#Адаптированная версия main.py для запуска внутри Airflow.

import sys
sys.path.insert(0, '/opt/airflow')

from src.extract import fetch_hero_stats
from src.transform import (
    calculate_hero_metrics,
    calculate_role_metrics,
    calculate_attr_metrics,
    find_best_per_position,
    find_top_by_picks_per_position,
    calculate_trends
)
from src.load import save_all
from src.quality_check import run_all_checks
from src.logger import setup_logger

logger = setup_logger()


def main():
    logger.info("=" * 60)
    logger.info("ЗАПУСК ETL-ПАЙПЛАЙНА DOTA 2 (AIRFLOW)")
    logger.info("=" * 60)
    
    data = fetch_hero_stats()
    
    heroes = calculate_hero_metrics(data)
    roles = calculate_role_metrics(data)
    attrs = calculate_attr_metrics(data)
    positions_best = find_best_per_position(data)
    positions_top = find_top_by_picks_per_position(data)
    
    heroes_sorted = sorted(heroes, key=lambda x: x['pub_winrate'], reverse=True)
    top_5_names = [h['name'] for h in heroes_sorted[:5]]
    trends = calculate_trends(data, top_5_names)
    
    quality_results = run_all_checks(heroes, roles, attrs)
    
    save_all(heroes, roles, attrs, positions_best, positions_top, trends)
    
    logger.info("=" * 60)
    logger.info("ПАЙПЛАЙН ЗАВЕРШЁН УСПЕШНО")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()