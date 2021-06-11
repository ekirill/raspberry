import aiofiles
from typing import Optional

from models.temperature import TempState

# thermal sensors paths
T1 = "/sys/bus/w1/devices/28-3c01d607a218/w1_slave"
T2 = "/sys/bus/w1/devices/28-3c01d075e72f/w1_slave"
T3 = "/sys/bus/w1/devices/28-3c01d075bb08/w1_slave"
T4 = "/sys/bus/w1/devices/28-3c01d075fdd4/w1_slave"

INCOMING_SENSORS = {
    "temp_in": T1,
    "temp_out": T2,
}

HEATING_CIRCLE_SENSORS = {
    "temp_in": T3,
    "temp_out": T4,
}


async def read_sensor(path) -> Optional[int]:
    async with aiofiles.open(path, mode='r') as f:
        async for ln in f:
            ln = ln.strip()
            if ln[-5:].isdigit():
                return round(float(ln[-5:]) / 1000.0)

async def get_temp_state() -> TempState:
    result = {
        "incoming": {},
        "heating_circle": {},
    }
    for k, sensor_path in INCOMING_SENSORS.items():
        result["incoming"][k] = await read_sensor(sensor_path)
    for k, sensor_path in HEATING_CIRCLE_SENSORS.items():
        result["heating_circle"][k] = await read_sensor(sensor_path)

    return TempState(**result)
