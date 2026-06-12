import os
from app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

# DELETED the db.engine.dispose() block

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))