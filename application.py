import os

from flask import Flask, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.utils import redirect
import requests

from models import *

app = Flask(__name__)

# Check for environment variable
if not "postgres://ojdceltofgrhxd:e437ecdc40f1a5eb1c54f62a6281bb0b4ac91d0d555c032a26de98707bd4f81b@ec2-52-23-14-156.compute-1.amazonaws.com:5432/d8r3lt1q14joff":
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(
    "postgres://ojdceltofgrhxd:e437ecdc40f1a5eb1c54f62a6281bb0b4ac91d0d555c032a26de98707bd4f81b@ec2-52-23-14-156.compute-1.amazonaws.com:5432/d8r3lt1q14joff")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# @app.route("/registration", methods=["GET"])
# def register():
#     return render_template("registration.html")


@app.route("/registration", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("registration.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db.execute("INSERT INTO login (username, password) VALUES (:username, :password)",
                   {"username": username, "password": password})
        db.commit()
        session["username"] = username

        if request.method =="POST":
            return redirect('/profile')
        return render_template("registration.html", username=username, password=password)


@app.route("/logon", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("logon.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        session["username"] = username
        user_info = db.execute("SELECT * FROM login WHERE username = :username", {"username": username}).fetchone()
        if password == user_info.password:
            return redirect("/profile")
        else:
            statement = "Wrong password"
    return render_template("logon.html", username=username, password=password, statement=statement)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "GET":
        return render_template("profile.html", username=session["username"])
    if request.method == "POST":
        book_name = request.form.get("title")
        searched_item = db.execute('SELECT * FROM books WHERE isbn ilike :search OR title ilike :search OR author '
                                   'ilike :search OR year ilike :search', {"search": '%' + book_name + '%'}).fetchall()
        session["book"] = searched_item
        if searched_item:
            return redirect("/books")

        else:
            statement = "No results found :( "
        return render_template("profile.html", username=session["username"], title=book_name,
                               searched_item=searched_item, book=session["book"], statement=statement)


@app.route("/books", methods=["GET"])
def books():
    return render_template("books.html", book=session["book"])


@app.route("/book/<int:book_id>/", methods=["GET", "POST"])
def book(book_id):
    book_info = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    key = "RZM6NJic0yxuUPAgBGhfA"
    res = requests.get(" https://www.goodreads.com/book/review_counts.json",
                       params={"key": key, "isbns": book_info.isbn})
    data = res.json()
    avg_review = data["books"][0]["average_rating"]

    username = session["username"]
    user = db.execute("SELECT * FROM login WHERE username = :username", {"username": username}).fetchone()
    user_id = user.id
    all_reviews = db.execute("SELECT * FROM reviews WHERE book = :book", {"book": book_id}).fetchall()
    more_reviews = db.execute("SELECT username, book, point, review FROM login JOIN reviews ON reviews.user_name = "
                              "login.id WHERE book = :book", {"book": book_id}).fetchall()

    can_post = 0
    for reviews in all_reviews:
        if reviews.user_name == user_id:
            can_post += 1
    if request.method == "GET":
        return render_template("book.html", book=book_info, avg_review=avg_review, all_reviews=all_reviews, more_reviews=more_reviews)
    if request.method == "POST":
        if can_post > 0:
            statement = "You can not review again. "
            return render_template("book.html", book=book_info, avg_review=avg_review, statement=statement, all_reviews=all_reviews, more_reviews=more_reviews)
        else:
            review = request.form.get("review")
            review_text = request.form.get("review_text")
            db.execute("INSERT INTO reviews (book, user_name, point, review) VALUES (:book, :user_name, :point, "
                       ":review)",
                       {"book": book_id, "user_name": user_id, "point": review, "review": review_text})
            statement = "Review has been submitted! "
            db.commit()
            return render_template("book.html", book=book_info, all_reviews=all_reviews, avg_review=avg_review, review=review, review_text=review_text, statement=statement, more_reviews=more_reviews)


@app.route("/logoff", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        return render_template("logoff.html")
    if request.method == "POST":
        session.pop("username", None)
        return redirect("/logon")
    return render_template("logoff.html")
