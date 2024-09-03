import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def view_data():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    logging.info("Connected to the database.")
    
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    
    logging.info(f"Number of rows fetched: {len(rows)}")
    
    if rows:
        for row in rows:
            print(row)
    else:
        print("No data found in the 'products' table.")
    
    conn.close()
    logging.info("Database connection closed.")

if __name__ == "__main__":
    view_data()
