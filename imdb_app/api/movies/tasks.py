import datetime
import os

import pandas as pd
from imdb_app.db.mongo_adapters import MongoAdapter


def update_file_processing_status(file_identifier: str,
                                  collection_name: str,
                                  status: str) -> None:
    collection_adapter = MongoAdapter(collection_name)
    collection_adapter.update_one({
        "_id": file_identifier
    },
        {
            "$set": {
                "status": status,
                "updated_at": datetime.datetime.utcnow()
            }
        })


def stream_file_to_db(filepath: str,
                      file_identifier: str,
                      process_collection: str,
                      import_collection_name: str):
    collection_adapter = MongoAdapter(import_collection_name)
    try:
        update_file_processing_status(file_identifier, process_collection, "InProgress")
        chunk_size = 50000  # Adjust based on your needs and memory constraints
        for chunk in pd.read_csv(filepath, chunksize=chunk_size, encoding="utf-8", keep_default_na=False):
            records = chunk.to_dict('records')
            collection_adapter.insert_many(records)
        update_file_processing_status(file_identifier, process_collection, "Success")
        os.remove(filepath)  # Clean up the uploaded file
    except Exception:
        update_file_processing_status(file_identifier, process_collection, "Failed")
        raise
