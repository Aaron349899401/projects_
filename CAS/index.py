from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, time, os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "change_this_secret"

LOCKOUT_TIME = 60
MAX_ATTEMPTS = 3
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        attempts INTEGER DEFAULT 0,
        lock_until REAL DEFAULT 0
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        image TEXT,
        author TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# OTHER STUFF
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "userID" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def is_valid(text):
    return text and len(text.strip()) > 0 and len(text) < 300

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- ROUTES ----------
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not is_valid(username) or not is_valid(password):
            return render_template("register.html", error="Invalid input")

        hashed_pw = generate_password_hash(password)
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO Users (username, password) VALUES (?, ?)",
                (username, hashed_pw)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html", error="Username already exists")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    remaining = None
    locked_out = False

    if 'lockout_until' in session:
        if time.time() < session['lockout_until']:
            locked_out = True
            remaining = int(session['lockout_until'] - time.time())
        else:
            session.pop('lockout_until', None)
            session['login_attempts'] = 0

    if request.method == "GET":
        return render_template("login.html", error=error, locked_out=locked_out, remaining=remaining)

    if locked_out:
        error = f"Too many attempts. Try again in {remaining} seconds."
        return render_template("login.html", error=error, locked_out=True, remaining=remaining)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM Users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if 'login_attempts' not in session:
        session['login_attempts'] = 0

    if user and check_password_hash(user["password"], password):
        session['login_attempts'] = 0
        session.pop('lockout_until', None)
        session["userID"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("stories"))

    session['login_attempts'] += 1
    if session['login_attempts'] >= MAX_ATTEMPTS:
        session['lockout_until'] = time.time() + LOCKOUT_TIME
        remaining = LOCKOUT_TIME
        session['login_attempts'] = 0
        locked_out = True
        error = f"Too many attempts. Locked out for {LOCKOUT_TIME} seconds."
    else:
        error = "Invalid username or password"

    return render_template("login.html", error=error, locked_out=locked_out, remaining=remaining)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/stories")
@login_required
def stories():
    conn = get_db()
    all_stories = conn.execute(
        "SELECT * FROM stories ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("stories.html", stories=all_stories)

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    user_stories = conn.execute(
        "SELECT * FROM stories WHERE author = ? ORDER BY id DESC",
        (session["username"],)
    ).fetchall()
    story_count = len(user_stories)
    conn.close()
    return render_template("dashboard.html", stories=user_stories, story_count=story_count)

@app.route("/add_story", methods=["GET", "POST"])
@login_required
def add_story():
    if request.method == "GET":
        return render_template("add_story.html")

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not is_valid(title) or not is_valid(content):
        return render_template("add_story.html", error="Title and content are required.")

    image = "https://via.placeholder.com/300x200.png?text=No+Image"

    file = request.files.get("image_file")
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image = "/" + filepath
    elif request.form.get("image_url"):
        url = request.form["image_url"].strip()
        if url.startswith("http://") or url.startswith("https://"):
            image = url

    conn = get_db()
    conn.execute(
        "INSERT INTO stories (title, content, image, author) VALUES (?, ?, ?, ?)",
        (title, content, image, session["username"])
    )
    conn.commit()
    conn.close()

    return redirect(url_for("stories"))

@app.route("/delete_story/<int:story_id>", methods=["POST"])
@login_required
def delete_story(story_id):
    conn = get_db()
    story = conn.execute(
        "SELECT * FROM stories WHERE id = ?", (story_id,)
    ).fetchone()

    if story and story["author"] == session["username"]:
        conn.execute("DELETE FROM stories WHERE id = ?", (story_id,))
        conn.commit()

    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/edit_story/<int:story_id>", methods=["GET", "POST"])
@login_required
def edit_story(story_id):
    conn = get_db()
    story = conn.execute(
        "SELECT * FROM stories WHERE id=?", (story_id,)
    ).fetchone()

    if not story or story["author"] != session["username"]:
        conn.close()
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not is_valid(title) or not is_valid(content):
            return render_template("edit_story.html", story=story, error="Title and content are required.")

        image = story["image"]

        file = request.files.get("image_file")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image = "/" + filepath
        elif request.form.get("image_url"):
            url = request.form["image_url"].strip()
            if url.startswith("http://") or url.startswith("https://"):
                image = url

        conn.execute(
            "UPDATE stories SET title = ?, content = ?, image = ? WHERE id = ?",
            (title, content, image, story_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("edit_story.html", story=story)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)