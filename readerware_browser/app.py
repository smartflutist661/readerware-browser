from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask.globals import request
from flask.templating import render_template
from flask.wrappers import Response

from readerware_browser.models.datatable_responses import (
    AuthorsResponse,
    BooksResponse,
)
from readerware_browser.pagination import paginate
from readerware_browser.queries.authors import (
    get_author,
    get_authors,
)
from readerware_browser.queries.books import (
    get_book,
    get_books,
)
from readerware_browser.queries.db_connection import get_db_connection

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


# TODO: Define books, authors, series routes (min; both books/authors/series tables and individual book/author/series pages)
# TODO: For authors/series summaries, include book count
# TODO: These are pretty duplicative, could probably simplify by passing type-ish of request
@APP.route("/api/books")
def books_data() -> BooksResponse | Response:
    with CONN.cursor() as cur:
        total_res = cur.execute("select count(*) as total_books from readerware;").fetchone()
        if total_res is not None:
            total_books = total_res["total_books"]

        filtered_books = get_books(request, cur)

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
    # TODO: Instead of loading an "author page" (what would it display?),
    # send to pre-filtered version of books table somehow?
    author_id = request.args.get("id", type=int)
    if author_id is None:
        return Response(f"Author with id {author_id} not found", 404)

    with CONN.cursor() as cur:
        author_res = get_author(author_id, cur)

    if author_res is None:
        return Response(f"Author with id {author_id} not found", 404)

    return render_template("author.html", title=f"{author_res['author']}", book=author_res)


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
