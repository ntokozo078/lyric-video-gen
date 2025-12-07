import warnings
import gc

# Suppress warnings
warnings.filterwarnings("ignore")

def transcribe_audio(audio_path, model_size="tiny"):
    """
    Strict Low-Memory version: Imports, runs, and DELETES whisper.
    """
    # 1. Local Import (Saves Gunicorn RAM)
    import whisper 

    print(f"⏳ Loading Whisper model: {model_size}...")
    
    # 2. Load Model
    model = whisper.load_model(model_size)
    
    print("Transcribing audio...")
    result = model.transcribe(audio_path, word_timestamps=True)
    
    # 3. CRITICAL: Delete Model from RAM immediately
    del model
    gc.collect() 
    print("🧹 RAM cleared.")
    
    # 4. Format Data
    transcription_data = {
        "full_text": result["text"],
        "segments": []
    }

    for segment in result["segments"]:
        for word in segment.get("words", []):
            transcription_data["segments"].append({
                "word": word["word"].strip(),
                "start": word["start"],
                "end": word["end"],
                "confidence": word["probability"]
            })
            
    return transcription_data