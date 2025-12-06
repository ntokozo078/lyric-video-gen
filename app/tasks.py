import os
from celery import Celery
from engine.renderer import generate_lyric_video

# Initialize Celery
# Note: Ensure Redis is running
celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery.task(bind=True)
def async_render_video(self, video_path, audio_path, transcription_data, output_path, style, position, animation):
    """
    Background Task: Renders the video.
    """
    # 1. Update Status to Processing
    self.update_state(state='PROCESSING', meta={'status': 'Starting Render Engine...'})
    
    # 2. Run the Engine
    # We do NOT use try/except here anymore. 
    # If this fails, Celery will automatically set state to 'FAILURE' 
    # and save the correct Error info for us.
    generate_lyric_video(
        video_path, audio_path, transcription_data, output_path, 
        style=style, position=position, animation=animation
    )
    
    # 3. Success
    return {'status': 'Task completed!', 'result': output_path}