import sqlite3
import logging
import os

# Setting up the logging to show messages with timestamps
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch and display data from the 'products' table
def view_data():
    # Get the directory of the current script and build the path to 'products.db'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'products.db')
    
    # Check if the database file exists
    if not os.path.exists(db_path):
        logging.error(f"Database file '{db_path}' not found.")
        return
    
    # Connecting to  database file 'products.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()  # We'll use this cursor to run SQL queries
    
    logging.info("Successfully connected to the database.")  # Logging the connection status

    # Running an SQL query to get everything from the 'products' table
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()  # Fetching all the results
    
    logging.info(f"Number of rows fetched: {len(rows)}")  # Log how many rows we got

    # If  found some rows, print each one; otherwise, let the user know there's no data
    if rows:
        for row in rows:
            try:
                print(row)
            except UnicodeEncodeError:
                print("Unable to print row due to encoding error.")
                logging.warning(f"Failed to print row: {row}")  # Log the issue
    else:
        print("No data found in the 'products' table.")  # if table is empty
    
    # Close the connection to the database when done
    conn.close()
    logging.info("Closed the database connection.")  # Log that we've closed the connection

if __name__ == "__main__":
    view_data()
