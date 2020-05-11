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

