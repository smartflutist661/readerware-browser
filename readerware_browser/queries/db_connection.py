import os
from typing import Any

import psycopg
from psycopg.connection import Connection
from psycopg.rows import dict_row


def get_db_connection() -> Connection[dict[str, Any]]:
    conn = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        row_factory=dict_row,
    )
    return conn
