WITH series_sorter as (
	select 
		series_list.listitem as series,
		series_list.rowkey as series_id,
		array_agg(readerware.author) as author_ids
	from readerware
	join series_list on series_list.rowkey = readerware.series
	group by series_list.listitem, series_list.rowkey
	order by regexp_replace(series_list.listitem, '^The |^A | ^An ', '') asc
),
genre_sorter as (
	select 
		category_list.listitem as genre,
		array_agg(readerware.author) as author_ids
	from readerware
	join category_list on category_list.rowkey = readerware.category1
	group by category_list.listitem
	order by category_list.listitem asc
),
authors AS (
    SELECT
    	cont1.rowkey as author_id,
        cont1.name as author,
        cont1.sort_name as author_sort,
        sum(cast(pages as integer)) as page_count,
        array((select genre from genre_sorter where cont1.rowkey = any(author_ids))) as genres,
        array((select series from series_sorter where cont1.rowkey = any(author_ids))) as serieses,
        array((select series_id from series_sorter where cont1.rowkey = any(author_ids))) as serieses_ids,
        count(distinct series_list.listitem) as series_count,
        count(distinct readerware.rowkey) as book_count
    FROM readerware
    join contributor as cont1 on cont1.rowkey = readerware.author
    left join category_list as cat1 on cat1.rowkey = readerware.category1
    left join series_list on series_list.rowkey = readerware.series
    group by cont1.rowkey, cont1.name, cont1.sort_name
)
SELECT * from authors