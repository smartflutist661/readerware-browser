CREATE TABLE contributor (
	rowkey int primary key,
	name text,
	sort_name text
);

INSERT INTO contributor (rowkey, name, sort_name)
VALUES 
(1, 'Author 1', '1, Author'),
(2, 'Author 2', '2, Author'),
(3, 'Author 3', '3, Author');

CREATE TABLE category_list (
	rowkey int primary key,
	listitem text
);

INSERT INTO category_list (rowkey, listitem)
VALUES
(1, 'Category 1'),
(2, 'Category 2'),
(3, 'Category 3'),
(4, 'Category 4'),
(5, 'Category 5'),
(6, 'Category 6');

CREATE TABLE series_list (
	rowkey int primary key,
	listitem text
);

INSERT INTO series_list (rowkey, listitem)
VALUES
(1, 'Series 1'),
(2, 'Series 2'),
(3, 'Series 3');

CREATE TABLE readerware (
	rowkey int primary key,
	author int references contributor,
	category1 int references category_list,
	category2 int references category_list,
	category3 int references category_list,
	series int references series_list,
	title text,
	pages int,
	read_count int,
	product_info text,
	series_number int,
	user1 text, -- series number chron
	user2 text, -- subseries
	user3 text -- subseries number
);

INSERT INTO readerware (rowkey, author, category1, category2, category3, series, title, pages, read_count, product_info, series_number, user1, user2, user3)
VALUES
(1, 1, 1, null, null, null, 'Book', 90, 0, null, null, null, null, null), -- standalone
(2, 2, 1, 2, null, 1, 'Book 1', 100, 0, null, 1, -100, null, null), -- standard chron series
(3, 2, 1, 2, 3, 1, 'Book 2', 150, 0, null, 2, -100, null, null),
(4, 3, 4, 2, null, 2, 'Book 1 Chron', 199, 1, null, 3, 1, null, null), -- nonchron series
(5, 3, 5, 3, null, 2, 'Book 2 Chron', 200, 1, null, 1, 2, null, null),
(6, 3, 6, 4, null, 2, 'Book 3 Chron', 300, 1, null, 2, 3, null, null),
(7, 2, null, null, null, 3, 'Book 1 Sub 1', 400, 2, null, 1, -100, 'Subseries 1', 1), -- subseries
(8, 3, null, null, null, 3, 'Book 2 Sub 1', 500, 2, null, 2, -100, 'Subseries 1', 2),
(9, 3, null, null, null, 3, 'Book 1 Sub 2', 999, 2, null, 3, -100, 'Subseries 2', 1),
(10, 3, null, null, null, 3, 'Book 2 Sub 2', 1000, 2, null, 4, -100, 'Subseries 2', 2),
(11, 2, null, null, null, 3, 'Book 2 Sub 2', 1001, 2, null, 5, -100, 'Subseries 2', 3);

-- Maybe this will get tests someday; for now, table just needs to exist
CREATE TABLE thumb_images (
	row_id int references readerware,
	image_index int,
	image_data bytea
);
