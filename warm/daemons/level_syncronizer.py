#!/usr/bin/env python3
import asyncio
import logging

from psycopg3 import OperationalError

from controllers.level import get_level, set_level
from repository.db import get_connection
from repository.level import get_level as db_get_level
from services.monitoring import get_statsd

logging.basicConfig(
    format='%(asctime)s %(message)s', level=logging.DEBUG
)

logger = logging.getLogger("level_sync")


async def level_sync():
    conn = await get_connection()
    while True:
        await asyncio.sleep(3.0)
        try:
            level = await get_level()

            db_level = await db_get_level(conn)
            get_statsd().gauge("warm.level", db_level)

            if db_level and db_level != level:
                logger.info(f"Level change detected {level} -> {db_level}")
                await set_level(db_level)
        except OperationalError as e:
            logger.error(f"DB ERROR, reconnecting: {e}")
            await conn.close()
            conn = await get_connection()
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    asyncio.run(level_sync())
