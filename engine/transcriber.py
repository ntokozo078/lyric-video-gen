import whisper
import warnings

# Suppress annoying warnings from the libraries
warnings.filterwarnings("ignore")

# GLOBAL VARIABLE: Start as None so we don't load it immediately
model = None

def transcribe_audio(audio_path, model_size="base"):
    """
    Uses OpenAI Whisper to convert audio to text with word-level timestamps.
    
    Args:
        audio_path (str): Path to the .wav file.
        model_size (str): 'tiny', 'base', 'small', 'medium', 'large'. 
                          'base' is a good balance of speed/accuracy for CPUs.
    
    Returns:
        dict: A structured dictionary containing full text and word segments.
    """
    global model

    # LAZY LOADING PATTERN
    # Check if the model is already loaded. If not, load it now.
    if model is None:
        print(f"⏳ Loading Whisper model: {model_size} (This happens only once)...")
        model = whisper.load_model(model_size)
    else:
        print("⚡ Model already loaded. Skipping setup.")
    
    print("Transcribing audio... this may take a moment.")
    
    # word_timestamps=True is CRITICAL for karaoke effects
    result = model.transcribe(audio_path, word_timestamps=True)
    
    # We clean up the data structure for our frontend
    transcription_data = {
        "full_text": result["text"],
        "segments": [] # We will build a cleaner list of segments
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