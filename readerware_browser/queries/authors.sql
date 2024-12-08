WITH authors AS (
    SELECT
    	cont1.rowkey as author_id,
        cont1.name as author,
        cont1.sort_name as author_sort,
        sum(cast(pages as integer)) as page_count,
        --encode(thumb_images.image_data, 'base64') as cover, -- Might be nice to make a cover collage
        array_agg(distinct cat1.listitem) as genres,
        --cat2.listitem as subgenre_1,
        --cat3.listitem as subgenre_2,
        array_agg(distinct series_list.listitem) as serieses,
        count(distinct series_list.listitem) as series_count,
        count(distinct readerware.rowkey) as book_count
    FROM readerware
    join contributor as cont1 on cont1.rowkey = readerware.author
    --left join thumb_images on thumb_images.row_id = readerware.rowkey
    left join category_list as cat1 on cat1.rowkey = readerware.category1
    --left join category_list as cat2 on cat2.rowkey = readerware.category2
    --left join category_list as cat3 on cat3.rowkey = readerware.category3
    left join series_list on series_list.rowkey = readerware.series
    group by cont1.rowkey, cont1.name, cont1.sort_name
)
SELECT * from authors