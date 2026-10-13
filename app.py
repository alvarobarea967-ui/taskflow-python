import os
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("TASKFLOW_DATABASE", BASE_DIR / "instance" / "taskflow.sqlite3"))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=str(DATABASE),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    def get_db():
        if "db" not in __import__("flask").g:
            __import__("flask").g.db = sqlite3.connect(app.config["DATABASE"])
            __import__("flask").g.db.row_factory = sqlite3.Row
            __import__("flask").g.db.execute("PRAGMA foreign_keys = ON")
        return __import__("flask").g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = __import__("flask").g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 120),
                description TEXT NOT NULL DEFAULT '',
                due_date TEXT,
                priority TEXT NOT NULL DEFAULT 'Medium'
                    CHECK(priority IN ('Low', 'Medium', 'High')),
                completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()

    with app.app_context():
        init_db()

    @app.get("/")
    def index():
        status = request.args.get("status", "all")
        query = request.args.get("q", "").strip()[:100]
        sql = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if status == "open":
            sql += " AND completed = 0"
        elif status == "completed":
            sql += " AND completed = 1"
        if query:
            sql += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        sql += " ORDER BY completed ASC, CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, due_date IS NULL, due_date ASC, id DESC"
        tasks = get_db().execute(sql, params).fetchall()
        return render_template("index.html", tasks=tasks, status=status, query=query, today=date.today().isoformat())

    @app.post("/tasks")
    def create_task():
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_date = request.form.get("due_date", "").strip() or None
        priority = request.form.get("priority", "Medium")
        if not title:
            flash("A task title is required.", "error")
            return redirect(url_for("index"))
        if len(title) > 120:
            flash("The title must be 120 characters or fewer.", "error")
            return redirect(url_for("index"))
        if len(description) > 2000:
            flash("The description must be 2,000 characters or fewer.", "error")
            return redirect(url_for("index"))
        if priority not in {"Low", "Medium", "High"}:
            priority = "Medium"
        if due_date:
            try:
                date.fromisoformat(due_date)
            except ValueError:
                flash("Please enter a valid due date.", "error")
                return redirect(url_for("index"))
        db = get_db()
        db.execute(
            "INSERT INTO tasks (title, description, due_date, priority) VALUES (?, ?, ?, ?)",
            (title, description, due_date, priority),
        )
        db.commit()
        flash("Task created.", "success")
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle_task(task_id):
        db = get_db()
        task = db.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if task is None:
            abort(404)
        db.execute("UPDATE tasks SET completed = ? WHERE id = ?", (0 if task["completed"] else 1, task_id))
        db.commit()
        flash("Task status updated.", "success")
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id):
        db = get_db()
        cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()
        if cursor.rowcount == 0:
            abort(404)
        flash("Task deleted.", "success")
        return redirect(url_for("index"))

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app


app = create_app()

if __name__ == "__main__":
    # Local development only. For production, use a production WSGI server.
    app.run(debug=False)
