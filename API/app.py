from flask import Flask, jsonify, request, g
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DatabaseScripts')))

from database import create_connection, close_connection#type:ignore


# Dynamically get the absolute path to the database file
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'DatabaseScripts', 'products.db')

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
         g.db = create_connection(db_path)
    return g.db

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

#  API endpoint to retrieve products
@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    
    products = []
    # Iterate through each row returned from the database
    for row in rows:
        # Map the row data to a product dictionary
        product = {
            'id': row[0],
            'image': row[1],
            'name': row[2],
            'price': row[3],
            'source': row[4]
        }
        products.append(product)
     # Return the list of products as a JSON response
    return jsonify(products)

@app.teardown_appcontext
 # Remove the database connection from the context
def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        close_connection(db)

if __name__ == "__main__":
    app.run(debug=True)
