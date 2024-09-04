import sys
import os
from flask import Flask, jsonify, request, g
import logging

# Add the parent directory to the sys.path to import modules correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the database connection functions
from Database.database import create_connection, close_connection

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        # Construct the full path to the products.db file
        db_path = os.path.join(os.path.dirname(__file__), '../database/products.db')
        g.db = create_connection(db_path)
    return g.db

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.url}")

@app.after_request
def log_response_info(response):
    logging.info(f"Response: {response.status_code}")
    return response

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Price Comparison API"

# Example API endpoint to retrieve products
@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    
    products = []
    for row in rows:
        product = {
            'id': row[0],
            'image': row[1],
            'name': row[2],
            'price': row[3],
            'source': row[4]
        }
        products.append(product)
    
    return jsonify(products)

@app.teardown_appcontext
def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        close_connection(db)

if __name__ == "__main__":
    app.run(debug=True)
