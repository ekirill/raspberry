import asyncio
import logging
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

from repository.db import get_connection
from repository.level import get_level as db_get_level

logging.basicConfig(
    format='%(asctime)s %(message)s', level=logging.DEBUG
)

logger = logging.getLogger("level")

# they say it works more precisely for servo
factory = PiGPIOFactory()
SERVO_PIN = 21

# 90 degree limited pulse min and max
MICROSERVO_9G = (0.000544, 0.0024 * 0.43)
FS5106S = (0.000620, 0.002600 * 0.53)

MIN_LEVEL = 1
MAX_LEVEL = 9


class PowerSelector:
    pulse = FS5106S

    _min_level = MIN_LEVEL
    _max_level = MAX_LEVEL

    _min_pos = -1.0
    _max_pos = 1.0
    _delta = (_max_pos - _min_pos) / (_max_level - _min_level)

    _level = (_max_level - _min_level + 1) // 2

    _pos_change_delta = 0.01
    _pos_change_time = 0.1

    def __init__(self, servo: Servo):
        self._servo = servo

    @classmethod
    async def create(cls, pin: int, level: int) -> "PowerSelector":
        servo = Servo(
            pin, 0.0,
            cls.pulse[0], cls.pulse[1], 20 / 1000,
            pin_factory=factory
        )
        instance = cls(servo)
        instance._level = level

        # dirty hack to give more time if servo was too far from level at init
        instance._servo.value = instance._pos
        await asyncio.sleep(5.0)
        instance.detach()

        return instance

    @property
    def _pos(self) -> float:
        # level 1 = 1
        # level 9 = -1

        # the servo is installed reversed,
        # so -1 - is max power, 1 - is min
        pos = self._max_pos - \
              (self._level - self._min_level) * self._delta

        if pos > self._max_pos:
            pos = self._max_pos

        if pos < self._min_pos:
            pos = self._min_pos
        return pos

    async def set_level(self, new_level):
        if new_level < self._min_level:
            new_level = self._min_level

        if new_level > self._max_level:
            new_level = self._max_level

        if self._level == new_level:
            return

        logger.info(f"Setting power level from {self._level} to {new_level}")
        old_pos = self._pos
        self._level = new_level

        await self._update_servo_pos(old_pos)

    def get_level(self) -> int:
        return self._level

    async def _update_servo_pos(self, old_pos: float):
        new_pos = self._pos
        logger.debug(f"Moving Servo pos from {old_pos} to {new_pos}")

        step = self._pos_change_delta
        if new_pos < old_pos:
            step = -step

        while abs(new_pos - old_pos) > abs(step):
            old_pos += step

            if old_pos > self._max_pos:
                old_pos = self._max_pos
            if old_pos < self._min_pos:
                old_pos = self._min_pos

            self._servo.value = old_pos
            await asyncio.sleep(self._pos_change_time)

        self._servo.value = new_pos
        await asyncio.sleep(3.0)
        self.detach()

    def detach(self):
        self._servo.detach()


_powerSelector = None


async def get_selector() -> PowerSelector:
    global _powerSelector

    if _powerSelector is None:
        conn = await get_connection()
        async with conn.transaction():
            level = await db_get_level(conn)
            if level is None:
                level = 4

            _powerSelector = await PowerSelector.create(SERVO_PIN, level)

    return _powerSelector


async def get_level() -> int:
    selector = await get_selector()
    return selector.get_level()


async def set_level(new_level: int):
    selector = await get_selector()
    await selector.set_level(new_level)
