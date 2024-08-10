from scraper.product_scraper import ProductScraper
from common.database_manager import DatabaseManager

# MySQL Connection Configuration
mysql_config = {
    'host': 'localhost',
    'database': 'prod_data',
    'user': 'root',
    'password': 'seecs@123'
}

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
