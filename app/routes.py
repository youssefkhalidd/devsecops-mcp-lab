import sqlite3

from flask import Blueprint, current_app, jsonify, request

from app.database import get_db

tickets_bp = Blueprint("tickets", **name**)

ALLOWED_STATUSES = {"open", "in_progress", "closed"}

def ticket_to_dict(ticket):
"""Convert a SQLite row into a JSON-serializable dictionary."""
return {
"id": ticket["id"],
"title": ticket["title"],
"description": ticket["description"],
"status": ticket["status"],
"created_at": ticket["created_at"],
}

def error_response(message, status_code):
"""Return a consistent JSON error response."""
return jsonify({"error": message}), status_code

def get_json_object():
"""Validate that the request body is a JSON object."""
if not request.is_json:
return None, error_response(
"Content-Type must be application/json",
415,
)

```
data = request.get_json(silent=True)

if not isinstance(data, dict):
    return None, error_response(
        "A valid JSON object is required",
        400,
    )

return data, None
```

def validate_ticket_fields(data, partial=False):
"""Validate ticket fields for create and update operations."""
allowed_fields = {"title", "description", "status"}

```
unknown_fields = set(data.keys()) - allowed_fields

if unknown_fields:
    return f"Unknown fields: {', '.join(sorted(unknown_fields))}"

if not partial and "title" not in data:
    return "The title field is required"

if "title" in data:
    title = data["title"]

    if not isinstance(title, str) or not title.strip():
        return "Title must be a non-empty string"

    if len(title.strip()) > 200:
        return "Title must not exceed 200 characters"

if "description" in data:
    description = data["description"]

    if not isinstance(description, str):
        return "Description must be a string"

    if len(description) > 5000:
        return "Description must not exceed 5000 characters"

if "status" in data:
    status = data["status"]

    if not isinstance(status, str) or status not in ALLOWED_STATUSES:
        return "Status must be open, in_progress, or closed"

return None
```

@tickets_bp.get("/health")
def health():
"""Return the application's health status."""
try:
get_db().execute("SELECT 1").fetchone()

```
    return jsonify({
        "status": "ok",
        "database": "ok",
    }), 200

except sqlite3.Error:
    current_app.logger.exception("Database health check failed")

    return error_response(
        "Service temporarily unavailable",
        503,
    )
```

@tickets_bp.get("/tickets")
def list_tickets():
"""Return all tickets, ordered by ID."""
database = get_db()

```
rows = database.execute(
    """
    SELECT id, title, description, status, created_at
    FROM tickets
    ORDER BY id ASC
    """
).fetchall()

return jsonify([ticket_to_dict(row) for row in rows]), 200
```

@tickets_bp.get("/tickets/[int:ticket_id](int:ticket_id)")
def get_ticket(ticket_id):
"""Return a single ticket by ID."""
database = get_db()

```
ticket = database.execute(
    """
    SELECT id, title, description, status, created_at
    FROM tickets
    WHERE id = ?
    """,
    (ticket_id,),
).fetchone()

if ticket is None:
    return error_response("Ticket not found", 404)

return jsonify(ticket_to_dict(ticket)), 200
```

@tickets_bp.post("/tickets")
def create_ticket():
"""Create a new ticket."""
data, error = get_json_object()

```
if error:
    return error

validation_error = validate_ticket_fields(data)

if validation_error:
    return error_response(validation_error, 400)

title = data["title"].strip()
description = data.get("description", "")
status = data.get("status", "open")

database = get_db()

try:
    cursor = database.execute(
        """
        INSERT INTO tickets (title, description, status)
        VALUES (?, ?, ?)
        """,
        (title, description, status),
    )

    database.commit()

    ticket = database.execute(
        """
        SELECT id, title, description, status, created_at
        FROM tickets
        WHERE id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()

    return jsonify(ticket_to_dict(ticket)), 201

except sqlite3.Error:
    database.rollback()

    current_app.logger.exception("Failed to create ticket")

    return error_response(
        "Unable to create ticket",
        500,
    )
```

@tickets_bp.patch("/tickets/[int:ticket_id](int:ticket_id)")
def update_ticket(ticket_id):
"""Update one or more fields on an existing ticket."""
data, error = get_json_object()

```
if error:
    return error

if not data:
    return error_response(
        "At least one field must be provided",
        400,
    )

validation_error = validate_ticket_fields(
    data,
    partial=True,
)

if validation_error:
    return error_response(validation_error, 400)

database = get_db()

existing_ticket = database.execute(
    "SELECT id FROM tickets WHERE id = ?",
    (ticket_id,),
).fetchone()

if existing_ticket is None:
    return error_response("Ticket not found", 404)

# Only allow fields explicitly supported by this API.
allowed_updates = {
    "title": (
        data["title"].strip()
        if "title" in data
        else None
    ),
    "description": (
        data["description"]
        if "description" in data
        else None
    ),
    "status": (
        data["status"]
        if "status" in data
        else None
    ),
}

updates = {
    field: value
    for field, value in allowed_updates.items()
    if field in data
}

# SQL identifiers cannot be supplied as ordinary bound parameters.
# These column names are safe because they come from our fixed allowlist.
set_clause = ", ".join(
    f"{column} = ?"
    for column in updates
)

values = list(updates.values())
values.append(ticket_id)

try:
    database.execute(
        f"""
        UPDATE tickets
        SET {set_clause}
        WHERE id = ?
        """,
        values,
    )

    database.commit()

    updated_ticket = database.execute(
        """
        SELECT id, title, description, status, created_at
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,),
    ).fetchone()

    return jsonify(ticket_to_dict(updated_ticket)), 200

except sqlite3.Error:
    database.rollback()

    current_app.logger.exception("Failed to update ticket")

    return error_response(
        "Unable to update ticket",
        500,
    )
```

@tickets_bp.delete("/tickets/[int:ticket_id](int:ticket_id)")
def delete_ticket(ticket_id):
"""Delete a ticket by ID."""
database = get_db()

```
try:
    cursor = database.execute(
        "DELETE FROM tickets WHERE id = ?",
        (ticket_id,),
    )

    database.commit()

    if cursor.rowcount == 0:
        return error_response("Ticket not found", 404)

    return "", 204

except sqlite3.Error:
    database.rollback()

    current_app.logger.exception("Failed to delete ticket")

    return error_response(
        "Unable to delete ticket",
        500,
    )
```
