import httpx
from typing import List, Dict, Union
from datetime import datetime
import pytz
import asyncio

# Brama Wyżynna
ZTM_DISPLAYS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/ee910ad8-8ffa-4e24-8ef9-d5a335b07ccb/download/displays.json"
ZTM_STOPS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/4c4025f0-01bf-41f7-a39f-d156d201b82b/download/stops.json"
WARSAW_TIMEZONE =  pytz.timezone("Europe/Warsaw")
ZTM_TIME_URL = "https://ckan2.multimediagdansk.pl/departures?stopId="

async def fetch_displays() -> List[Dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(ZTM_DISPLAYS_URL)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        data = response.json()
        print(f'fetch_displays data : {data}')
        return data.get("displays", [])

async def fetch_stops() -> List[Dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(ZTM_STOPS_URL)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        data = response.json()
        print(f'fetch_stops data : {data}')
        return data.get("stops", [])

def convert_utc_to_warsaw(utc_str: str) -> Union[str, None]:
    if not utc_str:
        return None
    dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    dt_warsaw = dt_utc.astimezone(WARSAW_TIMEZONE)
    return dt_warsaw.strftime("%Y-%m-%d %H:%M:%S")

async def get_departures_for_stop_name(stop_name: str) -> List[Dict]:
    displays = await fetch_displays()


    matched_displays = [
        d for d in displays if stop_name.lower() in d.get("name", "").lower()
    ]

    if not matched_displays:
        return []

    stop_ids = set()
    for d in matched_displays:

        if d.get("idStop1") and d["idStop1"] != 0:
            stop_ids.add(d["idStop1"])
        if d.get("idStop2") and d["idStop2"] != 0:
            stop_ids.add(d["idStop2"])

    if not stop_ids:
        return []


    async with httpx.AsyncClient() as client:
        tasks = [client.get(f"{ZTM_TIME_URL}{stop_id}") for stop_id in stop_ids]
        responses = await asyncio.gather(*tasks)

    combined_departures = []
    for resp, stop_id in zip(responses, stop_ids):
        resp.raise_for_status()
        data = resp.json()
        departures = data.get("departures", [])
        for dep in departures:
            dep["estimatedLocalTime"] = convert_utc_to_warsaw(dep.get("estimatedTime"))
            dep["stopId"] = stop_id
        combined_departures.extend(departures)


    combined_departures.sort(key=lambda d: d.get("estimatedLocalTime") or "")

    return combined_departures
