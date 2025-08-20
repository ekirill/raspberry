#!/usr/bin/env python3
import asyncio
import logging

from psycopg3 import OperationalError

from controllers.level import get_level, set_level, get_desired_level
from repository.db import get_connection
from repository.temperature import get_last_temp_state
from services.monitoring import get_statsd

logging.basicConfig(
    format='%(asctime)s %(message)s', level=logging.DEBUG
)

logger = logging.getLogger("level_sync")


MIN_TIME_TO_CHANGE = 20 * 60
LEVEL_SWITCH_THRESHOLD = 5


async def level_sync():
    conn = await get_connection()

    while True:
        await asyncio.sleep(5.0)

        try:
            level = await get_level()
            get_statsd().gauge("warm.level", level)

            new_level = None

            desired = await get_desired_level(conn)

            if desired:
                if desired.heaters_temp:
                    current_temp = await get_last_temp_state(conn)
                    if abs(desired.heaters_temp - current_temp.heating_circle.temp_in) > LEVEL_SWITCH_THRESHOLD:
                        new_level = desired.level
                else:
                    if desired.level != level:
                        new_level = desired.level

            if new_level:
                logger.info(f"Level change detected {level} -> {new_level}")
                await set_level(new_level)

        except OperationalError as e:
            logger.error(f"DB ERROR, reconnecting: {e}")
            await conn.close()
            conn = await get_connection()
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    asyncio.run(level_sync())
