import mysql.connector


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
