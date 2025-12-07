import warnings
import gc

# Suppress warnings
warnings.filterwarnings("ignore")

# GLOBAL VARIABLE
model = None

def transcribe_audio(audio_path, model_size="tiny"):
    """
    Ultra-Lazy version: Imports whisper ONLY when called to save RAM.
    """
    global model
    
   
    import whisper 
    # ---------------------------------

    print(f"⏳ Loading Whisper model: {model_size}...")
    
    # Load Model (Tiny saves RAM)
    if model is None:
        model = whisper.load_model(model_size)
    
    print("Transcribing audio...")
    result = model.transcribe(audio_path, word_timestamps=True)
    
    # Clean up immediately
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