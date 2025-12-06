import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_from_directory

# Import Helper Functions
from app.utils import allowed_file, save_upload

# Import Data Engineering Engines
from engine.audio import extract_audio
from engine.transcriber import transcribe_audio
from engine.translator import translate_lyrics  # Import Translation Engine

# Import Async Tasks
# Note: You must have Redis running for this to work
from app.tasks import async_render_video 

# Define the Blueprint
main = Blueprint('main', __name__)

# ----------------------------------------------------------------
# 1. VIEW ROUTES (Pages the user sees)
# ----------------------------------------------------------------

@main.route('/')
def index():
    """Renders the Homepage (Upload Form)."""
    return render_template('index.html')

@main.route('/editor/<filename>')
def editor(filename):
    """
    Renders the Editor Interface.
    Passes the filename so the template can load the specific video/JSON.
    """
    return render_template('editor.html', filename=filename)


# ----------------------------------------------------------------
# 2. INGESTION ROUTES (Upload & Process)
# ----------------------------------------------------------------

@main.route('/upload', methods=['POST'])
def upload_video():
    """
    Ingestion Pipeline: Upload -> Validation -> Audio Extraction -> Transcription
    """
    if 'video_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['video_file']

    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file or extension', 'danger')
        return redirect(request.url)

    try:
        # 1. Save Video
        video_path, filename = save_upload(file)
        
        # Define paths
        base_name = os.path.splitext(filename)[0]
        audio_path = os.path.join(current_app.config['AUDIO_FOLDER'], f"{base_name}.wav")
        json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
        
        # 2. Extract Audio
        extract_audio(video_path, audio_path)
        
        # 3. Transcribe (only if not cached)
        if not os.path.exists(json_path):
            transcription_data = transcribe_audio(audio_path, model_size="base")
            
            # Save to Cache
            with open(json_path, 'w') as f:
                json.dump(transcription_data, f, indent=4)
        
        flash('Upload successful! generated lyrics.', 'success')
        return redirect(url_for('main.editor', filename=filename))
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        flash(f'Processing Error: {str(e)}', 'danger')
        return redirect(url_for('main.index'))


# ----------------------------------------------------------------
# 3. TRANSFORMATION ROUTES (Translation & Updates)
# ----------------------------------------------------------------

@main.route('/translate/<filename>', methods=['POST'])
def translate_video(filename):
    """
    Translates the current JSON lyrics to a target language.
    """
    try:
        target_lang = request.json.get('lang', 'zu')
        base_name = os.path.splitext(filename)[0]
        json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            # Run Translation Engine
            data['segments'] = translate_lyrics(data['segments'], target_lang)
            
            # Save back to cache
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
                
            return jsonify({"status": "success", "segments": data['segments']})
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/update-data/<filename>', methods=['POST'])
def update_data(filename):
    """Saves the user's text edits to the JSON file."""
    base_name = os.path.splitext(filename)[0]
    json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
    
    try:
        new_data = request.json
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                current_data = json.load(f)
            
            # Update segments
            current_data['segments'] = new_data['segments']
            
            with open(json_path, 'w') as f:
                json.dump(current_data, f, indent=4)
                
            return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------------
# 4. EXPORT ROUTES (Async Rendering)
# ----------------------------------------------------------------

@main.route('/render', methods=['POST'])
def render_video():
    """
    Async Export Pipeline: Starts Celery Task instead of freezing server.
    """
    data = request.json
    filename = data.get('filename')
    style = data.get('style')
    # Use exact coordinates if provided (Draggable), else fallback to position name
    position = data.get('position_coords', data.get('position', 'pos-bottom')) 
    animation = data.get('animation')

    # Define paths
    base_name = os.path.splitext(filename)[0]
    video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    audio_path = os.path.join(current_app.config['AUDIO_FOLDER'], f"{base_name}.wav")
    json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
    
    # We create a unique output name
    output_filename = f"render_{style}_{base_name}.mp4"
    output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)

    if not os.path.exists(json_path):
        return jsonify({"error": "Transcription data missing"}), 404

    with open(json_path, 'r') as f:
        transcription_data = json.load(f)

    # FIRE AND FORGET: Start Celery Task
    # .delay() sends the task to Redis. The worker picks it up.
    task = async_render_video.delay(
        video_path, audio_path, transcription_data, output_path, 
        style, position, animation
    )

    # Return the Task ID to the frontend so it can poll for status
    return jsonify({"status": "processing", "task_id": task.id}), 202

@main.route('/status/<task_id>')
def taskstatus(task_id):
    """
    Polling Route: Frontend checks this every 2 seconds to see if video is done.
    """
    task = async_render_video.AsyncResult(task_id)
    
    response = {'state': task.state}
    
    if task.state == 'PENDING':
        response['status'] = 'Pending...'
    elif task.state != 'FAILURE':
        response['status'] = task.info.get('status', '')
        if 'result' in task.info:
            response['result'] = task.info['result']
            # Send download URL
            response['download_url'] = url_for('main.download_file', filename=os.path.basename(task.info['result']))
    else:
        # Something went wrong
        response['status'] = str(task.info)
        
    return jsonify(response)


# ----------------------------------------------------------------
# 5. DATA & FILE ROUTES
# ----------------------------------------------------------------

@main.route('/get-data/<filename>')
def get_data(filename):
    """Returns the JSON lyrics for the Editor."""
    base_name = os.path.splitext(filename)[0]
    json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
    
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Data not found"}), 404

@main.route('/media/<path:filename>')
def serve_media(filename):
    """Serves raw video/audio files to the HTML player."""
    media_folder = os.path.join(current_app.config['BASE_DIR'], 'media')
    return send_from_directory(media_folder, filename)

@main.route('/download/<filename>')
def download_file(filename):
    """Allows the user to download the final rendered video."""
    return send_from_directory(current_app.config['OUTPUT_FOLDER'], filename, as_attachment=True)