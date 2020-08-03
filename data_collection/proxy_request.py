import requests
from data_collection.misc import read_yaml
from urllib.request import urlretrieve

config = read_yaml('conf.yaml')
secrets = read_yaml(config['secrets'])


def proxy_get(url):
    headers = {
        "apikey": secrets['zenscrape_api_key']
    }
    params = (
        ("url", url),
        ("location", "na")
    )
    response = requests.get('https://app.zenscrape.com/api/v1/get', headers=headers, params=params)
    return response


def proxy_retrieve(url, *args):
    scrape_api = 'https://app.zenscrape.com/api/v1/get'
    req_string = f'{scrape_api}?apikey={secrets["zenscrape_api_key"]}&url={url}%2Fxml%2F&location=na'
    urlretrieve(req_string, *args)
