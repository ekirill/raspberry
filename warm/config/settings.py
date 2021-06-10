from environs import Env
from pathlib import Path

env = Env()
env.read_env()

PROJECT_PATH = Path(__file__).resolve().parent.parent
MIGRATIONS_PATH = PROJECT_PATH / "migrations"

DB_CONNECTION_STRING = env("WARM_DB_CONNECTION_STRING")
