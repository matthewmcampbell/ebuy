import psycopg2
import psycopg2.extras
from data_collection.misc import read_yaml
from functools import wraps

config = read_yaml('conf.yaml')
secrets = read_yaml(config['secrets'])


def psql_connect():
    return psycopg2.connect(
        "dbname={} user={} password={} host={} port={}".format(
            config['dbname'], config['user'], secrets['passwd'], config['host'], config['port']
        )
    )


def get_cursor(f):
    @wraps(f)
    def _return_f(*args, **kwargs):
        with psql_connect() as conn:
            with conn.cursor() as cur:
                try:
                    return f(*args, cur=cur, **kwargs)
                except Exception as e:
                    conn.rollback()
                    raise psycopg2.ProgrammingError
    return _return_f


@get_cursor
def mk_main_tbl(cur=None, table='main'):
    cur.execute("""CREATE TABLE IF NOT EXISTS {} (
        id BIGINT PRIMARY KEY,
        price NUMERIC(6,2),
        cond VARCHAR(25) NOT NULL,
        bundle VARCHAR(5) NOT NULL,
        text TEXT,
        seller_percent NUMERIC(4,1),
        seller_score INT,
        rating_count INT,
        bid_summary TEXT,
        bid_duration TEXT
        );
        """.format(table))


@get_cursor
def mk_img_tbl(cur=None, table='imgs', foreign_table='main'):
    cur.execute("""CREATE TABLE IF NOT EXISTS {} (
        idx SERIAL PRIMARY KEY,
        id BIGINT NOT NULL, 
        url VARCHAR(100) NOT NULL,
        CONSTRAINT fk_id
            FOREIGN KEY(id)
                REFERENCES {}(id)
        );
        """.format(table, foreign_table))


@get_cursor
def mk_bid_tbl(cur=None, table='bids', foreign_table='main'):
    cur.execute("""CREATE TABLE IF NOT EXISTS {} (
        idx SERIAL PRIMARY KEY,
        id BIGINT NOT NULL,
        user_id CHAR(5) NOT NULL,
        score INT,
        bid NUMERIC(6,2) NOT NULL,
        datetime timestamp NULL,
        CONSTRAINT fk_id
            FOREIGN KEY(id)
                REFERENCES {}(id)
        );
        """.format(table, foreign_table))


def mk_tables():
    mk_main_tbl()
    mk_img_tbl()
    mk_bid_tbl()
    return None


@get_cursor
def _drop_tbls(cur=None, tables=('imgs', 'bids', 'main')):
    '''DEV tool only. Drop tables.'''
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table};")


@get_cursor
def write(df, table, cur=None,):
    if len(df) > 0:
        df_columns = list(df)
        # create (col1,col2,...)
        columns = ",".join(df_columns)

        # create VALUES('%s', '%s",...) one '%s' per column
        values = "VALUES({})".format(",".join(["%s" for _ in df_columns]))
        # create INSERT INTO table (columns) VALUES('%s',...)
        insert_stmt = "INSERT INTO {} ({}) {}".format(table, columns, values)
        print(df.values)
        psycopg2.extras.execute_batch(cur, insert_stmt, df.values)


@get_cursor
def remove_existing_items(listings, table, cur=None, ):
    if len(listings) > 0:
        int_listings = list(map(str, listings))
        check_values = ','.join(int_listings)
        cur.execute(f'SELECT id FROM {table} WHERE id IN ({check_values});')
        fetched = cur.fetchall()
        exists = [item[0] for item in fetched]
        return list(set(listings) - set(exists))
    else:
        return listings


_drop_tbls()
# mk_main_tbl()
# mk_img_tbl()
# mk_bid_tbl()
# v = [133438070786, 353152221964]
# y = listings_to_items([v[0]], proxy=False)
# res1 = df_data_on_listings(y, bid_done=True)
# res2 = df_image_addresses(y)
# res3 = df_bid_histories(y)
#
# write(res1, 'main')
# write(res2, 'imgs')
# write(res3, 'bids')
#
# c = remove_existing_items(v, 'main')
