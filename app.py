import sqlite3
from pathlib import Path
from flask import Flask, request, redirect, url_for, render_template_string

DB_PATH = Path(__file__).parent / "notes.db"
app = Flask(__name__)


def get_db():
    # check_same_thread=False is safe because we use one connection per request
    # and rely on SQLite's internal locking + WAL mode for concurrency.
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_notes_id_desc ON notes(id DESC)"
        )


PAGE = """
<!doctype html>
<title>Notes</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; }
  form { display: flex; gap: .5rem; margin-bottom: 1.5rem; }
  input[type=text] { flex: 1; padding: .5rem; }
  button { padding: .5rem 1rem; cursor: pointer; }
  li { margin: .5rem 0; display: flex; justify-content: space-between; align-items: center; }
  .meta { color: #888; font-size: .8rem; margin-left: .5rem; }
  .del { background: #fee; border: 1px solid #fbb; }
</style>
<h1>Notes</h1>
<form method="post" action="/add">
  <input type="text" name="content" placeholder="Write a note..." required autofocus>
  <button type="submit">Add</button>
</form>
<ul>
{% for n in notes %}
  <li>
    <span>{{ n['content'] }}<span class="meta">{{ n['created_at'] }}</span></span>
    <form method="post" action="/delete/{{ n['id'] }}" style="margin:0">
      <button class="del" type="submit">×</button>
    </form>
  </li>
{% else %}
  <li><em>No notes yet.</em></li>
{% endfor %}
</ul>
"""


@app.route("/")
def index():
    with get_db() as conn:
        notes = conn.execute(
            "SELECT id, content, created_at FROM notes ORDER BY id DESC"
        ).fetchall()
    return render_template_string(PAGE, notes=notes)


@app.route("/add", methods=["POST"])
def add():
    content = request.form.get("content", "").strip()
    if content:
        with get_db() as conn:
            conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    return redirect(url_for("index"))


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete(note_id):
    with get_db() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return redirect(url_for("index"))


def create_app():
    init_db()
    return app


if __name__ == "__main__":
    import os
    init_db()
    port = int(os.environ.get("PORT", 5000))
    try:
        # Prefer waitress (production WSGI, multi-threaded) when available.
        from waitress import serve
        print(f"Serving on http://0.0.0.0:{port} (waitress, 8 threads)")
        serve(app, host="0.0.0.0", port=port, threads=8)
    except ImportError:
        # Fallback: Flask dev server with threading enabled.
        app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
