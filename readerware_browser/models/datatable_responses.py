from typing import (
    Generic,
    Optional,
    TypedDict,
    TypeVar,
)

from readerware_browser.models.book import Book

T = TypeVar("T")


class DataTableResponse(Generic[T], TypedDict):
    data: list[T]
    recordsFiltered: int
    recordsTotal: int
    draw: Optional[int]


class BooksResponse(DataTableResponse[Book]):
    pass
