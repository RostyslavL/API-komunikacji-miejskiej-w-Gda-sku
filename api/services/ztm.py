import httpx
from typing import List, Dict
# Brama Wyżynna
ZTM_DISPLAYS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/ee910ad8-8ffa-4e24-8ef9-d5a335b07ccb/download/displays.json"
ZTM_STOPS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/4c4025f0-01bf-41f7-a39f-d156d201b82b/download/stops.json"


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
