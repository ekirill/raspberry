from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


from models.temperature import TempState
from services.system import get_state, set_level

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class State(BaseModel):
    temperature: TempState
    level: int


class Level(BaseModel):
    level: int


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, level: int = None):
    if level is not None:
        await set_level(level)

    state = await get_state()
    levels = [
        {
            "level": idx,
            "on": idx == state.level
        }
        for idx in range(1, 10)
    ]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "state": state,
            "levels": levels,
        }
    )


@app.get("/state", response_model=State)
async def api_get_state():
    state = await get_state()
    return state


@app.post("/level")
async def api_set_level(level: Level):
    new_level = level.level
    await set_level(new_level)

    return {"status": "OK"}
