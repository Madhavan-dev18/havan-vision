import os
from app import create_app, db

# Force production config on Render to ensure secure cookie settings apply
app = create_app(os.getenv("FLASK_ENV", "production"))

# CRITICAL: Create tables if they do not exist.
# Wrapped in try/except so a transient DB connection issue at boot
# doesn't crash the whole process before Gunicorn can even bind the port.
with app.app_context():
    try:
        db.create_all()
        app.logger.info("Database tables verified/created successfully.")
    except Exception as e:
        app.logger.critical(f"DB INIT FAILED: {e}")

if __name__ == "__main__":
    # Render's port requirement
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))