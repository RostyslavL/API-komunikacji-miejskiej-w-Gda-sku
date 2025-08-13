import httpx
from typing import List, Dict, Union
from datetime import datetime
import pytz
# Brama Wyżynna
ZTM_DISPLAYS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/ee910ad8-8ffa-4e24-8ef9-d5a335b07ccb/download/displays.json"
ZTM_STOPS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/4c4025f0-01bf-41f7-a39f-d156d201b82b/download/stops.json"
WARSAW_TIMEZONE =  pytz.timezone("Europe/Warsaw")

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