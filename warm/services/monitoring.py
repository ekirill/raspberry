import statsd

from config.settings import STATSD_HOST, STATSD_PORT

_client = None


def get_statsd():
    global _client
    if _client is None:
        _client = statsd.StatsClient(STATSD_HOST, STATSD_PORT)

    return _client
