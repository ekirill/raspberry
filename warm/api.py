from fastapi import FastAPI
from pydantic import BaseModel

from controllers.level import MIN_LEVEL, MAX_LEVEL
from repository.db import get_connection
from repository.level import save_level, get_level
from repository.temperature import get_last_temp_state
from models.temperature import TempState

app = FastAPI()


class State(BaseModel):
    temperature: TempState
    level: int


class Level(BaseModel):
    level: int

@app.get("/", response_model=State)
async def get_state():
    conn = await get_connection()
    async with conn.transaction():
        temp_state = await get_last_temp_state(conn)
        level = await get_level(conn)

    return {
        "temperature": temp_state,
        "level": level,
    }


@app.post("/level")
async def set_level(level: Level):
    new_level = level.level
    if new_level < MIN_LEVEL:
        new_level = MIN_LEVEL
    if new_level > MAX_LEVEL:
        new_level = MAX_LEVEL

    conn = await get_connection()
    async with conn.transaction():
        await save_level(conn, new_level)

    return {"status": "OK"}
