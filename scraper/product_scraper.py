from common.webdriver_manager import WebDriverManager
from common.config_manager import ConfigManager
from .product_extractor import ProductExtractor
from selenium.common.exceptions import TimeoutException
import csv
import time
import random
from selenium.common.exceptions import TimeoutException


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
