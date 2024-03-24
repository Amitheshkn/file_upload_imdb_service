import pymongo.collection
from pymongo import MongoClient

from imdb_app.common.definitions import Collection

# Initialize MongoDB client
uri = "mongodb+srv://amithesh_sde:4vRqegXKE8hQ1pgm@cluster0.5yf4ox1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_client = MongoClient(uri)
db = mongo_client['Marrow']


def get_collection(collection_name: Collection) -> pymongo.collection.Collection:
    """Get a MongoDB collection."""
    return db[collection_name.value]
