from pathlib import Path
from typing import (
    Any,
    Optional,
    cast,
)

from flask.wrappers import (
    Request,
    Response,
)
from psycopg.cursor import Cursor

from readerware_browser.models.book import Book
from readerware_browser.search import build_search
from readerware_browser.sort import build_sort


def get_book_query_base() -> str:
    with (Path(__file__).parent / "books.sql").open(encoding="utf8") as books_query_file:
        return books_query_file.read()


def get_book(book_id: int, db_cursor: Cursor[dict[str, Any]]) -> Optional[Book]:
    query = get_book_query_base()
    query += " where book_id = %s;"

    return cast(Optional[Book], db_cursor.execute(query, [book_id]).fetchone())


def get_books(request: Request, db_cursor: Cursor[dict[str, Any]]) -> list[Book] | Response:

    query = get_book_query_base()

    query_params: list[str | int] = []

    search = build_search(request)
    if isinstance(search, Response):
        return search
    if search is not None:
        search_string, search_params = search
        query += search_string
        query_params.extend(search_params)

    query += build_sort(request)

    db_cursor.execute(query=query, params=query_params)
    return cast(list[Book], db_cursor.fetchall())
