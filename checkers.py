from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager#type:ignore
import sys
import logging
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
    Extracts product information from the current page using the provided Selenium WebDriver.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance used for navigating and interacting with the webpage.

    Returns:
        list of dict: A list of dictionaries where each dictionary contains information about a product, including image URL, name, and price.
    """
    #This is an empty list that will store the products that are scrapped from the checkers website
    products = []

    try:
        # This first checks if the main contanier div.product__listing.product__grid is present in the dom before continuing with rest of the code
        WebDriverWait(driver, 30).until(
           expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "div.product__listing.product__grid"))
        )

         # checking all the elements in the web page that matches the specifeied parameter
        product_items = driver.find_elements(By.CSS_SELECTOR, "div.item-product")
        #checks if there are no product-items found
        if not product_items:
            logging.warning("No product items found!")#uses the warning level 
            return products

        for item in product_items:
             # Makes empty variable to store the extracted data and sets the default to none
            image_src = None
            product_name = None
            product_price = None

            # Tries to find image for current product
            try:
                product_image = item.find_element(By.CSS_SELECTOR, "div.item-product__image.__image > a > img")
                image_src = product_image.get_attribute("src")
            except Exception as e:
                logging.debug(f"Error finding product image: {e}")#change log level to debug to find what went wrong 

            # Tries to find name for current product
            try:
                product_name_element = item.find_element(By.CSS_SELECTOR, "h3.item-product__name > a")
                product_name = product_name_element.text
            except Exception as e:
                logging.debug(f"Error finding product name: {e}")#change log level to debug to find what went wrong 

            # Tries to find price for current product
            try:
                product_price_element = item.find_element(By.CSS_SELECTOR, "div.special-price__price > span")
                product_price = product_price_element.text
            except Exception as e:
                logging.debug(f"Error finding product price: {e}")#change log level to debug to find what went wrong 

            # checks whether atleast one product elemnst are availble - image or name or price
            if image_src or product_name or product_price:
                #the dictionary below structures how extracted data is stored
                products.append({
                    "image": image_src,
                    "name": product_name,
                    "price": product_price,"source": "Checkers"
                })
#catches all expection that might occure 
    except Exception as e:
        logging.error(f"Error extracting content: {e}")#provides insight the excpection tha was caught
        logging.debug(driver.page_source)#logs the html of the page which helps find what went wrong
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
    chrome_options.add_argument("--headless")  # Uncomment to see browser actions 
    chrome_options.add_argument("--disable-extensions")#turns off extensions
    chrome_options.add_argument("--disable-gpu")# useful when in headless mode to prevnt rendering issues
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")


    # makes a new chrome driver with soeficfied options, installs proper version of chrome and applies settings from above 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    #makes an empty list to store product info extracted will be poulated with the dictionaries 
    all_products = []

    try:
        # Loop through pages from 0 to 355
        for page_number in range(0, 3):
            # Formats the URL with the current page number
            url = f'https://www.checkers.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={page_number}'
            
            logging.info(f"Scraping page {page_number}...")
            
            # Navigates to the URL
            driver.get(url)

            # makes sure page is fully loaded before trying to extract data
            WebDriverWait(driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # calls a function to extract from the current page 
            products = extract_product_info(driver)
            #allows script to gather data from all pages into one list 
            all_products.extend(products)

            # pauses the script between each page so doesn't overload the server
            time.sleep(2)

    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        logging.debug(driver.page_source)#logs html of page 
    #excuets below even if errors occur
    finally:
        #closes browser after each session 
        driver.quit()

    # For future use,will store in a database
    # For now, print to console
    return all_products if all_products else []

if __name__ == "__main__":
    main()
