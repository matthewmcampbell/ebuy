from bs4 import BeautifulSoup
from bs4.element import Tag
import requests
from html.parser import HTMLParser
from itertools import chain
from dataclasses import dataclass
from urllib.request import urlretrieve
from urllib.error import HTTPError
import pandas as pd
import numpy as np
from data_collection.misc import read_yaml, return_on_fail
from data_collection.proxy_request import proxy_get, proxy_retrieve
import operator
import re
import os


folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '../conf.yaml')
config = read_yaml(config_file)
secrets = read_yaml(os.path.join(folder, '..', config['secrets']))
DOWNLOAD_PATH = config['download_path']


class ItemCountParser(HTMLParser):
    """Child of HTMLParser. Adds in 'data' as it is found within
    html syntax. Look to HTMLParser docs for more details and
    examples."""
    data_sentence = ''

    def handle_data(self, data):
        self.data_sentence += data


def get_soup(url: str, proxy=False) -> BeautifulSoup:
    """Automated method to get BeautifulSoup object from url.
    Args:
        url: str
        proxy: bool indicated proxy usage.
    Returns:
        BeautifulSoup object."""
    response = proxy_get(url) if proxy else requests.get(url)
    page = response.text
    soup = BeautifulSoup(page, 'lxml')
    return soup


class ListingOptions:
    """Object to hold query options for ebay listings. Note
    that this doesn't contain the query itself! Options include:
    self.listing_types: 'all', 'offers', 'auction', 'buy_now'
    self.show_only: '', 'sold'
    self.location: '', 'usa'

    Note that, since the url-encoded options aren't intuitive,
    the attributes of ListingOptions get mapped to their url
    counterparts upon being set. See self.listing_types(...)
    for an example of this."""
    def __init__(self):
        self.listing_types = 'all'
        self.show_only = ''
        self.location = 'usa'
        self.listing_types_out = 'LH_All=1'
        self.show_only_out = ''
        self.location_out = 'LH_PrefLoc=1'

    listing_types = property(operator.attrgetter('_listing_types'))

    @listing_types.setter
    def listing_types(self, d):
        valid = ['all', 'offers', 'auction', 'buy_now']
        if d.lower() not in valid:
            print('Not a valid entry for this field.')
            self._listing_types = 'all'

        convert = dict(zip(valid, ['LH_All=1', 'LH_BO=1', 'LH_Auction=1', 'LH_BIN=1']))
        self._listing_types = d
        self.listing_types_out = convert[d]

    show_only = property(operator.attrgetter('_show_only'))

    @show_only.setter
    def show_only(self, d):
        valid = ['', 'sold']
        if d.lower() not in valid:
            print('Not a valid entry for this field.')
            self._show_only = ''

        convert = dict(zip(valid, ['', 'LH_Sold=1&LH_Complete=1']))
        self._show_only = d
        self.show_only_out = convert[d]

    location = property(operator.attrgetter('_location'))

    @location.setter
    def location(self, d):
        valid = ['', 'usa']
        if d.lower() not in valid:
            print('Not a valid entry for this field.')
            self._location = ''

        convert = dict(zip(valid, ['', 'LH_PrefLoc=1']))
        self._location = d
        self.location_out = convert[d]

    def get(self):
        """Combines and returns all options into url-friendly sub-string."""
        return '&'.join((self.listing_types_out, self.show_only_out, self.location_out))


def get_listings(query: str, options=ListingOptions(), proxy=False, debug=True) -> list:
    """Method to get all listing ids for a given query and ListingOptions.
    Args:
        query: str to pass into Ebay for search.
        options: ListingOptions to control options like location, Buy It Now, etc.
        proxy: bool to control proxy usage.
        debug: bool to control debug pring messages.
    Returns:
        [int, ..., int]"""
    def format_search(query: str, pgn=1) -> str:
        query_keywords = query.strip().split()
        frmt_query = '+'.join(query_keywords)
        ebay_str = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={frmt_query}&_sacat=0&{options.get()}&rt=nc"
        if pgn > 1:
            ebay_str += f'&_pgn={pgn}'
        return ebay_str

    def count_results(url: str) -> int:
        soup = get_soup(url, proxy)
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
            soup = get_soup(url, proxy)
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
    """Object to store all item info from listing page for a
    particular item id. Contains many 'get' methods for each
    attribute, most of them including a decorator to default
    to a NaN-like string or int. This is critical as the html
    for the Ebay pages will, eventually, be altered and ruin
    the existing methods. They should be updated regularly to
    accommodate this."""
    item_id: int = 0
    price: float = 0.0
    cond: str = 'N/A'
    bundle: str = 'N/A'
    text: str = 'N/A'
    seller_percent: float = 0.0
    seller_score: int = 0
    rating_count: int = 0
    images: tuple = ()
    bids: pd.DataFrame = pd.DataFrame({})
    bid_summary: str = 'N/A'
    bid_duration: str = 'N/A'
    url: str = f"https://www.ebay.com/itm/{item_id}"
    soup:  BeautifulSoup = get_soup(url)
    proxy: bool = False

    def get_url(self, bid_done=False) -> str:
        orig = 'nordt=true&orig_cvip=true' if bid_done else ''
        return f"https://www.ebay.com/itm/{self.item_id}?{orig}"

    def get_soup(self) -> BeautifulSoup:
        return get_soup(self.url, self.proxy)

    def update_init(self, **kwargs):
        """Method to gather both the relevant url and BeautifulSoup."""
        self.url = self.get_url(**kwargs)
        self.soup = self.get_soup()

    def get_item_data(self, debug=False, **kwargs) -> tuple:
        """Main method to be called. Calls all other data collecting methods
        that aren't called in update_init()."""
        self.price = self.get_curr_price(debug=debug)
        self.cond = self.get_condition(debug=debug)
        self.bundle = self.get_custom_bundle(debug=debug)
        self.text = self.get_main_text(debug=debug)
        self.seller_percent = self.get_feedback_percent(debug=debug)
        self.seller_score = self.get_feedback_score(debug=debug)
        self.rating_count = self.get_product_rating_count(debug=debug)
        self.images = self.get_images(debug=debug, **kwargs)
        self.bid_summary, self.bid_duration = self.get_bid_summary(debug=debug)
        return (self.item_id, self.price, self.cond, self.bundle, self.text,
                self.seller_percent, self.seller_score, self.rating_count,
                self.bid_summary, self.bid_duration)

    @return_on_fail(None)
    def get_curr_price(self, debug=False) -> float:
        dollar_html = str(self.soup.find_all(class_='notranslate')[0])
        parser = ItemCountParser()
        parser.feed(dollar_html)
        try:
            dollars = parser.data_sentence.split()[1]  # Pull the numbers out of string
        except Exception as e:
            print(f'Could not get dollars for query {self.item_id}.') if debug else False
            print(e) if debug else False
            dollars = '0'

        def rm_dollar_sign(s): return s[1:]

        def rm_commas(s): return ''.join(s.split(','))

        dollars = float(rm_commas(rm_dollar_sign(dollars)))
        return dollars

    @return_on_fail('N/A')
    def get_condition(self, debug=False):
        cond_html = str(self.soup.find_all(class_='condText')[0])
        parser = ItemCountParser()
        parser.feed(cond_html)
        return parser.data_sentence

    @return_on_fail('N/A')
    def get_custom_bundle(self, debug=False):
        bundle_html = str(self.soup.find_all(class_='prodDetailSec')[0])
        parser = ItemCountParser()
        parser.feed(bundle_html)
        if 'No\n' in parser.data_sentence:
            return 'No'
        elif 'Yes\n' in parser.data_sentence:
            return 'Yes'
        else:
            print(f'Could not get bundle info for query {self.item_id}.') if debug else False
            return 'N/A'

    @return_on_fail('N/A')
    def get_main_text(self, debug=False):
        """Get the main seller text from the page.
        This one is a bit trickier, need to pull a url
        from the seller page that redirects to another.

        :return str
        """
        url_to_seller_text = self.soup.find(id='desc_ifr')['src']
        seller_soup = get_soup(url_to_seller_text, self.proxy)
        text_html = str(seller_soup.find(id='ds_div'))
        parser = ItemCountParser()
        parser.feed(text_html)
        return parser.data_sentence.strip()

    @return_on_fail(np.nan)
    def get_feedback_percent(self, debug=False) -> float:
        """Return the sellers feedback percentage. 0-100"""
        url_to_seller_text = str(self.soup.find(id='si-fb'))
        parser = ItemCountParser()
        parser.feed(url_to_seller_text)
        return float(parser.data_sentence.split('%')[0])

    @return_on_fail(np.nan)
    def get_feedback_score(self, debug=False) -> int:
        score_html = str(self.soup.find_all(class_='mbg-l')[0])
        parser = ItemCountParser()
        parser.feed(score_html)
        return int(parser.data_sentence.strip().split('\n')[0][1:])

    @return_on_fail(np.nan)
    def get_product_rating_count(self, debug=False) -> int:
        review_html = str(self.soup.find_all(class_='prodreview')[0])
        parser = ItemCountParser()
        parser.feed(review_html)
        try:
            review_count = parser.data_sentence.split()[0]  # Pull the numbers out of string
        except Exception as e:
            print(f'Could not get dollars for query {self.item_id}.') if debug else False
            print(e) if debug else False
            review_count = '0'

        def rm_commas(s): return ''.join(s.split(','))
        review_count = int(rm_commas(review_count))
        return review_count

    @return_on_fail(tuple('N/A'))
    def get_images(self, size='thumb', debug=False) -> tuple:
        size = size.lower()
        if size.lower() not in ['thumb', 'full']:
            print('image size not recognized; defaulting to thumbnail.')
            size = 'thumb'

        image_urls_html = self.soup.find_all(class_='tdThumb')

        def rough_parser(thumb: str) -> str:
            mark_1 = thumb.find("https://i.ebayimg.com/images/g/")
            mark_2 = thumb[mark_1:].find('"')
            return thumb[mark_1: mark_1 + mark_2]

        def get_full_size_url(thumb_url: str) -> str:
            return thumb_url.replace('s-l64', 's-l1600')

        image_urls = list(map(lambda x: rough_parser(str(x)), image_urls_html))
        image_urls = list(set(image_urls))
        if size == 'full':
            image_urls = list(map(get_full_size_url, image_urls))
        image_location = []
        for i, image in enumerate(image_urls):
            try:
                save_path = f'{DOWNLOAD_PATH}{self.item_id}{size}_{i}.jpg'
                if self.proxy:
                    proxy_retrieve(image, save_path)
                else:
                    urlretrieve(image, save_path)
                image_location.append(save_path)
            except HTTPError as e:
                print(e) if debug else False
                print(f'Failed to get image for {self.item_id} img #{i}') if debug else False
        return tuple(image_location)

    @return_on_fail(pd.DataFrame({}))
    def get_bidding_history(self, ) -> pd.DataFrame:
        url = f"https://www.ebay.com/bfl/viewbids/{self.item_id}?item={self.item_id}&rt=nc"
        soup = get_soup(url, self.proxy)
        records_html = soup.find_all(class_='ui-component-table_tr_detailinfo')

        def record_parser(record):
            if 'Cancelled' in record or 'Retracted' in record:
                return None
            parser = ItemCountParser()
            parser.feed(record)
            bid_data = parser.data_sentence
            bid_user = bid_data[:5]  # Will have the form of a***e.
            feedback_chunk, amt_time_chunk = bid_data.split('$')
            if bid_user.lower() == 'start':
                user_score = np.nan
            else:
                user_score = feedback_chunk.split('(')[-1].split()[-1][:-1]  # NASTY LINE
            dollar_dec_loc = amt_time_chunk.find('.')
            bid_amt = amt_time_chunk[:dollar_dec_loc + 3]
            if re.search('[a-zA-Z]', bid_amt):  # Check if we have any non-US currency.
                bid_amt = '0.00'
            dt = amt_time_chunk[dollar_dec_loc + 3:]

            def clean_datetime(dt):
                date, time = dt.split('at')
                date, time = date.strip(), time.strip()
                # if len(time) < 14:
                #     time = '0' + time  # Zero-padding once to get formatting consistent for pd.to_datetime()
                time = time[:-3]  # Removing timezone info
                return date, time

            date, time = clean_datetime(dt)
            return bid_user, user_score, bid_amt, f'{date} {time}'

        records = list(map(lambda record: record_parser(str(record)), records_html))
        valid_records = [record for record in records if record]
        col_names = ['user_id', 'score', 'bid', 'datetime']
        df_records = pd.DataFrame(valid_records, columns=col_names)
        df_records['id'] = self.item_id
        df_return = df_records[['id', 'user_id', 'score', 'bid', 'datetime']]  # Reordering columns for easy sql later.
        self.bids = df_return
        return df_return

    @return_on_fail('N/A')
    def get_bid_summary(self, debug=False):
        url = f"https://www.ebay.com/bfl/viewbids/{self.item_id}?item={self.item_id}&rt=nc"
        soup = get_soup(url, self.proxy)
        record_html = str(soup.find_all(class_='app-bid-info_wrapper')[0])
        parser = ItemCountParser()
        parser.feed(record_html)
        data = parser.data_sentence
        return data, data.split('Duration:')[-1]


def listings_to_items(listings: list, proxy: bool) -> list:
    """Method that maps Item class on top of list of ids.
    Args:
        listings: [int, ..., int] a list of item ids.
        proxy: bool to control proxy usage.
    Returns:
        [Item, ..., Item]"""
    return [Item(listing, proxy=proxy) for listing in listings]


def nan_to_none(f):
    """Wrapper method to convert np.nan's to None. This needs
    to happen for proper PSQL read ins. Really a nuisance though.
    Args:
        f: function
    Returns:
        _return_f: modified f function."""
    def _return_f(*args, **kwargs):
        df = f(*args, **kwargs)
        df_ret = df.copy().astype('object')
        df_ret[df_ret.isnull()] = None
        return df_ret
    return _return_f


@nan_to_none
def df_data_on_listings(listings: list, bid_done=False, **kwargs) -> pd.DataFrame:
    """Method to gather item data into dataframe. This method
    is currently doing too much and causes bad coupling. Should
    separate out the for loop into it's own function.
    Args:
        listings: [Item, ..., Item] list of Items
        bid_done: bool to control if bids should be accounted
        kwargs: the parameters to feed to Item.get_item_data
    Return:
        pd.DataFrame"""
    data = []
    for i, listing in enumerate(listings):
        print(f'Progress: {i}/{len(listings)}')
        listing.update_init(bid_done=bid_done)
        data.append(listing.get_item_data(**kwargs))
        listing.get_bidding_history()
    columns = ['id', 'price', 'cond', 'bundle', 'text',
               'seller_percent', 'seller_score', 'rating_count',
               'bid_summary', 'bid_duration']
    df = pd.DataFrame(data, columns=columns)
    return df


@nan_to_none
def df_image_addresses(listings: list) -> pd.DataFrame:
    """Method to gather image addresses (on local machine).
    Args:
        listings: [Item, ..., Item] list of Items
    Returns:
        pd.DataFrame"""
    data = []
    for listing in listings:
        for image_url in listing.images:
            data.append((listing.item_id, image_url))
    columns = ['id', 'url']
    df = pd.DataFrame(data, columns=columns).reset_index(drop=True)
    df.index.rename('idx', inplace=True)
    return df


@nan_to_none
def df_bid_histories(listings: list) -> pd.DataFrame:
    """Method to gather bid histories on items.
        Args:
            listings: [Item, ..., Item] list of Items
        Returns:
            pd.DataFrame"""
    df = pd.concat([listing.bids for listing in listings]).reset_index(drop=True)
    df.index.rename('idx', inplace=True)
    return df


# x = [114230556674, 143595870217]
# item = Item(x[0], proxy=True)
# df = df_data_on_listings([item], bid_done=True)
