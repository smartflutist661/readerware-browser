from typing import TypedDict


class Series(TypedDict):
    author: str
    author_sort: str
    author_id: int
    page_count: int
    genre: str
    series: str
    series_sort: str
    series_id: int
    series_length: int
    subserieses: str
    book_count: int
