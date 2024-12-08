WITH books AS (
    SELECT
    	readerware.rowkey as book_id,
        title,
        regexp_replace(title, '^The |^A | ^An ', '') as title_sort,
        cont1.name as author,
        cont1.sort_name as author_sort,
        cont1.rowkey as author_id,
        cast(pages as integer) as page_count,
        encode(thumb_images.image_data, 'base64') as cover,
        cat1.listitem as genre,
        cat2.listitem as subgenre_1,
        cat3.listitem as subgenre_2,
        series_list.listitem as series,
        regexp_replace(series_list.listitem, '^The |^A | ^An ', '') as series_sort,
        series_list.rowkey as series_id,
        case
        	when series_list.listitem is null then null
        	else series_number
        end as series_number,
        case
        	when series_list.listitem is null then null
        	when cast(readerware.user1 as integer) = -100 then series_number
        	when cast(readerware.user1 as integer) < 0 then null
        end as series_number_chron,
        readerware.user2 as subseries,
        case
        	when readerware.user2 is null then null 
        	else cast(readerware.user3 as integer)
        end as subseries_number,
        product_info as description
    FROM readerware
    left join contributor as cont1 on cont1.rowkey = readerware.author
    left join thumb_images on thumb_images.row_id = readerware.rowkey
    left join category_list as cat1 on cat1.rowkey = readerware.category1
    left join category_list as cat2 on cat2.rowkey = readerware.category2
    left join category_list as cat3 on cat3.rowkey = readerware.category3
    left join series_list on series_list.rowkey = readerware.series
    where thumb_images.image_index = 0 or thumb_images.image_index is null
)