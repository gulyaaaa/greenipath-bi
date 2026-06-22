import sqlite3
import yfinance as yf
import pandas as pd
import numpy as np
import os
import time
import random
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/greenipath-bi/greenipath.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

# ── Создаём таблицы для real-time данных ─────────────────────────────────────
def init_realtime_tables():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS rt_co2_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        price_eur REAL,
        change_pct REAL,
        source TEXT
    );

    CREATE TABLE IF NOT EXISTS rt_monitoring_stream (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        project_id INTEGER,
        project_name TEXT,
        indicator TEXT,
        value REAL,
        unit TEXT,
        status TEXT
    );
    """)
    conn.commit()
    conn.close()
    print("Таблицы real-time созданы")

# ── Канал 1: Реальные цены CO₂ с рынка ───────────────────────────────────────
def fetch_co2_price():
    """
    Подтягивает цену углеродных единиц EU ETS через Yahoo Finance.
    Тикер: KRBN (KraneShares Global Carbon ETF) — торгуется на NYSE,
    отражает стоимость углеродных единиц на глобальном рынке.
    """
    try:
        ticker = yf.Ticker("KRBN")
        hist = ticker.history(period="5d", interval="1d")
        if not hist.empty:
            latest = hist.iloc[-1]
            prev   = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]
            price  = round(float(latest["Close"]), 2)
            change = round((float(latest["Close"]) - float(prev["Close"]))
                           / float(prev["Close"]) * 100, 2)
            conn = get_conn()
            conn.execute("""
                INSERT INTO rt_co2_prices (timestamp, price_eur, change_pct, source)
                VALUES (?, ?, ?, ?)
            """, (datetime.now().isoformat(), price, change, "Yahoo Finance / KRBN ETF"))
            conn.commit()
            conn.close()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] CO₂ цена: ${price} ({change:+.2f}%)")
            return price, change
        else:
            print("Нет данных от Yahoo Finance, используем последнюю цену")
            return get_last_co2_price()
    except Exception as e:
        print(f"Ошибка получения цены CO₂: {e}")
        return get_last_co2_price()

def get_last_co2_price():
    """Возвращает последнюю сохранённую цену CO₂"""
    conn = get_conn()
    row = conn.execute("""
        SELECT price_eur, change_pct FROM rt_co2_prices
        ORDER BY id DESC LIMIT 1
    """).fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    # Базовая цена если данных ещё нет
    return 24.50, 0.0

# ── Канал 2: Симуляция потока мониторинговых данных ──────────────────────────
PROJECTS = [
    (1, "Сибирское лесовосстановление",    "Лесной"),
    (2, "Ветровая генерация — Казахстан",  "ВИЭ — Ветер"),
    (3, "Охрана торфяников — Индонезия",   "Торфяники"),
    (4, "Солнечная генерация — Индия",     "ВИЭ — Солнце"),
]

# Базовые значения для каждого типа проекта
BASE_VALUES = {
    "Лесной":      {"Запас углерода в биомассе (т CO₂/га)": 155.0, "Площадь (га)": 18500},
    "ВИЭ — Ветер": {"Выработка э/э (МВт·ч/день)": 890.0,          "Мощность (МВт)": 48},
    "Торфяники":   {"Площадь охраняемых торфяников (га)": 45200,   "Уровень воды (м)": 0.42},
    "ВИЭ — Солнце":{"Выработка э/э (МВт·ч/день)": 520.0,          "Инсоляция (кВт·ч/м²)": 5.8},
}

def simulate_monitoring_reading():
    """
    Генерирует реалистичное мониторинговое измерение.
    Значения варьируются вокруг базовых с небольшим шумом —
    имитация данных с полевых датчиков и приборов учёта.
    """
    project_id, project_name, project_type = random.choice(PROJECTS)
    indicators = BASE_VALUES.get(project_type, {})
    if not indicators:
        return

    indicator, base_val = random.choice(list(indicators.items()))

    # Реалистичное отклонение ±3%
    noise = random.uniform(-0.03, 0.03)
    value = round(base_val * (1 + noise), 2)

    # Статус зависит от отклонения
    if abs(noise) < 0.01:
        status = "Норма"
    elif abs(noise) < 0.02:
        status = "Внимание"
    else:
        status = "Отклонение"

    unit = indicator.split("(")[-1].replace(")", "").strip() if "(" in indicator else "ед."
    ind_name = indicator.split("(")[0].strip()

    conn = get_conn()
    conn.execute("""
        INSERT INTO rt_monitoring_stream
        (timestamp, project_id, project_name, indicator, value, unit, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), project_id, project_name,
          ind_name, value, unit, status))
    conn.commit()
    conn.close()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
          f"{project_name} | {ind_name}: {value} {unit} [{status}]")

# ── Получение данных для дашборда ────────────────────────────────────────────
def get_latest_co2_price():
    """Возвращает последние 30 записей цены CO₂ для графика"""
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT timestamp, price_eur, change_pct, source
        FROM rt_co2_prices
        ORDER BY id DESC LIMIT 30
    """, conn)
    conn.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
    return df

def get_latest_monitoring_stream(limit=20):
    """Возвращает последние измерения из потока мониторинга"""
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT timestamp, project_name, indicator, value, unit, status
        FROM rt_monitoring_stream
        ORDER BY id DESC LIMIT {limit}
    """, conn)
    conn.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def get_stream_stats():
    """Статистика по потоку за последний час"""
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT project_name,
               COUNT(*) as readings,
               SUM(CASE WHEN status='Норма' THEN 1 ELSE 0 END) as normal,
               SUM(CASE WHEN status='Отклонение' THEN 1 ELSE 0 END) as anomaly
        FROM rt_monitoring_stream
        WHERE timestamp >= datetime('now', '-1 hour')
        GROUP BY project_name
    """, conn)
    conn.close()
    return df

# ── Запуск потока (используется в отдельном процессе) ────────────────────────
def run_stream(co2_interval=300, monitoring_interval=30):
    """
    Запускает непрерывный поток данных:
    - Цена CO₂ обновляется каждые 5 минут
    - Мониторинговые данные каждые 30 секунд
    """
    print("=" * 50)
    print("GreenIPath Real-Time Data Stream запущен")
    print(f"Цена CO₂: каждые {co2_interval} сек.")
    print(f"Мониторинг: каждые {monitoring_interval} сек.")
    print("=" * 50)

    last_co2_fetch = 0

    while True:
        now = time.time()

        # Обновляем цену CO₂
        if now - last_co2_fetch >= co2_interval:
            fetch_co2_price()
            last_co2_fetch = now

        # Мониторинговое измерение
        simulate_monitoring_reading()
        time.sleep(monitoring_interval)

# ── Инициализация при первом запуске ─────────────────────────────────────────
def seed_initial_data():
    """Заполняет начальные исторические данные чтобы графики не были пустыми"""
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM rt_co2_prices").fetchone()[0]
    conn.close()

    if count == 0:
        print("Заполняем начальные данные...")
        # Генерируем 24 часа исторических цен
        base_price = 24.50
        conn = get_conn()
        for i in range(48):
            ts = datetime.now() - timedelta(minutes=30 * (48 - i))
            price = round(base_price + random.uniform(-1.5, 1.5), 2)
            change = round(random.uniform(-2.5, 2.5), 2)
            conn.execute("""
                INSERT INTO rt_co2_prices (timestamp, price_eur, change_pct, source)
                VALUES (?, ?, ?, ?)
            """, (ts.isoformat(), price, change, "Historical seed"))
        conn.commit()
        conn.close()

    conn = get_conn()
    count2 = conn.execute("SELECT COUNT(*) FROM rt_monitoring_stream").fetchone()[0]
    conn.close()

    if count2 == 0:
        print("Заполняем начальный поток мониторинга...")
        conn = get_conn()
        for i in range(100):
            ts = datetime.now() - timedelta(seconds=30 * (100 - i))
            project_id, project_name, project_type = random.choice(PROJECTS)
            indicators = BASE_VALUES.get(project_type, {})
            indicator, base_val = random.choice(list(indicators.items()))
            noise = random.uniform(-0.03, 0.03)
            value = round(base_val * (1 + noise), 2)
            status = "Норма" if abs(noise) < 0.01 else ("Внимание" if abs(noise) < 0.02 else "Отклонение")
            unit = indicator.split("(")[-1].replace(")", "").strip() if "(" in indicator else "ед."
            ind_name = indicator.split("(")[0].strip()
            conn.execute("""
                INSERT INTO rt_monitoring_stream
                (timestamp, project_id, project_name, indicator, value, unit, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ts.isoformat(), project_id, project_name,
                  ind_name, value, unit, status))
        conn.commit()
        conn.close()
        print("Начальные данные заполнены!")

if __name__ == "__main__":
    init_realtime_tables()
    seed_initial_data()
    fetch_co2_price()
    print("\nЗапускаем поток данных... (Ctrl+C для остановки)")
    run_stream()
