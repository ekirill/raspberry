from pydantic import BaseModel

from controllers.level import MIN_LEVEL, MAX_LEVEL, get_desired_level
from models.temperature import TempState
from repository.db import get_connection
from controllers.level import get_level
from repository.desired import save_level
from repository.temperature import get_last_temp_state


class State(BaseModel):
    temperature: TempState
    level: int


async def get_state() -> State:
    conn = await get_connection()
    async with conn.transaction():
        temp_state = await get_last_temp_state(conn)
        desired = await get_desired_level(conn)
        level = desired.level

    return State(
        temperature=temp_state,
        level=level,
    )


async def set_level(new_level: int):
    if new_level < MIN_LEVEL:
        new_level = MIN_LEVEL
    if new_level > MAX_LEVEL:
        new_level = MAX_LEVEL

    conn = await get_connection()
    async with conn.transaction():
        await save_level(conn, new_level)
