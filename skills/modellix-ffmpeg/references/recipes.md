# Local edit recipes

Run `scripts/check_ffmpeg.py --json` and probe the input before these commands. Quote paths. Pass `-n`. Write a new file, and ask for the output path when the user did not name one.

Even sizes, `yuv420p`, `libx264`, `aac`, and `-movflags +faststart` are the default shape of a re-encoded video.

## Scale and reframe

Fit inside a frame and pad the rest:

```bash
ffmpeg -i "input.mp4" \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -c:v libx264 -crf 20 -preset medium -c:a aac -movflags +faststart \
  -n "framed.mp4"
```

Scale to a width and keep the aspect ratio. `-2` keeps the height even:

```bash
ffmpeg -i "input.mp4" \
  -vf "scale=1280:-2,format=yuv420p" \
  -c:v libx264 -crf 20 -preset medium -c:a aac -movflags +faststart \
  -n "scaled.mp4"
```

Fill a frame by cropping only when the user asked to fill, not to fit:

```bash
ffmpeg -i "input.mp4" \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p" \
  -c:v libx264 -crf 20 -preset medium -c:a aac -movflags +faststart \
  -n "filled.mp4"
```

Odd source dimensions, with no other scale requested:

```bash
ffmpeg -i "input.mp4" \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" \
  -c:v libx264 -crf 20 -preset medium -c:a aac -movflags +faststart \
  -n "even.mp4"
```

## Compress

CRF 18 is a high-quality master. CRF 23 is a normal delivery file. CRF 28 is a small preview. Lower CRF is larger and cleaner. `medium` is the default preset.

```bash
ffmpeg -i "input.mp4" \
  -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  -n "preview.mp4"
```

## Extract or replace audio

```bash
ffmpeg -i "input.mp4" -vn -c:a aac -b:a 192k -n "voice.m4a"
ffmpeg -i "input.mp4" -vn -c:a pcm_s16le -n "voice.wav"
```

Replace the soundtrack with another file and keep the picture. End at the shorter of the two unless the user asked for a different duration:

```bash
ffmpeg -i "picture.mp4" -i "voice.m4a" \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac \
  -shortest \
  -movflags +faststart \
  -n "with-voice.mp4"
```

`-c:v copy` here is safe only because the picture stream is not being cut or scaled. If the container rejects the copied video, re-encode video with `libx264` and `yuv420p` instead of retrying copy.

## Trim

Re-encode. `-ss` is the start, `-t` is the duration to keep, `-to` is the end timestamp.

```bash
ffmpeg -i "input.mp4" -ss 00:00:05 -t 00:00:10 \
  -c:v libx264 -crf 20 -preset medium \
  -c:a aac \
  -movflags +faststart \
  -n "clip.mp4"
```

Do not use `-c copy` for a trim. A seek that misses a keyframe can drop the picture while the audio continues.

## Speed

`setpts` multiplies timestamps, so 2x speed is `0.5*PTS` and half speed is `2.0*PTS`. One `atempo` stage must stay between 0.5 and 2.0. For 4x audio, chain `atempo=2.0,atempo=2.0`.

```bash
ffmpeg -i "input.mp4" \
  -filter_complex "[0:v]setpts=0.5*PTS,format=yuv420p[v];[0:a]atempo=2.0[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 20 -preset medium -c:a aac \
  -movflags +faststart \
  -n "double-speed.mp4"
```

Drop audio only when the user asked for a silent result:

```bash
ffmpeg -i "input.mp4" \
  -filter:v "setpts=0.5*PTS,format=yuv420p" -an \
  -c:v libx264 -crf 20 -preset medium \
  -movflags +faststart \
  -n "double-speed-silent.mp4"
```

## Fade

`st` plus `d` for a fade-out has to come from the probed duration. For a 10 second clip and a 1 second fade-out, `st` is 9. Do not hard-code that number for a different file.

```bash
ffmpeg -i "input.mp4" \
  -vf "fade=t=in:st=0:d=1,fade=t=out:st=9:d=1,format=yuv420p" \
  -c:v libx264 -crf 20 -preset medium -c:a copy \
  -movflags +faststart \
  -n "faded.mp4"
```

Audio fade, leaving the picture untouched:

```bash
ffmpeg -i "input.mp4" \
  -af "afade=t=in:st=0:d=1,afade=t=out:st=9:d=1" \
  -c:v copy -c:a aac \
  -movflags +faststart \
  -n "audio-faded.mp4"
```

## Thumbnail

```bash
ffmpeg -i "input.mp4" -ss 00:00:01 -frames:v 1 -q:v 2 -n "thumbnail.jpg"
```

Pick `-ss` inside the probed duration. One frame is a new image file, not a replacement of the video.
