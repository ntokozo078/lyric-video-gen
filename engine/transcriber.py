import warnings
import gc

warnings.filterwarnings("ignore")

def transcribe_audio(audio_path, model_size="tiny"):
    # IMPORT HERE TO SAVE MEMORY ON STARTUP
    import whisper 

    print(f"⏳ Loading Whisper model: {model_size}...")
    model = whisper.load_model(model_size)
    
    print("Transcribing audio...")
    result = model.transcribe(audio_path, word_timestamps=True)
    
    # DELETE MODEL IMMEDIATELY TO FREE RAM
    del model
    gc.collect() 
    
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