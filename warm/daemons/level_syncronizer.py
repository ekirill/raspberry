#!/usr/bin/env python3
import asyncio
import logging
from time import time

from psycopg3 import OperationalError

from controllers.level import get_level, set_level, get_desired_level
from repository.db import get_connection
from services.monitoring import get_statsd

logging.basicConfig(
    format='%(asctime)s %(message)s', level=logging.DEBUG
)

logger = logging.getLogger("level_sync")


MIN_TIME_TO_CHANGE = 20 * 60


async def level_sync():
    conn = await get_connection()
    last_change_time = None

    while True:
        await asyncio.sleep(5.0)

        try:
            level = await get_level()
            get_statsd().gauge("warm.level", level)

            if last_change_time and time() - last_change_time < MIN_TIME_TO_CHANGE:
                continue

            desired_level = await get_desired_level(conn)
            # desired_level = await db_get_level(conn)

            if desired_level and desired_level != level:
                logger.info(f"Level change detected {level} -> {desired_level}")
                await set_level(desired_level)
                last_change_time = time()
        except OperationalError as e:
            logger.error(f"DB ERROR, reconnecting: {e}")
            await conn.close()
            conn = await get_connection()
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    asyncio.run(level_sync())
