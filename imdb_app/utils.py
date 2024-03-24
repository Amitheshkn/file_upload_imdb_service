import os

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def store_files(file: FileStorage,
                sub_folder: str) -> str:
    """
    Saves an uploaded file to a specified sub-folder within the application's upload directory.

    :param file: The file object from Flask 'request.files'
    :param sub_folder: The sub-folder within the UPLOAD_FOLDER where the file should be stored
    :return: The path to the saved file
    """
    if not file:
        raise ValueError("No file provided for saving.")

    filename = secure_filename(file.filename)
    save_path = os.path.join("/tmp/file_processing", sub_folder, filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)

    return save_path
