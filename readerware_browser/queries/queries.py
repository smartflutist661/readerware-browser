from pathlib import Path
from typing import (
    Any,
    Literal,
    Optional,
    cast,
)

from flask.wrappers import (
    Request,
    Response,
)
from psycopg.cursor import Cursor

from readerware_browser.models.author import Author
from readerware_browser.models.book import Book
from readerware_browser.models.series import Series
from readerware_browser.search import build_search
from readerware_browser.sort import build_sort

QueryType = Literal["books", "authors", "series"]


def get_query_base(query_type: QueryType) -> str:
    with (Path(__file__).parent / f"{query_type}.sql").open(encoding="utf8") as query_file:
        return query_file.read()


def get_by_id(
    query_id: int,
    query_type: QueryType,
    db_cursor: Cursor[dict[str, Any]],
) -> Optional[Book]:
    query = get_query_base(query_type)
    query += f" SELECT * from {query_type} where id = %s;"

    return cast(Optional[Book], db_cursor.execute(query, [query_id]).fetchone())


def get_base_query_params(
    query_type: QueryType,
    author_id: Optional[int],
    series_id: Optional[int],
    unread: Optional[bool],
) -> tuple[list[str], list[str | int | float]]:
    query_terms = []
    query_params: list[str | int | float] = []

    if author_id is not None:
        if query_type == "authors":
            query_terms.append("id = %s")
            query_params.append(author_id)
        else:
            query_terms.append("author_id = %s")
            query_params.append(author_id)

    if series_id is not None:
        if query_type == "series":
            query_terms.append("id = %s")
            query_params.append(series_id)
        elif query_type == "authors":
            query_terms.append("%s = ANY(serieses_ids)")
            query_params.append(series_id)
        else:
            query_terms.append("series_id = %s")
            query_params.append(series_id)

    # Ternary: None = all, True = unread, False = read
    if unread is not None:
        if unread is True:
            query_terms.append("read_count = %s")
        else:
            query_terms.append("read_count > %s")
        query_params.append(0)

    return query_terms, query_params


def get_total(
    query_type: QueryType,
    db_cursor: Cursor[dict[str, Any]],
    author_id: Optional[int],
    series_id: Optional[int],
    unread: Optional[bool],
) -> int | Response:
    query = get_query_base(query_type) + f" SELECT count(*) as total from {query_type}"

    query_terms, query_params = get_base_query_params(query_type, author_id, series_id, unread)

    if len(query_terms) > 0:
        query += " where " + " AND ".join(query_terms)

    total_res = db_cursor.execute(query + ";", query_params).fetchone()
    if total_res is not None:
        return int(total_res["total"])

    return Response(f"No {query_type} found", 404)


def get_items(
    request: Request,
    query_type: QueryType,
    db_cursor: Cursor[dict[str, Any]],
    author_id: Optional[int],
    series_id: Optional[int],
    unread: Optional[bool],
) -> list[Book] | list[Author] | list[Series] | Response:

    query = get_query_base(query_type) + f" SELECT * from {query_type}"

    query_terms, query_params = get_base_query_params(query_type, author_id, series_id, unread)

    if query_type == "books":
        valid_columns = Book.__annotations__.keys()
    elif query_type == "authors":
        valid_columns = Author.__annotations__.keys()
    elif query_type == "series":
        valid_columns = Series.__annotations__.keys()
    else:
        raise ValueError(f"Unrecognized query type {query_type}, unable to retrieve valid columns")

    search = build_search(request, valid_columns)
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
