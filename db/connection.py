import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ["DB_NAME"]

def get_connection():
    return psycopg2.connect(dbname = DB_NAME)