from fastapi import FastAPI
from pydantic import BaseModel

from controllers.level import get_level
from controllers.temperature import get_temp_state
from models.temperature import TempState

app = FastAPI()


class State(BaseModel):
    temperature: TempState
    level: int


class Level(BaseModel):
    level: int

@app.get("/", response_model=State)
async def get_state():
    return {
        "temperature": await get_temp_state(),
        "level": get_level(),
    }


@app.post("/level")
def set_level(level: Level):
    return {"status": "OK"}
