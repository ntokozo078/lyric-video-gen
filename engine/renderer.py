import os
import platform
import math
from moviepy.config import change_settings

# --- CROSS-PLATFORM CONFIGURATION ---
# This fixes the "WinError 2" on your laptop AND works on the Cloud.
if platform.system() == "Windows":
    # ⚠️ IMPORTANT: Verify this path matches your computer exactly!
    # Common paths:
    # r"C:\Program Files\ImageMagick-7.1.3-Q16-HDRI\magick.exe"
    # r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
    change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.3-Q16-HDRI\magick.exe"})
else:
    # Linux / Render.com Path
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip

def get_emoji_font():
    """Returns a font that supports emojis based on the OS."""
    system = platform.system()
    if system == "Windows": return "Segoe-UI-Emoji"
    elif system == "Darwin": return "Apple-Color-Emoji"
    return "Noto-Color-Emoji" # Linux default

def generate_lyric_video(video_path, audio_path, transcription_data, output_path, 
                         style="style-clean", position="pos-bottom", animation="anim-none"):
    """
    Renders the final video with lyrics.
    Optimized for Low-RAM environments (Render Free Tier).
    """
    print(f"🎬 Starting Render: Style={style}, Pos={position}, Anim={animation}")
    
    # 1. Load Video
    video = VideoFileClip(video_path)
    
    # --- CRITICAL RAM FIX FOR CLOUD ---
    # If the video is 1080p or 4k, it consumes ~1.5GB RAM to process.
    # We resize it to 480p (Mobile Quality) to stay under 512MB RAM.
    if video.h > 480:
        print(f"📉 Downscaling video from {video.h}p to 480p to save RAM...")
        video = video.resize(height=480)
    # ----------------------------------

    # 2. Load & Attach Audio
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)
    
    w, h = video.size
    
    # --- POSITION LOGIC ---
    if position == "pos-top":
        base_y = h * 0.15 # Top 15%
    elif position == "pos-center":
        base_y = 'center'
    else: # pos-bottom (default)
        base_y = h * 0.80 # Bottom 20%

    # --- STYLE CONFIGURATION ---
    font = 'Arial-Bold'
    fontsize = 40 if w < 600 else 60 # Adjust font size for 480p
    color = 'white'
    stroke_color = 'black'
    stroke_width = 2
    
    if style == 'style-ig-glow':
        font = 'Times-New-Roman-Bold-Italic'
        stroke_color = '#00d2ff'
        stroke_width = 1
    elif style == 'style-ig-green':
        font = 'Arial-Black'
        color = '#39ff14'
        stroke_width = 0
    elif style == 'style-emoji':
        font = get_emoji_font()
        fontsize = int(fontsize * 1.2)
        color = 'yellow'

    clips = [video]

    # --- TEXT GENERATION LOOP ---
    print(f"📝 Processing {len(transcription_data['segments'])} text segments...")
    
    for segment in transcription_data["segments"]:
        word = segment["word"]
        start = segment["start"]
        end = segment["end"]
        duration = end - start
        if duration < 0.1: duration = 0.1

        # Create Text Clip
        try:
            txt = (TextClip(word, fontsize=fontsize, color=color, font=font, 
                            stroke_color=stroke_color, stroke_width=stroke_width)
                   .set_start(start)
                   .set_duration(duration))
        except Exception as e:
            print(f"⚠️ Font Error: {e}. Fallback to Arial.")
            txt = (TextClip(word, fontsize=fontsize, color='white', font='Arial')
                   .set_start(start)
                   .set_duration(duration))

        # --- ANIMATION LOGIC ---
        if animation == "anim-slide":
            def slide(t):
                if t < 0.2:
                    y_off = 50 * (1 - t/0.2)
                    return ('center', base_y + y_off if base_y != 'center' else h/2 + y_off)
                return ('center', base_y)
            txt = txt.set_position(slide)

        elif animation == "anim-bounce":
            def bounce(t):
                y_off = abs(math.sin(t * 10)) * 15
                return ('center', base_y - y_off if base_y != 'center' else h/2 - y_off)
            txt = txt.set_position(bounce)

        elif animation == "anim-karaoke":
            # Simple zoom pulse
            txt = txt.resize(lambda t: 1 + 0.2 * math.sin(t * 3.14))
            txt = txt.set_position(('center', base_y))

        else: # anim-pop or none
            txt = txt.set_position(('center', base_y))
            if animation == "anim-pop":
                txt = txt.crossfadein(0.1)

        clips.append(txt)

    # 3. COMPOSITE & RENDER
    # We combine all text clips over the video
    final = CompositeVideoClip(clips)
    
    print("🚀 Writing video file... (This may take a minute)")
    
    # --- RENDER SETTINGS (Optimized for Speed/Memory) ---
    final.write_videofile(
        output_path, 
        fps=24, 
        codec='libx264', 
        audio_codec='aac', 
        # 'ultrafast' uses less CPU/RAM but makes slightly larger files. Perfect for free servers.
        preset='ultrafast', 
        # threads=1 ensures we don't spike memory usage
        threads=1,
        # Remove temporary audio file automatically
        temp_audiofile='temp-audio.m4a', 
        remove_temp=True
    )
    
    video.close()
    print("✅ Video Render Complete!")