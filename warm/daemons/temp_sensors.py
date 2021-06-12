#!/usr/bin/env python3
import asyncio
import logging

from controllers import temperature
from repository.db import get_connection
from repository.temperature import get_last_temp_state, save_temp_state

logging.basicConfig(
    format='%(asctime)s %(message)s', level=logging.DEBUG
)

logger = logging.getLogger("temp_sensors")


async def monitor_sensors():
    conn = await get_connection()
    async with conn.transaction():
        latest_temps = await get_last_temp_state(conn)

    logger.info(f"Latest DB temps are: {latest_temps.dict() if latest_temps else None}")

    while True:
        temps = await temperature.get_temp_state()

        need_save = latest_temps is None
        if not need_save:
            need_save = (
                latest_temps.incoming.temp_in != temps.incoming.temp_in or
                latest_temps.incoming.temp_out != temps.incoming.temp_out or
                latest_temps.heating_circle.temp_in != temps.heating_circle.temp_in or
                latest_temps.heating_circle.temp_out != temps.heating_circle.temp_out
            )

        if need_save:
            logger.info(f"Temps changed: {temps.dict()}")
            async with conn.transaction():
                await save_temp_state(conn, temps)
            latest_temps = temps

        await asyncio.sleep(60.0)


if __name__ == "__main__":
    asyncio.run(monitor_sensors())