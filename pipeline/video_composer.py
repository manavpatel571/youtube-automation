"""
Step 4b: Compose the final YouTube Short video using MoviePy.
Overlays dynamic subtitles and meme images.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    VideoFileClip,
)
from rich.console import Console

import config

console = Console()

def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get a font, falling back to default if custom fonts aren't available."""
    font_names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "calibrib.ttf" if bold else "calibri.ttf",
        "segoeui.ttf",
    ]
    
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except (OSError, IOError):
            continue
    
    win_fonts = Path("C:/Windows/Fonts")
    for font_name in font_names:
        font_path = win_fonts / font_name
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except (OSError, IOError):
                continue
    
    return ImageFont.load_default()

def compose_video(
    script: dict,
    image_paths: list[Path],
    output_path: Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    console.print("[cyan]Composing video with subtitles and memes...[/cyan]")
    
    W, H = config.VIDEO_WIDTH, config.VIDEO_HEIGHT
    
    frames_dir = output_path.parent / "frames"
    frames_dir.mkdir(exist_ok=True)
    
    segment_clips = []
    
    for i, segment in enumerate(script.get("segments", [])):
        bg_path = image_paths[i] if i < len(image_paths) else image_paths[-1]
        audio_path = segment.get("audio_path")
        duration = segment.get("duration", 0)
        word_timings = segment.get("word_timings", [])
        memes = segment.get("memes", [])
        
        if not audio_path or duration <= 0 or not word_timings:
            continue
            
        speaker = segment.get("speaker", "main")
        text_color = (255, 100, 255, 255) if speaker == "girl" else (255, 215, 0, 255)
            
        # Load background
        try:
            bg_base = Image.open(bg_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
        except Exception:
            bg_base = Image.new("RGBA", (W, H), config.COLORS["bg_dark"])
            
        # Add dark overlay
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        for y in range(H):
            ratio = y / H
            alpha = 100 if ratio > 0.5 else 50
            draw_ov.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
        bg_base = Image.alpha_composite(bg_base, overlay)
        
        font = _get_font(120, bold=True)
        
        # Load memes
        active_memes = []
        for meme in memes:
            local_path = meme.get("local_path")
            trigger = meme.get("trigger_word", "").lower()
            if local_path and Path(local_path).exists():
                meme_img = Image.open(local_path).convert("RGBA")
                meme_img.thumbnail((900, 900))
                
                # Find start idx using the first word of the trigger phrase
                first_trigger_word = trigger.split()[0] if trigger else ""
                start_idx = 0
                for w_idx, w_info in enumerate(word_timings):
                    if first_trigger_word and first_trigger_word in w_info["clean_word"]:
                        start_idx = w_idx
                        break
                active_memes.append({
                    "local_path": local_path,
                    "start_idx": start_idx
                })
        
        # Create a clip for each word
        word_clips = []
        for w_idx, w_info in enumerate(word_timings):
            word_str = w_info["word"].upper()
            
            frame_img = bg_base.copy()
            
            # Draw text
            draw = ImageDraw.Draw(frame_img)
            bbox = draw.textbbox((0, 0), word_str, font=font)
            text_w = bbox[2] - bbox[0]
            x = (W - text_w) // 2
            y = int(H * 0.65)
            
            # Shadow and text
            draw.text((x + 4, y + 4), word_str, font=font, fill=(0, 0, 0, 255))
            draw.text((x, y), word_str, font=font, fill=text_color)
            
            # Save frame
            frame_path = frames_dir / f"seg_{i}_word_{w_idx}.jpg"
            frame_img.convert("RGB").save(frame_path, "JPEG", quality=90)
            
            word_duration = w_info["end"] - w_info["start"]
            clip = ImageClip(str(frame_path)).with_duration(word_duration)
            word_clips.append(clip)
            
        # Concatenate word clips for this segment
        segment_video = concatenate_videoclips(word_clips, method="chain")
        audio_clip = AudioFileClip(audio_path)
        segment_video = segment_video.with_audio(audio_clip)
        
        # Composite memes on top so GIFs can animate
        comp_clips = [segment_video]
        for meme in active_memes:
            local_path = meme["local_path"]
            start_time = word_timings[meme["start_idx"]]["start"]
            meme_dur = duration - start_time
            
            is_gif = local_path.lower().endswith(".gif")
            if is_gif:
                try:
                    m_clip = VideoFileClip(local_path, has_mask=True)
                    if hasattr(m_clip, "with_loop"):
                        m_clip = m_clip.with_loop()
                except Exception:
                    m_clip = ImageClip(local_path)
            else:
                m_clip = ImageClip(local_path)
            
            try:
                if hasattr(m_clip, 'resized'):
                    m_clip = m_clip.resized(width=800)
                    if m_clip.h > 800:
                        m_clip = m_clip.resized(height=800)
                else:
                    m_clip = m_clip.resize(width=800)
                    if m_clip.h > 800:
                        m_clip = m_clip.resize(height=800)
            except Exception:
                pass
            
            mx = (W - m_clip.w) // 2
            my = int(H * 0.15)
            
            if hasattr(m_clip, 'with_position'):
                m_clip = m_clip.with_position((mx, my)).with_start(start_time).with_duration(meme_dur)
            else:
                m_clip = m_clip.set_position((mx, my)).set_start(start_time).set_duration(meme_dur)
                
            comp_clips.append(m_clip)
            
        segment_video = CompositeVideoClip(comp_clips, size=(W, H)).with_duration(duration)
        
        segment_clips.append(segment_video)
        console.print(f"  Segment {i+1} prepared")
        
    if not segment_clips:
        raise ValueError("No valid segments to compose.")
        
    final_video = concatenate_videoclips(segment_clips, method="compose")
    
    console.print("  Encoding video...")
    final_video.write_videofile(
        str(output_path),
        fps=config.VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        logger=None,
    )
    
    final_video.close()
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    console.print(f"[green]Video saved: {output_path} ({file_size_mb:.1f} MB)[/green]")
    
    return output_path

def compose_music_video(
    script: dict,
    image_paths: list[Path],
    audio_path: Path,
    output_path: Path,
) -> Path:
    """Compose the 6 PM music video format with a single audio track and timed slides."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    console.print("[cyan]Composing music video...[/cyan]")
    
    W, H = config.VIDEO_WIDTH, config.VIDEO_HEIGHT
    
    audio_clip = AudioFileClip(str(audio_path))
    total_duration = audio_clip.duration
    
    segments = script.get("segments", [])
    num_segments = len(segments)
    
    if num_segments == 0:
        raise ValueError("No segments in script.")
        
    segment_duration = total_duration / num_segments
    
    segment_clips = []
    
    font = _get_font(90, bold=True)
    
    for i, segment in enumerate(segments):
        bg_path = image_paths[i] if i < len(image_paths) else image_paths[-1]
        text = segment.get("text", "").upper()
        memes = segment.get("memes", [])
        
        try:
            bg_base = Image.open(bg_path).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
        except Exception:
            bg_base = Image.new("RGBA", (W, H), config.COLORS["bg_dark"])
            
        # Add dark overlay
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        for y in range(H):
            ratio = y / H
            alpha = 100 if ratio > 0.5 else 50
            draw_ov.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
        bg_base = Image.alpha_composite(bg_base, overlay)
        
        # Draw lyric text
        draw = ImageDraw.Draw(bg_base)
        
        # Simple text wrapping
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            bbox = draw.textbbox((0, 0), " ".join(current_line), font=font)
            if bbox[2] - bbox[0] > W - 100:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
            
        y = int(H * 0.70)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
            x = (W - text_w) // 2
            
            draw.text((x + 4, y + 4), line, font=font, fill=(0, 0, 0, 255))
            draw.text((x, y), line, font=font, fill=(255, 100, 255, 255)) # Pink color for music video
            
            y += bbox[3] - bbox[1] + 20
            
        frame_path = output_path.parent / f"music_seg_bg_{i}.jpg"
        bg_base.convert("RGB").save(frame_path, "JPEG", quality=90)
        
        bg_clip = ImageClip(str(frame_path)).with_duration(segment_duration)
        comp_clips = [bg_clip]
        
        valid_memes = [m for m in memes if m.get("local_path") and Path(m.get("local_path")).exists()]
        if valid_memes:
            meme_dur = segment_duration / len(valid_memes)
            for m_idx, meme in enumerate(valid_memes):
                local_path = meme.get("local_path")
                start_time = m_idx * meme_dur
                
                is_gif = local_path.lower().endswith(".gif")
                if is_gif:
                    try:
                        m_clip = VideoFileClip(local_path, has_mask=True)
                        if hasattr(m_clip, "with_loop"):
                            m_clip = m_clip.with_loop()
                    except Exception:
                        m_clip = ImageClip(local_path)
                else:
                    m_clip = ImageClip(local_path)
                
                # Resize and position safely for both MoviePy v1 and v2
                try:
                    if hasattr(m_clip, 'resized'):
                        m_clip = m_clip.resized(width=800)
                        if m_clip.h > 800:
                            m_clip = m_clip.resized(height=800)
                    else:
                        m_clip = m_clip.resize(width=800)
                        if m_clip.h > 800:
                            m_clip = m_clip.resize(height=800)
                except Exception:
                    pass
                
                mx = (W - m_clip.w) // 2
                my = int(H * 0.15)
                
                # In MoviePy v1 it's set_position, in v2 it's with_position
                if hasattr(m_clip, 'with_position'):
                    m_clip = m_clip.with_position((mx, my)).with_start(start_time).with_duration(meme_dur)
                else:
                    m_clip = m_clip.set_position((mx, my)).set_start(start_time).set_duration(meme_dur)
                    
                comp_clips.append(m_clip)
        
        segment_clip = CompositeVideoClip(comp_clips, size=(W, H)).with_duration(segment_duration)
        segment_clips.append(segment_clip)
        
    final_video = concatenate_videoclips(segment_clips, method="compose")
    final_video = final_video.with_audio(audio_clip)
    
    console.print("  Encoding music video...")
    final_video.write_videofile(
        str(output_path),
        fps=config.VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        logger=None,
    )
    
    final_video.close()
    audio_clip.close()
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    console.print(f"[green]Music Video saved: {output_path} ({file_size_mb:.1f} MB)[/green]")
    
    return output_path

