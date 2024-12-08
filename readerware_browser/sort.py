from flask.wrappers import Request

MAX_SORT_COLS = 3
SORT_COLS = (
    "title",
    "author",
    "page_count",
    "genre",
    "series",
    "series_number",
    "series_number_chron",
    "subseries",
    "subseries_number",
    "book_count",
    "series_count",
    # TODO: Sort by author genres/series?
)


def build_sort(request: Request) -> str:
    # sort
    sorts = []
    for sort_col_num in range(MAX_SORT_COLS):
        sort_col_index = request.args.get(f"order[{sort_col_num}][column]")
        if sort_col_index is None and sort_col_num > 0:
            break
        sort_col_name = request.args.get(f"columns[{sort_col_index}][data]")
        # Specify allowed sort parameters to prevent SQL injection
        # Can't parameterize "order by"
        print(sort_col_name)
        if sort_col_name not in SORT_COLS or sort_col_name == "author":
            sort_col_name = "author_sort"
        elif sort_col_name == "title":
            sort_col_name = "title_sort"
        sort_direction = request.args.get(f"order[{sort_col_num}][dir]")
        if sort_direction not in ("asc", "desc"):
            sort_direction = "asc"
        sorts.append(f"{sort_col_name} {sort_direction}")
    print(sorts)
    return " order by " + ", ".join(sorts) + ";"
