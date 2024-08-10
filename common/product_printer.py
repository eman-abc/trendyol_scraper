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
