import warnings
import gc
import os

# Suppress warnings
warnings.filterwarnings("ignore")

def transcribe_audio(audio_path, model_size="tiny"):
    """
    Uses Faster-Whisper (CTranslate2) to save RAM.
    This runs without PyTorch, using ~200MB RAM instead of ~600MB.
    """
    print(f"⚡ Starting transcription (Faster-Whisper / {model_size})...")
    
    # 1. Local Import to save start-up memory
    from faster_whisper import WhisperModel

    # 2. Load Model
    # cpu_threads=1 is critical for the Free Tier limit
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=1)

    print("Transcribing audio...")
    # 3. Transcribe
    segments, info = model.transcribe(audio_path, word_timestamps=True)
    
    # 4. Process segments (Faster-Whisper returns a generator, so we iterate now)
    transcription_data = {
        "full_text": "",
        "segments": []
    }

    full_text_pieces = []

    for segment in segments:
        full_text_pieces.append(segment.text)
        for word in segment.words:
            transcription_data["segments"].append({
                "word": word.word.strip(),
                "start": word.start,
                "end": word.end,
                "confidence": word.probability
            })
            
    transcription_data["full_text"] = " ".join(full_text_pieces)
    
    # 5. Clean up
    del model
    gc.collect() 
    print("🧹 RAM cleared.")
            
    return transcription_data