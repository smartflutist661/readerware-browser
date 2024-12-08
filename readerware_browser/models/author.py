from typing import TypedDict


class Author(TypedDict):
    author_id: int
    author: str
    author_sort: str
    page_count: int
    genres: list[str]
    serieses: list[str]
    book_count: int
    series_count: int
