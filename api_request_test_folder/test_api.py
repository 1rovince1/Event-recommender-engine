from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Dict, Any
import json

app = FastAPI()

@app.get('/event_data', response_model = Dict[str, Any])
async def get_event_data():
    with open('data/all_events.json', 'r') as file:
        json_obj_1 = json.load(file)

    return json_obj_1

@app.get('/user_data', response_model = Dict[str, Any])
async def get_user_data():
    with open('data/event_user_data.json', 'r') as file:
        json_obj_2 = json.load(file)

    return JSONResponse(content=json_obj_2)