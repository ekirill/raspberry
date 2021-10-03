from environs import Env
from pathlib import Path

env = Env()
env.read_env()

PROJECT_PATH = Path(__file__).resolve().parent.parent
MIGRATIONS_PATH = PROJECT_PATH / "migrations"

DB_CONNECTION_STRING = env("WARM_DB_CONNECTION_STRING")

STATSD_HOST = env("WARM_STATSD_HOST")
STATSD_PORT = env("WARM_STATSD_PORT")
