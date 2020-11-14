import datetime
import os

from data_collection.misc import read_yaml
from data_collection import req_to_db as rdb, request as req

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
secrets = read_yaml(os.path.join(folder, '..', config['secrets']))
logs = config['logging_path']

proxy = True
batch_size = 5
if not os.path.exists(logs):
    os.mkdir(logs)


def main(throttle=0):
    """Main method for data_collection folder. Sets up listing
    options and query, gets response from Ebay (can use proxy
    to safeguard against getting blacklisted), scrapes responses
    into Item objects then writes the data into postgres DB. The
    writing process is done in batches (5 or 10 is a good idea).
    Args:
        throttle: int
            if 0, nothing happens. if >0, only gathers that many
            items."""
    rdb.mk_tables()

    options = req.ListingOptions()
    options.listing_types = 'auction'
    options.show_only = 'sold'

    listings = req.get_listings('Super Smash Bros Melee', options, proxy)
    listings_needed = rdb.remove_existing_items(listings, 'main')
    print(f'Found {len(listings_needed)} new entries for database out of {len(listings)} online.')
    if throttle:
        listings_needed = listings_needed[:throttle]
        print(f'Throttling to {len(listings_needed)} items.')

    df1_fails = []
    df2_fails = []
    df3_fails = []

    for i in range(len(listings_needed)//batch_size + 1):
        try:
            batch = listings_needed[i*batch_size: (i+1)*batch_size]
            print('Initializing items...')
            items = req.listings_to_items(batch, proxy)
            print('Getting data on items...')
            df1 = req.df_data_on_listings(items, bid_done=True, size='full')
            df2 = req.df_image_addresses(items)
            df3 = req.df_bid_histories(items)

            print('Writing to database...')
            try:
                rdb.write(df1, 'main')
            except:
                df1_fails.append(df1)
            try:
                rdb.write(df2, 'imgs')
            except:
                df2_fails.append(df2)
            try:
                rdb.write(df3, 'bids')
            except:
                df3_fails.append(df3)
        except Exception as e:
            print('Failure on parse.')
            print(e)

    # Logging section
    df_fails = [df1_fails, df2_fails, df3_fails]
    label = ['main', 'imgs', 'bids']
    for i, label in enumerate(label):
        for df in df_fails[i]:
            df.to_csv(f'{logs}{label}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')
    return None


if __name__ == '__main__':
    main()
