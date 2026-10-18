import os
from pathlib import Path

from flask import Flask

from app.database import init_app, init_db

def create_app(test_config=None):
app = Flask(**name**, instance_relative_config=True)

```
default_database = Path(app.instance_path) / "tickets.db"

app.config.from_mapping(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY"),
    DATABASE=str(default_database),
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,
)

if test_config is not None:
    app.config.update(test_config)

if not app.config["SECRET_KEY"]:
    app.config["SECRET_KEY"] = "development-only-not-for-production"

# Register database lifecycle handlers.
init_app(app)

# Initialize the database schema.
with app.app_context():
    init_db()

# Register API routes.
from app.routes import tickets_bp

app.register_blueprint(tickets_bp)

return app
