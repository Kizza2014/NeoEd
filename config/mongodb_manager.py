from pymongo import MongoClient, ReadPreference
from pymongo.errors import ServerSelectionTimeoutError


MONGODB_MEMBER1 = 'localhost:27027'
MONGODB_MEMBER2 = 'localhost:27028'
MONGODB_MEMBER3 = 'localhost:27029'

class MongoDBManager:
    _instance = None

    @staticmethod
    def get_instance():
        if MongoDBManager._instance is None:
            MongoDBManager._instance = MongoDBManager()
        return MongoDBManager._instance

    def __init__(self):
        _ = ','.join([MONGODB_MEMBER1, MONGODB_MEMBER2, MONGODB_MEMBER3])
        self.connection_string = f'mongodb://{_}'
        self.connection = MongoClient(self.connection_string)
        self.session = None

    def check_connection(self):
        try:
            info = self.connection.server_info()
            print(f'Connected to MongoDB. Server info: {info}')
        except ServerSelectionTimeoutError:
            print('Connection timed out.')

        return self.connection

    def close(self):
        if self.connection is not None:
            self.connection.close()
            print('Connection closed.')
        else:
            print('Connection unavailable.')

    def get_session(self):
        self.session = self.connection.start_session()
        return self.session

    def end_session(self):
        if self.session is not None:
            self.session.end_session()
            self.session = None

    def get_db(self, db_name: str):
        db = self.connection.get_database(db_name)
        print(f'Used {db_name}')
        return db

    def get_collection(self, db_name, collection_name):
        db = self.connection.get_database(db_name)
        collection = db.get_collection(collection_name).with_options(
            read_preference=ReadPreference.PRIMARY_PREFERRED
        )
        print(f'Used {db_name}.{collection_name}')
        return collection
