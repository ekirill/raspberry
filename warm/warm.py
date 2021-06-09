#!/usr/bin/env python3
import logging
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
    
logging.basicConfig(
    format='%(asctime)s %(message)s', level=logging.DEBUG
)

logger = logging.getLogger("warm")

# they say it works more precisely for servo
factory = PiGPIOFactory()

MICROSERVO_9G = (0.000544, 0.0024 * 0.43)
FS5106S = (0.000620 * 1.05, 0.002600 * 0.55)


class PowerSelector:
    _min_pulse = FS5106S[0]
    _max_pulse = FS5106S[1]
    
    _min_level = 1
    _max_level = 9
    
    _min_pos = -1.0
    _max_pos = 1.0
    _delta = (_max_pos - _min_pos) / (_max_level - _min_level)
    
    _level = (_max_level - _min_level + 1) // 2
    
    def __init__(self, pin):
        self._servo = Servo(
            pin, self._pos,
            self._min_pulse, self._max_pulse, 20/1000,
            pin_factory=factory
        )
        self.set_level(self._level)
    
    @property
    def _pos(self):
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
    
    def set_level(self, new_level):
        if new_level < self._min_level:
            new_level = self._min_level
        
        if new_level > self._max_level:
            new_level = self._max_level
        
        self._level = new_level
        
        logger.info(f"Setting power level to {new_level}")
        pos = self._pos
        logger.debug(f"Servo pos is set to {pos}")
        self._servo.value = self._pos
        sleep(3)
        self._servo.detach()
    
    def detach(self):
        self._servo.detach()

def main():
    logger.info("Start")
    power = PowerSelector(21)
    try:
        while True:
            for level in range(1, 10):
                power.set_level(level)
            for level in range(8, 0, -1):
                power.set_level(level)
    finally:
        power.detach()

if __name__ == "__main__":
    main()	
