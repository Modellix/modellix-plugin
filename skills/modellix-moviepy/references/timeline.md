# Timeline

Use this when more than one clip, or a voiceover, has to land on purpose. A single title on one clip stays in `references/text-overlay.md`.

Run `scripts/check_moviepy.py --json` first. Continue only when `ok` is true.

## Measure, then place

Open every picture and sound file and read `.duration` before choosing `with_start`. Write those durations down. Place the next scene after the previous scene's real duration plus the gap the user asked for. Do not invent timestamps and then stretch the clips to match.

```python
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip, afx

opening = VideoFileClip("outputs/opening.mp4").without_audio()
dock = VideoFileClip("outputs/dock.mp4").without_audio()
voice_opening = AudioFileClip("outputs/opening.mp3")
voice_dock = AudioFileClip("outputs/dock.mp3")

# opening lasts voice_opening.duration; dock starts after it, plus a short gap.
dock_start = voice_opening.duration + 0.3
opening = opening.with_duration(voice_opening.duration).with_start(0)
dock = dock.with_duration(voice_dock.duration).with_start(dock_start)
voice_opening = voice_opening.with_start(0)
voice_dock = voice_dock.with_start(dock_start)
```

`.without_audio()` on the pictures keeps their original sound from playing under the voiceover. Skip it only when the user wants that source audio.

## Titles on the same clock

A title uses the same `with_start` and `with_duration` as the scene it belongs to. Build the PNG with the helper in `references/text-overlay.md`.

```python
title = (
    ImageClip(render_text_png("NORTH DOCK", 72, "#FFFFFF", font_path))
    .with_start(0.4)
    .with_duration(1.6)
    .with_position(("center", 880))
)
```

## Ducked music

Music sits under the voice, quieter, for the whole spot.

```python
music = (
    AudioFileClip("outputs/bed.mp3")
    .with_effects([afx.MultiplyVolume(0.22)])
    .with_start(0)
)
audio = CompositeAudioClip([music, voice_opening, voice_dock])
```

If `afx.MultiplyVolume` is missing in the installed moviepy 2.x, use that install's audio volume effect class with `with_effects`. Do not call moviepy 1.x methods such as `volumex` or `set_start`.

## One composite

Set `size` to the frame you actually want. Set the audio on the composite, then write a new file.

```python
spot = CompositeVideoClip(
    [opening, dock, title],
    size=opening.size,
).with_audio(audio)
spot.write_videofile(
    "outputs/spot.mp4",
    fps=30,
    codec="libx264",
    audio_codec="aac",
)
```

Stop if `outputs/spot.mp4` exists or is one of the inputs.

## Leave these jobs to FFmpeg

- Joining finished clips that need no new layers.
- Trimming, scaling, compressing, or extracting audio from one file.
- Burning an SRT or other subtitle file across the whole timeline.

Those belong to `modellix-ffmpeg`. Come back here only when a layer of text or a timed stack still has to be built.
