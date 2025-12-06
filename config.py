import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this-in-prod'
    
    # Base Directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Media Paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'media', 'uploads')
    AUDIO_FOLDER = os.path.join(BASE_DIR, 'media', 'audio')
    CACHE_FOLDER = os.path.join(BASE_DIR, 'media', 'cache')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'media', 'outputs')
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    # Allowed Extensions
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}
    
    # Max Upload Size (e.g., 50MB)
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024