# Dota 2 Hero Balance Analysis

ETL-пайплайн для анализа баланса персонажей в Dota 2 на основе данных OpenDota API.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Status](https://img.shields.io/badge/Status-Active-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Описание

Проект автоматически собирает статистику по героям Dota 2, рассчитывает метрики баланса (winrate, pickrate) и выявляет имбалансных героев. Пайплайн работает по классической ETL-схеме: Extract → Transform → Quality Check → Load.

**Цель проекта:** автоматизировать процесс выявления имбалансных героев в Dota 2, чтобы помочь геймдизайнерам принимать решения о нерфах и бафах на основе данных.

## Функциональность

- **Extract:** получение данных из OpenDota API.
- **Transform:** расчёт метрик по героям, ролям, атрибутам, позициям.
- **Quality Check:** проверка качества данных.
- **Load:** сохранение результатов в CSV (в будущем — в PostgreSQL).

## Метрики

- **Winrate (pub)** — винрейт в пабликах.
- **Winrate (pro)** — винрейт в профессиональных матчах.
- **Pickrate** — доля героя от всех пиков.
- **Pick share** — доля пиков героя на конкретной позиции.
- **Spread** — разброс винрейта внутри группы (роли, атрибута).

## Аналитические срезы

1. **Топ-5 сильных в пабликах** — имбы для большинства игроков.
2. **Топ-5 слабых в пабликах** — герои, требующие бафа.
3. **Топ-5 сильных в про** — имбы для профессионалов.
4. **Лучший герой на каждую позицию** — с фильтром по ролям и доле пиков.
5. **Сила ролей и атрибутов** — с разбросом внутри группы.
6. **Динамика winrate за 7 дней** — тренды изменения баланса.

## Технологический стек

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.10+ |
| HTTP-запросы | requests |
| Таблицы | tabulate |
| База данных | PostgreSQL 15 |
| Оркестрация | Apache Airflow 2.7.3 |
| Визуализация | Metabase |
| Контейнеризация | Docker + Docker Compose |
| Источник данных | OpenDota API |

## Структура проекта

```
dota2herobalance/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── quality_check.py
├── logs/
├── data/
├── main.py
├── requirements.txt
└── README.md
```

### Описание модулей

| Модуль | Назначение |
|--------|------------|
| `config.py` | Конфигурация (пороги, переводы) |
| `logger.py` | Логирование |
| `extract.py` | Запрос к API |
| `transform.py` | Расчёт метрик |
| `load.py` | Сохранение в CSV и PostgreSQL |
| `db.py` | Подключение к PostgreSQL |
| `quality_check.py` | Проверки качества |
| `main.py` | Точка входа |

## Установка и запуск

**Требования:** Docker Desktop, Python 3.10+.

### Запустить все сервисы (PostgreSQL, Airflow, Metabase)

```
docker-compose up -d --build
```

### Установить зависимости локально (для запуска main.py)

```
pip install -r requirements.txt
```

### Создать таблицы в PostgreSQL (один раз)

```
docker exec -it dota2_postgres psql -U dota2 -d dota2db
```

### Запустить пайплайн вручную (локально)

```
py main.py
```

## Доступ к сервисам:

| Сервис | URL | Логин / Пароль|
|--------|-----|-------------|
| Airflow | http://localhost:8080 | admin / admin |
| Metabase | http://localhost:3000 | (свой) |
| PostgreSQL | localhost:5432 | dota2 / dota2pass |

## Источник данных

**[OpenDota API](https://api.opendota.com/api/heroStats)** — бесплатный API с статистикой по Dota 2.

## Автор

**Смолин Сергей ([GitHub](https://github.com/owyxx))** - курсовая работа по дисциплине «Инжиниринг данных».

Самарский Государственный Технический Университет, 2026.