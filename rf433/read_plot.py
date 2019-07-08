#!/usr/bin/env python3

from datetime import datetime
import redis
import RPi.GPIO as GPIO
import json

MAX_DURATION = 10
RECEIVE_PIN = 5
REDIS_DATA_KEY = 'rf433_plotdata'


def save_plot_data(plot_data):
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    r.set(REDIS_DATA_KEY, json.dumps(plot_data))


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RECEIVE_PIN, GPIO.IN)

    plot_data = [[], []]  # [[time of reading], [signal reading]]
    cumulative_time = 0
    beginning_time = datetime.now()
    print('**Started recording**')
    while cumulative_time < MAX_DURATION:
        time_delta = datetime.now() - beginning_time
        plot_data[0].append(time_delta)
        plot_data[1].append(GPIO.input(RECEIVE_PIN))
        cumulative_time = time_delta.seconds
    print('**Ended recording**')
    print(len(plot_data[0]), 'samples recorded')
    GPIO.cleanup()

    print('**Processing results**')
    for i in range(len(plot_data[0])):
        plot_data[0][i] = plot_data[0][i].seconds + plot_data[0][i].microseconds / 1000000.0
    save_plot_data(plot_data)
