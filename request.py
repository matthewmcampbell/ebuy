from bs4 import BeautifulSoup
from bs4.element import Tag
import requests


def query_ebay(query: str) -> list:

    def format_search(query: str) -> str:
        query_keywords = query.strip().split()
        frmt_query = '+'.join(query_keywords)
        ebay_str = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={frmt_query}&_sacat=0&LH_All=1&rt=nc"
        return ebay_str

    def get_item_ids(url: str) -> list:
        response = requests.get(url)
        page = response.text
        soup = BeautifulSoup(page, 'lxml')
        tags = soup.find_all(class_='s-item__link')
        links = [tag['href'] for tag in tags]

        def rip_item_id(link: Tag) -> int:
            address = link.split('?')[0]
            item_id = address[address.rfind('/') + 1:]
            return int(item_id)

        item_ids = [rip_item_id(link) for link in links]
        return item_ids

    url = format_search(query)
    item_ids = get_item_ids(url)
    return item_ids


print(query_ebay('Super Smash Bros Melee'))
