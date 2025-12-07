import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_from_directory

# Helpers
from app.utils import allowed_file, save_upload

# Engines
from engine.audio import extract_audio
from engine.transcriber import transcribe_audio
from engine.renderer import generate_lyric_video

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
        return redirect(request.url)
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(request.url)

    try:
        video_path, filename = save_upload(file)
        base_name = os.path.splitext(filename)[0]
        audio_path = os.path.join(current_app.config['AUDIO_FOLDER'], f"{base_name}.wav")
        json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
        
        # 1. Extract Audio
        extract_audio(video_path, audio_path)
        
        # 2. Transcribe (Directly)
        if not os.path.exists(json_path):
            transcription_data = transcribe_audio(audio_path, model_size="tiny")
            with open(json_path, 'w') as f:
                json.dump(transcription_data, f, indent=4)
        
        return redirect(url_for('main.editor', filename=filename))
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return redirect(url_for('main.index'))

@main.route('/update-data/<filename>', methods=['POST'])
def update_data(filename):
    base_name = os.path.splitext(filename)[0]
    json_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{base_name}.json")
    try:
        new_data = request.json
        with open(json_path, 'w') as f:
            json.dump(new_data, f, indent=4)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/render', methods=['POST'])
def render_video():
    """
    Synchronous Render: The browser will wait here until it finishes.
    """
    try:
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

        # DIRECT CALL (Blocking)
        generate_lyric_video(
            video_path, audio_path, transcription_data, output_path, 
            style, position, animation
        )
        
        # Immediate Download Response
        return jsonify({
            "status": "success",
            "download_url": url_for('main.download_file', filename=output_filename)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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