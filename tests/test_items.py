from typing import Any

from flask import Flask
from psycopg.connection import Connection

from readerware_browser.queries.queries import get_items

# TODO: Test a bunch of Ajax requests
# TODO: Test expected values by ID


def test_all_books(app: Flask, conn: Connection[dict[str, Any]]) -> None:
    with app.test_request_context() as mock_context:
        items = get_items(
            mock_context.request,
            "books",
            conn.cursor(),
            author_id=None,
            series_id=None,
            unread=None,
        )
    assert isinstance(items, list)
    assert len(items) == 11


def test_unread_books(app: Flask, conn: Connection[dict[str, Any]]) -> None:
    with app.test_request_context() as mock_context:
        items = get_items(
            mock_context.request,
            "books",
            conn.cursor(),
            author_id=None,
            series_id=None,
            unread=True,
        )
    assert isinstance(items, list)
    assert len(items) == 3


def test_read_books(app: Flask, conn: Connection[dict[str, Any]]) -> None:
    with app.test_request_context() as mock_context:
        items = get_items(
            mock_context.request,
            "books",
            conn.cursor(),
            author_id=None,
            series_id=None,
            unread=False,
        )
    assert isinstance(items, list)
    assert len(items) == 8


def test_all_authors(app: Flask, conn: Connection[dict[str, Any]]) -> None:
    with app.test_request_context() as mock_context:
        items = get_items(
            mock_context.request,
            "authors",
            conn.cursor(),
            author_id=None,
            series_id=None,
            unread=None,
        )
    assert isinstance(items, list)
    assert len(items) == 3


def test_all_series(app: Flask, conn: Connection[dict[str, Any]]) -> None:
    with app.test_request_context() as mock_context:
        items = get_items(
            mock_context.request,
            "series",
            conn.cursor(),
            author_id=None,
            series_id=None,
            unread=None,
        )
    assert isinstance(items, list)
    assert len(items) == 3
