#Конфигурация ETL-пайплайна для анализа баланса Dota 2. Все настройки собраны в одном месте.

API_URL = "https://api.opendota.com/api/heroStats"

MIN_PUB_PICKS = 10000           # Минимум паблик-матчей для анализа
MIN_PRO_PICKS = 10              # Минимум про-матчей для анализа
MIN_POSITION_PICKS = 1000       # Минимум матчей на позиции
MIN_POSITION_SHARE = 0.10       # Минимум 10% пиков героя на позиции
MIN_POSITION_1_PICKS = 5000     # Минимум 5000 пиков на позиции 1
MIN_POSITION_1_SHARE = 0.05     # Минимум 5% доли для позиции 1

POSITIONS = {
    1: "Carry (поз. 1)",
    2: "Mid (поз. 2)",
    3: "Offlane (поз. 3)",
    4: "Soft Support (поз. 4)",
    5: "Hard Support (поз. 5)"
}

POSITION_ROLES = {
    1: ['Carry'],
    2: ['Nuker', 'Escape'],
    3: ['Initiator', 'Durable'],
    4: ['Support', 'Disabler'],
    5: ['Support']
}

DATA_DIR = "data"
LOGS_DIR = "logs"
LOG_FILE = "logs/etl.log"

CSV_FILES = {
    'hero_stats': 'hero_stats',
    'role_stats': 'role_stats',
    'attr_stats': 'attr_stats',
    'best_position': 'best_position',
    'top_picks_position': 'top_picks_position',
    'trends': 'trends'
}

ATTR_TRANSLATIONS = {
    'str': 'Strength (Сила)',
    'agi': 'Agility (Ловкость)',
    'int': 'Intelligence (Интеллект)',
    'all': 'Universal (Универсал)'
}

ROLE_TRANSLATIONS = {
    'Carry': 'Carry (Керри)',
    'Support': 'Support (Поддержка)',
    'Nuker': 'Nuker (Нюкер)',
    'Disabler': 'Disabler (Дизейблер)',
    'Initiator': 'Initiator (Инициатор)',
    'Durable': 'Durable (Стойкий)',
    'Escape': 'Escape (Побег)',
    'Pusher': 'Pusher (Пушер)'
}

ATTACK_TYPE_TRANSLATIONS = {
    'Melee': 'Melee (Ближний бой)',
    'Ranged': 'Ranged (Дальний бой)'
}