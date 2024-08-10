import csv
import time
import random
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import subprocess

# MySQL Connection Configuration
mysql_config = {
    'host': 'localhost',
    'database': 'prod_data',
    'user': 'root',
    'password': 'seecs@123'
}

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def insert_product_data(self, product_data):
        insert_query = """
        INSERT INTO trendyol (
            title, brand_name, short_description, product_url, image_url,
            social_proof, rating_score, review_count, price, badges
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        try:
            for data in product_data:
                # Convert list to string for badges
                badge_texts = ', '.join(data['badges'])
                
                self.cursor.execute(insert_query, (
                    data['title'],
                    data['brand_name'],
                    data['short_description'],
                    data['product_url'],
                    data['image_url'],
                    data['social_proof'],
                    data['rating_score'],
                    data['review_count'],
                    data['price'],
                    badge_texts,
                ))
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"Error inserting data: {err}")
            self.conn.rollback()


class ConfigManager:
    def __init__(self, driver_path):
        self.driver_path = driver_path

    def get_driver_options(self):
        user_data_dir = r"C:\Users\user\AppData\Local\Google\Chrome\User Data"
        profile_dir = "Profile 2"
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"--profile-directory={profile_dir}")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--headless")
        return chrome_options

class WebDriverManager:
    def __init__(self, config):
        self.driver_path = config.driver_path
        self.driver = None
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.setup_driver(config.get_driver_options())
        self.clear_cache()

    def setup_driver(self, chrome_options):
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def clear_cache(self):
        try:
            # Access Chrome DevTools Protocol
            self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
            print("Cache cleared successfully.")
        except Exception as e:
            print(f"Error clearing cache: {e}")

    def load_page(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 40).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class^="prdct-cntnr-wrppr"]'))
        )
        
        WebDriverWait(self.driver, 40).until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '[class="tab__link tab__link-active"]'),
            'ALL PRODUCTS'  
        )
        )

    def close_driver(self):
        if self.driver:
            self.driver.quit()

class HtmlParser:
    @staticmethod
    def parse_html(element):
        inner_html = element.get_attribute('innerHTML')
        return BeautifulSoup(inner_html, 'html.parser')

    @staticmethod
    def get_element_text(soup, selector, multiple=False):
        if multiple:
            elements = soup.select(selector)
            return [element.text.strip() for element in elements] if elements else None
        else:
            element = soup.select_one(selector)
            return element.text.strip() if element else None

class ProductExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.product_urls = []  # List to store product URLs

    def extract_products(self):
        elements = self.driver.find_elements(By.CSS_SELECTOR, '[class="p-card-wrppr with-campaign-view add-to-bs-card"] ')
        products = []
        for element in elements:
            try:
                soup = HtmlParser.parse_html(element)
                product_data = self.extract_product_data(soup)
                if product_data:
                    products.append(product_data)
                    self.product_urls.append(product_data['product_url'])  # store product URL
                    ProductPrinter.print_product_data(product_data)
                break #edit here
            except Exception as e:
                print(f"Error extracting product data: {e}")
                continue
        return products

    def extract_product_data(self, soup):
        try:
            # Print the soup to debug and verify HTML structure
            print(soup.prettify())

            # Extract title and brand name
            title_element = soup.find('span', class_='prdct-desc-cntnr-name hasRatings')
            brand_name_element = soup.find('span', class_='prdct-desc-cntnr-ttl')
            description_element = soup.find('div', class_='product-desc-sub-text')

            title = title_element.get_text(strip=True) if title_element else 'N/A'
            brand_name = brand_name_element.get_text(strip=True) if brand_name_element else 'N/A'
            short_description = description_element.get_text(strip=True) if description_element else 'N/A'

            # Extract the product URL
            product_url_element = soup.find('a', href=True)
            product_url = product_url_element['href'] if product_url_element else ''
            full_product_url = "https://www.trendyol.com" + product_url  # Ensure this is the correct base URL

            # Extract the image URL
            image_element = soup.find('img', class_='p-card-img')
            image_url = image_element['src'] if image_element else 'N/A'

            # Extract social proof
            social_proof_element = soup.find('div', class_='social-proof')
            social_proof = social_proof_element.get_text(strip=True) if social_proof_element else 'N/A'

            # Extract rating score and review count
            rating_score_element = soup.find('span', class_='rating-score')
            review_count_element = soup.find('span', class_='ratingCount')
            rating_score = rating_score_element.get_text(strip=True) if rating_score_element else 'N/A'
            review_count = review_count_element.get_text(strip=True).strip("()") if review_count_element else 'N/A'

            # Extract price
            price_element = soup.find('div', class_='prc-box-dscntd')
            price = price_element.get_text(strip=True) if price_element else 'N/A'

            # Extract badges
            badge_elements = soup.find_all('div', class_='product-badge')
            badge_texts = [badge.get_text(strip=True) for badge in badge_elements] if badge_elements else []

            # Extract delivery info
            delivery_info = []  # Adjust this based on the actual delivery info elements present
            delivery_info_element = soup.find('span', class_='prdct-tlvrm-tp')
            if delivery_info_element:
                delivery_info.append(delivery_info_element.get_text(strip=True))
            delivery_info_element = soup.find('span', class_='prdct-tlvrm-bttm')
            if delivery_info_element:
                delivery_info.append(delivery_info_element.get_text(strip=True))

            product_data = {
                'title': title,
                'brand_name': brand_name,
                'short_description': short_description,
                'product_url': full_product_url,
                'image_url': image_url,
                'social_proof': social_proof,
                'rating_score': rating_score,
                'review_count': review_count,
                'price': price,
                'badges': badge_texts,
            }

            return product_data

        except Exception as e:
            print(f"Error extracting data: {e}")
            return None


class ProductPrinter:
    @staticmethod
    def print_product_data(product):
        print("Product Title:", product['title'])
        print("Brand Name:", product['brand_name'])
        print("Short Description:", product['short_description'])
        print("URL:", product['product_url'])
        print("Image URL:", product['image_url'])
        print("Social Proof:", product['social_proof'])
        print("Rating:", product['rating_score'])
        print("Reviews:", product['review_count'])
        print("Price:", product['price'])
        print("Badges:", ", ".join(product['badges']))
        print()

class ProductScraper:
    def __init__(self, driver_path, base_url, output_csv, num_pages, db_manager):
        self.config = ConfigManager(driver_path)
        self.driver_manager = WebDriverManager(self.config)
        self.product_extractor = ProductExtractor(self.driver_manager.driver)
        self.output_csv = output_csv
        self.base_url = base_url
        self.num_pages = num_pages
        self.all_products = []  # List to store all product data
        self.product_urls=[]
        self.db_manager=db_manager

    def run(self):
        try:
            self.scrape_products()
        finally:
            self.driver_manager.close_driver()

    def scrape_products(self):
        for page in range(1, self.num_pages + 1):
            try:
                url = f"{self.base_url}&pi={page}"
                print(f"Scraping URL: {url}")  # Debugging output
                self.driver_manager.load_page(url)
                products = self.product_extractor.extract_products()
                filtered_products = [product for product in products if product['product_url'] not in self.product_urls]

                # Add URLs of the new products to the set
                for product in filtered_products:
                    self.product_urls.append(product['product_url'])
                    
                if filtered_products:
                    self.all_products.extend(filtered_products)  # Append products to the list
                    write_header = (page == 1)  # Write header only for the first page
                    self.write_products_to_csv(filtered_products, write_header)
                    self.db_manager.insert_product_data(filtered_products)  # Insert extracted product data into the database
                
                time.sleep(random.randint(3, 6))

            except TimeoutException:
                print(f"Timeout while loading page {page}")
            except Exception as e:
                print(f"Error scraping page: {e}")

    def write_products_to_csv(self, products, write_header):
        fieldnames = ['title', 'brand_name', 'short_description', 'product_url', 'image_url', 'social_proof', 'rating_score', 'review_count', 'price', 'badges']
        mode = 'a'  # Append mode
        try:
            with open(self.output_csv, mode, newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                for product in products:
                    writer.writerow(product)
            print(f"Products saved to {self.output_csv}")
        except IOError as e:
            print(f"Error saving to CSV file: {e}")



if __name__ == "__main__":
    driver_path = r"C:\Users\user\OneDrive\Documents\chromedriver-win64\chromedriver.exe"
    base_url = "https://www.trendyol.com/sr?mid=105012&os=1"  # Replace with the actual base URL of the product category
    output_csv = r"C:\Users\user\OneDrive\Documents\trendyol_scraper\data\trendyol_products.csv"
    num_pages = 44  # Number of pages to scrape
    db_manager = DatabaseManager(mysql_config)
    db_manager.connect()

    try:
        scraper = ProductScraper(driver_path, base_url, output_csv, num_pages, db_manager)
        scraper.run()
    finally:
        db_manager.disconnect()
