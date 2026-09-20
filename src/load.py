#Модуль Load: сохранение результатов ETL-пайплайна.

import csv
import os
from datetime import datetime
from .config import DATA_DIR, CSV_FILES
from .db import get_connection
from .logger import setup_logger

logger = setup_logger()


def get_today_dir() -> str:
    today = datetime.now().strftime('%Y-%m-%d')
    path = os.path.join(DATA_DIR, today)
    os.makedirs(path, exist_ok=True)

    return path


def save_to_csv(filename: str, data: list, fieldnames: list) -> None:
    today_dir = get_today_dir()
    filepath = os.path.join(today_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    logger.info(f"Сохранено: {filepath}")


def save_heroes_to_db(heroes: list) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        for h in heroes:
            cur.execute("""
                INSERT INTO hero_stats 
                (hero_id, name, primary_attr, attack_type, roles, 
                 pub_pick, pub_winrate, pro_pick, pro_winrate, pickrate, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hero_id, date) DO UPDATE SET
                    name = EXCLUDED.name,
                    pub_pick = EXCLUDED.pub_pick,
                    pub_winrate = EXCLUDED.pub_winrate,
                    pro_pick = EXCLUDED.pro_pick,
                    pro_winrate = EXCLUDED.pro_winrate,
                    pickrate = EXCLUDED.pickrate
            """, (
                h['hero_id'], h['name'], h['primary_attr'], h['attack_type'],
                h['roles'], h['pub_pick'], h['pub_winrate'], h['pro_pick'],
                h['pro_winrate'], h['pickrate'], h['date']
            ))
    logger.info(f"Загружено в PostgreSQL: {len(heroes)} героев")


def save_roles_to_db(roles: list) -> None:
    date = datetime.now().strftime('%Y-%m-%d')
    with get_connection() as conn:
        cur = conn.cursor()
        for r in roles:
            cur.execute("""
                INSERT INTO role_stats 
                (role, avg_winrate, heroes_count, best_hero, best_winrate,
                 worst_hero, worst_winrate, spread, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (role, date) DO UPDATE SET
                    avg_winrate = EXCLUDED.avg_winrate,
                    best_hero = EXCLUDED.best_hero,
                    best_winrate = EXCLUDED.best_winrate,
                    worst_hero = EXCLUDED.worst_hero,
                    worst_winrate = EXCLUDED.worst_winrate,
                    spread = EXCLUDED.spread
            """, (
                r['role'], r['avg_winrate'], r['heroes_count'],
                r['best_hero'], r['best_winrate'], r['worst_hero'],
                r['worst_winrate'], r['spread'], date
            ))
    logger.info(f"Загружено в PostgreSQL: {len(roles)} ролей")


def save_attrs_to_db(attrs: list) -> None:
    date = datetime.now().strftime('%Y-%m-%d')
    with get_connection() as conn:
        cur = conn.cursor()
        for a in attrs:
            cur.execute("""
                INSERT INTO attr_stats 
                (attr, avg_winrate, heroes_count, best_hero, best_winrate,
                 worst_hero, worst_winrate, spread, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (attr, date) DO UPDATE SET
                    avg_winrate = EXCLUDED.avg_winrate,
                    best_hero = EXCLUDED.best_hero,
                    best_winrate = EXCLUDED.best_winrate,
                    worst_hero = EXCLUDED.worst_hero,
                    worst_winrate = EXCLUDED.worst_winrate,
                    spread = EXCLUDED.spread
            """, (
                a['attr'], a['avg_winrate'], a['heroes_count'],
                a['best_hero'], a['best_winrate'], a['worst_hero'],
                a['worst_winrate'], a['spread'], date
            ))
    logger.info(f"Загружено в PostgreSQL: {len(attrs)} атрибутов")


def save_positions_to_db(positions_best: list) -> None:
    date = datetime.now().strftime('%Y-%m-%d')
    with get_connection() as conn:
        cur = conn.cursor()
        for p in positions_best:
            cur.execute("""
                INSERT INTO best_position 
                (position, name, winrate, picks, share, roles, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (position, date) DO UPDATE SET
                    name = EXCLUDED.name,
                    winrate = EXCLUDED.winrate,
                    picks = EXCLUDED.picks,
                    share = EXCLUDED.share
            """, (
                p['position'], p['name'], p['winrate'],
                p['picks'], p['share'], p['roles'], date
            ))
    logger.info(f"Загружено в PostgreSQL: {len(positions_best)} позиций")


def save_top_picks_to_db(positions_top: list) -> None:
    date = datetime.now().strftime('%Y-%m-%d')
    with get_connection() as conn:
        cur = conn.cursor()
        for p in positions_top:
            cur.execute("""
                INSERT INTO top_picks_position 
                (position, name, picks, winrate, date)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                p['position'], p['name'], p['picks'], p['winrate'], date
            ))
    logger.info(f"Загружено в PostgreSQL: {len(positions_top)} записей по пикам")


def save_trends_to_db(trends: list) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        count = 0
        for t in trends:
            for day in t['trend']:
                cur.execute("""
                    INSERT INTO trends 
                    (hero, date, picks, wins, winrate)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    t['name'], day['date'], day['picks'],
                    day['wins'], day['winrate']
                ))
                count += 1
    logger.info(f"Загружено в PostgreSQL: {count} записей трендов")


def save_all(heroes, roles, attrs, positions_best, positions_top, trends) -> None:
    logger.info("Сохранение результатов...")
    today = datetime.now().strftime('%Y-%m-%d')
    
    save_to_csv(f"{CSV_FILES['hero_stats']}_{today}.csv", heroes, [
        'hero_id', 'name', 'primary_attr', 'attack_type', 'roles',
        'pub_pick', 'pub_winrate', 'pro_pick', 'pro_winrate', 'pickrate', 'date'
    ])
    save_to_csv(f"{CSV_FILES['role_stats']}_{today}.csv", roles, [
        'role', 'avg_winrate', 'heroes_count', 'best_hero', 'best_winrate',
        'worst_hero', 'worst_winrate', 'spread'
    ])
    save_to_csv(f"{CSV_FILES['attr_stats']}_{today}.csv", attrs, [
        'attr', 'avg_winrate', 'heroes_count', 'best_hero', 'best_winrate',
        'worst_hero', 'worst_winrate', 'spread'
    ])
    save_to_csv(f"{CSV_FILES['best_position']}_{today}.csv", positions_best, [
        'position', 'name', 'winrate', 'picks', 'share', 'roles'
    ])
    save_to_csv(f"{CSV_FILES['top_picks_position']}_{today}.csv", positions_top, [
        'position', 'name', 'picks', 'winrate'
    ])
    
    trends_flat = []
    for t in trends:
        for day in t['trend']:
            trends_flat.append({
                'hero': t['name'],
                'date': day['date'],
                'picks': day['picks'],
                'wins': day['wins'],
                'winrate': day['winrate']
            })
    save_to_csv(f"{CSV_FILES['trends']}_{today}.csv", trends_flat, [
        'hero', 'date', 'picks', 'wins', 'winrate'
    ])
    
    logger.info("Все результаты сохранены в CSV")

    
    logger.info("Загрузка в PostgreSQL...")
    save_heroes_to_db(heroes)
    save_roles_to_db(roles)
    save_attrs_to_db(attrs)
    save_positions_to_db(positions_best)
    save_top_picks_to_db(positions_top)
    save_trends_to_db(trends)
    logger.info("Все результаты загружены в PostgreSQL")