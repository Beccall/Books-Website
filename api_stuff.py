import requests


def main():
    # path parameter: /0441172717
    # query parameter: ?key=RZM6NJic0yxuUPAgBGhfA
    # 2 query params: ?key1=value1&key2=value2

    # https://www.goodreads.com/book/review_counts.json?isbns=0743484355&key=RZM6NJic0yxuUPAgBGhfA
    isbn = "0743484355"
    key = "RZM6NJic0yxuUPAgBGhfA"
    res = requests.get(" https://www.goodreads.com/book/review_counts.json",
                       params={"key": key, "isbns": isbn})

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful")

    data = res.json()

    avg_review = data["books"][0]["average_rating"]
    total_count = data["books"][0]["ratings_count"]

    print(f"average rating is: {avg_review}, out of {total_count} reviews")

main()