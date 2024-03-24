import os

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from imdb_app.core.config import CONF


def store_files(file: FileStorage,
                sub_folder: str) -> str:
    if not file:
        raise ValueError("No file provided for saving.")

    filename = secure_filename(file.filename)
    save_path = os.path.join(CONF.application.file_path, sub_folder, filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)

    return save_path
