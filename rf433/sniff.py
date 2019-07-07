#!/usr/bin/env python3.7

import time
# import matplotlib.pyplot as pyplot
from RPi import GPIO

RECEIVED_SIGNALS = []  #[[time of reading], [signal reading]]
MAX_DURATION = 5
RECEIVE_PIN = 6

MICROSECOND = 0.000001
MIN_TE = 250 * MICROSECOND
MAX_TE = 450 * MICROSECOND


SIGNALS = [(), ()]

PREV = 0
CURRENT = 1

VAL = 0
TM = 1

CAME = {
    "state": 0,
}


def read():
    val = GPIO.input(RECEIVE_PIN)
    val = int(val == GPIO.HIGH)

    if SIGNALS[CURRENT]:
        SIGNALS[PREV] = SIGNALS[CURRENT]

    SIGNALS[CURRENT] = (val, time.time())


def get_change_tm():
    if SIGNALS[CURRENT] and SIGNALS[PREV]:
        return SIGNALS[CURRENT][TM] - SIGNALS[PREV][TM]


def process_came():
    if CAME['state'] == 0:
        if SIGNALS[CURRENT][VAL] == 0:
            CAME['state'] = 1
        return

    change_tm = get_change_tm()
    if change_tm is None:
        CAME['state'] = 0
        return

    if CAME['state'] == 1:
        if SIGNALS[CURRENT][VAL] == 0:
            return

        if MIN_TE <= change_tm <= MAX_TE:
            CAME['state'] = 2
            CAME['data'] = [0] * 24
            print("START CAME")
        else:
            print(f"{change_tm:.06f}")
            CAME['state'] = 0

        return

    if CAME['state'] == 2:
        if SIGNALS[CURRENT][VAL] == 1:
            pass
        else:
            pass
            # if((p_len>5000)&&(came.dat_bit==CM_BITS12 || came.dat_bit==CM_BITS24)) came.state=100;



if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RECEIVE_PIN, GPIO.IN)
    cumulative_time = 0

    print('**Started recording**')

    try:
        while True:
            read()
            process_came()



    except KeyboardInterrupt:
        pass

