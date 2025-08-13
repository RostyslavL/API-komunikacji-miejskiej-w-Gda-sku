from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from services import ztm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping_api():
    return {"message": "API is working"}
#
@app.get("/displays")
async def get_displays():
    displays = await ztm.fetch_displays()
    return {"displays": displays}



@app.get("/stops")
async def get_stops():
    stops = await ztm.fetch_stops()
    return {"stops": stops}

@app.get("/departures")
async def departures(
    stop_name: str = Query(
        ..., description="Substring of stop name, e.g. 'Brama Wyżynna'"
    )
):
    departures = await ztm.get_departures_for_stop_name(stop_name)
    if not departures:
        raise HTTPException(
            status_code=404,
            detail=f"No departures found for stops matching '{stop_name}'",
        )
    return {"stopName": stop_name, "departures": departures}



