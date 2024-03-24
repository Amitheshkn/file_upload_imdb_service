import datetime
import os

import pandas as pd
from bson import ObjectId
from threading import Thread
from imdb_app.common.definitions import Collection
from imdb_app.common.definitions import FileStatus
import imdb_app.api.movies.collection_structures as coll
from imdb_app.db.mongo_adapters import MongoAdapter


def update_file_processing_status(file_identifier: ObjectId,
                                  collection_name: Collection,
                                  status: FileStatus) -> None:
    collection_adapter = MongoAdapter(collection_name)
    collection_adapter.update_document({
        "_id": file_identifier
    },
        {
            "$set": {
                "status": status,
                "updated_at": datetime.datetime.utcnow()
            }
        })


def stream_file_to_db(filepath: str,
                      user_ctx: dict[str, str],
                      process_collection_name: Collection,
                      import_collection_name: Collection) -> str:
    now = datetime.datetime.utcnow()
    file_identifier = MongoAdapter(Collection.FILE_PROCESS).insert_document({
        coll.FileProcess.USER_ID: user_ctx.get("user_id"),
        coll.FileProcess.STATUS: FileStatus.INITIATED,
        coll.FileProcess.CREATED_AT: now,
        coll.FileProcess.UPDATED_AT: now
    })
    # Start the file processing in a background thread
    thread = Thread(target=start_background_job_processing,
                    args=(filepath, file_identifier, process_collection_name, import_collection_name))
    thread.daemon = True
    thread.start()
    return str(file_identifier)


def start_background_job_processing(filepath: str,
                                    file_identifier: ObjectId,
                                    process_collection_name: Collection,
                                    import_collection_name: Collection):
    collection_adapter = MongoAdapter(import_collection_name)
    try:
        update_file_processing_status(file_identifier, process_collection_name, FileStatus.IN_PROGRESS)
        # Adjust based on your needs and memory constraints
        chunk_size = 50000
        for chunk in pd.read_csv(filepath, chunksize=chunk_size, encoding="utf-8", keep_default_na=False):
            records = chunk.to_dict("records")

            # Add file tracking and timestamp information
            now = datetime.datetime.utcnow()
            for record in records:
                record.update({
                    "file_process_id": str(file_identifier),
                    "created_at": now,
                    "updated_at": now
                })

            collection_adapter.insert_documents(records)
        update_file_processing_status(file_identifier, process_collection_name, FileStatus.SUCCESS)
    except Exception as e:
        update_file_processing_status(file_identifier, process_collection_name, FileStatus.FAILED)
        print(f"Error processing file {filepath}: {e}")
    finally:
        os.remove(filepath)
