import aiofiles
from typing import Optional

from models.temperature import TempState

# thermal sensors paths
T1 = "/sys/bus/w1/devices/28-3c01d607a218/w1_slave"
T2 = "/sys/bus/w1/devices/28-3c01d075e72f/w1_slave"
T3 = "/sys/bus/w1/devices/28-3c01d075bb08/w1_slave"
T4 = "/sys/bus/w1/devices/28-3c01d075fdd4/w1_slave"

INCOMING_SENSOR_PATH = T1
OUTDOOR_SENSOR_PATH = T2

HEATING_CIRCLE_SENSORS = {
    "temp_in": T3,
    "temp_out": T4,
}


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
        "heating_circle": {},
        "incoming": await read_sensor(INCOMING_SENSOR_PATH),
        "outdoor": await read_sensor(OUTDOOR_SENSOR_PATH),
    }

    for k, sensor_path in HEATING_CIRCLE_SENSORS.items():
        result["heating_circle"][k] = await read_sensor(sensor_path)

    return TempState(**result)
