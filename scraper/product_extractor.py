from common.product_printer import ProductPrinter
from common.html_parser import HtmlParser
from selenium.webdriver.common.by import By

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
