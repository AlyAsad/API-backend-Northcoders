from connection import get_connection
import json
from psycopg2.extras import execute_values


def create_tables(conn):
    with conn.cursor() as cur:
        with open('db/seed.sql', 'r') as file:
            sql_content = filter(None, file.read().split(";"))
        
        for query in sql_content:
            cur.execute(query)
            print(cur.statusmessage)


def load_data(filename):
    with open(filename) as f:
        return json.load(f)


def make_query(table, entry):
    columns = ", ".join(entry)
    return f"INSERT INTO {table} ({columns}) VALUES %s"



def seed_tables(conn):
    tables = ["users", "venues", "events", "rsvps"]
    for table in tables:
        data = load_data("db/data/" + table + ".json")
        query = make_query(table, data[0])
        values = [tuple(entry.values()) for entry in data]

        with conn.cursor() as cur:
            execute_values(cur, query, values)
            print(cur.statusmessage)

    conn.commit()




def seed():
    conn = get_connection()
    create_tables(conn)
    seed_tables(conn)
    conn.close()


if __name__ == "__main__":
    seed()