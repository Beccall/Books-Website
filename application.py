import os

from flask import Flask, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.utils import redirect
import requests

app = Flask(__name__)

# Check for environment variable
if not "postgres://nibcjksikejyqm:d9780941b69e9a14c322e1229e69328dbb12d80f1b45b1ce48f8a9cb4e8b0926@ec2-35-171-31-33" \
       ".compute-1.amazonaws.com:5432/dff5f1uksmubk5":
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(
    "postgres://nibcjksikejyqm:d9780941b69e9a14c322e1229e69328dbb12d80f1b45b1ce48f8a9cb4e8b0926@ec2-35-171-31-33"
    ".compute-1.amazonaws.com:5432/dff5f1uksmubk5")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET"])
def index():

    message = None
    if 'username' in session:
        message = f"Welcome back, {session['username']}"
    return render_template("index.html", message=message)


@app.route("/registration", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("registration.html")
    if request.method == "POST":
        statement = None
        username = request.form.get("username")
        password = request.form.get("password")
        check_user = db.execute("SELECT * FROM login WHERE username = :username", {"username": username}).fetchone()
        if check_user is None and len(password) >= 8:
            db.execute("INSERT INTO login (username, password) VALUES (:username, :password)",
                       {"username": username, "password": password})
            db.commit()
            session["username"] = username
            if request.method == "POST":
                return redirect('/profile')

        elif check_user:
            statement = "Username already exists. "
        elif len(password) < 8:
            statement = "Password must be 8 or more characters"

        return render_template("registration.html", username=username, password=password, statement=statement)


@app.route("/logon", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/")
    else:
        if request.method == "GET":
            return render_template("logon.html")
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user_info = db.execute("SELECT * FROM login WHERE username = :username", {"username": username}).fetchone()
            if password == user_info.password:
                session["username"] = username
                return redirect("/")
            else:
                statement = "Wrong password"
            return render_template("logon.html", username=username, password=password, statement=statement)


@app.route("/profile", methods=["GET"])
def profile():
    if "username" not in session:
        return redirect("/logon")
    else:
        user = db.execute('SELECT * FROM login WHERE username= :username', {"username": session['username']}).fetchone()
        users_reviews = db.execute('SELECT title, point, review FROM books JOIN reviews ON reviews.book '
                               '= books.id WHERE user_name = :username',
                               {"username": user.id}).fetchall()
        return render_template("profile.html", username=session["username"], user_reviews=users_reviews)


@app.route("/search", methods=["GET", "POST"])
def search():
    if "username" not in session:
        return redirect("/logon")
    else:
        if request.method == "GET":
            return render_template("search.html")
        if request.method == "POST":
            session["search"] = request.form.get("title")
            searched_item = db.execute('SELECT * FROM books WHERE isbn ilike :search OR title ilike :search OR author '
                                           'ilike :search OR year ilike :search', {"search": '%' + session["search"] + '%'}).fetchall()
            session["book"] = searched_item
            if searched_item:
                return redirect('/books')

            else:
                statement = "No results found. Please search again. "
            return render_template("search.html", username=session["username"], title=session["search"],
                               searched_item=searched_item, book=session["book"], statement=statement)


@app.route("/books", methods=["POST", "GET"])
def books():
    if "username" not in session:
        return redirect("/logon")
    elif "book" not in session:
        return redirect("/search")
    else:
        return render_template("books.html", book=session["book"], search=session["search"])


@app.route("/book/<int:book_id>/", methods=["GET", "POST"])
def book(book_id):
    if "username" not in session:
        return redirect("/logon")
    else:
        book_info = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        key = "RZM6NJic0yxuUPAgBGhfA"
        res = requests.get(" https://www.goodreads.com/book/review_counts.json",
                           params={"key": key, "isbns": book_info.isbn})
        data = res.json()
        avg_review = data["books"][0]["average_rating"]
        total_count = data["books"][0]["ratings_count"]
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
            return render_template("book.html", book=book_info, avg_review=avg_review, total_count=total_count,
                                   all_reviews=all_reviews, more_reviews=more_reviews)
        if request.method == "POST":
            if can_post > 0:
                statement = "You can not review again. "
                return render_template("book.html", book=book_info, avg_review=avg_review, statement=statement,
                                       all_reviews=all_reviews, more_reviews=more_reviews, total_count=total_count)
            else:
                review = request.form.get("review")
                review_text = request.form.get("review_text")
                db.execute("INSERT INTO reviews (book, user_name, point, review) VALUES (:book, :user_name, :point, "
                           ":review)",
                           {"book": book_id, "user_name": user_id, "point": review, "review": review_text})
                statement = "Review has been submitted! "
                db.commit()
                return render_template("book.html", book=book_info, all_reviews=all_reviews, avg_review=avg_review,
                                       review=review, review_text=review_text, statement=statement,
                                       more_reviews=more_reviews, total_count=total_count)


@app.route("/logoff", methods=["GET", "POST"])
def logout():
    if "username" not in session:
        return render_template("logon.html")
    if request.method == "GET":
        return render_template("logoff.html")
    if request.method == "POST":
        session.pop("username", None)
        session.pop("book", None)
        session.pop("search", None)
        return redirect("/logon")
    return render_template("logoff.html")


@app.route("/api/<book_isbn>")
def book_api(book_isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 422
    key = "RZM6NJic0yxuUPAgBGhfA"
    res = requests.get(" https://www.goodreads.com/book/review_counts.json",
                       params={"key": key, "isbns": book.isbn})
    data = res.json()
    avg_review = data["books"][0]["average_rating"]
    total_count = data["books"][0]["ratings_count"]

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": total_count,
        "average_score": avg_review

    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
