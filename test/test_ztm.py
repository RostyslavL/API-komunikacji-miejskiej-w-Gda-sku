from app.services.ztm import _utc_to_local, parse_departure
from datetime import datetime
import zoneinfo

def test_utc_to_local():
    s = "2025-08-12T12:00:00Z"
    dt = _utc_to_local(s)
    assert dt.tzinfo is not None
    assert dt.tzinfo.key == "Europe/Warsaw" or "Warsaw" in dt.tzname()

def test_parse_departure_minimum():
    raw = {
        "estimatedTime": "2023-08-01T12:00:00Z",
        "status": "REALTIME",
        "routeShortName": "6",
        "headsign": "Brama Wyżynna",
        "delayInSeconds": 60
    }
    p = parse_departure(raw)
    assert p["line"] == "6"
    assert p["status"] == "REALTIME"
    assert int(p["delay_seconds"]) == 60
    assert "time_local" in p
