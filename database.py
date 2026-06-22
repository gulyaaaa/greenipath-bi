import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "greenipath.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS dim_project (
        project_id INTEGER PRIMARY KEY,
        project_name TEXT,
        project_code TEXT,
        country TEXT,
        region TEXT,
        project_type TEXT,
        standard TEXT,
        status TEXT,
        start_date TEXT,
        credit_period_years INTEGER,
        investment_usd REAL
    );

    CREATE TABLE IF NOT EXISTS dim_period (
        period_id INTEGER PRIMARY KEY,
        project_id INTEGER,
        period_number INTEGER,
        period_start TEXT,
        period_end TEXT,
        status TEXT
    );

    CREATE TABLE IF NOT EXISTS fact_carbon_calc (
        calc_id INTEGER PRIMARY KEY,
        project_id INTEGER,
        period_id INTEGER,
        gross_reduction_tco2 REAL,
        leakage_tco2 REAL,
        net_reduction_tco2 REAL,
        buffer_tco2 REAL,
        eligible_credits_tco2 REAL
    );

    CREATE TABLE IF NOT EXISTS fact_credits_issued (
        issuance_id INTEGER PRIMARY KEY,
        project_id INTEGER,
        period_id INTEGER,
        registry TEXT,
        issued_credits REAL,
        sold_credits REAL,
        buffer_credits REAL,
        avg_price_usd REAL,
        revenue_usd REAL,
        issuance_date TEXT,
        cost_per_credit_usd REAL
    );
    """)

    # Проекты
    projects = [
        (1, "Сибирское лесовосстановление", "SIB-FOR-001", "Россия", "Сибирь", "Лесной", "Verra VCS", "Активный", "2021-03-15", 20, 1200000),
        (2, "Ветровая генерация — Казахстан", "KAZ-WIN-002", "Казахстан", "Акмолинская обл.", "ВИЭ — Ветер", "Gold Standard", "Активный", "2020-07-01", 10, 3500000),
        (3, "Охрана торфяников — Индонезия", "IDN-PEA-003", "Индонезия", "Калимантан", "Торфяники", "Verra VCS", "На верификации", "2022-01-10", 30, 2800000),
        (4, "Солнечная генерация — Индия", "IND-SOL-004", "Индия", "Раджастхан", "ВИЭ — Солнце", "Gold Standard", "Активный", "2019-11-20", 10, 2100000),
        (5, "Управление отходами — Бразилия", "BRA-WAS-005", "Бразилия", "Параиба", "Отходы", "Plan Vivo", "Разработка", "2023-06-01", 15, 900000),
    ]
    c.executemany("INSERT OR IGNORE INTO dim_project VALUES (?,?,?,?,?,?,?,?,?,?,?)", projects)

    # Периоды мониторинга
    periods = [
        (1,  1, 1, "2021-03-15", "2022-03-14", "Верифицирован"),
        (2,  1, 2, "2022-03-15", "2023-03-14", "Верифицирован"),
        (3,  1, 3, "2023-03-15", "2024-03-14", "Верифицирован"),
        (4,  2, 1, "2020-07-01", "2021-06-30", "Верифицирован"),
        (5,  2, 2, "2021-07-01", "2022-06-30", "Верифицирован"),
        (6,  2, 3, "2022-07-01", "2023-06-30", "Верифицирован"),
        (7,  2, 4, "2023-07-01", "2024-06-30", "В процессе"),
        (8,  3, 1, "2022-01-10", "2023-01-09", "Верифицирован"),
        (9,  3, 2, "2023-01-10", "2024-01-09", "На верификации"),
        (10, 4, 1, "2019-11-20", "2020-11-19", "Верифицирован"),
        (11, 4, 2, "2020-11-20", "2021-11-19", "Верифицирован"),
        (12, 4, 3, "2021-11-20", "2022-11-19", "Верифицирован"),
        (13, 4, 4, "2022-11-20", "2023-11-19", "Верифицирован"),
        (14, 5, 1, "2023-06-01", "2024-05-31", "Мониторинг"),
    ]
    c.executemany("INSERT OR IGNORE INTO dim_period VALUES (?,?,?,?,?,?)", periods)

    # Расчёты CO₂
    calcs = [
        (1,  1, 1,  52000,  5200, 46800, 4680, 42120),
        (2,  1, 2,  60500,  6050, 54450, 5445, 49005),
        (3,  1, 3,  67800,  6780, 61020, 6102, 54918),
        (4,  2, 4,  181538, 0,    181538,9077, 172461),
        (5,  2, 5,  189584, 0,    189584,9479, 180105),
        (6,  2, 6,  195052, 0,    195052,9753, 185299),
        (7,  2, 7,  201344, 0,    201344,10067,191277),
        (8,  3, 8,  187400, 28110,159290,23894,135396),
        (9,  3, 9,  189200, 28380,160820,24123,136697),
        (10, 4, 10, 150880, 0,    150880,7544, 143336),
        (11, 4, 11, 154710, 0,    154710,7736, 146975),
        (12, 4, 12, 157960, 0,    157960,7898, 150062),
        (13, 4, 13, 160925, 0,    160925,8046, 152879),
    ]
    c.executemany("INSERT OR IGNORE INTO fact_carbon_calc VALUES (?,?,?,?,?,?,?,?)", calcs)

    # Выпуск и продажа единиц
    issuances = [
        (1,  1, 1,  "Verra Registry",  42120, 38000, 4680,  8.50,  323000,  "2022-08-10", 5.20),
        (2,  1, 2,  "Verra Registry",  49005, 44500, 5445,  9.20,  409400,  "2023-09-05", 5.40),
        (3,  1, 3,  "Verra Registry",  54918, 51000, 6102,  10.50, 535500,  "2024-10-01", 5.60),
        (4,  2, 4,  "Gold Standard",   172461,168000,9077,  6.80,  1142400, "2021-10-15", 3.10),
        (5,  2, 5,  "Gold Standard",   180105,175000,9479,  7.20,  1260000, "2022-11-20", 3.20),
        (6,  2, 6,  "Gold Standard",   185299,180000,9753,  7.90,  1422000, "2023-12-10", 3.30),
        (7,  3, 8,  "Verra Registry",  135396,120000,23894, 12.50, 1500000, "2023-07-22", 7.80),
        (8,  4, 10, "Gold Standard",   143336,140000,7544,  5.90,  826000,  "2020-12-18", 2.80),
        (9,  4, 11, "Gold Standard",   146975,143000,7736,  6.30,  900900,  "2021-12-22", 2.90),
        (10, 4, 12, "Gold Standard",   150062,147000,7898,  7.10,  1043700, "2022-12-15", 3.00),
        (11, 4, 13, "Gold Standard",   152879,149000,8046,  7.80,  1162200, "2023-12-20", 3.10),
    ]
    c.executemany("INSERT OR IGNORE INTO fact_credits_issued VALUES (?,?,?,?,?,?,?,?,?,?,?)", issuances)

    conn.commit()
    conn.close()
    print("База данных создана успешно!")

if __name__ == "__main__":
    init_db()