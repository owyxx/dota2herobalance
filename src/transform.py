#Модуль Transform: расчёт метрик баланса героев Dota 2.

from datetime import datetime, timedelta
from collections import defaultdict

from .config import (
    MIN_PRO_PICKS, MIN_POSITION_PICKS, MIN_POSITION_SHARE,
    MIN_POSITION_1_PICKS, MIN_POSITION_1_SHARE,
    POSITIONS, POSITION_ROLES
)
from .logger import setup_logger

logger = setup_logger()


def calculate_hero_metrics(data: list) -> list:
    logger.info("Расчёт метрик героев...")
    heroes = []
    total_pub_picks = sum(h['pub_pick'] for h in data)
    
    for hero in data:
        if hero['pub_pick'] == 0:
            continue
        
        pub_winrate = (hero['pub_win'] / hero['pub_pick']) * 100
        pickrate = (hero['pub_pick'] / total_pub_picks) * 100
        
        if hero['pro_pick'] >= MIN_PRO_PICKS:
            pro_winrate = (hero['pro_win'] / hero['pro_pick']) * 100
        else:
            pro_winrate = None
        
        heroes.append({
            'hero_id': hero['id'],
            'name': hero['localized_name'],
            'primary_attr': hero['primary_attr'],
            'attack_type': hero['attack_type'],
            'roles': ', '.join(hero['roles']),
            'pub_pick': hero['pub_pick'],
            'pub_winrate': round(pub_winrate, 2),
            'pro_pick': hero['pro_pick'],
            'pro_winrate': round(pro_winrate, 2) if pro_winrate is not None else None,
            'pickrate': round(pickrate, 3),
            'date': datetime.now().strftime('%Y-%m-%d')
        })
    
    logger.info(f"Рассчитано метрик для {len(heroes)} героев")
    return heroes


def calculate_role_metrics(data: list) -> list:
    logger.info("Расчёт метрик ролей...")
    role_stats = defaultdict(lambda: {'total_pick': 0, 'total_win': 0, 'heroes': []})
    
    for hero in data:
        if hero['pub_pick'] == 0:
            continue
        for role in hero['roles']:
            role_stats[role]['total_pick'] += hero['pub_pick']
            role_stats[role]['total_win'] += hero['pub_win']
            hero_winrate = (hero['pub_win'] / hero['pub_pick']) * 100
            role_stats[role]['heroes'].append({
                'name': hero['localized_name'],
                'winrate': hero_winrate,
                'pub_pick': hero['pub_pick']
            })
    
    result = []
    for role, stats in role_stats.items():
        if stats['total_pick'] > 0:
            avg_winrate = (stats['total_win'] / stats['total_pick']) * 100
            heroes_sorted = sorted(stats['heroes'], key=lambda x: x['winrate'], reverse=True)
            best = heroes_sorted[0]
            worst = heroes_sorted[-1]
            
            result.append({
                'role': role,
                'avg_winrate': round(avg_winrate, 2),
                'heroes_count': len(stats['heroes']),
                'best_hero': best['name'],
                'best_winrate': round(best['winrate'], 2),
                'worst_hero': worst['name'],
                'worst_winrate': round(worst['winrate'], 2),
                'spread': round(best['winrate'] - worst['winrate'], 2)
            })
    
    result_sorted = sorted(result, key=lambda x: x['avg_winrate'], reverse=True)
    logger.info(f"Рассчитано метрик для {len(result_sorted)} ролей")
    return result_sorted


def calculate_attr_metrics(data: list) -> list:
    logger.info("Расчёт метрик атрибутов...")
    attr_stats = defaultdict(lambda: {'total_pick': 0, 'total_win': 0, 'heroes': []})
    
    for hero in data:
        if hero['pub_pick'] == 0:
            continue
        attr = hero['primary_attr']
        attr_stats[attr]['total_pick'] += hero['pub_pick']
        attr_stats[attr]['total_win'] += hero['pub_win']
        hero_winrate = (hero['pub_win'] / hero['pub_pick']) * 100
        attr_stats[attr]['heroes'].append({
            'name': hero['localized_name'],
            'winrate': hero_winrate,
            'pub_pick': hero['pub_pick']
        })
    
    result = []
    for attr, stats in attr_stats.items():
        if stats['total_pick'] > 0:
            avg_winrate = (stats['total_win'] / stats['total_pick']) * 100
            heroes_sorted = sorted(stats['heroes'], key=lambda x: x['winrate'], reverse=True)
            best = heroes_sorted[0]
            worst = heroes_sorted[-1]
            
            result.append({
                'attr': attr,
                'avg_winrate': round(avg_winrate, 2),
                'heroes_count': len(stats['heroes']),
                'best_hero': best['name'],
                'best_winrate': round(best['winrate'], 2),
                'worst_hero': worst['name'],
                'worst_winrate': round(worst['winrate'], 2),
                'spread': round(best['winrate'] - worst['winrate'], 2)
            })
    
    result_sorted = sorted(result, key=lambda x: x['avg_winrate'], reverse=True)
    logger.info(f"Рассчитано метрик для {len(result_sorted)} атрибутов")
    return result_sorted


def find_best_per_position(data: list) -> list:
    logger.info("Поиск лучших героев по позициям...")
    result = []
    
    for pos_num, pos_name in POSITIONS.items():
        required_roles = POSITION_ROLES[pos_num]
        best_hero = None
        best_winrate = 0
        
        if pos_num == 1:
            min_picks = MIN_POSITION_1_PICKS
            min_share = MIN_POSITION_1_SHARE
        else:
            min_picks = MIN_POSITION_PICKS
            min_share = MIN_POSITION_SHARE
        
        for hero in data:
            picks = hero.get(f"{pos_num}_pick", 0)
            wins = hero.get(f"{pos_num}_win", 0)
            total_pub_picks = hero['pub_pick']
            
            if picks < min_picks or total_pub_picks == 0:
                continue
            
            hero_roles = hero['roles']
            has_role = any(role in hero_roles for role in required_roles)
            position_share = picks / total_pub_picks
            has_share = position_share >= min_share
            
            if has_role and has_share:
                winrate = (wins / picks) * 100
                if winrate > best_winrate:
                    best_winrate = winrate
                    best_hero = {
                        'position': pos_name,
                        'name': hero['localized_name'],
                        'winrate': round(winrate, 2),
                        'picks': picks,
                        'share': round(position_share * 100, 1),
                        'roles': ', '.join(hero_roles)
                    }
        
        if best_hero:
            result.append(best_hero)
    
    logger.info(f"Найдено лучших героев для {len(result)} позиций")
    return result


def find_top_by_picks_per_position(data: list, top_n: int = 5) -> list:
    logger.info(f"Поиск топ-{top_n} героев по пикам на позициях...")
    result = []
    
    for pos_num, pos_name in POSITIONS.items():
        heroes_on_pos = []
        
        for hero in data:
            picks = hero.get(f"{pos_num}_pick", 0)
            if picks >= MIN_POSITION_PICKS:
                heroes_on_pos.append({
                    'position': pos_name,
                    'name': hero['localized_name'],
                    'picks': picks,
                    'winrate': round((hero.get(f"{pos_num}_win", 0) / picks) * 100, 2)
                })
        
        heroes_on_pos.sort(key=lambda x: x['picks'], reverse=True)
        result.extend(heroes_on_pos[:top_n])
    
    logger.info(f"Найдено {len(result)} записей по пикам на позициях")
    return result


def calculate_trends(data: list, top_heroes: list) -> list:
    logger.info(f"Расчёт трендов для {len(top_heroes)} героев...")
    result = []
    
    for hero in data:
        if hero['localized_name'] not in top_heroes:
            continue
        
        trend = []
        for i in range(7):
            picks = hero['pub_pick_trend'][i]
            wins = hero['pub_win_trend'][i]
            
            if picks > 0:
                winrate = (wins / picks) * 100
                day_offset = 6 - i
                date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')
                trend.append({
                    'date': date,
                    'picks': picks,
                    'wins': wins,
                    'winrate': round(winrate, 2)
                })
        
        result.append({
            'name': hero['localized_name'],
            'trend': trend
        })
    
    logger.info(f"Рассчитано трендов для {len(result)} героев")
    return result

if __name__ == "__main__":
    from .extract import fetch_hero_stats
    
    data = fetch_hero_stats()
    heroes = calculate_hero_metrics(data)
    roles = calculate_role_metrics(data)
    attrs = calculate_attr_metrics(data)
    positions = find_best_per_position(data)
    top_picks = find_top_by_picks_per_position(data)
    
    print(f"\nГероев: {len(heroes)}")
    print(f"Ролей: {len(roles)}")
    print(f"Атрибутов: {len(attrs)}")
    print(f"Позиций с лучшими героями: {len(positions)}")
    print(f"Записей по пикам: {len(top_picks)}")
    
    print("\n=== ТОП-5 СИЛЬНЫХ В ПАБЛИКАХ ===")
    heroes_sorted = sorted(heroes, key=lambda x: x['pub_winrate'], reverse=True)
    for h in heroes_sorted[:5]:
        print(f"{h['name']:20} | Pub: {h['pub_winrate']:5.2f}%")