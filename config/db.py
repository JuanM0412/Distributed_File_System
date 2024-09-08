from pymongo import MongoClient
from config.env import MONGO_CLIENT, DB_NAME


class Database:
    def __init__(self, uri: str, db_name: str):
        self._client = MongoClient(uri)
        self._db = self._client[db_name]


    @property
    def client(self):
        return self._client


    @property
    def db(self):
        return self._db
    
    # Collections
    @property
    def users(self):
        return self._db.users
    
    
    @property
    def dataNodes(self):
        return self._db.dataNodes


database = Database(uri=MONGO_CLIENT, db_name=DB_NAME)