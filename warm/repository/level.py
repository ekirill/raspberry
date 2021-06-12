from typing import Optional


async def get_level(connection) -> Optional[int]:
    async with connection.cursor() as cur:
        await cur.execute("SELECT level FROM warm.level ORDER BY dt DESC LIMIT 1")
        row = await cur.fetchone()
        if row:
            return row[0]

async def save_level(connection, level: int):
    async with connection.cursor() as cur:
        await cur.execute("INSERT INTO warm.level (level) VALUES (%s)", (level,))
