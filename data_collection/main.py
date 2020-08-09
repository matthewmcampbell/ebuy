from data_collection.misc import read_yaml
from data_collection import req_to_db as rdb, request as req
import datetime
import os

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
secrets = read_yaml(os.path.join(folder, '..', config['secrets']))
logs = config['logging_path']
proxy = True
batch_size = 5
if not os.path.exists(logs):
    os.mkdir(logs)


def main(throttle=5):
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
    for i in range(len(listings_needed)//batch_size):
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
    label = dict(zip([df1_fails, df2_fails, df3_fails], ['main', 'imgs', 'bids']))
    for df_fails in label.keys():
        for df in df_fails:
            df.to_csv(f'{logs}{label[df_fails]}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')
    return None


if __name__ == '__main__':
    main(0)
