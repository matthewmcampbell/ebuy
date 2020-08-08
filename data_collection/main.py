from data_collection.misc import read_yaml
from data_collection import req_to_db as rdb, request as req

config = read_yaml('data_collection/conf.yaml')
secrets = read_yaml(config['secrets'])
proxy = True
batch_size = 5

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
            rdb.write(df1, 'main')
            rdb.write(df2, 'imgs')
            rdb.write(df3, 'bids')
            print('Success.')
        except Exception as e:  # Logging might be nice here.
            print('Failure')
            print(e)
    return None


if __name__ == '__main__':
    main(0)
