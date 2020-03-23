import os

from flask import Flask, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.utils import redirect

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


@app.route("/registration", methods=["GET"])
def register():
    return render_template("registration.html")


@app.route("/registration", methods=["POST"])
def register2():
    username = request.form.get("username")
    password = request.form.get("password")

    db.execute("INSERT INTO login (username, password) VALUES (:username, :password)",
               {"username": username, "password": password})
    db.commit()

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
            hello = "Wrong password"
    return render_template("logon.html", username=username, password=password, hello=hello)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "GET":
        return render_template("profile.html", username=session["username"])
    if request.method == "POST":
        book_name = request.form.get("title")
        searched_item = db.execute("SELECT * FROM books WHERE title like :search", {"search": '%' + book_name + '%'}).fetchall()
        session["book"] = searched_item
        if searched_item:
            return redirect("/books")

        else:
            statement = "No results found :( "
        return render_template("profile.html", username=session["username"], title=book_name,
                               searched_item=searched_item, book=session["book"], statement=statement)


@app.route("/books", methods=["GET", "POST"])
def books():
    return render_template("books.html", username=session["username"], book=session["book"])


@app.route("/book/<int:book_id>", methods=["GET"])
def book(book_id):
    book_info = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    return render_template("book.html", book=book_info)


@app.route("/logoff", methods=["GET", "POST"])
def logout():
    if request.method == "GET":
        return render_template("logoff.html")
    if request.method == "POST":
        session.pop("username", None)
        return redirect("/logon")
    return render_template("logoff.html", username=session["username"])

#
