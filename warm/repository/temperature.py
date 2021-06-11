from typing import Optional

from models.temperature import TempState


async def get_last_temp_state(connection) -> Optional[TempState]:
    async with connection.cursor() as cur:
        await cur.execute("SELECT t1, t2, t3, t4 FROM warm.temperature ORDER BY dt DESC LIMIT 1")
        row = await cur.fetchone()
        if row:
            result = {
                "incoming": {
                    "temp_in": row[0],
                    "temp_out": row[1],
                },
                "heating_circle": {
                    "temp_in": row[2],
                    "temp_out": row[3],
                },
            }
            return TempState(**result)

async def save_temp_state(connection, temp_state: TempState):
    async with connection.cursor() as cur:
        await cur.execute(
            "INSERT INTO warm.temperature (t1, t2, t3, t4) VALUES (%s, %s, %s, %s)",
            (
                temp_state.incoming.temp_in, temp_state.incoming.temp_out,
                temp_state.heating_circle.temp_in, temp_state.heating_circle.temp_out,
            )
        )
