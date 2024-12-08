WITH series_aggs as (
	SELECT
        sum(cast(pages as integer)) as page_count,
        series_list.rowkey as series_id,
        max(readerware.series_number) as series_length,
        array_agg(distinct readerware.user2) as subserieses,
        count(distinct readerware.rowkey) as book_count
    FROM readerware
    join series_list on series_list.rowkey = readerware.series
    group by series_list.rowkey
),
serieses AS (
    SELECT
    	cont1.name as author,
        cont1.sort_name as author_sort,
        cont1.rowkey as author_id,
        page_count,
        cat1.listitem as genre,
        series_list.listitem as series,
        regexp_replace(series_list.listitem, '^The |^A | ^An ', '') as series_sort,
        series_list.rowkey as series_id,
        series_length,
        subserieses,
        book_count
    FROM readerware
    left join contributor as cont1 on cont1.rowkey = readerware.author
    left join category_list as cat1 on cat1.rowkey = readerware.category1
    join series_list on series_list.rowkey = readerware.series
    join series_aggs on series_list.rowkey = series_aggs.series_id
)
select * from (select distinct on (series_id) * from serieses)