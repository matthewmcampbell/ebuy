import requests
import shutil
from data_collection.misc import read_yaml
from urllib.request import urlretrieve
import os

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '../conf.yaml')
config = read_yaml(config_file)
secrets = read_yaml(os.path.join(folder, '..', config['secrets']))


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


def proxy_retrieve(url, filename):
    headers = {
        "apikey": secrets['zenscrape_api_key']
    }
    params = (
        ("url", url),
        ("location", "na")
    )
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get('https://app.zenscrape.com/api/v1/get', stream=True, headers=headers, params=params)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        # print('Image successfully Downloaded: ', filename)
    else:
        print('Image couldn\'t be retrieved: ', filename)