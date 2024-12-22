import os
from typing import Generator
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

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
MONGO_URI = get_env_var('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = get_env_var('MONGO_DB')

class MongoDBConnection:
    _client = None

    def __init__(self):
        if not MongoDBConnection._client:
            try:
                MongoDBConnection._client = MongoClient(MONGO_URI)
                MongoDBConnection._client.admin.command('ping')
            except ConnectionFailure as e:
                raise RuntimeError(f"Failed to connect to MongoDB: {e}")
        self.db = MongoDBConnection._client[DB_NAME]


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_collection(self, collection_name):
        return self.db[collection_name]

def get_mongo_connection() -> Generator[MongoDBConnection, None, None]:
    """
    Usage:
        @app.get("/")
        async def root(db: MongoDBConnection = Depends(get_mongo_connection)):
            with db as connection:
                collection = connection.db['collection_name']
                return collection.find_one()
    """
    with MongoDBConnection() as db:
        yield db