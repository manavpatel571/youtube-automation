"""
Step 4a: Generate background images for video segments using Gemini.
Creates futuristic tech-themed images for each segment of the Short.
"""

from pathlib import Path
from PIL import Image
import io
from google import genai
from google.genai import types
from rich.console import Console

import config

console = Console()


def generate_segment_image(
    prompt: str, 
    output_path: str | Path,
    index: int = 0,
) -> Path:
    """
    Generate a single background image for a video segment.
    
    Args:
        prompt: Image generation prompt (from script writer).
        output_path: Where to save the image.
        index: Segment index (for logging).
        
    Returns:
        Path to the saved image.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = genai.Client(api_key=config.GEMINI_API_KEY)

    # Enhance the prompt with style directives for vertical format
    enhanced_prompt = f"""Generate a stunning, cinematic background image for a YouTube Short.

Style: Highly cinematic wide-angle shot, photorealistic, 8k resolution, 
dramatic lighting, depth of field, professional cinematography, 
dark futuristic cyberpunk aesthetic, deep blacks and dark blues with glowing accents.

Subject Context (Crucial): {prompt}

Requirements:
- The image MUST perfectly reflect the Subject Context.
- Leave space at center for text overlay.
- No text, words, or logos in the image.
- Dark enough for white text to be easily readable on top.
- High visual impact, cinematic movie frame."""

    import time

    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=config.GEMINI_IMAGE_MODEL,
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    aspect_ratio="9:16",
                )
            )

            # Extract image from response
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    image_data = part.inline_data.data
                    
                    # Open with Pillow and resize to exact video dimensions
                    img = Image.open(io.BytesIO(image_data))
                    img = img.resize(
                        (config.VIDEO_WIDTH, config.VIDEO_HEIGHT), 
                        Image.Resampling.LANCZOS
                    )
                    img.save(output_path, "PNG", quality=95)
                    
                    console.print(f"[green]  ✓ Segment {index + 1} image saved[/green]")
                    return output_path

            raise ValueError("No image data in response")
        except Exception as e:
            console.print(f"[yellow]  ⚠ Gemini Image API rate-limited: {e}[/yellow]")
            console.print(f"[cyan]    → Generating free AI background via Pollinations.ai...[/cyan]")
            return _generate_pollinations_image(prompt, output_path, index)


def _generate_pollinations_image(prompt: str, output_path: Path, index: int) -> Path:
    """Generate free vertical AI image using Pollinations.ai (FLUX model)."""
    import urllib.parse
    import urllib.request
    
    clean_prompt = f"cinematic 9:16 portrait photography, highly photorealistic movie frame, dark cyberpunk, {prompt}, 8k ultra detail"
    encoded_prompt = urllib.parse.quote(clean_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={config.VIDEO_WIDTH}&height={config.VIDEO_HEIGHT}&nologo=true&seed={index + 42}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as response:
            image_bytes = response.read()
            img = Image.open(io.BytesIO(image_bytes))
            img = img.resize((config.VIDEO_WIDTH, config.VIDEO_HEIGHT), Image.Resampling.LANCZOS)
            img.save(output_path, "PNG", quality=95)
            console.print(f"[green]  ✓ Segment {index + 1} AI image generated via Pollinations.ai[/green]")
            return output_path
    except Exception as err:
        console.print(f"[yellow]  ⚠ Pollinations image failed: {err}[/yellow]")
        console.print(f"[yellow]    → Using gradient fallback[/yellow]")
        return _generate_fallback_image(output_path, index)


def _generate_fallback_image(output_path: Path, index: int) -> Path:
    """Generate a gradient fallback image when AI generation fails."""
    from PIL import ImageDraw
    
    img = Image.new("RGB", (config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)
    
    # Create a vertical gradient with different colors per segment
    color_sets = [
        ((15, 10, 40), (5, 5, 15)),      # Deep purple to black
        ((10, 20, 40), (5, 5, 20)),      # Dark blue to black
        ((30, 10, 30), (5, 5, 15)),      # Dark magenta to black
        ((10, 25, 25), (5, 10, 10)),     # Dark teal to black
        ((25, 15, 10), (10, 5, 5)),      # Dark amber to black
    ]
    
    top_color, bottom_color = color_sets[index % len(color_sets)]
    
    for y in range(config.VIDEO_HEIGHT):
        ratio = y / config.VIDEO_HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (config.VIDEO_WIDTH, y)], fill=(r, g, b))
    
    img.save(output_path, "PNG")
    return output_path


def generate_all_images(segments: list[dict], work_dir: Path) -> list[Path]:
    """
    Generate images for all segments.
    
    Args:
        segments: List of segment dicts (each has 'image_prompt').
        work_dir: Directory to save images in.
        
    Returns:
        List of paths to generated images.
    """
    images_dir = work_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[cyan]🎨 Generating {len(segments)} background images...[/cyan]")
    
    image_paths = []
    for i, segment in enumerate(segments):
        prompt = segment.get("image_prompt", "futuristic AI technology abstract background")
        output_path = images_dir / f"segment_{i:02d}.png"
        
        path = generate_segment_image(prompt, output_path, index=i)
        image_paths.append(path)
    
    console.print(f"[green]✓ All {len(image_paths)} images generated[/green]")
    return image_paths


if __name__ == "__main__":
    # Test with a single image
    test_prompt = "Futuristic Google AI laboratory with holographic displays"
    output = config.DRAFTS_DIR / "test_image.png"
    generate_segment_image(test_prompt, output)
