from typing import (
    TypedDict,
    TypeVar,
)

T = TypeVar("T")


class Book(TypedDict):
    title: str
    title_sort: str
    author: str
    author_sort: str
    page_count: int
    cover: str
