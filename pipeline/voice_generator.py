"""
Step 3: Generate voiceover audio using ElevenLabs TTS API.
Converts the script text to speech per segment and calculates word timings.
"""

import os
from pathlib import Path
from elevenlabs.client import ElevenLabs
from rich.console import Console
from moviepy import AudioFileClip

import config

console = Console()

def generate_voice_for_script(script: dict, drafts_dir: Path) -> dict:
    """
    Convert text to speech for each segment.
    Updates script with 'audio_path' and 'word_timings' per segment.
    """
    drafts_dir.mkdir(parents=True, exist_ok=True)
    client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
    
    console.print("[cyan]🎙 Generating voiceover per segment...[/cyan]")
    
    for i, segment in enumerate(script.get("segments", [])):
        text = segment.get("text", "")
        if not text:
            continue
            
        output_path = drafts_dir / f"segment_{i}_voice.mp3"
        
        speaker = segment.get("speaker", "main")
        current_voice_id = config.GIRL_VOICE_ID if speaker == "girl" else config.VOICE_ID
        
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=current_voice_id,
            model_id=config.ELEVENLABS_MODEL,
            output_format="mp3_44100_128",
        )
        
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
                
        # Get duration
        clip = AudioFileClip(str(output_path))
        duration = clip.duration
        clip.close()
        
        segment["audio_path"] = str(output_path)
        segment["duration"] = duration
        
        # Calculate word timings (uniform distribution)
        words = text.split()
        num_words = len(words)
        time_per_word = duration / max(1, num_words)
        
        word_timings = []
        for w_idx, word in enumerate(words):
            clean_word = "".join([c for c in word if c.isalnum()]).lower()
            word_timings.append({
                "word": word,
                "clean_word": clean_word,
                "start": w_idx * time_per_word,
                "end": (w_idx + 1) * time_per_word
            })
            
        segment["word_timings"] = word_timings
        console.print(f"  ✓ Segment {i+1} audio saved ({duration:.1f}s)")
        
    return script
