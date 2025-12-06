import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """
    Checks if the uploaded file has a valid extension (mp4, mov, avi).
    Defined in config.py
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_upload(file_storage):
    """
    Saves the uploaded file with a secure, unique name.
    Returns the full path and the unique filename.
    """
    original_filename = secure_filename(file_storage.filename)
    # Generate a unique ID to prevent overwrites (e.g., video_a1b2.mp4)
    unique_id = str(uuid.uuid4())[:8] 
    extension = original_filename.rsplit('.', 1)[1].lower()
    new_filename = f"{unique_id}_{original_filename}"
    
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
    file_storage.save(save_path)
    
    return save_path, new_filename