import httpx
from typing import List, Dict, Union, Tuple
from datetime import datetime
import pytz
import asyncio

# ZTM API Configuration
ZTM_DISPLAYS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/ee910ad8-8ffa-4e24-8ef9-d5a335b07ccb/download/displays.json"
ZTM_STOPS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/4c4025f0-01bf-41f7-a39f-d156d201b82b/download/stops.json"
WARSAW_TIMEZONE = pytz.timezone("Europe/Warsaw")
ZTM_TIME_URL = "https://ckan2.multimediagdansk.pl/departures?stopId="


async def fetch_displays() -> Tuple[Dict, List[Dict]]:

    async with httpx.AsyncClient() as client:
        response = await client.get(ZTM_DISPLAYS_URL)
        if response.status_code == 404:
            return {}, []
        response.raise_for_status()
        data = response.json()


        if isinstance(data, list):

            displays = data
        elif isinstance(data, dict):

            displays = data.get("displays", [])
            if not displays:
                displays = data.get("data", [])

            if not displays and "name" in data:
                displays = [data]
        else:
            displays = []

        print(f'fetch_displays data keys: {data.keys() if isinstance(data, dict) else type(data)}')
        print(
            f'displays type: {type(displays)}, length: {len(displays) if isinstance(displays, list) else "not a list"}')
        return data, displays


async def fetch_stops() -> Tuple[Dict, List[Dict]]:
    async with httpx.AsyncClient() as client:
        response = await client.get(ZTM_STOPS_URL)
        if response.status_code == 404:
            return {}, []
        response.raise_for_status()
        data = response.json()
        stops = data.get("stops", [])
        print(f'fetch_stops data keys: {data.keys() if isinstance(data, dict) else type(data)}')
        return data, stops


def convert_utc_to_warsaw(utc_str: str) -> Union[str, None]:
    if not utc_str:
        return None
    try:
        dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        dt_warsaw = dt_utc.astimezone(WARSAW_TIMEZONE)
        return dt_warsaw.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"Error converting time '{utc_str}': {e}")
        return None


async def get_departures_for_stop_name(stop_name: str) -> List[Dict]:
    data, displays = await fetch_displays()

    if not displays:
        print(f"No displays found. Data structure: {type(data)}")
        return []

    print(f"Displays type: {type(displays)}")
    if displays:
        print(f"First display type: {type(displays[0])}")
        print(f"First display content: {displays[0]}")

    flat_displays = []
    for item in displays:
        if isinstance(item, list):
            flat_displays.extend(item)
        elif isinstance(item, dict):
            flat_displays.append(item)
        else:
            print(f"Unexpected item type in displays: {type(item)}")

    matched_displays = [
        d for d in flat_displays if isinstance(d, dict) and stop_name.lower() in d.get("name", "").lower()
    ]

    if not matched_displays:
        print(f"No displays found matching '{stop_name}'")
        return []

    stop_ids = set()
    for d in matched_displays:
        if d.get("idStop1") and d["idStop1"] != 0:
            stop_ids.add(d["idStop1"])
        if d.get("idStop2") and d["idStop2"] != 0:
            stop_ids.add(d["idStop2"])

    if not stop_ids:
        print("No valid stop IDs found in matched displays")
        return []

    print(f"Found stop IDs: {stop_ids}")

    try:
        async with httpx.AsyncClient() as client:
            tasks = [client.get(f"{ZTM_TIME_URL}{stop_id}") for stop_id in stop_ids]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        print(f"Error fetching departures: {e}")
        return []

    combined_departures = []
    for resp, stop_id in zip(responses, stop_ids):
        try:
            if isinstance(resp, Exception):
                print(f"Error for stop {stop_id}: {resp}")
                continue

            resp.raise_for_status()
            data = resp.json()
            departures = data.get("departures", [])

            for dep in departures:
                dep["estimatedLocalTime"] = convert_utc_to_warsaw(dep.get("estimatedTime"))
                dep["stopId"] = stop_id

            combined_departures.extend(departures)
            print(f"Added {len(departures)} departures for stop {stop_id}")

        except Exception as e:
            print(f"Error processing departures for stop {stop_id}: {e}")
            continue

    combined_departures.sort(key=lambda d: d.get("estimatedLocalTime") or "")

    print(f"Total departures found: {len(combined_departures)}")
    return combined_departures