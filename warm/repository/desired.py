from typing import Optional

from pydantic import BaseModel


class Desired(BaseModel):
    heaters_temp: Optional[int]
    level: Optional[float]


async def get_desired(connection) -> Optional[Desired]:
    async with connection.cursor() as cur:
        await cur.execute("SELECT level, heaters_temp FROM warm.desired ORDER BY dt DESC LIMIT 1")
        row = await cur.fetchone()
        if row:
            return Desired(
                level=row[0],
                heaters_temp=row[1],
            )

async def save_level(connection, level: int):
    async with connection.cursor() as cur:
        await cur.execute("INSERT INTO warm.desired (level) VALUES (%s)", (level,))
