import os
import tempfile
import unittest

from app import create_app


class TaskFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.sqlite3")
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE": self.db_path,
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_task(self, title="Study Python", **extra):
        data = {"title": title, "description": "", "priority": "Medium"}
        data.update(extra)
        return self.client.post("/tasks", data=data, follow_redirects=True)

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TaskFlow", response.data)

    def test_create_task(self):
        response = self.create_task("Finish homework")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Finish homework", response.data)

    def test_blank_title_is_rejected(self):
        response = self.create_task("   ")
        self.assertIn(b"A task title is required.", response.data)
        self.assertNotIn(b'class="task-title-row"><h3></h3>', response.data)

    def test_task_can_be_completed(self):
        self.create_task("Test completion")
        with self.app.app_context():
            from flask import current_app
            import sqlite3
            db = sqlite3.connect(current_app.config["DATABASE"])
            task_id = db.execute("SELECT id FROM tasks WHERE title = ?", ("Test completion",)).fetchone()[0]
            db.close()
        response = self.client.post(f"/tasks/{task_id}/toggle", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Completed", response.data)

    def test_task_can_be_deleted(self):
        self.create_task("Task to delete")
        with self.app.app_context():
            from flask import current_app
            import sqlite3
            db = sqlite3.connect(current_app.config["DATABASE"])
            task_id = db.execute("SELECT id FROM tasks WHERE title = ?", ("Task to delete",)).fetchone()[0]
            db.close()
        response = self.client.post(f"/tasks/{task_id}/delete", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Task to delete", response.data)

    def test_search_filters_tasks(self):
        self.create_task("Learn Flask")
        self.create_task("Practise SQL")
        response = self.client.get("/?q=Flask")
        self.assertIn(b"Learn Flask", response.data)
        self.assertNotIn(b"Practise SQL", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_missing_task_returns_404(self):
        response = self.client.post("/tasks/99999/delete")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
