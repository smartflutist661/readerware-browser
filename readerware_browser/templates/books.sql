WITH books AS (
    SELECT
        title,
        regexp_replace(title, '^The |^A | ^An ', '') as title_sort,
        contributor.name as author,
        contributor.sort_name as author_sort,
        cast(pages as integer) as page_count,
        encode(thumb_images.image_data, 'base64') as cover
    FROM readerware
    left join contributor on contributor.rowkey = readerware.author
    left join thumb_images on thumb_images.row_id = readerware.rowkey
    where thumb_images.image_index = 0 or thumb_images.image_index is null
)
SELECT * from books