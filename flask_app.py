from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "birthday_secret_key_change_this_later")

# Always use the folder where this Python file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database will be:
# /home/vijayb1432/mysite/birthday.db
DATABASE = os.path.join(BASE_DIR, "birthday.db")


# =========================================================
# DATABASE
# =========================================================

def get_db():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the users table if it doesn't already exist."""

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    """
    Start the website from the Sign Up page.

    If the user is already logged in, send them to the quiz.
    """

    if "user_id" in session:
        return redirect(url_for("quiz"))

    return redirect(url_for("signup"))


# =========================================================
# SIGN UP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # -------------------------------------------------
        # Validate fields
        # -------------------------------------------------

        if not name or not email or not password or not confirm_password:
            return render_template(
                "signup.html",
                error="Please fill in all fields."
            )

        # -------------------------------------------------
        # Password length
        # -------------------------------------------------

        if len(password) != 12:
            return render_template(
                "signup.html",
                error="Password must be exactly 12 characters long."
            )

        # -------------------------------------------------
        # Check password confirmation
        # -------------------------------------------------

        if password != confirm_password:
            return render_template(
                "signup.html",
                error="Passwords do not match."
            )

        # -------------------------------------------------
        # Hash password
        # -------------------------------------------------

        hashed_password = generate_password_hash(password)

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO users
                (name, email, password)
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email,
                    hashed_password
                )
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return render_template(
                "signup.html",
                error="This email is already registered."
            )

        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:

            return render_template(
                "login.html",
                error="Please enter your email and password."
            )

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()

        # -------------------------------------------------
        # Check credentials
        # -------------------------------------------------

        if user and check_password_hash(
            user["password"],
            password
        ):

            # Store user information
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            # Reset quiz every time user logs in
            session["puzzle_solved"] = False

            # Go to quiz
            return redirect(url_for("quiz"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("signup"))


# =========================================================
# QUIZ
# =========================================================

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    # -----------------------------------------------------
    # User must be logged in
    # -----------------------------------------------------

    if "user_id" not in session:
        return redirect(url_for("login"))

    error = None

    # -----------------------------------------------------
    # Handle quiz submission
    # -----------------------------------------------------

    if request.method == "POST":

        q1 = request.form.get("q1", "").strip()
        q2 = request.form.get("q2", "").strip()
        q3 = request.form.get("q3", "").strip()

        # -------------------------------------------------
        # Correct answers
        # -------------------------------------------------

        correct_q1 = "12-12-2022"
        correct_q2 = "Alfredo chicken pasta"
        correct_q3 = "Hazelnut"

        # -------------------------------------------------
        # Check all answers
        # -------------------------------------------------

        if (
            q1 == correct_q1
            and q2 == correct_q2
            and q3 == correct_q3
        ):

            session["puzzle_solved"] = True

            return redirect(url_for("birthday"))

        # -------------------------------------------------
        # Wrong answer
        # -------------------------------------------------

        error = (
            "Hmm... someone needs to remember "
            "our story a little better! Try again."
        )

    return render_template(
        "quiz.html",
        error=error
    )


# =========================================================
# BIRTHDAY
# =========================================================

@app.route("/birthday")
def birthday():

    # Login required
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Quiz required
    if not session.get("puzzle_solved"):
        return redirect(url_for("quiz"))

    return render_template(
        "birthday.html",
        name=session.get("user_name")
    )


# =========================================================
# VIDEO
# =========================================================

@app.route("/video")
def video():

    # Login required
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Quiz required
    if not session.get("puzzle_solved"):
        return redirect(url_for("quiz"))

    return render_template(
        "video.html",
        name=session.get("user_name")
    )


# =========================================================
# LETTER
# =========================================================

@app.route("/letter")
def letter():

    # Login required
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Quiz required
    if not session.get("puzzle_solved"):
        return redirect(url_for("quiz"))

    return render_template(
        "letter.html",
        name=session.get("user_name")
    )


# =========================================================
# RESET SURPRISE
# =========================================================

@app.route("/reset")
def reset():
    """
    Reset the quiz status without deleting the account.
    Useful while testing the website.
    """

    if "user_id" not in session:
        return redirect(url_for("login"))

    session["puzzle_solved"] = False

    return redirect(url_for("quiz"))


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>404</h1>
    <p>Page not found.</p>
    <a href="/">Go Home</a>
    """, 404


@app.errorhandler(500)
def internal_server_error(error):

    return """
    <h1>500</h1>
    <p>Something went wrong.</p>
    <a href="/">Go Home</a>
    """, 500


# =========================================================
# START APPLICATION
# =========================================================

# Initialize database when the module is imported.
# This is important for PythonAnywhere WSGI.
init_db()


# Only run Flask's development server locally.
# PythonAnywhere will NOT execute this section.
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )