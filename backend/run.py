# backend/run.py
from app import create_app

# Initialize the Flask application using the development configuration
app = create_app("development")

if __name__ == "__main__":
    # Run the server on port 5000
    app.run(debug=True, port=5000)