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

from readerware_browser.models.author import Author
from readerware_browser.search import build_search
from readerware_browser.sort import build_sort

# TODO: This is nearly identical to `books`, probably simplify


def get_author_query_base() -> str:
    with (Path(__file__).parent / "authors.sql").open(encoding="utf8") as authors_query_file:
        return authors_query_file.read()


def get_author(author_id: int, db_cursor: Cursor[dict[str, Any]]) -> Optional[Author]:
    query = get_author_query_base()
    query += " where author_id = %s;"

    return cast(Optional[Author], db_cursor.execute(query, [author_id]).fetchone())


def get_authors(request: Request, db_cursor: Cursor[dict[str, Any]]) -> list[Author] | Response:

    query = get_author_query_base()

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
    return cast(list[Author], db_cursor.fetchall())
