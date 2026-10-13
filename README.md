# TaskFlow — Python Task Manager

TaskFlow is a small task-management web application built with Python, Flask, and SQLite. It was created as a portfolio project to practise web development, database operations, validation, testing, and safe configuration.

## Features

- Create tasks with a title, description, due date, and priority.
- Mark tasks as completed or reopen them.
- Delete tasks.
- Search by title or description.
- Filter tasks by status.
- Responsive layout for desktop and mobile.
- SQLite database created automatically.
- Automated tests using Python's built-in `unittest` framework.

## Tech stack

- Python 3.10+
- Flask
- SQLite
- HTML and CSS
- `unittest`

## Project structure

```text
taskflow-python/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── tests/
    └── test_app.py
```

## Run locally

### 1. Install Python

Use Python 3.10 or newer. Check your version:

```bash
python --version
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, try Command Prompt:

```bat
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the secret key

Copy `.env.example` to `.env` and replace the sample secret with a random value. The application loads `.env` automatically with `python-dotenv`. You can also set environment variables directly in your terminal; those values take precedence in most shell setups.

PowerShell:

```powershell
$env:SECRET_KEY = "put-a-long-random-secret-here"
```

macOS/Linux:

```bash
export SECRET_KEY="put-a-long-random-secret-here"
```

The application has a development fallback key so it can run easily on a local machine. Do not use that fallback in a public production deployment. Never commit your real `.env` file or secrets to GitHub.

### 5. Start the application

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Run the tests

From the project root, with the virtual environment activated:

```bash
python -m unittest discover -s tests -v
```

The tests use a temporary database, so they do not change your local task database.

## Security notes

- SQL queries use placeholders for user-provided values.
- Titles and descriptions are validated on the server.
- Jinja templates escape text by default.
- `.env`, virtual environments, and the local database are ignored by Git.
- The built-in Flask development server is for local development only.
- Before a public deployment, add CSRF protection, production-grade configuration, HTTPS, and a production WSGI server.

## Learning notes

### Why Flask?
Flask is a lightweight Python web framework. It maps URLs to Python functions and renders HTML templates.

### Why SQLite?
SQLite stores the data in a local database file, so the project does not need a separate database server.

### What is a route?
A route connects an HTTP path and method to a Python function. For example, `GET /` shows tasks and `POST /tasks` creates a task.

### Why use SQL placeholders?
A query such as `WHERE id = ?` keeps user input separate from SQL instructions and helps prevent SQL injection.

## Ideas for future improvements

- Add user accounts and login.
- Add CSRF protection.
- Add pagination and task editing.
- Add due-date reminders.
- Add Docker and a deployment workflow.
- Add more tests for invalid dates and priority values.

## License

This project is provided for learning and portfolio use. Add a license file if you want to specify reuse terms.

LINK: https://taskflow-python.onrender.com
