import os
from dotenv import load_dotenv

# FIXED: Explicitly load the .env variables before doing anything else
load_dotenv()

from app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)