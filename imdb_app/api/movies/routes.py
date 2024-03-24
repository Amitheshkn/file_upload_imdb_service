from flask import Blueprint, request, jsonify
from werkzeug.datastructures import FileStorage

from common.authorization import check_authentication
from common.authorization import get_user_ctx_from_token
from imdb_app.api.movies.actions import MovieActions
from imdb_app.utils import store_files

movies_app = Blueprint("movies", __name__, template_folder="templates")

ALLOWED_EXTENSIONS = {"csv"}


@movies_app.route("/upload", methods=["POST"])
@check_authentication
def upload_file():
    actions = MovieActions()
    files = request.files

    file_validation = actions.check_file_validation(files)
    if file_validation:
        return jsonify({
            f"Error - {file_validation}"
        }), 400

    file: FileStorage = files.get("file")
    file_path = store_files(file, "movies")

    user_ctx = get_user_ctx_from_token(request)
    actions.process_file(file_path, user_ctx)

    return jsonify({'message': 'File successfully uploaded and is being processed.'}), 202


@movies_app.route('/movies', methods=['GET'])
@check_authentication
def list_movies(current_user):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    actions = MovieActions()
    response = actions.get_movies(page, page_size=page_size)
    return jsonify(response)


@movies_app.route('/upload/item/<file_process_id>/status', methods=['GET'])
@check_authentication
def upload_status(file_process_id):
    actions = MovieActions()
    response = actions.get_upload_status(file_process_id)
    return jsonify(response)