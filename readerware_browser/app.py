import os
from pathlib import Path
from typing import Any

import psycopg
from flask import Flask
from flask.globals import request
from flask.templating import render_template
from psycopg.connection import Connection
from psycopg.rows import dict_row

APP = Flask(__name__)


def get_db_connection() -> Connection[dict[str, Any]]:
    conn = psycopg.connect(
        # TODO: Populate server env vars or otherwise acquire connection info
        # dotenv?
        host="localhost",
        dbname="test",
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        row_factory=dict_row,
    )
    return conn


@APP.route("/")
def index() -> str:
    return render_template("index.html", title="Books")


# TODO: TypedDict returns
# TODO: Some functions
# TODO: Define books, authors, series routes (min; both authors/series tables and individual author/series pages)
# TODO: For authors/series summaries, include book count
@APP.route("/api/data")
def data() -> dict[str, list[dict[str, Any]] | int | None]:
    conn = get_db_connection()
    cur = conn.cursor()

    total_res = cur.execute("select count(*) as total_books from readerware;").fetchone()
    if total_res is not None:
        total_books = total_res["total_books"]

    with (Path(__file__).parent / "templates" / "books.sql").open(
        encoding="utf8"
    ) as books_query_file:
        query = books_query_file.read()

    query_params: list[str] = []

    # search
    search = request.args.get("search[value]")

    if search != "" and search is not None:
        print(search, type(search))
        search_strings = [f"%{search_string}%" for search_string in search.split()]
        total_search_strings = len(search_strings)
        if total_search_strings > 10:
            raise ValueError("Too many search strings")
        query += " where " + " OR ".join(
            ["author like %s"] * total_search_strings + ["title like %s"] * total_search_strings
        )
        query_params += search_strings * 2

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
    books = cur.fetchall()
    cur.close()
    conn.close()

    total_filtered = len(books)

    # pagination
    start = request.args.get("start", type=int)
    length = request.args.get("length", type=int)
    if start is None:
        start = 0
    if length is None:
        length = total_filtered
    books = books[start : start + length]

    # response
    return {
        "data": books,
        "recordsFiltered": total_filtered,
        "recordsTotal": total_books,
        "draw": request.args.get("draw", type=int),
    }
