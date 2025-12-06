from moviepy.editor import VideoFileClip

def extract_audio(video_path, output_audio_path):
    """
    Loads a video file and saves its audio track as a WAV file.
    We use WAV because it is uncompressed and easiest for AI models to read.
    """
    try:
        # Load the video
        video = VideoFileClip(video_path)
        
        # Check if video actually has audio
        if video.audio is None:
            raise ValueError("This video has no sound!")
            
        # Write the audio file (verbose=False quiets the terminal logs)
        video.audio.write_audiofile(output_audio_path, codec='pcm_s16le', verbose=False, logger=None)
        
        # Close the clip to release system memory (Crucial for servers!)
        video.close()
        
    except Exception as e:
        print(f"Error extracting audio: {e}")
        raise e