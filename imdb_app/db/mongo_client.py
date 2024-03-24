import pymongo.collection
from pymongo import MongoClient

from imdb_app.common.definitions import Collection
from imdb_app.common.definitions import Database
from imdb_app.core.config import CONF

# Initialize MongoDB client
uri = CONF.database.mongo_uri
mongo_client = MongoClient(uri)
db = mongo_client[Database.MARROW]


def get_collection(collection_name: Collection) -> pymongo.collection.Collection:
    """Get a MongoDB collection."""
    return db[collection_name.value]
