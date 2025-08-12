import sqlite3
from typing import Optional, Dict, Any, List

DB_PATH = "tristar.db"

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # tabela stops (cache stopId)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stopId INTEGER UNIQUE,
        stopName TEXT,
        subName TEXT,
        type TEXT,
        created_at TEXT
    )""")
    # tabela historii odjazdów
    cur.execute("""
    CREATE TABLE IF NOT EXISTS departures_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stopId INTEGER,
        line TEXT,
        direction TEXT,
        time_local TEXT,
        status TEXT,
        delay_seconds INTEGER,
        fetched_at TEXT
    )""")
    conn.commit()
    conn.close()

def insert_stop(stop: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO stops (stopId, stopName, subName, type, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (stop.get("stopId"), stop.get("stopName"), stop.get("subName"), stop.get("type")))
    conn.commit()
    conn.close()

def get_stops_cached() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute("SELECT * FROM stops")
    rows = cur.fetchall()
    conn.close()
    return rows

def save_departures_history(rows: List[Dict[str, Any]]):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for r in rows:
        cur.execute("""
            INSERT INTO departures_history
            (stopId, line, direction, time_local, status, delay_seconds, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (r["stopId"], r["line"], r["direction"], r["time_local"], r["status"], r["delay_seconds"]))
    conn.commit()
    conn.close()
