from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import subprocess

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
