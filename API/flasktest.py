from flask import Flask, jsonify, request
import logging
from DatabaseScripts.database import create_connection, update_or_insert_product, close_connection

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a connection to the SQLite database
conn = create_connection('products.db')

# Middleware Example: Logging Requests
@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.url}")

@app.after_request
def log_response_info(response):
    logging.info(f"Response: {response.status_code}")
    return response

@app.route('/')
def home():
    return "Welcome to the Price Comparison API"

# Close the database connection when the server shuts down
@app.teardown_appcontext
def close_db_connection(exception):
    close_connection(conn)

if __name__ == "__main__":
    app.run(debug=True)
