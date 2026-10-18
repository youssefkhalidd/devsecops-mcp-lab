import os
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL CHECK (length(trim(title)) > 0),
description TEXT NOT NULL DEFAULT '',
status TEXT NOT NULL DEFAULT 'open'
CHECK (status IN ('open', 'in_progress', 'closed')),
created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def get_db():
"""Return the SQLite connection associated with this application context."""
if "db" not in g:
database_path = current_app.config["DATABASE"]

```
    # Create the parent directory for file-backed databases.
    if database_path != ":memory:":
        Path(database_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    connection = sqlite3.connect(
        database_path,
        timeout=5.0,
    )

    # Return rows that support both index-based and column-name access.
    connection.row_factory = sqlite3.Row

    # Enforce SQLite foreign-key constraints when we add relationships.
    connection.execute("PRAGMA foreign_keys = ON")

    # Set a busy timeout to reduce immediate failures under contention.
    connection.execute("PRAGMA busy_timeout = 5000")

    g.db = connection

return g.db
```

def close_db(_error=None):
"""Close the connection associated with the current application context."""
connection = g.pop("db", None)

```
if connection is not None:
    connection.close()
```

def init_db():
"""Create the database schema if it does not already exist."""
database = get_db()
database.executescript(SCHEMA)
database.commit()

def init_app(app):
"""Register database lifecycle handlers with the Flask application."""
app.teardown_appcontext(close_db)

```
@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Database initialized.")
