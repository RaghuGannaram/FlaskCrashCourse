from flask import Flask, render_template, request, session
from markupsafe import escape

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>\n"


@app.route("/greet")
def greet():
    user_name = request.args.get("name")
    # Can lead to XSS attack, e.g. http://localhost:5000/greet?name=<script>alert("Hacked...!")</script>
    return f"<p>Hello, {user_name}!</p>\n"


@app.route("/safe_greet")
def safe_greet():
    user_name = request.args.get("name")
    secured_user_name = escape(user_name)
    # Now safe from XSS attacks
    return f"<p>Hello, {secured_user_name}!</p>\n"


@app.route("/add/<a>/<b>")
def add(a, b):
    try:
        sum_result = int(a) + int(b)
        return f"<p>The sum of {a} and {b} is {sum_result}.</p>\n"
    except ValueError:
        return "<p>Please provide two integers in the URL.</p>\n"


@app.route("/multiply/<int:a>/<int:b>")
def multiply(a, b):
    product_result = a * b
    return f"<p>The product of {a} and {b} is {product_result}.</p>\n"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Here you would normally validate the username and password
        session["username"] = username
        session["authenticated"] = True
        return f"<p>Logged in as {escape(username)}.</p>\n"
    return """
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    """


@app.post("/logout")
def logout():
    if(not session.get("authenticated")):
        return "<p>You are not logged in.</p>\n", 401
    session.pop("username", None)
    session["authenticated"] = False
    return "<p>You have been logged out.</p>\n"

@app.post("/overall_rating")
def overall_rating():
    if not session.get("authenticated"):
        return "<p>Please log in to submit a rating.</p>\n", 401
    data = request.get_json()
    print(data)
    if not data or "rating" not in data:
        return "<p>Invalid data. Please provide a rating.</p>\n", 400
    if not (1 <= data.get("rating") <= 5):
        return "<p>Rating must be between 1 and 5.</p>\n", 400

    print(f"Received rating: {data.get('rating')}")
    return f"<p>Thank you for your rating of {data.get('rating')}!</p>\n"


@app.route("/profile")
@app.route("/profile/<username>")
def profile(username="Guest"):
    return render_template("profile.html", username=username)


@app.get("/about")
def about():
    return render_template("about.html")


@app.route("/health_check")
def health_check():
    app.logger.info("Health check endpoint was called.")
    return {
        "status": "OK",
        "message": "The server is running smoothly.",
    }, 200


@app.errorhandler(404)
def page_not_found(error):
    return render_template("not_found.html"), 404


# To run the server, use the command: python server.py
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# Otherwise, to run using flask directly, use: flask --app server run --host=0.0.0.0 --port=5000 --debug
