#Главный модуль ETL-пайплайна для анализа баланса Dota 2.

from datetime import datetime
from tabulate import tabulate

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
from src.config import ATTR_TRANSLATIONS
from src.logger import setup_logger

logger = setup_logger()

TABLE_FORMAT = 'grid'


def print_heroes_table(heroes_sorted, title, n=5, reverse=False):
    if reverse:
        selected = heroes_sorted[-n:]
    else:
        selected = heroes_sorted[:n]
    
    table = []
    for h in selected:
        table.append([
            h['name'],
            f"{h['pub_winrate']:.2f}%",
            f"{h['pickrate']:.2f}%"
        ])
    
    print(f"\n=== {title} ===")
    print(tabulate(table, headers=['Герой', 'Winrate (pub)', 'Pickrate'], tablefmt=TABLE_FORMAT))


def print_pro_table(pro_sorted, n=5, reverse=False):
    if not pro_sorted:
        return
    
    actual_n = min(n, len(pro_sorted))
    
    if reverse:
        selected = pro_sorted[-actual_n:]
    else:
        selected = pro_sorted[:actual_n]
    
    table = []
    for h in selected:
        table.append([
            h['name'],
            f"{h['pro_winrate']:.2f}%",
            h['pro_pick']
        ])
    
    title = f"ТОП-{actual_n} {'СЛАБЫХ' if reverse else 'СИЛЬНЫХ'} В ПРО"
    print(f"\n=== {title} ===")
    print(tabulate(table, headers=['Герой', 'Winrate (pro)', 'Матчей в про'], tablefmt=TABLE_FORMAT))


def print_best_positions(positions_best):
    table = []
    for p in positions_best:
        table.append([
            p['position'],
            p['name'],
            f"{p['winrate']:.2f}%",
            f"{p['share']:.1f}%"
        ])
    
    print("\n=== ЛУЧШИЙ ГЕРОЙ НА КАЖДУЮ ПОЗИЦИЮ ===")
    print(tabulate(
        table,
        headers=['Позиция', 'Герой', 'Winrate', 'Доля пиков'],
        tablefmt=TABLE_FORMAT
    ))


def print_roles_table(roles):
    table = []
    for r in roles:
        table.append([
            r['role'],
            f"{r['avg_winrate']:.2f}%",
            r['best_hero'],
            f"{r['best_winrate']:.2f}%",
            r['worst_hero'],
            f"{r['worst_winrate']:.2f}%",
            f"{r['spread']:.2f}%"
        ])
    
    print("\n=== СИЛА РОЛЕЙ ===")
    print(tabulate(
        table,
        headers=['Роль', 'Avg winrate', 'Лучший герой', 'Winrate', 'Худший герой', 'Winrate', 'Разброс'],
        tablefmt=TABLE_FORMAT
    ))


def print_attrs_table(attrs):
    table = []
    for a in attrs:
        attr_ru = ATTR_TRANSLATIONS.get(a['attr'], a['attr'])
        table.append([
            attr_ru,
            f"{a['avg_winrate']:.2f}%",
            a['best_hero'],
            f"{a['best_winrate']:.2f}%",
            a['worst_hero'],
            f"{a['worst_winrate']:.2f}%",
            f"{a['spread']:.2f}%"
        ])
    
    print("\n=== СИЛА АТРИБУТОВ ===")
    print(tabulate(
        table,
        headers=['Атрибут', 'Avg winrate', 'Лучший герой', 'Winrate', 'Худший герой', 'Winrate', 'Разброс'],
        tablefmt=TABLE_FORMAT
    ))


def print_trends(trends):
    table = []
    for t in trends:
        first = t['trend'][0]['winrate']
        last = t['trend'][-1]['winrate']
        change = last - first
        if change > 0:
            arrow = "↑"
        elif change < 0:
            arrow = "↓"
        else:
            arrow = "→"
        table.append([
            t['name'],
            f"{first:.2f}%",
            f"{last:.2f}%",
            f"{change:+.2f}% {arrow}"
        ])
    
    print("\n=== ДИНАМИКА WINRATE ЗА 7 ДНЕЙ ===")
    print(tabulate(
        table,
        headers=['Герой', '7 дней назад', 'Сегодня', 'Изменение'],
        tablefmt=TABLE_FORMAT
    ))


def print_summary(heroes, roles, attrs, positions_best, trends):
    heroes_sorted = sorted(heroes, key=lambda x: x['pub_winrate'], reverse=True)
    pro_heroes = [h for h in heroes if h['pro_winrate'] is not None]
    pro_sorted = sorted(pro_heroes, key=lambda x: x['pro_winrate'], reverse=True)
    
    print("\n" + "=" * 70)
    print(f"АНАЛИЗ БАЛАНСА DOTA 2 — {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 70)

    print_heroes_table(heroes_sorted, "ТОП-5 СИЛЬНЫХ В ПАБЛИКАХ")
    print_heroes_table(heroes_sorted, "ТОП-5 СЛАБЫХ В ПАБЛИКАХ", reverse=True)
    print_pro_table(pro_sorted, n=5, reverse=False)
    if len(pro_sorted) > 5:
        print_pro_table(pro_sorted, n=5, reverse=True)
    print_best_positions(positions_best)
    print_roles_table(roles)
    print_attrs_table(attrs)
    print_trends(trends)


def main():
    """Главная функция пайплайна."""
    logger.info("=" * 60)
    logger.info("ЗАПУСК ETL-ПАЙПЛАЙНА DOTA 2")
    logger.info("=" * 60)

    logger.info("ЭТАП 1: Извлечение данных")
    data = fetch_hero_stats()

    logger.info("ЭТАП 2: Трансформация данных")
    heroes = calculate_hero_metrics(data)
    roles = calculate_role_metrics(data)
    attrs = calculate_attr_metrics(data)
    positions_best = find_best_per_position(data)
    positions_top = find_top_by_picks_per_position(data)
    heroes_sorted = sorted(heroes, key=lambda x: x['pub_winrate'], reverse=True)
    top_5_names = [h['name'] for h in heroes_sorted[:5]]
    trends = calculate_trends(data, top_5_names)

    logger.info("ЭТАП 3: Проверка качества данных")
    quality_results = run_all_checks(heroes, roles, attrs)
    
    logger.info("ЭТАП 4: Загрузка данных")
    save_all(heroes, roles, attrs, positions_best, positions_top, trends)

    print_summary(heroes, roles, attrs, positions_best, trends)

    logger.info("=" * 60)
    logger.info("ПАЙПЛАЙН ЗАВЕРШЁН УСПЕШНО")
    logger.info(f"Ошибок качества: {quality_results['total_errors']}")
    logger.info(f"Предупреждений: {quality_results['total_warnings']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()