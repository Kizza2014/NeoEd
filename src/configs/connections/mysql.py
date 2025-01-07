import os
from typing import Generator
from mysql.connector import pooling, Error as MySQLError
from dotenv import load_dotenv
from mysql.connector.pooling import PooledMySQLConnection

# Load environment variables and verify file exists
env_path = 'src/.env'
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Environment file not found at {env_path}")
load_dotenv(env_path)


# Validate and get environment variables with default values
def get_env_var(var_name: str, default: str = None) -> str:
    value = os.getenv(var_name)
    if value is None:
        if default is None:
            raise ValueError(f"Required environment variable '{var_name}' is not set")
        return default
    return value


# Configure database connection settings
DB_CONFIG = {
    'host': get_env_var('MYSQL_HOST', 'localhost'),
    'port': int(get_env_var('MYSQL_PORT', '3306')),
    'user': get_env_var('MYSQL_USER'),
    'password': get_env_var('MYSQL_PASS'),
    'database': get_env_var('MYSQL_DB'),
}

# Create connection pool with error handling
try:
    CONNECTION_POOL = pooling.MySQLConnectionPool(
        pool_name="neoed_pool",
        pool_size=20,
        **DB_CONFIG
    )
except MySQLError as e:
    raise RuntimeError(f"Failed to create connection pool: {e}")


class MySQLConnection:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = CONNECTION_POOL.get_connection()
        self.cursor = self.conn.cursor(dictionary=True)  # Use dictionary cursor for named columns
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()


def get_mysql_connection() -> Generator[MySQLConnection, None, None]:
    """
    Database dependency for FastAPI.
    Usage:
        @app.get("/")
        async def root(db: DatabaseConnection = Depends(get_db)):
            with db as connection:
                connection.cursor.execute("SELECT * FROM table")
                return connection.cursor.fetchall()
    """
    with MySQLConnection() as db:
        yield db


def get_mysql_cnx() -> PooledMySQLConnection:
    return CONNECTION_POOL.get_connection()
