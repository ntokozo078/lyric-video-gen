import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_from_directory

# Helpers
from app.utils import allowed_file, save_upload

# Engines (Translator Removed)
from engine.audio import extract_audio
from engine.transcriber import transcribe_audio

# Async Task
from app.tasks import async_render_video 

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/editor/<filename>')
def editor(filename):
    return render_template('editor.html', filename=filename)

@main.route('/upload', methods=['POST'])
def upload_video():
    if 'video_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['video_file']
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file', 'danger')
        return redirect(request.url)

    try:
        video_path, filename = save_upload(file)
        base_name = os.path.splitext(filename)[0]
        audio_path = os.path.join(current_app.config['AUDIO_FOLDER'], f"{base_name}.wav")
        json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
        
        extract_audio(video_path, audio_path)
        
        if not os.path.exists(json_path):
            # Transcribe (Memory safe version)
            transcription_data = transcribe_audio(audio_path, model_size="tiny")
            with open(json_path, 'w') as f:
                json.dump(transcription_data, f, indent=4)
        
        return redirect(url_for('main.editor', filename=filename))
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@main.route('/update-data/<filename>', methods=['POST'])
def update_data(filename):
    base_name = os.path.splitext(filename)[0]
    json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
    try:
        new_data = request.json
        with open(json_path, 'w') as f:
            json.dump(new_data, f, indent=4) # Assuming full object passed
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/render', methods=['POST'])
def render_video():
    data = request.json
    filename = data.get('filename')
    style = data.get('style')
    position = data.get('position', 'pos-bottom') 
    animation = data.get('animation')

    base_name = os.path.splitext(filename)[0]
    video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    audio_path = os.path.join(current_app.config['AUDIO_FOLDER'], f"{base_name}.wav")
    json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
    output_filename = f"render_{style}_{base_name}.mp4"
    output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)

    with open(json_path, 'r') as f:
        transcription_data = json.load(f)

    # Async Render
    task = async_render_video.delay(
        video_path, audio_path, transcription_data, output_path, 
        style, position, animation
    )
    return jsonify({"status": "processing", "task_id": task.id}), 202

@main.route('/status/<task_id>')
def taskstatus(task_id):
    task = async_render_video.AsyncResult(task_id)
    response = {'state': task.state}
    if task.state == 'PENDING':
        response['status'] = 'Pending...'
    elif task.state != 'FAILURE':
        response['status'] = task.info.get('status', '')
        if 'result' in task.info:
            response['download_url'] = url_for('main.download_file', filename=os.path.basename(task.info['result']))
    else:
        response['status'] = str(task.info)
    return jsonify(response)

@main.route('/get-data/<filename>')
def get_data(filename):
    base_name = os.path.splitext(filename)[0]
    json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Data not found"}), 404

@main.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(os.path.join(current_app.config['BASE_DIR'], 'media'), filename)

@main.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(current_app.config['OUTPUT_FOLDER'], filename, as_attachment=True)