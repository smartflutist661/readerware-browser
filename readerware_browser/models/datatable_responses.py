from typing import (
    Generic,
    Optional,
    TypedDict,
    TypeVar,
)

from readerware_browser.models.author import Author
from readerware_browser.models.book import Book
from readerware_browser.models.series import Series

T = TypeVar("T")


class DataTableResponse(Generic[T], TypedDict):
    data: list[T]
    recordsFiltered: int
    recordsTotal: int
    draw: Optional[int]


class BooksResponse(DataTableResponse[Book]):
    pass


class AuthorsResponse(DataTableResponse[Author]):
    pass


class SeriesResponse(DataTableResponse[Series]):
    pass
