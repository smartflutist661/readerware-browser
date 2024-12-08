import json
from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from flask import Flask
from flask.globals import request
from flask.templating import render_template
from flask.wrappers import Response

from readerware_browser.models.datatable_responses import (
    AuthorsResponse,
    BooksResponse,
    SeriesResponse,
)
from readerware_browser.pagination import paginate
from readerware_browser.queries.db_connection import get_db_connection
from readerware_browser.queries.queries import (
    QueryType,
    get_by_id,
    get_items,
    get_total,
)

load_dotenv(Path(__file__).parents[1] / ".env")

APP = Flask(__name__)

CONN = get_db_connection()


def get_bool_from_param(val: str) -> bool:
    return bool(json.loads(val.lower()))


@APP.route("/")
def index() -> str:
    return render_template("index.html", title="Home")


@APP.route("/books")
def books() -> str | Response:
    book_id = request.args.get("id", type=int)

    if book_id is None:
        return render_template(
            "books.html",
            title="Books",
            unread=request.args.get("unread", type=get_bool_from_param),
        )

    with CONN.cursor() as cur:
        book_res = get_by_id(book_id, "books", cur)

    if book_res is None:
        return Response(f"Book with id {book_id} not found", 404)

    book_res["description"] = (
        "".join(f"<p>{line}</p>" for line in book_res["description"].split("\n"))
        if book_res["description"] is not None
        else ""
    )

    return render_template(
        "book.html", title=f"{book_res['title']} - {book_res['author']}", book=book_res
    )


@APP.route("/authors")
def authors() -> str | Response:
    author_id = request.args.get("id", type=int)
    if author_id is None:
        return render_template("authors.html", title="Authors")

    with CONN.cursor() as cur:
        author_res = get_by_id(author_id, "authors", cur)

    if author_res is None:
        return Response(f"Author with id {author_id} not found", 404)

    return render_template(
        "books.html",
        title=f"{author_res['author']}",
        author_id=author_id,
        series_id=None,
    )


@APP.route("/series")
def series() -> str | Response:
    series_id = request.args.get("id", type=int)

    if series_id is None:
        return render_template("series.html", title="Series")

    with CONN.cursor() as cur:
        series_res = get_by_id(series_id, "series", cur)

    if series_res is None:
        return Response(f"Series with id {series_id} not found", 404)

    return render_template(
        "books.html",
        title=f"Series: {series_res['series']} - {series_res['author']}",
        series_id=series_id,
        author_id=None,
    )


# TODO: Format, link, concatenate multiple authors
# TODO: Cover collages for authors/series?
@APP.route("/api/data")
def data() -> BooksResponse | AuthorsResponse | SeriesResponse | Response:

    query_type = cast(QueryType, request.args.get("query_type", type=str))
    author_id = request.args.get("author_id", type=int)
    series_id = request.args.get("series_id", type=int)
    unread = request.args.get("unread", type=get_bool_from_param)

    with CONN.cursor() as cur:
        total_books = get_total(query_type, cur, author_id, series_id, unread)
        if isinstance(total_books, Response):
            return total_books

        filtered_items = get_items(request, query_type, cur, author_id, series_id, unread)

    if isinstance(filtered_items, Response):
        return filtered_items

    total_filtered = len(filtered_items)

    paginated_items = paginate(request, filtered_items)  # type: ignore[misc]

    # response
    return {
        "data": paginated_items,
        "recordsFiltered": total_filtered,
        "recordsTotal": total_books,
        "draw": request.args.get("draw", type=int),
    }
