from Database.database import create_connection, create_table, update_or_insert_product, close_connection
from Webscraping.checkers import main as checkers
from Webscraping.picknpay import main as pnp
from Webscraping.woolworths import main as woolworths
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Step 1: Create a connection to the database
    conn = create_connection('products.db')
    if conn is None:
        logging.error("Failed to create database connection. Exiting.")
        return

    # Step 2: Create the products table
    create_table(conn)

    # Step 3: Run the web scrapers and store data in the database
    try:
        logging.info("Running Woolworths scraper...")
        woolworths_products = woolworths()  # Run Woolworths scraper
        for product in woolworths_products:
            update_or_insert_product(conn, product)
        logging.info(f"Woolworths scraper completed: {len(woolworths_products)} products found.")
    except Exception as e:
        logging.error(f"Woolworths scraper failed: {e}")
    
    try:
        logging.info("Running Checkers scraper...")
        checkers_products = checkers()  # Run Checkers scraper
        for product in checkers_products:
            update_or_insert_product(conn, product)
        logging.info(f"Checkers scraper completed: {len(checkers_products)} products found.")
    except Exception as e:
        logging.error(f"Checkers scraper failed: {e}")

    try:
        logging.info("Running PnP scraper...")
        pnp_products = pnp()  # Run PnP scraper
        for product in pnp_products:
            update_or_insert_product(conn, product)
        logging.info(f"PnP scraper completed: {len(pnp_products)} products found.")
    except Exception as e:
        logging.error(f"PnP scraper failed: {e}")
    
    # Step 4: Close the database connection
    close_connection(conn)

if __name__ == "__main__":
    main()