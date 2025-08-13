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

@app.get("/displays")
def get_displays():
    displays = ztm.fetch_displays()
    return {"displays": displays}


@app.get("/stops")
def get_stops():
    stops = ztm.fetch_stops()
    return {"stops": stops}



