from fastapi import FastAPI, Query, HTTPException
from app.services import ztm
from app import db
import json

app = FastAPI(title="Brama Wyżynna Departures")

CONFIG = "config/stops.json"
with open(CONFIG, "r", encoding="utf-8") as f:
    cfg = json.load(f)

API_BASE = cfg.get("api_base")
STOP01 = cfg.get("01")
STOP02 = cfg.get("02")

@app.get("/departures")
def departures(combined: bool = True):
    if not API_BASE:
        raise HTTPException(400, "API base not set in config/stops.json")
    data = {}
    if STOP01:
        data["01"] = ztm.get_departures_api(API_BASE, STOP01)
    if STOP02:
        data["02"] = ztm.get_departures_api(API_BASE, STOP02)
    if combined:
        return data.get("01", []) + data.get("02", [])
    return data

@app.get("/history")
def history(limit: int = Query(100, gt=0, le=1000)):
    conn = sqlite3.connect(db.DB_PATH)
    conn.row_factory = db.dict_factory
    cur = conn.cursor()
    cur.execute("SELECT * FROM departures_history ORDER BY fetched_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
