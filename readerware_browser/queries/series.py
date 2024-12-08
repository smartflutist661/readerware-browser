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

from readerware_browser.models.series import Series
from readerware_browser.search import build_search
from readerware_browser.sort import build_sort

# TODO: This is nearly identical to `books`, probably simplify
VALID_COLUMNS = Series.__annotations__.keys()


def get_series_query_base() -> str:
    with (Path(__file__).parent / "serieses.sql").open(encoding="utf8") as series_query_file:
        return series_query_file.read()


def get_series(series_id: int, db_cursor: Cursor[dict[str, Any]]) -> Optional[Series]:
    query = get_series_query_base()
    query += " where series_id = %s;"

    return cast(Optional[Series], db_cursor.execute(query, [series_id]).fetchone())


def get_serieses(request: Request, db_cursor: Cursor[dict[str, Any]]) -> list[Series] | Response:

    query = get_series_query_base()

    query_params: list[str | int | float] = []

    search = build_search(request, VALID_COLUMNS)
    if isinstance(search, Response):
        return search
    if search is not None:
        search_string, search_params = search
        query += " where " + search_string
        query_params.extend(search_params)

    query += build_sort(request)

    db_cursor.execute(query=query, params=query_params)
    return cast(list[Series], db_cursor.fetchall())
