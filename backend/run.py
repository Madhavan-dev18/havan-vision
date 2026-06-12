import os
from app import create_app, db

# Force production config on Render to ensure secure cookie settings apply
app = create_app(os.getenv("FLASK_ENV", "production"))

# CRITICAL: Create tables if they do not exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Render's port requirement
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))