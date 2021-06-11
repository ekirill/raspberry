#!/usr/bin/env python3
import os

from repository import db
from config.settings import MIGRATIONS_PATH

def migrate():
    conn = db.get_connection_sync()
    for dirpath, dnames, fnames in os.walk(MIGRATIONS_PATH):
        for f in fnames:
            if f.endswith(".sql"):
                f = os.path.join(dirpath, f)
                print(f"Executing {f} ...", end="")
                with open(f) as fh:
                    sql = fh.read()
                    with conn.transaction():
                        with conn.cursor() as cur:
                            cur.execute(sql)
                print(f"OK")

        break


if __name__ == "__main__":
    migrate()
