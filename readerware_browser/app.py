import os
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv
from flask import Flask
from flask.globals import request
from flask.templating import render_template
from flask.wrappers import Response
from psycopg.connection import Connection
from psycopg.rows import dict_row

from readerware_browser.search import build_search

load_dotenv(Path(__file__).parents[1] / ".env")

APP = Flask(__name__)


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


@APP.route("/")
def index() -> str:
    return render_template("index.html", title="Home")


@APP.route("/books")
def books() -> str:
    return render_template("books.html", title="Books")


# TODO: TypedDict returns
# TODO: Some functions
# TODO: Define books, authors, series routes (min; both books/authors/series tables and individual book/author/series pages)
# TODO: For authors/series summaries, include book count
@APP.route("/api/books")
def books_data() -> dict[str, list[dict[str, Any]] | int | None] | Response:
    conn = get_db_connection()
    cur = conn.cursor()

    total_res = cur.execute("select count(*) as total_books from readerware;").fetchone()
    if total_res is not None:
        total_books = total_res["total_books"]

    with (Path(__file__).parent / "templates" / "books.sql").open(
        encoding="utf8"
    ) as books_query_file:
        query = books_query_file.read()

    query_params: list[str | int] = []

    search = build_search(request)
    print(search)
    if isinstance(search, Response):
        return search
    if search is not None:
        search_string, search_params = search
        query += search_string
        query_params.extend(search_params)

    # sort
    max_sort_cols = 3
    sorts = []
    for sort_col_num in range(max_sort_cols):
        sort_col_index = request.args.get(f"order[{sort_col_num}][column]")
        if sort_col_index is None and sort_col_num > 0:
            break
        sort_col_name = request.args.get(f"columns[{sort_col_index}][data]")
        # Specify allowed sort parameters to prevent SQL injection
        # Can't parameterize "order by"
        if sort_col_name not in ("title", "author", "page_count") or sort_col_name == "author":
            sort_col_name = "author_sort"
        elif sort_col_name == "title":
            sort_col_name = "title_sort"
        sort_direction = request.args.get(f"order[{sort_col_num}][dir]")
        if sort_direction not in ("asc", "desc"):
            sort_direction = "asc"
        sorts.append(f"{sort_col_name} {sort_direction}")
    query += " order by " + ", ".join(sorts) + ";"

    cur.execute(query=query, params=query_params)
    books_res = cur.fetchall()
    cur.close()
    conn.close()

    total_filtered = len(books_res)

    # pagination
    start = request.args.get("start", type=int)
    length = request.args.get("length", type=int)
    if start is None:
        start = 0
    if length is None:
        length = total_filtered
    books_res = books_res[start : start + length]

    # response
    return {
        "data": books_res,
        "recordsFiltered": total_filtered,
        "recordsTotal": total_books,
        "draw": request.args.get("draw", type=int),
    }
