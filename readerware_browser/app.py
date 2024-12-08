from pathlib import Path

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
from readerware_browser.queries.authors import (
    get_author,
    get_authors,
)
from readerware_browser.queries.books import (
    get_book,
    get_books,
    get_total_books,
)
from readerware_browser.queries.db_connection import get_db_connection
from readerware_browser.queries.series import (
    get_series,
    get_serieses,
)

load_dotenv(Path(__file__).parents[1] / ".env")

APP = Flask(__name__)

CONN = get_db_connection()


@APP.route("/")
def index() -> str:
    return render_template("index.html", title="Home")


@APP.route("/books")
def books() -> str:
    return render_template("books.html", title="Books")


@APP.route("/authors")
def authors() -> str:
    return render_template("authors.html", title="Authors")


@APP.route("/serieses")
def serieses() -> str:
    return render_template("serieses.html", title="Series")


@APP.route("/book")
def book() -> str | Response:
    book_id = request.args.get("id", type=int)
    if book_id is None:
        return Response(f"Book with id {book_id} not found", 404)

    with CONN.cursor() as cur:
        book_res = get_book(book_id, cur)

    if book_res is None:
        return Response(f"Book with id {book_id} not found", 404)

    return render_template(
        "book.html", title=f"{book_res['title']} - {book_res['author']}", book=book_res
    )


# TODO: These are pretty duplicative, could probably simplify by passing type-ish of request
# TODO: Format, link, concatenate multiple authors, series, genres
# Sort these internally? Series by favorite, authors alph for series, order for books
@APP.route("/api/books")
def books_data() -> BooksResponse | Response:

    author_id = request.args.get("author_id", type=int)
    series_id = request.args.get("series_id", type=int)

    with CONN.cursor() as cur:
        total_books = get_total_books(cur, author_id, series_id)
        if isinstance(total_books, Response):
            return total_books

        filtered_books = get_books(request, cur, author_id, series_id)

    if isinstance(filtered_books, Response):
        return filtered_books

    total_filtered = len(filtered_books)

    paginated_books = paginate(request, filtered_books)

    # response
    return {
        "data": paginated_books,
        "recordsFiltered": total_filtered,
        "recordsTotal": total_books,
        "draw": request.args.get("draw", type=int),
    }


@APP.route("/author")
def author() -> str | Response:
    author_id = request.args.get("id", type=int)
    if author_id is None:
        return Response("Author ID not in request", 400)

    with CONN.cursor() as cur:
        author_res = get_author(author_id, cur)

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
        return Response("Series ID not in request", 400)

    with CONN.cursor() as cur:
        series_res = get_series(series_id, cur)

    if series_res is None:
        return Response(f"Series with id {series_id} not found", 404)

    return render_template(
        "books.html",
        title=f"Series: {series_res['series']} - {series_res['author']}",
        series_id=series_id,
        author_id=None,
    )


@APP.route("/api/authors")
def authors_data() -> AuthorsResponse | Response:
    with CONN.cursor() as cur:
        total_res = cur.execute(
            """
        select count(distinct readerware.author) as total_authors
        from readerware
        join contributor on contributor.rowkey = readerware.author;
        """  # Join filter to prevent authors with no books
        ).fetchone()
        if total_res is not None:
            total_authors = total_res["total_authors"]

        filtered_authors = get_authors(request, cur)

    if isinstance(filtered_authors, Response):
        return filtered_authors

    total_filtered = len(filtered_authors)

    paginated_authors = paginate(request, filtered_authors)

    # response
    return {
        "data": paginated_authors,
        "recordsFiltered": total_filtered,
        "recordsTotal": total_authors,
        "draw": request.args.get("draw", type=int),
    }


@APP.route("/api/series")
def series_data() -> SeriesResponse | Response:
    with CONN.cursor() as cur:
        total_res = cur.execute(
            """
        select count(distinct readerware.series) as total_series
        from readerware
        join series_list on series_list.rowkey = readerware.series;
        """  # Join filter to prevent series with no books
        ).fetchone()
        if total_res is not None:
            total_series = total_res["total_series"]

        filtered_series = get_serieses(request, cur)

    if isinstance(filtered_series, Response):
        return filtered_series

    total_filtered = len(filtered_series)

    paginated_series = paginate(request, filtered_series)

    # response
    return {
        "data": paginated_series,
        "recordsFiltered": total_filtered,
        "recordsTotal": total_series,
        "draw": request.args.get("draw", type=int),
    }
