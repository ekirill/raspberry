#!/usr/bin/env python3.7
import time
from typing import NamedTuple, Optional

from RPi import GPIO

LED_STATE = {
    'latest_signal': None,
    'state': GPIO.LOW,
    'change_time': time.time(),
}
LED_CHANGE_DELAY = 1.0

RECEIVE_PIN = 5
OUTPUT_PIN = 21
MICROSECOND = 0.000001
MIN_DELAY_TE = 5000
TRANSMIT_TIME = 0.3
LAZY_SLEEP_TIME = 0.01
STARTED_TO_LISTEN = None

PREV = 0
CURRENT = 1

IN_PROGRESS = False
WORD = []
POSSIBLE_WORD_LENGTH = 24


VALID_CODES = {16773830}


class SignalData(NamedTuple):
    value: int
    tm: float


SIGNALS = [SignalData(0, 0), SignalData(0, 0)]


def send_switch():
    if LED_STATE['latest_signal'] is None:
        LED_STATE['latest_signal'] = time.time()
    else:
        if time.time() - LED_STATE['latest_signal'] > LED_CHANGE_DELAY:
            LED_STATE['latest_signal'] = time.time()
            return

    if time.time() - LED_STATE['change_time'] > LED_CHANGE_DELAY:
        LED_STATE['state'] = GPIO.HIGH if LED_STATE['state'] == GPIO.LOW else GPIO.LOW
        LED_STATE['change_time'] = time.time()
        GPIO.output(OUTPUT_PIN, LED_STATE['state'])

        LED_STATE['latest_signal'] = None
        print("SET LED TO", LED_STATE['state'])


class CharData(NamedTuple):
    low_length: int
    high_length: int

    @property
    def value(self) -> int:
        # short high means `1`
        return int(self.low_length > self.high_length)

    def is_valid(self) -> bool:
        min_tm = min(self.high_length, self.low_length)
        max_tm = max(self.high_length, self.low_length)
        return min_tm >= 100 and 900 >= max_tm >= min_tm * 1.4

    def is_boundary(self) -> bool:
        return self.low_length > MIN_DELAY_TE

    def __str__(self):
        if self.is_boundary():
            chartype = "BOUNDARY"
        elif self.is_valid():
            chartype = "INNER"
        else:
            chartype = "INVALID"
        return (
            f"{chartype} {self.value} {self.low_length} {self.high_length}"
        )


class Word(NamedTuple):
    binary: str

    @property
    def decimal(self):
        return int(self.binary, 2)


def read():
    val = GPIO.input(RECEIVE_PIN)

    if not SIGNALS[CURRENT].tm:
        SIGNALS[CURRENT] = SignalData(val, time.time())
        return

    if SIGNALS[CURRENT].value == val:
        return

    new_current = SignalData(val, time.time())
    ch = None
    if val == GPIO.LOW and SIGNALS[PREV].tm:
        low_tm = SIGNALS[CURRENT].tm - SIGNALS[PREV].tm
        high_tm = new_current.tm - SIGNALS[CURRENT].tm
        if low_tm > 1.0:
            low_tm = 1.0
        if high_tm > 1.0:
            high_tm = 1.0
        ch = CharData(
            low_length=int(low_tm / MICROSECOND),
            high_length=int(high_tm / MICROSECOND),
        )
    SIGNALS[PREV] = SIGNALS[CURRENT]
    SIGNALS[CURRENT] = SignalData(val, time.time())

    return ch


def process_char(ch: CharData) -> Optional[Word]:
    global IN_PROGRESS
    global WORD

    if ch.is_boundary():
        if IN_PROGRESS:
            if len(WORD) == POSSIBLE_WORD_LENGTH:
                res = Word("".join(str(ch.value) for ch in WORD))
            else:
                res = None
            WORD = []
            return res
        else:
            WORD = []
            IN_PROGRESS = True
            return

    if not ch.is_valid():
        if IN_PROGRESS:
            IN_PROGRESS = False
            WORD = []
            return

    if IN_PROGRESS:
        WORD.append(ch)

    if len(WORD) > POSSIBLE_WORD_LENGTH:
        IN_PROGRESS = False
        WORD = []


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RECEIVE_PIN, GPIO.IN)
    GPIO.setup(OUTPUT_PIN, GPIO.OUT)
    GPIO.output(OUTPUT_PIN, LED_STATE['state'])
    cumulative_time = 0

    print('**Started recording**')

    try:
        while True:
            read_ch = read()
            if read_ch:
                STARTED_TO_LISTEN = time.time()
                word = process_char(read_ch)
                if word:
                    print(word.binary, word.decimal)
                    if word.decimal in VALID_CODES:
                        send_switch()

            if STARTED_TO_LISTEN:
                if time.time() - STARTED_TO_LISTEN > TRANSMIT_TIME:
                    STARTED_TO_LISTEN = None

            if not STARTED_TO_LISTEN:
                time.sleep(LAZY_SLEEP_TIME)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
