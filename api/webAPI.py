
from fastapi import FastAPI, Query, HTTPException
import json
app = FastAPI(title="Brama Wyżynna Departures")

@app.get("/ping")
def ping_api():
    return {"message": "API is working"}
