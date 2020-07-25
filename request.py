from abc import ABC

from bs4 import BeautifulSoup
from bs4.element import Tag
import requests
from html.parser import HTMLParser
from itertools import chain


class ItemCountParser(HTMLParser):
    data_sentence = ''

    def handle_data(self, data):
        self.data_sentence += data


def get_listings(query: str, debug=True) -> list:

    def format_search(query: str, pgn=1) -> str:
        query_keywords = query.strip().split()
        frmt_query = '+'.join(query_keywords)
        ebay_str = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={frmt_query}&_sacat=0&LH_All=1&rt=nc"
        if pgn > 1:
            ebay_str += f'&_pgn={pgn}'
        return ebay_str

    def get_soup(url: str) -> BeautifulSoup:
        response = requests.get(url)
        page = response.text
        soup = BeautifulSoup(page, 'lxml')
        return soup

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


x = get_listings('Super Smash Bros Melee')  # Costs about 10 calls atm.
