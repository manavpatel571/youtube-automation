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
        
        font = _get_font(80, bold=True)
        
        # Load memes
        active_memes = []
        for meme in memes:
            local_path = meme.get("local_path")
            trigger = meme.get("trigger_word", "").lower()
            if local_path and Path(local_path).exists():
                meme_img = Image.open(local_path).convert("RGBA")
                meme_img.thumbnail((900, 900))
                
                # Find start idx
                start_idx = 0
                for w_idx, w_info in enumerate(word_timings):
                    if trigger in w_info["clean_word"]:
                        start_idx = w_idx
                        break
                active_memes.append({
                    "img": meme_img,
                    "start_idx": start_idx
                })
        
        # Create a clip for each word
        word_clips = []
        for w_idx, w_info in enumerate(word_timings):
            word_str = w_info["word"].upper()
            
            frame_img = bg_base.copy()
            
            # Draw memes that should be active
            for meme in active_memes:
                if w_idx >= meme["start_idx"]:
                    meme_img = meme["img"]
                    mx = (W - meme_img.width) // 2
                    my = int(H * 0.2)
                    frame_img.alpha_composite(meme_img, (mx, my))
                    
            # Draw text
            draw = ImageDraw.Draw(frame_img)
            bbox = draw.textbbox((0, 0), word_str, font=font)
            text_w = bbox[2] - bbox[0]
            x = (W - text_w) // 2
            y = int(H * 0.65)
            
            # Shadow and text
            draw.text((x + 4, y + 4), word_str, font=font, fill=(0, 0, 0, 255))
            draw.text((x, y), word_str, font=font, fill=(255, 215, 0, 255))  # Gold color
            
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
