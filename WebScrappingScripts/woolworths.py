import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
import sys
import time
import logging
import traceback

# This line handles characters that aren't default and prevents errors later on.
sys.stdout.reconfigure(encoding='utf-8')

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_product_info(driver):
    """
    Extracts product information from the current page using the provided Selenium WebDriver.
    """
    products = []

    try: # Wait until the banner wrapper is present
        WebDriverWait(driver, 50).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "div.banner-wrapper"))
        )

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
 # Wait until all product items are present
        WebDriverWait(driver, 50).until(
            expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-list__item"))
        )

        product_items = driver.find_elements(By.CSS_SELECTOR, "div.product-list__item")
        if not product_items:
            logging.warning("No product items found!")
            return products

        for item in product_items:
            driver.execute_script("arguments[0].scrollIntoView();", item)
            time.sleep(0.5)

            image_src = None
            product_name = None
            product_price = None
# Try to find the product image
            try:
                product_image = item.find_element(By.CSS_SELECTOR, "div.product--image > img")
                image_src = product_image.get_attribute("src")
            except Exception as e:
                logging.debug(f"Error finding product image: {e}")
# Try to find the product name
            try:
                product_name_element = item.find_element(By.CSS_SELECTOR, "div.range--title.product-card__name > a")
                product_name = product_name_element.text
            except Exception:
                try:
                    logging.info("First selector failed, trying the second one...")
                    product_name_element = item.find_element(By.CSS_SELECTOR, "div.product--desc > a > h2")
                    product_name = product_name_element.text
                except Exception as e:
                    logging.warning(f"Both selectors failed to find the product name: {e}")
  # Try to find the product price
            try:
                product_price_element = item.find_element(By.CSS_SELECTOR, "span.font-graphic > strong")
                product_price = product_price_element.text
            except Exception as e:
                logging.debug(f"Error finding product price: {e}")
 # If any product data is found, append it to the list
            if any([image_src, product_name, product_price]):
                products.append({
                    "image": image_src,
                    "name": product_name,
                    "price": product_price,
                    "source": "Woolworths"
                })

    except Exception as e:
        logging.error(f"Error extracting product info: {e}")
        logging.debug(traceback.format_exc())

    return products

def main():
    """
    Main function to set up the Selenium WebDriver, navigate through pages, and extract product information.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    all_products = []

    try:
        for page_number in range(0, 322):
            offset = page_number * 24
            url = f'https://www.woolworths.co.za/cat/Food/_/N-1z13sk5?No={offset}&Nrpp=24'

            for attempt in range(3):  # Retry up to 3 times
                try:
                    logging.info(f"Scraping page {page_number} with offset {offset}...")
                    
                    driver.get(url)
                    WebDriverWait(driver, 20).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    
                    # If successful, break out of retry loop
                    break
                except Exception as e:
                    logging.warning(f"Timeout or error on page {page_number}: {e}")
                    if attempt < 2:
                        logging.info("Retrying...")
                        time.sleep(5)  # Wait before retrying
                    else:
                        logging.error(f"Failed to load page {page_number} after 3 attempts.")
                        return all_products  # Return collected products so far in case of failure

            # Extract product information
            products = extract_product_info(driver)
            all_products.extend(products)

            # Random delay between 2 and 5 seconds to avoid overloading the server
            time.sleep(random.uniform(2, 5))

    finally:
        driver.quit()
    #print(all_products)
    return all_products if all_products else []

if __name__ == "__main__":
    main()
