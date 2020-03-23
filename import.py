import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv

engine = create_engine("postgres://ojdceltofgrhxd:e437ecdc40f1a5eb1c54f62a6281bb0b4ac91d0d555c032a26de98707bd4f81b@ec2-52-23-14-156.compute-1.amazonaws.com:5432/d8r3lt1q14joff")
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
               {"isbn": isbn, "title": title, "author": author, "year": year})

    # print(f"Added book with isbn# {isbn} and title: {title}, written by: {author} in the year: {year}")
db.commit()