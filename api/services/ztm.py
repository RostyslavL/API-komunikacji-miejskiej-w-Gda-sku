import requests
from typing import List, Dict, Optional
from dateutil import parser as date_parser
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
from app import db

API_BASE = "https://ckan.multimediagdansk.pl"  # baza CKAN; endpointy użyj poniżej
STOPS_JSON_URL = "https://ckan.multimediagdansk.pl/dataset/tristar/resource/..." 

LOCAL_TZ = ZoneInfo("Europe/Warsaw")

def _utc_to_local(utc_str: str) -> str:
    dt = date_parser.isoparse(utc_str)
    if dt.tzinfo is None:
        from zoneinfo import ZoneInfo
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    local = dt.astimezone(LOCAL_TZ)
    return local.isoformat()

def parse_departure(raw: dict) -> Dict[str, Optional[str]]:
    estimated = raw.get("estimatedTime") or raw.get("estimatedDepartureTime")
    scheduled = raw.get("scheduledTime") or raw.get("plannedDepartureTime")
    time_src = estimated or scheduled
    time_local = _utc_to_local(time_src) if time_src else None

    return {
        "line": str(raw.get("routeShortName") or raw.get("line") or ""),
        "direction": str(raw.get("headsign") or raw.get("direction") or ""),
        "time_local": time_local,
        "status": raw.get("status", "SCHEDULED"),
        "delay_seconds": int(raw.get("delayInSeconds") or raw.get("delay") or 0)
    }

def get_departures_api(api_base: str, stop_id: int) -> List[Dict]:
   url = f"{api_base.rstrip('/')}/dataset/tristar/resource/stops/departures"  # przykładowy, dostosuj
    params = {"stopId": stop_id}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    raw_list = data.get("departures") if isinstance(data, dict) and "departures" in data else data
    parsed = []
    for raw in raw_list:
        try:
            p = parse_departure(raw)
            p["stopId"] = stop_id
            parsed.append(p)
        except Exception:
            continue
 # pomoc do parsowania stops.json lokalnie          
def find_brama_wyzynna_from_stopsfile(path: str) -> Dict[str, int]:
    """
    Parsuje lokalny stops.json i zwraca dict {"01": stopId, "02": stopId}
    Heurystyka: stopName zawiera 'Brama Wyżynna' i subName '01'/'02' lub subName zawiera '01'/'02'.
    """
    with open(path, "r", encoding="utf-8") as f:
        stops = json.load(f)
    results = {}
    for s in stops:
        name = (s.get("stopName") or "").lower()
        sub = (s.get("subName") or "").lower()
        if "brama wyżynna" in name or "brama wyzynna" in name:
            if "01" in sub or "01" in name:
                results["01"] = s.get("stopId")
                db.insert_stop(s)
            if "02" in sub or "02" in name:
                results["02"] = s.get("stopId")
                db.insert_stop(s)
    return results
