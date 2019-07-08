#!/usr/bin/env python3
import json
from typing import List

import matplotlib.pyplot as pyplot
import redis

REDIS_DATA_KEY = 'rf433_plotdata'
MAX_DURATION = 10


def get_plot_data() -> List:
    r = redis.Redis(host='raspberrypi', port=6379, db=0)
    raw_data = r.get(REDIS_DATA_KEY)
    plot_data = json.loads(raw_data)
    return plot_data


if __name__ == '__main__':
    plot_data = get_plot_data()

    print('**Plotting results**')
    pyplot.plot(plot_data[0], plot_data[1])
    pyplot.axis([0, MAX_DURATION, -1, 2])
    pyplot.show()
