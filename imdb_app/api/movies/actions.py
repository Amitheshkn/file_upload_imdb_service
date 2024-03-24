import datetime
from typing import Optional

from bson import ObjectId
from flask import jsonify
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.datastructures import FileStorage

from imdb_app.api.movies.tasks import stream_file_to_db
from imdb_app.db.mongo_adapters import MongoAdapter


class MovieActions:
    def check_file_validation(self,
                              files: ImmutableMultiDict[str, FileStorage]) -> Optional[str]:
        if "file" not in files:
            return "No file 'part'"

        file = files["file"]
        if file.filename == "":
            return "File not found"

        if not file.filename.endswith('.csv'):
            return "Invalid file type selected. Allowed types - 'CSV' files only"

    def process_file(self,
                     file_path: str,
                     user_ctx: dict[str, str]):
        try:
            now = datetime.datetime.utcnow(),
            file_identifier = MongoAdapter("file_process").insert_one({
                "user_id": user_ctx.get("user_id"),
                "status": "Initiated",
                "created_at": now,
                "updated_at": now
            })
            stream_file_to_db(file_path, file_identifier, "file_process", "movies")
            return {
                "message": "CSV upload initiated",
                "file_process_id": str(file_identifier)
            }

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def get_movies(self,
                   page: int,
                   /,
                   *,
                   page_size: int = 10):
        collection_adapter = MongoAdapter("movies")
        movies = collection_adapter.find_many({}, page_size=page_size, page=page)
        total_count = collection_adapter.count_documents({})
        # Optionally, convert the documents from BSON to JSON
        # movies_json = dumps(movies)

        return {
            "movies": movies,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size  # Calculate the total number of pages
        }

    def get_upload_status(self,
                          file_process_id: str):
        file_processing_details = MongoAdapter("file_process").find_one({
            "_id": ObjectId(file_process_id)
        })
        return {
            "file_process_id": file_process_id,
            "status": file_processing_details["status"]
        }
