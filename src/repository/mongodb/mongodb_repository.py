from src.configs.connections.mongodb import MongoDBConnection


class MongoDBRepositoryInterface:
    def __init__(self, connection: MongoDBConnection):
        self.connection = connection