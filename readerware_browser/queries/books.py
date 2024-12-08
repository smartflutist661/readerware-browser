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

VALID_COLUMNS = Book.__annotations__.keys()


def get_book_query_base() -> str:
    with (Path(__file__).parent / "books.sql").open(encoding="utf8") as books_query_file:
        return books_query_file.read()


def get_total_books(
    db_cursor: Cursor[dict[str, Any]],
    author_id: Optional[int],
    series_id: Optional[int],
) -> int | Response:
    query = get_book_query_base() + "SELECT count(*) as total_books from books"

    query_terms = []
    query_params = []

    if author_id is not None:
        query_terms.append("author_id = %s")
        query_params.append(author_id)

    if series_id is not None:
        query_terms.append("series_id = %s")
        query_params.append(series_id)

    if len(query_terms) > 0:
        query += " where " + " AND ".join(query_terms)

    total_res = db_cursor.execute(query + ";", query_params).fetchone()
    if total_res is not None:
        return int(total_res["total_books"])

    return Response("No books found", 404)


def get_book(book_id: int, db_cursor: Cursor[dict[str, Any]]) -> Optional[Book]:
    query = get_book_query_base()
    query += " SELECT * from books where book_id = %s;"

    return cast(Optional[Book], db_cursor.execute(query, [book_id]).fetchone())


def get_books(
    request: Request,
    db_cursor: Cursor[dict[str, Any]],
    author_id: Optional[int],
    series_id: Optional[int],
) -> list[Book] | Response:

    query = get_book_query_base() + " SELECT * from books"

    query_terms = []
    query_params: list[str | int | float] = []

    if author_id is not None:
        query_terms.append("author_id = %s")
        query_params.append(author_id)

    if series_id is not None:
        query_terms.append("series_id = %s")
        query_params.append(series_id)

    search = build_search(request, VALID_COLUMNS)
    if isinstance(search, Response):
        return search

    if search is not None or len(query_terms) > 0:
        query += " where "

    if len(query_terms) > 0:
        query += "(" + " AND ".join(query_terms) + ")"

    if search is not None and len(query_terms) > 0:
        query += " AND ("

    if search is not None:
        search_string, search_params = search
        query += search_string
        query_params.extend(search_params)

    if search is not None and len(query_terms) > 0:
        query += ")"

    query += build_sort(request)

    db_cursor.execute(query=query, params=query_params)
    return cast(list[Book], db_cursor.fetchall())
