import psycopg3

from config.settings import DB_CONNECTION_STRING


async def get_connection():
    return await psycopg3.AsyncConnection.connect(DB_CONNECTION_STRING)

def get_connection_sync():
    return psycopg3.connect(DB_CONNECTION_STRING)
