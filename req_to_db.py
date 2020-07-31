import psycopg2
import psycopg2.extras
from misc import read_yaml
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
def select_all(cur=None):
    cur.execute("SELECT * FROM ebuy_smash;")
    print(cur.fetchall())


@get_cursor
def simple_write(cur=None):
    cur.execute("INSERT INTO ebuy_smash (id, price, cond, bundle, text, seller_percent, seller_score, rating_count) VALUES (1, 2.00, 'ab', 'ab', 'ab', 100.0, 1, 1);")


@get_cursor
def mk_main_tbl(cur=None, table='ebuy_smash'):
    cur.execute("""CREATE TABLE IF NOT EXISTS {} (
        id INT PRIMARY KEY,
        price NUMERIC(6,2) NOT NULL,
        cond CHAR(25) NOT NULL,
        bundle CHAR(5) NOT NULL,
        text CHAR(1000) NOT NULL,
        seller_percent NUMERIC(4,1) NOT NULL,
        seller_score INT NOT NULL,
        rating_count INT NOT NULL
        );
        """.format(table))


@get_cursor
def write_to_db(df, cur=None, table='ebuy_smash'):
    if len(df) > 0:
        df_columns = list(df)
        # create (col1,col2,...)
        columns = ",".join(df_columns)

        # create VALUES('%s', '%s",...) one '%s' per column
        values = "VALUES({})".format(",".join(["%s" for _ in df_columns]))

        # create INSERT INTO table (columns) VALUES('%s',...)
        insert_stmt = "INSERT INTO {} ({}) {}".format(table, columns, values)

        psycopg2.extras.execute_batch(cur, insert_stmt, df.values)


mk_main_tbl()
simple_write()
select_all()
