import aiofiles
from typing import Optional

from models.temperature import TempState

# thermal sensors paths
T1_red = "/sys/bus/w1/devices/28-000000bc5414/w1_slave"
T2_yellow = "/sys/bus/w1/devices/28-000000c0593e/w1_slave"


async def read_sensor(path) -> Optional[int]:
    async with aiofiles.open(path, mode='r') as f:
        async for ln in f:
            if " t=" not in ln:
                continue
            ln = ln.strip()
            t = ln[-7:].replace("t", " ").replace("=", " ").strip()
            return round(float(t) / 1000.0)


async def get_temp_state() -> TempState:
    result = {
        "incoming": await read_sensor(T1_red),
        "outdoor": 1,
        "heating_circle": {
            "temp_in": await read_sensor(T2_yellow),
            "temp_out": 1,
        },
    }

    return TempState(**result)
