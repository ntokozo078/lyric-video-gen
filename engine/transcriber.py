import whisper
import warnings
import gc # Garbage Collector

warnings.filterwarnings("ignore")

def transcribe_audio(audio_path, model_size="tiny"):
    """
    Low-Memory version: Loads model, runs, and deletes it immediately.
    """
    print(f"⏳ Loading Whisper model: {model_size}...")
    
    # 1. Load Model (Tiny saves RAM)
    model = whisper.load_model(model_size)
    
    print("Transcribing audio...")
    # 2. Transcribe
    result = model.transcribe(audio_path, word_timestamps=True)
    
    # 3. Aggressive Cleanup (Crucial for Free Tier)
    del model
    gc.collect() 
    print("🧹 Memory cleaned up.")
    
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