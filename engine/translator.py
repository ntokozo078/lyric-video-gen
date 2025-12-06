from deep_translator import GoogleTranslator

def translate_lyrics(segments, target_lang='zu'):
    """
    Translates a list of lyric segments to the target language.
    target_lang: 'zu' (Zulu), 'fr' (French), 'es' (Spanish), etc.
    """
    print(f"🌍 Translating {len(segments)} lines to {target_lang}...")
    
    translator = GoogleTranslator(source='auto', target=target_lang)
    
    translated_segments = []
    
    # We translate word-by-word or phrase-by-phrase
    # Note: Context might be lost in word-by-word, but it keeps timestamps accurate.
    for seg in segments:
        original_word = seg['word']
        try:
            # Check if it's just punctuation/emoji, skip translation
            if len(original_word) < 2: 
                translated_word = original_word
            else:
                translated_word = translator.translate(original_word)
        except:
            translated_word = original_word
            
        translated_segments.append({
            "word": translated_word,
            "start": seg['start'],
            "end": seg['end'],
            "confidence": seg.get('confidence', 1.0)
        })
        
    return translated_segments