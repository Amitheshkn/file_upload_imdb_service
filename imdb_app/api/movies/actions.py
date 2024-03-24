from typing import Optional

from bson import ObjectId
from flask import jsonify, Response
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import ImmutableMultiDict

import imdb_app.api.movies.collection_structures as coll
from imdb_app.api.movies.tasks import stream_file_to_db
from imdb_app.common.definitions import Collection
from imdb_app.db.mongo_adapters import MongoAdapter


class MovieActions:
    def check_file_validation(self,
                              files: ImmutableMultiDict[str, FileStorage]) -> Optional[str]:
        if "file" not in files:
            return "No file - 'part'"

        file = files["file"]
        if file.filename == "":
            return "File not found"

        if not file.filename.endswith('.csv'):
            return "Invalid file type selected. Allowed types - 'CSV' files only"

    def process_file(self,
                     file_path: str,
                     user_ctx: dict[str, str]) -> tuple[Response, int]:
        try:
            file_identifier = stream_file_to_db(file_path, user_ctx, Collection.FILE_PROCESS, Collection.MOVIES)
            return jsonify({
                "message": "CSV upload initiated",
                "file_process_id": str(file_identifier)
            }), 200

        except Exception as e:
            return jsonify(
                {"error": str(e)}
            ), 400

    def get_movies(self,
                   page: int,
                   page_size: int = 10) -> tuple[Response, int]:
        skip = (page - 1) * page_size
        collection_adapter = MongoAdapter(Collection.MOVIES)
        docs = collection_adapter.find_documents({}, skip_value=skip, limit=page_size)
        for doc in docs:
            doc["movie_id"] = str(doc.pop("_id"))

        total_count = collection_adapter.count_documents({})
        return jsonify({
            "movies": docs,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size  # Calculate the total number of pages
        }), 200

    def get_upload_status(self,
                          file_process_id: str) -> tuple[Response, int]:
        file_processing_details = MongoAdapter(Collection.FILE_PROCESS).find_document({
            "_id": ObjectId(file_process_id)
        })
        return jsonify({
            "file_process_id": file_process_id,
            "status": file_processing_details[coll.FileProcess.STATUS]
        }), 200
