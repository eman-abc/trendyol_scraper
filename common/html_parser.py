from bs4 import BeautifulSoup

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
