from pydantic import BaseModel

from controllers.level import MIN_LEVEL, MAX_LEVEL
from models.temperature import TempState
from repository.db import get_connection
from repository.level import get_level, save_level
from repository.temperature import get_last_temp_state


class State(BaseModel):
    temperature: TempState
    level: int


async def get_state() -> State:
    conn = await get_connection()
    async with conn.transaction():
        temp_state = await get_last_temp_state(conn)
        level = await get_level(conn)

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
        current = await get_level(conn)
        if current != new_level:
            await save_level(conn, new_level)
