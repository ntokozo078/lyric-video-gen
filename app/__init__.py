import os
from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure media directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CACHE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # Register Routes
    from app.routes import main
    app.register_blueprint(main)

    return app