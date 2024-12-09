from collections.abc import Generator
from pathlib import Path
from typing import Any

import psycopg
import pytest
from flask import Flask
from flask.testing import FlaskClient
from psycopg.connection import Connection
from psycopg.rows import dict_row
from pytest_postgresql.executor import PostgreSQLExecutor

from readerware_browser import APP


@pytest.fixture(name="app", scope="session")
def app_fixture() -> Generator[Flask, None, None]:
    APP.config.update(
        {
            "TESTING": True,
        }
    )

    yield APP


@pytest.fixture(name="conn", scope="session")
def conn_fixture(
    postgresql_proc: PostgreSQLExecutor,
) -> Generator[Connection[dict[str, Any]], None, None]:

    conn = psycopg.connect(
        dbname=postgresql_proc.user,
        user=postgresql_proc.user,
        password=postgresql_proc.password,
        host=postgresql_proc.host,
        port=postgresql_proc.port,
        row_factory=dict_row,
    )

    with open(Path(__file__).parent / "test_setup.sql", encoding="utf8") as sql_file:
        conn.cursor().execute(sql_file.read())
        conn.commit()

    yield conn


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
