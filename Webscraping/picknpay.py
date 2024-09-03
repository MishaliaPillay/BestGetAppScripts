from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager#type:ignore
import logging
import sys
import traceback
import time
# This line handles characters that aren't default/
# , it prevents errors later on also ensures\
#  that these non default charcters are displayed correctly.
sys.stdout.reconfigure(encoding='utf-8')

#Logging which helps to track progress and and problems with the code
#Info is the level of the logged message and the formant give the timestamp of the message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def extract_product_info(driver):
    """
        Extracts product information from a given web page using the provided Selenium WebDriver.

        Args:
            driver (webdriver.Chrome): The Selenium WebDriver instance used for navigating and interacting with the webpage.

        Returns:
            list of dict: A list of dictionaries where each dictionary contains information about a product, including image URL, name, and price.
        """
     #This is an empty list that will store the products that are scrapped from the pnp website
    products = []

    try:
         # This first checks if the main contanier div.cx-product-container--grid.ml-0.mr-0.ng-star-inserted is present in the dom before continuing with rest of the code
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.cx-product-container--grid.ml-0.mr-0.ng-star-inserted"))
        )

         # checking all the elements in the web page that matches the specifeied parameter
        product_items = driver.find_elements(By.CSS_SELECTOR, "ui-product-grid-item.ng-star-inserted")
        #checks if there are no product-items found
        if not product_items:
            print("No product items found!")
            return products

        for item in product_items:
            # Makes empty variable to store the extracted data and sets the default to none
            image_src = None
            product_name = None
            product_price = None

           # Tries to find image for current product
            try:
                product_image = item.find_element(By.CSS_SELECTOR, "img")
                image_src = product_image.get_attribute("src")
            except Exception as e:
                print(f"Error finding product image: {e}")

            # Tries to find name for current product
            try:
                product_name_element = item.find_element(By.CSS_SELECTOR, "div.product-grid-item__info-container > a > span")
                product_name = product_name_element.text
            except Exception as e:
                print(f"Error finding product name: {e}")

            # Tries to find price for current product
            try:
                product_price_element = item.find_element(By.CSS_SELECTOR, "div.cms-price-display > div > div.price")
                product_price = product_price_element.text
            except Exception as e:
                print(f"Error finding product price: {e}")

            # checks whether atleast one product elemnst are availble - image or name or price
            if image_src or product_name or product_price:
                products.append({
                    "image": image_src,
                    "name": product_name,
                    "price": product_price, "source": "Pick n pay"
                })
#catches all expection that might occur
    except Exception as e:
        print(f"Error extracting product info: {e}")
        traceback.print_exc()
        # Print the html of current page
        print(driver.page_source)
#if try is successful it returns a list of dictionires for each product
    return products

def main():
    """
    Main function to set up the Selenium WebDriver, navigate through pages, and extract product information.

    This function configures the Chrome WebDriver, navigates through multiple pages of the product listing,
    and extracts product information using the `extract_product_info` function. It collects data from all pages
    and prints the results to the console.
"""
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")# Uncomment to see browser actions 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

     # makes a new chrome driver with soeficfied options, installs proper version of chrome and applies settings from above 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    #makes an empty list to store product info extracted will be poulated with the dictionaries 
    all_products = []

    try:
        # Loop through pages from 0 to 71
        for page_number in range(0, 3):
            # Format the URL with the current page number
            url = f'https://www.pnp.co.za/c/pnpbase?query=:relevance:allCategories:pnpbase:category:food-cupboard-423144840&currentPage={page_number}'
            
            print(f"Scraping page {page_number}...")
            
            # Navigate to the URL
            driver.get(url)

            # makes sure page is fully loaded before trying to extract data
            WebDriverWait(driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

             # calls a function to extract from the current pag
            products = extract_product_info(driver)
            #allows script to gather data from all pages into one list
            all_products.extend(products)

            time.sleep(1)  # pauses the script between each page so doesn't overload the server

    finally:
         #closes browser after each session
        driver.quit()

    # For future use, will store in a database


    
    # For now, print to console
    return all_products if all_products else []

if __name__ == "__main__":
    main()
