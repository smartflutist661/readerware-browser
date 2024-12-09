from typing import Any

from psycopg.connection import Connection

from readerware_browser.queries.queries import get_total


def test_books_total(conn: Connection[dict[str, Any]]) -> None:
    assert get_total("books", conn.cursor(), author_id=None, series_id=None, unread=None) == 11


def test_unread_books_total(conn: Connection[dict[str, Any]]) -> None:
    assert get_total("books", conn.cursor(), author_id=None, series_id=None, unread=True) == 3


def test_read_books_total(conn: Connection[dict[str, Any]]) -> None:
    assert get_total("books", conn.cursor(), author_id=None, series_id=None, unread=False) == 8


def test_author_books_total(conn: Connection[dict[str, Any]]) -> None:
    assert get_total("books", conn.cursor(), author_id=1, series_id=None, unread=None) == 1
    assert get_total("books", conn.cursor(), author_id=2, series_id=None, unread=None) == 4
    assert get_total("books", conn.cursor(), author_id=3, series_id=None, unread=None) == 6


def test_authors_total(conn: Connection[dict[str, Any]]) -> None:
    assert get_total("authors", conn.cursor(), author_id=None, series_id=None, unread=None) == 3
    assert get_total("authors", conn.cursor(), author_id=1, series_id=None, unread=None) == 1
    assert get_total("authors", conn.cursor(), author_id=2, series_id=None, unread=None) == 1
    assert get_total("authors", conn.cursor(), author_id=3, series_id=None, unread=None) == 1


# This page does not exist
def test_author_series_total(conn: Connection[dict[str, Any]]) -> None:
    assert get_total("series", conn.cursor(), author_id=1, series_id=None, unread=None) == 0
    # TODO: The multi-author series is currently arbitrarily associated with one of the authors
    # Need to handle multi-author series more correctly
    auth2_total = get_total("series", conn.cursor(), author_id=2, series_id=None, unread=None)
    assert isinstance(auth2_total, int) and auth2_total >= 1
    auth3_total = get_total("series", conn.cursor(), author_id=3, series_id=None, unread=None)
    assert isinstance(auth3_total, int) and auth3_total >= 1


def test_series_books_total(conn: Connection[dict[str, Any]]) -> None:
    assert get_total("books", conn.cursor(), author_id=None, series_id=1, unread=None) == 2
    assert get_total("books", conn.cursor(), author_id=None, series_id=2, unread=None) == 3
    assert get_total("books", conn.cursor(), author_id=None, series_id=3, unread=None) == 5


# This page does not exist
def test_series_authors_total(conn: Connection[dict[str, Any]]) -> None:
    assert get_total("authors", conn.cursor(), author_id=None, series_id=1, unread=None) == 1
    assert get_total("authors", conn.cursor(), author_id=None, series_id=2, unread=None) == 1
    assert get_total("authors", conn.cursor(), author_id=None, series_id=3, unread=None) == 2


def test_series_total(conn: Connection[dict[str, Any]]) -> None:
    assert get_total("series", conn.cursor(), author_id=None, series_id=None, unread=None) == 3
    assert get_total("series", conn.cursor(), author_id=None, series_id=1, unread=None) == 1
    assert get_total("series", conn.cursor(), author_id=None, series_id=2, unread=None) == 1
    assert get_total("series", conn.cursor(), author_id=None, series_id=3, unread=None) == 1
