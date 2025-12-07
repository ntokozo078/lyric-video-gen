import platform
import math
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import os
import platform
from moviepy.config import change_settings

# --- CROSS-PLATFORM CONFIG ---
if platform.system() == "Windows":
    # YOUR LOCAL PATH (Verify this file exists!)
    change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})
else:
    # CLOUD PATH
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

import math
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip

# ... rest of your code ...

import platform
import math
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
# ... rest of your code ...
def get_emoji_font():
    system = platform.system()
    if system == "Windows": return "Segoe-UI-Emoji"
    elif system == "Darwin": return "Apple-Color-Emoji"
    return "Noto-Color-Emoji"

def generate_lyric_video(video_path, audio_path, transcription_data, output_path, 
                         style="style-clean", position="pos-bottom", animation="anim-none"):
    
    print(f"🎬 Rendering: Style={style}, Pos={position}, Anim={animation}")
    
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)
    
    w, h = video.size
    
    # --- POSITION LOGIC ---
    # We define WHERE the text sits (Y-axis)
    if position == "pos-top":
        base_y = h * 0.15 # Top 15%
    elif position == "pos-center":
        base_y = 'center' # MoviePy keyword for exact center
    else: # pos-bottom
        base_y = h * 0.80 # Bottom 20% (Safe zone)

    # --- STYLE LOGIC ---
    font = 'Arial-Bold'
    fontsize = 70
    color = 'white'
    stroke_color = 'black'
    stroke_width = 2
    
    if style == 'style-ig-glow':
        font = 'Times-New-Roman-Bold-Italic'
        stroke_color = '#00d2ff'
        stroke_width = 2
    elif style == 'style-ig-green':
        font = 'Arial-Black'
        color = '#39ff14'
        stroke_width = 0
    elif style == 'style-emoji':
        font = get_emoji_font()
        fontsize = 90
        color = 'yellow' # Emoji fallback color

    clips = [video]

    for segment in transcription_data["segments"]:
        word = segment["word"]
        start = segment["start"]
        end = segment["end"]
        duration = end - start
        if duration < 0.1: duration = 0.1

        # Create Text
        try:
            txt = (TextClip(word, fontsize=fontsize, color=color, font=font, 
                           stroke_color=stroke_color, stroke_width=stroke_width)
                   .set_start(start)
                   .set_duration(duration))
        except:
            # Fallback if font fails
            txt = (TextClip(word, fontsize=fontsize, color='white', font='Arial')
                   .set_start(start)
                   .set_duration(duration))

        # --- ANIMATION LOGIC ---
        
        # 1. Slide Up
        if animation == "anim-slide":
            def slide(t):
                if t < 0.2:
                    y_off = 100 * (1 - t/0.2)
                    return ('center', base_y + y_off if base_y != 'center' else h/2 + y_off)
                return ('center', base_y)
            txt = txt.set_position(slide)

        # 2. Bounce
        elif animation == "anim-bounce":
            def bounce(t):
                y_off = abs(math.sin(t * 10)) * 30
                return ('center', base_y - y_off if base_y != 'center' else h/2 - y_off)
            txt = txt.set_position(bounce)

        # 3. Karaoke (Scale)
        elif animation == "anim-karaoke":
            # MoviePy scale animation is complex, simple zoom effect:
            txt = txt.resize(lambda t: 1 + 0.3 * math.sin(t * 3.14)) # Pulse size
            txt = txt.set_position(('center', base_y))

        # 4. Default / Pop / Typewriter
        else:
            txt = txt.set_position(('center', base_y))
            if animation == "anim-pop":
                txt = txt.crossfadein(0.1)

        clips.append(txt)

    final = CompositeVideoClip(clips)
    final.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)
    video.close()