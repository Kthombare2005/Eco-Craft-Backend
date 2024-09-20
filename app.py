from flask import Flask, request, jsonify, make_response
import psycopg2
from psycopg2 import Error
from werkzeug.security import generate_password_hash, check_password_hash
import sys

app = Flask(__name__)

# Function to create PostgreSQL connection
def create_postgresql_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",            # Your PostgreSQL host
            user="postgres",             # Your PostgreSQL username
            password="Ketan@2005",       # Your PostgreSQL password
            database="Eco-Craft"         # Your database name
        )
        print("PostgreSQL Database connection successful")
        return connection
    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}", file=sys.stderr)
        return None

# Establish PostgreSQL connection
postgresql_connection = create_postgresql_connection()

# Handle preflight (OPTIONS) requests
@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

# Login route
@app.route('/login', methods=['POST'])
def login():
    cursor = None
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if postgresql_connection is None:
            return jsonify({"message": "Database connection failed"}), 500

        cursor = postgresql_connection.cursor()

        # Fetch user from the database by email
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "Invalid email or password"}), 400

        stored_password_hash = user[3]  # Assuming password is stored in the 4th column

        # Compare the hashed password in the database with the entered password
        if not check_password_hash(stored_password_hash, password):
            return jsonify({"message": "Invalid email or password"}), 400

        # If the password matches, return the user information
        return jsonify({
            "message": "Login successful",
            "user": {
                "name": user[1],  # Assuming name is in the 2nd column
                "email": user[2],  # Assuming email is in the 3rd column
                "role": user[4]   # Assuming role is in the 5th column
            }
        }), 200

    except Exception as e:
        print(f"Error during login: {e}", file=sys.stderr)
        return jsonify({"message": "Internal server error"}), 500

    finally:
        if cursor:
            cursor.close()

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)

