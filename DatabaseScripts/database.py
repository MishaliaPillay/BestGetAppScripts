import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None

def create_table(conn):
    """Create the products table if it doesn't already exist."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image TEXT,
                name TEXT NOT NULL,
                price TEXT,
                source TEXT
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")

def get_product_by_name_and_source(conn, name, source):
    """Get a product by name and source."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, price FROM products WHERE name = ? AND source = ?
    ''', (name, source))
    return cursor.fetchone()

def update_product(conn, product_id, updated_product):
    """Update a product in the products table."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products
            SET image = ?, name = ?, price = ?, source = ?
            WHERE id = ?
        ''', (updated_product['image'], updated_product['name'], updated_product['price'], updated_product['source'], product_id))
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"Error: {e}")

def insert_product(conn, product):
    """Insert a product into the products table."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (image, name, price, source)
            VALUES (?, ?, ?, ?)
        ''', (product['image'], product['name'], product['price'], product['source']))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
def update_or_insert_product(conn, product):
    """Update the product if it exists and the price or image has changed, or insert it if it doesn't exist."""
    existing_product = get_product_by_name_and_source(conn, product['name'], product['source'])
    
    if existing_product:
        product_id, existing_price = existing_product
        # Fetch the current image for this product
        cursor = conn.cursor()
        cursor.execute('SELECT image FROM products WHERE id = ?', (product_id,))
        existing_image = cursor.fetchone()[0]
        
        # Update the product if the price or image has changed
        if existing_price != product['price'] or existing_image != product['image']:
            update_product(conn, product_id, product)
    else:
        # Insert new product if it doesn't exist
        insert_product(conn, product)


def close_connection(conn):
    """Close the database connection."""
    if conn:
        conn.close()
