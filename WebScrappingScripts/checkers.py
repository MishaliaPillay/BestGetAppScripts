from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager#type:ignore
import sys
import logging
import time

# This line handles characters that aren't default, to prevent errors and display non-default characters correctly.
sys.stdout.reconfigure(encoding='utf-8')

# Logging helps to track progress and problems with the code.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_product_info(driver):
    products = []

    try:
        # Wait for the product grid or main container to be loaded
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.product__listing.product__grid"))
        )

        # Wait for all product items to be present in the DOM
        product_items = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.item-product"))
        )

        for item in product_items:
            image_src = None
            product_name = None
            product_price = None

            # Retry logic for missing information (price, image, name)
            retries = 3
            while retries > 0 and (product_price is None or product_name is None or image_src is None):
                retries -= 1

                # Find the price for the current product (relative to the current item)
                try:
                    product_price_element = item.find_element(By.CSS_SELECTOR, "div.special-price__price > span")
                    product_price = product_price_element.text
                except Exception as e:
                    logging.debug(f"Error finding product price: {e}")

                # Find the image for the current product
                try:
                    product_image = item.find_element(By.CSS_SELECTOR, "div.item-product__image.__image > a > img")
                    image_src = product_image.get_attribute("src")
                except Exception as e:
                    logging.debug(f"Error finding product image: {e}")

                # Find the name for the current product
                try:
                    product_name_element = item.find_element(By.CSS_SELECTOR, "h3.item-product__name > a")
                    product_name = product_name_element.text
                except Exception as e:
                    logging.debug(f"Error finding product name: {e}")

                time.sleep(1)  # Small delay before retrying

            # If the image, name, and price were found, store the product information
            if image_src and product_name and product_price:
                products.append({
                    "image": image_src,
                    "name": product_name,
                    "price": product_price,
                    "source": "Checkers"
                })
            else:
                logging.warning(f"Skipping product due to missing info: name={product_name}, price={product_price}, image={image_src}")

    except Exception as e:
        logging.error(f"Error extracting content: {e}")
        logging.debug(driver.page_source)

    return products

def main():
    """
    Main function to set up the Selenium WebDriver, navigate through pages, and extract product information.
    """
    # Sets the preferences for the chrome browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Uncomment to see browser actions 
    chrome_options.add_argument("--disable-extensions")  # Turns off extensions
    chrome_options.add_argument("--disable-gpu")  # Useful when in headless mode to prevent rendering issues
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")

    # Creates a new Chrome driver with specified options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    all_products = []

    try:
        # Loop through pages
        for page_number in range(0, 355):
            url = f'https://www.checkers.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page_number}'

            logging.info(f"Scraping page {page_number}...")
            
            # Navigate to the URL
            driver.get(url)

            # Wait for the page to fully load
            WebDriverWait(driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # Extract products from the current page
            products = extract_product_info(driver)
            all_products.extend(products)

            time.sleep(2)  # Pause to avoid overloading the server

    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        logging.debug(driver.page_source)
    finally:
        # Close the browser after the session
        driver.quit()

    return all_products if all_products else []

if __name__ == "__main__":
    products = main()
    for i, product in enumerate(products, 1):
        print(f"Product {i}: {product}")
