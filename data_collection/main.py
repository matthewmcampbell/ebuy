from data_collection.misc import read_yaml
from data_collection import req_to_db as rdb, request as req

config = read_yaml('conf.yaml')
secrets = read_yaml(config['secrets'])
proxy = True


def main(throttle=50):
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
    print('Initializing items...')
    items = req.listings_to_items(listings_needed, proxy)
    print('Getting data on items...')
    df1 = req.df_data_on_listings(items, bid_done=True)
    print('Getting item images...')
    df2 = req.df_image_addresses(items)
    print('Getting bid histories...')
    df3 = req.df_bid_histories(items)

    print('Writing to database...')
    rdb.write(df1, 'main')
    rdb.write(df2, 'imgs')
    rdb.write(df3, 'bids')
    print('Success.')
    return None


if __name__ == '__main__':
    main()
