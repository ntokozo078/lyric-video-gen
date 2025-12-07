import warnings
import gc
import os

# Suppress warnings
warnings.filterwarnings("ignore")

def transcribe_audio(audio_path, model_size="tiny"):
    """
    Ultra-Low Memory Version for Free Tier Hosting.
    """
    # 1. Force PyTorch to use minimal threads (Saves RAM)
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"

    print("⚡ Starting transcription (Low RAM Mode)...")
    
    # 2. Local Imports (Only load heavy libraries NOW)
    import torch
    import whisper
    
    # Force single-thread execution for PyTorch
    torch.set_num_threads(1)

    print(f"⏳ Loading Whisper model: {model_size}...")
    
    # 3. Load Model
    # We use 'cpu' explicitly to avoid looking for GPU drivers (saves RAM)
    model = whisper.load_model(model_size, device="cpu")
    
    print("Transcribing audio...")
    result = model.transcribe(audio_path, word_timestamps=True, fp16=False) # fp16=False is safer for CPU
    
    # 4. CRITICAL: Delete Model from RAM immediately
    del model
    del torch
    gc.collect() 
    print("🧹 RAM cleared.")
    
    # 5. Format Data
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