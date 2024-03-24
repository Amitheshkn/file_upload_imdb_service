from typing import Optional

from bson import ObjectId
from pymongo import results

from imdb_app.common.definitions import Collection
from imdb_app.db.mongo_client import get_collection


class MongoAdapter:
    def __init__(self,
                 collection_name: Collection):
        self.collection = get_collection(collection_name)

    def find_document(self,
                      query: dict) -> Optional[dict]:
        return self.collection.find_one(query)

    def find_documents(self,
                       query: dict,
                       /,
                       *,
                       exclude_fields: list[str] = None,
                       include_fields: list[str] = None,
                       skip_value: int = 0,
                       limit: int = 10) -> list[dict]:
        query_fields = {}
        if exclude_fields:
            query_fields.update(dict((field, 0) for field in exclude_fields))
        if include_fields:
            query_fields.update(dict((field, 0) for field in exclude_fields))
        if query_fields:
            documents = self.collection.find(query, query_fields)
        else:
            documents = self.collection.find(query)
        if limit:
            documents = documents.skip(skip_value).limit(limit)
        return list(documents)

    def insert_document(self,
                        document: dict) -> ObjectId:
        result = self.collection.insert_one(document)
        return result.inserted_id

    def insert_documents(self,
                         documents: list[dict]) -> results.InsertManyResult:
        return self.collection.insert_many(documents)

    def update_document(self,
                        query: dict,
                        update_document: dict,
                        /,
                        *,
                        upsert: bool = False) -> results.UpdateResult:
        result = self.collection.update_one(query, update_document, upsert=upsert)
        return result

    def remove_document(self,
                        query: dict) -> results.DeleteResult:
        result = self.collection.delete_one(query)
        return result

    def count_documents(self,
                        query: dict) -> int:
        return self.collection.count_documents(query)
