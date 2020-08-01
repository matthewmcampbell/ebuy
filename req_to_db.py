import psycopg2
import psycopg2.extras
from misc import read_yaml
from functools import wraps
from request import listings_to_items, get_bid_histories, get_image_addresses, get_data_on_listings

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
def select_all(cur=None):
    cur.execute("SELECT * FROM ebuy_smash;")
    print(cur.fetchall())


@get_cursor
def simple_write(cur=None):
    cur.execute("INSERT INTO ebuy_smash (id, price, cond, bundle, text, seller_percent, seller_score, rating_count) VALUES (1, 2.00, 'ab', 'ab', 'ab', 100.0, 1, 1);")


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
        rating_count INT
        );
        """.format(table))


@get_cursor
def mk_img_tbl(cur=None, table='imgs', foreign_table='main'):
    cur.execute("""CREATE TABLE IF NOT EXISTS {} (
        idx INT PRIMARY KEY,
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
        idx INT PRIMARY KEY,
        id BIGINT NOT NULL,
        user_id CHAR(5) NOT NULL,
        score INT NOT NULL,
        bid NUMERIC(6,2) NOT NULL,
        datetime timestamp,
        CONSTRAINT fk_id
            FOREIGN KEY(id)
                REFERENCES {}(id)
        );
        """.format(table, foreign_table))

@get_cursor
def _drop_tbls(cur=None, tables=('imgs', 'bids', 'main')):
    '''DEV tool only. Drop tables.'''
    for table in tables:
        cur.execute(f"DROP TABLE {table};")



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


_drop_tbls()
mk_main_tbl()
mk_img_tbl()
mk_bid_tbl()
y = [303634334633]
y = listings_to_items(y)
res1 = get_data_on_listings(y, bid_done=True)
res2 = get_image_addresses(y)
res3 = get_bid_histories(y)

write(res1, 'main')
write(res2, 'imgs')
write(res3, 'bids')
