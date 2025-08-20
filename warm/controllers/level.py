import asyncio
import logging
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

from repository.db import get_connection
from repository.desired import get_desired, Desired
from repository.level import get_level as db_get_level
from repository.temperature import get_last_temp_state

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

    _pos_change_delta = 0.05
    _pos_change_time = 0.2

    def __init__(self, servo: Servo):
        self._servo = servo
        self._current_pos = 0.0

    @classmethod
    async def create(cls, pin: int, level: float) -> "PowerSelector":
        servo = Servo(
            pin, 0.0,
            cls.pulse[0], cls.pulse[1], 20 / 1000,
            pin_factory=factory
        )
        instance = cls(servo)
        instance._level = level

        instance._servo.value = instance._pos
        instance._current_pos = instance._pos

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

    async def set_level(self, new_level: float, force: bool = False):
        if new_level < self._min_level:
            new_level = self._min_level

        if new_level > self._max_level:
            new_level = self._max_level

        if self._level == new_level:
            if not force:
                return
            logger.info(f"Resyncing power level {new_level}")    
        else:
            logger.info(f"Setting power level from {self._level} to {new_level}")

        self._level = new_level

        await self._update_servo_pos()

    async def resync(self, level: float):
        return await self.set_level(level, force=True)

    def get_level(self) -> float:
        return self._level

    async def _update_servo_pos(self):
        new_pos = self._pos
        old_pos = self._current_pos
        logger.debug(f"Moving Servo pos from {old_pos} to {new_pos}")

        step = self._pos_change_delta
        if abs(new_pos - old_pos) > step:
            logger.debug("Slow mode ON")
            if new_pos < old_pos:
                step = -step

            while abs(new_pos - old_pos) > abs(step):
                old_pos = round(old_pos + step, 2)

                if old_pos > self._max_pos or old_pos < self._min_pos:
                    break

                self._servo.value = old_pos
                logger.debug(f"Slow mode pos {old_pos}")
                await asyncio.sleep(self._pos_change_time)

        self._servo.value = new_pos
        self._current_pos = new_pos


_powerSelector = None


async def get_selector() -> PowerSelector:
    global _powerSelector

    if _powerSelector is None:
        conn = await get_connection()
        async with conn.transaction():
            desired = await get_desired_level(conn)
            level = 4
            if desired and desired.level:
                level = desired.level

            _powerSelector = await PowerSelector.create(SERVO_PIN, level)

    return _powerSelector


async def get_level() -> float:
    selector = await get_selector()
    return selector.get_level()


async def set_level(new_level: float):
    selector = await get_selector()
    await selector.set_level(new_level)


async def resync_level(level: float):
    selector = await get_selector()
    await selector.resync(level)


def evaluate_level(desired_temp: int, incoming_temp: int) -> float:
    desired_percentage = desired_temp / incoming_temp
    # formula is evaluated by https://planetcalc.ru/5992/ and some historical stat data
    level = 162.99 * (desired_percentage**3) - 307.49 * (desired_percentage**2) + 193.44 * desired_percentage - 38.63

    if level < MIN_LEVEL:
        level = MIN_LEVEL
    if level > MAX_LEVEL:
        level = MAX_LEVEL

    return float(level)


async def get_desired_level(conn) -> Desired:
    desired = await get_desired(conn)
    if desired:
        if desired.level:
            return Desired(
                level=float(desired.level),
                heaters_temp=None,
            )

        if desired.heaters_temp:
            temp_state = await get_last_temp_state(conn)
            if temp_state:
                evaluated_level = evaluate_level(desired.heaters_temp, temp_state.incoming)
                return Desired(
                    level=evaluated_level,
                    heaters_temp=desired.heaters_temp,
                )

    db_level = await db_get_level(conn)
    return Desired(
        level=float(db_level),
        heaters_temp=None,
    )
