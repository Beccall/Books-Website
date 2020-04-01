CREATE TABLE books(
    id SERIAL PRIMARY KEY,
    isb INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE login(
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);
CREATE TYPE NameEnum AS ENUM('1','2','3','4','5');

CREATE TABLE reviews(
    id SERIAL PRIMARY KEY,
    book INTEGER REFERENCES books,
    user_name INTEGER REFERENCES login,
    point NameEnum NOT NULL
    review VARCHAR
);

ALTER TABLE reviews ADD COLUMN review VARCHAR;

INSERT INTO reviews
    (book, user_name, point)
    VALUES (5464, 7, '5'
    );

INSERT INTO reviews
    (book, user_name, point, review)
    VALUES (5464, 8, '1', 'basically crap'
    );

INSERT INTO reviews
    (book, user_name, point, review)
    VALUES (5464, 10, '4', ''
    );

SELECT title FROM books JOIN reviews ON reviews.book = books.id;
SELECT username, book, point, review FROM login JOIN reviews ON reviews.user_name = login.id;

ALTER TABLE books ALTER COLUMN isbn TYPE varchar;
