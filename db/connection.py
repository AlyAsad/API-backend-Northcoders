import psycopg2


def get_connection():
    return psycopg2.connect(dbname = "nc_plus_one")