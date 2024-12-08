from typing import TypedDict


class Book(TypedDict):
    id: int
    title: str
    title_sort: str
    author: str
    author_sort: str
    page_count: int
    cover: str
    genre: str
    subgenre_1: str
    subgenre_2: str
    series: str
    series_sort: str
    series_id: int
    series_number: float
    series_number_chron: int
    subseries: str
    subseries_number: int
    description: str
    read_count: int
