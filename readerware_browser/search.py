from typing import (
    Literal,
    Optional,
)

from flask.wrappers import (
    Request,
    Response,
)

STRING_CONDITIONS = (
    "=",
    "!=",
    "starts",
    "!starts",
    "contains",
    "!contains",
    "ends",
    "!ends",
    "null",
    "!null",
)

STRING_COLS = ("author", "title", "genre", "series", "subseries", "genres", "serieses")
NUM_COLS = (
    "page_count",
    "series_number",
    "subseries_number",
    "series_number_chron",
    "book_count",
    "series_count",
)

NUM_CONDITIONS = (
    "=",
    "!=",
    "<",
    "<=",
    ">=",
    ">",
    "between",
    "!between",
    "null",
    "!null",
)

# TODO: This file could use a good cleanup


def build_search(request: Request) -> Optional[tuple[str, tuple[str | int, ...]] | Response]:

    basic_search_param = request.args.get("search[value]")
    do_basic_search = basic_search_param != "" and basic_search_param is not None
    if do_basic_search:
        res = build_basic_search(basic_search_param)  # type: ignore[arg-type] ## False positive, checked for None above
        if isinstance(res, Response):
            return res
        basic_search_string, basic_search_params = res

    total_searchbuilder_criteria = len(
        [
            param
            for param in request.args.keys()
            if "searchBuilder" in param and "condition" in param
        ]
    )
    if total_searchbuilder_criteria > 10:
        return Response("Too many search criteria", 400)

    search_builder_outer_logic = request.args.get("searchBuilder[logic]")
    if search_builder_outer_logic is None or search_builder_outer_logic not in ("AND", "OR"):
        if do_basic_search:
            return basic_search_string, basic_search_params
        return None

    advanced_search_string, advanced_search_params = process_criteria(
        request,
        "searchBuilder[criteria]",
        search_builder_outer_logic,  # type: ignore[arg-type] ## Checked above
    )

    if advanced_search_string != "":
        if not do_basic_search:
            return f" where {advanced_search_string}", advanced_search_params
        return (
            basic_search_string + " AND (" + advanced_search_string + ")",
            basic_search_params + advanced_search_params,
        )

    if do_basic_search:
        return basic_search_string, basic_search_params
    return None


def process_criteria(
    request: Request,
    base_param: str,
    join_logic: Literal["AND", "OR"],
) -> tuple[str, tuple[str | int, ...]]:
    query_terms = []
    query_params: list[str | int] = []

    criterion_val: Optional[str | int]

    for criterion_num in range(10):
        nested_logic = request.args.get(f"{base_param}[{criterion_num}][logic]")
        if nested_logic is not None:
            if nested_logic in ("AND", "OR"):
                nested_query, nested_query_params = process_criteria(
                    request,
                    f"{base_param}[{criterion_num}][criteria]",
                    nested_logic,  # type: ignore[arg-type] ## Checked above
                )
                if nested_query != "":
                    query_terms.append(f"({nested_query})")
                    query_params.extend(nested_query_params)
        else:
            criterion_type = request.args.get(f"{base_param}[{criterion_num}][type]")
            if criterion_type is None:
                break
            criterion_col = request.args.get(f"{base_param}[{criterion_num}][origData]")
            criterion_cond = request.args.get(f"{base_param}[{criterion_num}][condition]")
            if (
                criterion_type == "string"
                and criterion_col in STRING_COLS
                and criterion_cond in STRING_CONDITIONS
            ) or (
                criterion_type == "num"
                and criterion_col in NUM_COLS
                and criterion_cond in NUM_CONDITIONS
            ):
                if criterion_cond in ("=", "!=", "<", "<=", ">", ">="):
                    if criterion_type == "num":
                        if criterion_col in ("page_count"):
                            criterion_val = request.args.get(
                                f"{base_param}[{criterion_num}][value1]", type=int
                            )
                    elif criterion_type == "string":
                        criterion_val = request.args.get(
                            f"{base_param}[{criterion_num}][value1]", type=str
                        )
                    if criterion_val is not None:
                        query_terms.append(f"{criterion_col} {criterion_cond} %s")
                        query_params.append(criterion_val)
                elif criterion_cond in ("null", "!null"):
                    if criterion_type == "string":
                        if "!" in criterion_cond:
                            query_terms.append(
                                f"({criterion_col} is not null or {criterion_col} != '')"
                            )
                        else:
                            query_terms.append(
                                f"({criterion_col} is null or {criterion_col} = '')"
                            )
                    elif criterion_type == "num":
                        if "!" in criterion_cond:
                            query_terms.append(f"{criterion_col} is not null")
                        else:
                            query_terms.append(f"{criterion_col} is null")
                elif (
                    criterion_cond
                    in ("starts", "!starts", "contains", "!contains", "ends", "!ends")
                    and criterion_type == "string"
                ):
                    criterion_val = request.args.get(
                        f"{base_param}[{criterion_num}][value1]", type=str
                    )
                    if criterion_val is not None:
                        if "!" in criterion_cond:
                            query_terms.append(f"lower({criterion_col}) not like lower(%s)")
                        else:
                            query_terms.append(f"lower({criterion_col}) like lower(%s)")

                        if "starts" in criterion_cond:
                            query_params.append(f"{criterion_val}%")
                        elif "ends" in criterion_cond:
                            query_params.append(f"%{criterion_val}")
                        elif "contains" in criterion_cond:
                            query_params.append(f"%{criterion_val}%")
                elif criterion_cond in ("between", "!between") and criterion_type == "num":
                    criterion_val_1 = request.args.get(
                        f"{base_param}[{criterion_num}][value1]", type=int
                    )
                    criterion_val_2 = request.args.get(
                        f"{base_param}[{criterion_num}][value2]", type=int
                    )
                    if criterion_val_1 is not None and criterion_val_2 is not None:
                        if "!" in criterion_cond:
                            query_terms.append(f"{criterion_col} not between %s and %s")
                        else:
                            query_terms.append(f"{criterion_col} between %s and %s")

                        query_params.extend([criterion_val_1, criterion_val_2])

    return f" {join_logic} ".join(query_terms), tuple(query_params)


def build_basic_search(search_param: str) -> tuple[str, tuple[str, ...]] | Response:
    search_strings = [f"%{search_string}%" for search_string in search_param.split()]
    total_search_strings = len(search_strings)
    if total_search_strings > 10:
        return Response("Too many search terms", 400)

    query = " where " + " OR ".join(
        sum(
            (
                [f"lower({string_search_col}) like lower(%s)"] * total_search_strings
                for string_search_col in STRING_COLS  # FIXME: This needs to be filtered by valid table columns
            ),
            [],
        )
    )
    query_params = search_strings * len(STRING_COLS)
    return query, tuple(query_params)
