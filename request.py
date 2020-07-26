from bs4 import BeautifulSoup
from bs4.element import Tag
import requests
from html.parser import HTMLParser
from itertools import chain
from dataclasses import dataclass, astuple

class ItemCountParser(HTMLParser):
    data_sentence = ''

    def handle_data(self, data):
        self.data_sentence += data

def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(page, 'lxml')
    return soup


def get_listings(query: str, debug=True) -> list:

    def format_search(query: str, pgn=1) -> str:
        query_keywords = query.strip().split()
        frmt_query = '+'.join(query_keywords)
        ebay_str = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={frmt_query}&_sacat=0&LH_All=1&rt=nc"
        if pgn > 1:
            ebay_str += f'&_pgn={pgn}'
        return ebay_str

    def count_results(url: str) -> int:
        soup = get_soup(url)
        html_counts = str(soup.find_all(class_='srp-controls__count-heading')[0])
        parser = ItemCountParser()
        parser.feed(html_counts)
        try:
            count = parser.data_sentence.split()[0]  # Pull the numbers out of string
        except Exception as e:
            print('Could not get count of all listings for the query.') if debug else False
            print(e) if debug else False
            count = '0'

        def rm_commas(s): return ''.join(s.split(','))
        count = int(rm_commas(count))
        return count

    def get_listings_single_pg(*args) -> list:
        def get_item_ids(url: str) -> list:
            soup = get_soup(url)
            tags = soup.find_all(class_='s-item__link')
            links = [tag['href'] for tag in tags]

            def rip_item_id(link: Tag) -> int:
                address = link.split('?')[0]
                item_id = address[address.rfind('/') + 1:]
                return int(item_id)

            item_ids = [rip_item_id(link) for link in links]
            return item_ids

        url = format_search(*args)
        item_ids = get_item_ids(url)
        return item_ids

    url = format_search(query)
    count = count_results(url)
    total_pgs = count//50 + bool(count % 50)  # silly way to get a ceiling. Leaving at 50 for now.

    listings = [get_listings_single_pg(query, pgn) for pgn in range(1, total_pgs + 1)]

    return [listing for listing in chain(*listings)]


@dataclass
class Item:
    item_id: int = 0
    price: float = 0.0
    cond: str = 'N/A'
    bundle: bool = False
    text: str = 'N/A'
    rating_count: int = 0
    images: str = 'N/A'  # pointers to file locations maybe...
    url: str = f"https://www.ebay.com/itm/{item_id}"
    soup:  BeautifulSoup = get_soup(url)

    def get_url(self) -> str:
        return f"https://www.ebay.com/itm/{self.item_id}"

    def get_soup(self) -> BeautifulSoup:
        return get_soup(self.url)

    def update_init(self):
        self.url = self.get_url()
        self.soup = self.get_soup()

    def get_item_data(self, item_id: int) -> tuple:

        price = self.get_curr_price()
        cond = self.get_condition()
        return item_id, price, cond

    def get_curr_price(self, debug=False) -> float:
        dollar_html = str(self.soup.find_all(class_='notranslate')[0])
        parser = ItemCountParser()
        parser.feed(dollar_html)
        try:
            dollars = parser.data_sentence.split()[1]  # Pull the numbers out of string
        except Exception as e:
            print('Could not get count of all listings for the query.') if debug else False
            print(e) if debug else False
            dollars = '0'

        def rm_dollar_sign(s): return s[1:]

        def rm_commas(s): return ''.join(s.split(','))

        dollars = float(rm_commas(rm_dollar_sign(dollars)))
        return dollars

    def get_condition(self,):
        cond_html = str(self.soup.find_all(class_='condText')[0])
        parser = ItemCountParser()
        parser.feed(cond_html)
        return parser.data_sentence

    def get_custom_bundle(self,):
        pass

    def get_main_text(self,):
        pass

    def get_product_rating_count(self,):
        pass

    def get_images(self,):
        pass


item_test = Item(133474223992)


# get_item_data(133474223992)

def get_bidding_hist(item_id):
    url = f"https://www.ebay.com/bfl/viewbids/{item_id}?item={item_id}&rt=nc"
    soup = get_soup(url)


# x = get_listings('Super Smash Bros Melee')  # Costs about 10 calls atm.
