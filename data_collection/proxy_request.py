import os
import requests
import shutil

from data_collection.misc import read_yaml

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '../conf.yaml')
config = read_yaml(config_file)
secrets = read_yaml(os.path.join(folder, '..', config['secrets']))


def proxy_get(url):
    """Method to utilize Zenscrape API for proxy url gets.
    Args:
        url: str
    Returns:
        html response"""
    headers = {
        "apikey": secrets['zenscrape_api_key']
    }
    params = (
        ("url", url),
        ("location", "na")
    )
    response = requests.get('https://app.zenscrape.com/api/v1/get',
                            headers=headers, params=params)
    return response


def proxy_retrieve(url, filename):
    """Method to utilize Zenscrape API for image downloads.
    Args:
        url: str
        filename: str of image write address
    Returns:
        None"""
    headers = {
        "apikey": secrets['zenscrape_api_key']
    }
    params = (
        ("url", url),
        ("location", "na")
    )
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get('https://app.zenscrape.com/api/v1/get',
                     stream=True, headers=headers, params=params)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        r.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    else:
        print('Image couldn\'t be retrieved: ', filename)
    return None