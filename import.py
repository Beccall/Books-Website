import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv

engine = create_engine("postgres://nibcjksikejyqm:d9780941b69e9a14c322e1229e69328dbb12d80f1b45b1ce48f8a9cb4e8b0926"
                       "@ec2-35-171-31-33.compute-1.amazonaws.com:5432/dff5f1uksmubk5")
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
               {"isbn": isbn, "title": title, "author": author, "year": year})

    # print(f"Added book with isbn# {isbn} and title: {title}, written by: {author} in the year: {year}")
db.commit()