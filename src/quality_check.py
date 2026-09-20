#Модуль Quality Check: проверка качества данных.

from .logger import setup_logger

logger = setup_logger()


class QualityCheckError(Exception):
    pass


def check_heroes(heroes: list) -> dict:
    logger.info("Проверка качества данных по героям...")
    results = {
        'total_heroes': len(heroes),
        'errors': [],
        'warnings': []
    }
    
    # 1. Проверка: есть ли герои
    if len(heroes) == 0:
        results['errors'].append("Нет данных по героям")
        return results
    
    # 2. Проверка: винрейт в диапазоне 0-100%
    for h in heroes:
        if not (0 <= h['pub_winrate'] <= 100):
            results['errors'].append(
                f"{h['name']}: pub_winrate = {h['pub_winrate']}% (вне диапазона 0-100%)"
            )
    
    # 3. Проверка: pro_winrate в диапазоне (если есть)
    for h in heroes:
        if h['pro_winrate'] is not None:
            if not (0 <= h['pro_winrate'] <= 100):
                results['errors'].append(
                    f"{h['name']}: pro_winrate = {h['pro_winrate']}% (вне диапазона 0-100%)"
                )
    
    # 4. Проверка: нет пропусков в ключевых полях
    for h in heroes:
        if not h['name']:
            results['errors'].append(f"Герой с id={h['hero_id']}: пустое имя")
        if h['pub_pick'] <= 0:
            results['errors'].append(f"{h['name']}: pub_pick = {h['pub_pick']}")
    
    # 5. Проверка: нет дубликатов по hero_id
    hero_ids = [h['hero_id'] for h in heroes]
    if len(hero_ids) != len(set(hero_ids)):
        results['errors'].append("Обнаружены дубликаты по hero_id")
    
    # 6. Предупреждение: слишком мало героев
    if len(heroes) < 100:
        results['warnings'].append(
            f"Мало героев: {len(heroes)}. Ожидалось ~127."
        )
    
    logger.info(f"Проверка героев: ошибок — {len(results['errors'])}, предупреждений — {len(results['warnings'])}")
    return results


def check_roles(roles: list) -> dict:
    logger.info("Проверка качества данных по ролям...")
    results = {
        'total_roles': len(roles),
        'errors': [],
        'warnings': []
    }
    
    if len(roles) == 0:
        results['errors'].append("Нет данных по ролям")
        return results
    
    for r in roles:
        if not (0 <= r['avg_winrate'] <= 100):
            results['errors'].append(
                f"Роль {r['role']}: avg_winrate = {r['avg_winrate']}%"
            )
        if r['heroes_count'] == 0:
            results['warnings'].append(f"Роль {r['role']}: 0 героев")
    
    logger.info(f"Проверка ролей: ошибок — {len(results['errors'])}, предупреждений — {len(results['warnings'])}")
    return results


def check_attrs(attrs: list) -> dict:
    logger.info("Проверка качества данных по атрибутам...")
    results = {
        'total_attrs': len(attrs),
        'errors': [],
        'warnings': []
    }
    
    if len(attrs) == 0:
        results['errors'].append("Нет данных по атрибутам")
        return results
    
    for a in attrs:
        if not (0 <= a['avg_winrate'] <= 100):
            results['errors'].append(
                f"Атрибут {a['attr']}: avg_winrate = {a['avg_winrate']}%"
            )
    
    logger.info(f"Проверка атрибутов: ошибок — {len(results['errors'])}, предупреждений — {len(results['warnings'])}")
    return results


def run_all_checks(heroes: list, roles: list, attrs: list) -> dict:
    logger.info("=" * 50)
    logger.info("ЗАПУСК ПРОВЕРОК КАЧЕСТВА ДАННЫХ")
    logger.info("=" * 50)
    
    heroes_check = check_heroes(heroes)
    roles_check = check_roles(roles)
    attrs_check = check_attrs(attrs)
    
    total_errors = (
        len(heroes_check['errors']) +
        len(roles_check['errors']) +
        len(attrs_check['errors'])
    )
    total_warnings = (
        len(heroes_check['warnings']) +
        len(roles_check['warnings']) +
        len(attrs_check['warnings'])
    )
    
    logger.info("=" * 50)
    logger.info(f"ИТОГО: ошибок — {total_errors}, предупреждений — {total_warnings}")
    logger.info("=" * 50)
    
    if total_errors > 0:
        logger.error("ОБНАРУЖЕНЫ ОШИБКИ:")
        for err in heroes_check['errors'] + roles_check['errors'] + attrs_check['errors']:
            logger.error(f"  - {err}")
    
    if total_warnings > 0:
        logger.warning("ПРЕДУПРЕЖДЕНИЯ:")
        for warn in heroes_check['warnings'] + roles_check['warnings'] + attrs_check['warnings']:
            logger.warning(f"  - {warn}")
    
    return {
        'heroes': heroes_check,
        'roles': roles_check,
        'attrs': attrs_check,
        'total_errors': total_errors,
        'total_warnings': total_warnings
    }


if __name__ == "__main__":
    from .extract import fetch_hero_stats
    from .transform import (
        calculate_hero_metrics, calculate_role_metrics, calculate_attr_metrics
    )
    
    data = fetch_hero_stats()
    heroes = calculate_hero_metrics(data)
    roles = calculate_role_metrics(data)
    attrs = calculate_attr_metrics(data)
    
    results = run_all_checks(heroes, roles, attrs)
    
    print(f"\nОшибок: {results['total_errors']}")
    print(f"Предупреждений: {results['total_warnings']}")