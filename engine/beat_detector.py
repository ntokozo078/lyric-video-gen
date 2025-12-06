import librosa
import numpy as np

def detect_beats(audio_path):
    """
    Analyzes the audio file to find the beat (tempo) and timestamp locations of beats.
    
    Args:
        audio_path (str): Path to the .wav file.
        
    Returns:
        list: A list of floats representing the timestamps (seconds) where a beat occurs.
    """
    print("Analyzing audio rhythm...")
    
    # Load audio (sr=22050 is standard for music analysis)
    y, sr = librosa.load(audio_path, sr=22050)
    
    # Isolate the harmonic and percussive components (better for beat tracking)
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    # Track beats using the percussive component
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr)
    
    # Convert frame indices to time (seconds)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Convert numpy array to standard Python list for JSON serialization
    return beat_times.tolist()