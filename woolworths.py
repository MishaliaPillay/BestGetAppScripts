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

# This line handles characters that aren't default/
# , it prevents errors later on also ensures\
#  that these non default charcters are displayed correctly.
sys.stdout.reconfigure(encoding='utf-8')

#Logging which helps to track progress and and problems with the code
#Info is the level of the logged message and the formant give the timestamp of the message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_product_info(driver):
    """
    Extracts product information from the current page using the provided Selenium WebDriver.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance used for navigating and interacting with the webpage.

    Returns:
        list of dict: A list of dictionaries where each dictionary contains information about a product, including image URL, name, and price.
"""
    #This is an empty list that will store the products that are scrapped from the checkers website
    products = []

    try:
         # This first checks if the main contanier div.banner-wrapper is present in the dom before continuing with rest of the code
        WebDriverWait(driver, 50).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "div.banner-wrapper"))
        )

        # Scroll through the page to load all items
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new items to load

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Wait for product items to be present
        WebDriverWait(driver, 50).until(
            expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-list__item"))
        )

        # Fetch all product items,# checking all the elements in the web page that matches the specifeied parameter
        product_items = driver.find_elements(By.CSS_SELECTOR, "div.product-list__item")
        #checks if there are not product-items found
        if not product_items:
            logging.warning("No product items found!")#uses the warning level 
            return products

        for item in product_items:
            # Scrolls the item into view
            driver.execute_script("arguments[0].scrollIntoView();", item)
            time.sleep(0.5)  # Gives time for image to load

            # Makes empty variable to store the extracted data and sets the default to none
            image_src = None
            product_name = None
            product_price = None

            # Tries to find image for current product
            try:
                product_image = item.find_element(By.CSS_SELECTOR, "div.product--image > img")
                image_src = product_image.get_attribute("src")
            except Exception as e:
                logging.debug(f"Error finding product image: {e}")#change log level to debug to find what went wrong

            # Tries to find name for current producte
            try:
                product_name_element = item.find_element(By.CSS_SELECTOR, "div.range--title.product-card__name > a")
                product_name = product_name_element.text
            except Exception:
                try:
                    logging.info("First selector failed, trying the second one...")
                    product_name_element = item.find_element(By.CSS_SELECTOR, "div.product--desc > a > h2")
                    product_name = product_name_element.text
                except Exception as e:
                    logging.warning(f"Both selectors failed to find the product name: {e}")#change log level to debug to find what went wrong

            # Tries to find price for current product
            try:
                product_price_element = item.find_element(By.CSS_SELECTOR, "span.font-graphic > strong")
                product_price = product_price_element.text
            except Exception as e:
                logging.debug(f"Error finding product price: {e}")#change log level to debug to find what went wrong 

            # checks is any conditions is met image , name or price 
            if any([image_src, product_name, product_price]):
                products.append({
                    "image": image_src,
                    "name": product_name,
                    "price": product_price,"source": "Woolworths"
                })

    except Exception as e:
        logging.error(f"Error extracting product info: {e}")#provides insight the excpection tha was caught
        logging.debug(traceback.format_exc()) #captures and then formats the ecpection
#if try is successful it returns a list of dictionires for each product
    return products

def main():
    """
    Main function to set up the Selenium WebDriver, navigate through pages, and extract product information.

    This function configures the Chrome WebDriver, navigates through multiple pages of the product listing,
    and extracts product information using the `extract_product_info` function. It collects data from all pages
    and prints the results to the console.
    """
    # Sets the preferences for the chrome browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")# Uncomment to see browser actions 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # makes a new chrome driver with soeficfied options, installs proper version of chrome and applies settings from above 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    #makes an empty list to store product info extracted will be poulated with the dictionaries 
    all_products = []

    try:
        # Iterate over pages from 0 to 326 (increments of 24)
        for page_number in range(0, 4):
            offset = page_number * 24
            # Format the URL with the current offset
            url = f'https://www.woolworths.co.za/cat/Food/_/N-1z13sk5?No={offset}&Nrpp=24'
            
            logging.info(f"Scraping page {page_number} with offset {offset}...")
            
            # Navigate to the URL
            driver.get(url)

            # makes sure page is fully loaded before trying to extract datad
            WebDriverWait(driver, 20).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # calls a function to extract from the current page
            products = extract_product_info(driver)
            #allows script to gather data from all pages into one list
            all_products.extend(products)

            time.sleep(1)  # pauses the script between each page so doesn't overload the server

    finally:
        #closes browser after each session 
        driver.quit()

    # For future use, store in a database
    return all_products if all_products else []

if __name__ == "__main__":
    main()
