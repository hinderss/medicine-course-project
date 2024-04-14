import os
from werkzeug.datastructures.file_storage import FileStorage
from app import app
from werkzeug.utils import secure_filename


def save_file(file: FileStorage):
    filename = secure_filename(file.filename)
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(photo_path)
    return filename
