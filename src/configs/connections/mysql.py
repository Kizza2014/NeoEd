import os

from mysql.connector import pooling
from dotenv import load_dotenv


load_dotenv('src/.env')


HOST = os.getenv('MYSQL_HOST')
PORT = os.getenv('MYSQL_PORT')
USER = os.getenv('MYSQL_USER')
PASSWORD = os.getenv('MYSQL_PASS')
DATABASE = os.getenv('MYSQL_DB')

CONNECTION_POOL = pooling.MySQLConnectionPool(
    pool_name="neoed_pool",
    pool_size=20,
    host=HOST,
    port=PORT,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)

def get_connection():
    conn = CONNECTION_POOL.get_connection()
    try:
        yield conn
    finally:
        conn.close()