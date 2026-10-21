# Text overlay

Draw words with Pillow, then place the PNG. `TextClip` clips ascenders and descenders in moviepy 2.x, so leave it unused.

Run `scripts/check_moviepy.py --json` first. Continue only when `ok` is true.

## Font file

Use the path the user gave when that file exists. Otherwise take the first candidate that exists:

- `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`
- `/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf`
- `/Library/Fonts/Arial.ttf`
- `/System/Library/Fonts/Supplemental/Arial.ttf`
- `C:\Windows\Fonts\arial.ttf`

If the user named a file and it is missing, or none of the candidates exist, ask for a font file. Do not download a font and do not pick a bold macOS face as a standing default.

## Render a PNG

Cache by the text, size, color, and font path so a rebuild skips the same drawing.

```python
import hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def render_text_png(txt, size, hex_color, font_path, cache_dir="./text_cache"):
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(f"{txt}|{size}|{hex_color}|{font_path}".encode()).hexdigest()[:16]
    path = cache / f"{key}.png"
    if path.exists():
        return str(path)

    font = ImageFont.truetype(font_path, size)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = probe.textbbox((0, 0), txt, font=font)
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = max(20, size // 4)
    image = Image.new("RGBA", (width + pad * 2, height + pad * 2), (0, 0, 0, 0))
    rgb = tuple(int(hex_color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    ImageDraw.Draw(image).text(
        (pad - bbox[0], pad - bbox[1]),
        txt,
        font=font,
        fill=(*rgb, 255),
    )
    image.save(path)
    return str(path)
```

The padding is what keeps the tops of capitals and the tails of letters inside the image. A tight bbox without it is the same failure `TextClip` has.

## Place it on one clip

```python
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip

picture = VideoFileClip("outputs/scene.mp4")
title = (
    ImageClip(render_text_png("NORTH DOCK", 72, "#FFFFFF", font_path))
    .with_duration(picture.duration)
    .with_position(("center", 880))
)
final = CompositeVideoClip([picture, title], size=picture.size)
final.write_videofile("outputs/scene-titled.mp4", fps=30, codec="libx264", audio_codec="aac")
```

`outputs/scene-titled.mp4` must be a new path. If it already exists, ask before replacing it.

## Lower third

Put a semi-transparent bar under the words so a busy frame stays readable. `ColorClip` takes an RGB tuple, not a hex string.

```python
from moviepy import ColorClip, ImageClip, VideoFileClip, CompositeVideoClip

talking = VideoFileClip("outputs/speaker.mp4")
width, height = talking.size
bar = (
    ColorClip((width, 140), color=(20, 24, 38))
    .with_duration(talking.duration)
    .with_opacity(0.75)
    .with_position(("center", height - 160))
)
name = (
    ImageClip(render_text_png("ADA LOPEZ", 64, "#F06859", font_path))
    .with_duration(talking.duration)
    .with_position((80, height - 150))
)
role = (
    ImageClip(render_text_png("Harbor pilot", 36, "#FFFFFF", font_path))
    .with_duration(talking.duration)
    .with_position((80, height - 80))
)
CompositeVideoClip([talking, bar, name, role], size=talking.size).write_videofile(
    "outputs/speaker-named.mp4",
    fps=30,
    codec="libx264",
    audio_codec="aac",
)
```

## Contrast plate

When the whole frame is too busy for a title, put a translucent plate between the picture and the words:

```python
plate = (
    ColorClip(picture.size, color=(20, 24, 38))
    .with_duration(picture.duration)
    .with_opacity(0.55)
)
CompositeVideoClip([picture, plate, title], size=picture.size)
```

Order is picture, plate, text. A plate above the text hides the words.
