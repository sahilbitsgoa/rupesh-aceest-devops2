from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "mysecretkey123"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_NAME = os.path.join(BASE_DIR, "aceest_fitness.db")


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    print("Using database at:", DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES ('admin', 'admin', 'Admin')
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT
        )
    """)

    conn.commit()
    conn.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password)
        )
        row = cur.fetchone()
        conn.close()

        if row:
            session["username"] = username
            session["role"] = row["role"]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"]
    )


@app.route("/add-client", methods=["GET", "POST"])
@login_required
def add_client():
    message = None
    error = None

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        height = request.form.get("height")
        weight = request.form.get("weight")
        program = request.form.get("program")

        if not name or not program:
            error = "Name and Program are required"
        else:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO clients (name, age, height, weight, program)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, age, height, weight, program))
                conn.commit()
                conn.close()
                message = "Client added successfully"
            except sqlite3.IntegrityError:
                error = "Client with this name already exists"
            except Exception as e:
                error = f"Error: {str(e)}"

    return render_template("add_client.html", message=message, error=error)


@app.route("/clients")
@login_required
def clients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients ORDER BY id DESC")
    clients_data = cur.fetchall()
    conn.close()

    return render_template("clients.html", clients=clients_data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)