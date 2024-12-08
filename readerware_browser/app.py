import os
from pathlib import Path
from typing import (
    Any,
    cast,
)

import psycopg
from dotenv import load_dotenv
from flask import Flask
from flask.globals import request
from flask.templating import render_template
from flask.wrappers import Response
from psycopg.connection import Connection
from psycopg.rows import dict_row

from readerware_browser.models.book import Book
from readerware_browser.models.datatable_responses import BooksResponse
from readerware_browser.pagination import paginate
from readerware_browser.search import build_search
from readerware_browser.sort import build_sort

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


# TODO: Define books, authors, series routes (min; both books/authors/series tables and individual book/author/series pages)
# TODO: For authors/series summaries, include book count
@APP.route("/api/books")
def books_data() -> BooksResponse | Response:
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

    query += build_sort(request)

    cur.execute(query=query, params=query_params)
    books_res = cast(list[Book], cur.fetchall())
    cur.close()
    conn.close()

    total_filtered = len(books_res)

    books_res = paginate(request, books_res)

    # response
    return {
        "data": books_res,
        "recordsFiltered": total_filtered,
        "recordsTotal": total_books,
        "draw": request.args.get("draw", type=int),
    }
