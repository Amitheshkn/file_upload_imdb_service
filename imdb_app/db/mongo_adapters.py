# app/mongo_adapter.py
from typing import Any

from imdb_app.db.mongo_client import get_collection


class MongoAdapter:
    def __init__(self, collection_name):
        self.collection = get_collection(collection_name)

    def find_one(self, query):
        return self.collection.find_one(query)

    def find_many(self,
                  query: dict[str, Any],
                  /,
                  *,
                  projection: dict[str, Any] = None,
                  page: int = 1,
                  page_size: int = 10) -> list[dict]:
        """
        Retrieves documents from the collection based on a query.

        :param query: The search query as a dictionary.
        :param projection: The fields to include or exclude.
        :param page: The page number for pagination.
        :param page_size: The number of documents per page.
        :return: A list of documents.
        """
        # Calculate the number of documents to skip
        skip = (page - 1) * page_size
        documents = self.collection.find(filter=query, projection=projection).skip(skip).limit(page_size)
        return list(documents)

    def insert_one(self, document):
        result = self.collection.insert_one(document)
        return result.inserted_id

    def update_one(self,
                   query: dict,
                   update: dict,
                   /,
                   *,
                   upsert: bool = False):
        result = self.collection.update_one(query, update, upsert=upsert)
        return result.modified_count

    def delete_one(self, query):
        result = self.collection.delete_one(query)
        return result.deleted_count

    def insert_many(self, documents):
        return self.collection.insert_many(documents)

    def count_documents(self, query: dict[str, Any]) -> int:
        """
        Counts the number of documents matching the query.

        :param query: The search query as a dictionary.
        :return: The count of documents.
        """
        return self.collection.count_documents(query)
