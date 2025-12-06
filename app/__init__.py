import os
from flask import Flask
from celery import Celery  # Added this missing import
from config import Config

def make_celery(app):
    """
    Helper function to configure Celery with Flask's config.
    """
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    # Optional: Logic to ensure tasks run within the Flask context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app(config_class=Config):
    """
    Flask Application Factory
    """
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