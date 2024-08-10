from selenium.webdriver.chrome.options import Options

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
