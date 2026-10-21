# Concatenate local clips

Probe every input before choosing a path. Compare video width, height, frame rate, and pixel format, plus audio presence and sample rate.

Stream copy is valid only when all of those match and either every clip has audio or none of them do. Otherwise normalize, then concatenate.

Ask for an output path when the user did not name one. Pass `-n`. Do not overwrite an input.

## File list

Write a temporary list yourself. One line per clip, in order:

```text
file '/absolute/path/clip-a.mp4'
file '/absolute/path/clip-b.mp4'
```

Escape a single quote inside a path as `'\''`. Delete the list after FFmpeg exits. `-safe 0` is only for this generated list, because absolute paths sit outside the working directory.

## Matching inputs

```bash
ffmpeg -f concat -safe 0 -i "/tmp/modellix-concat.txt" -c copy -n "joined.mp4"
```

If this fails or the duration is short, the streams did not actually match. Delete the partial output if FFmpeg created one, and use the re-encode path. Do not run the same copy command again.

## Inputs that differ

Pick one target from the user's request. When they did not name a frame size or rate, use the first clip's even width and height and a constant frame rate that ffprobe already reported (commonly 24, 25, or 30).

Normalize each clip to its own new file. Letterbox with `pad` when the aspect ratios differ. Do not crop unless the user asked to fill the frame.

```bash
ffmpeg -i "clip-a.mp4" \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p" \
  -c:v libx264 -crf 20 -preset medium \
  -c:a aac -ar 48000 -ac 2 \
  -movflags +faststart \
  -n "clip-a.norm.mp4"
```

A clip with no audio still needs a silent stereo track when the other clips have audio. Pass the probed duration of that clip as `-t` on `anullsrc`. Do not leave a placeholder duration in the command you run.

```bash
ffmpeg -i "silent.mp4" -f lavfi -t <probed-duration> -i anullsrc=channel_layout=stereo:sample_rate=48000 \
  -filter_complex "[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p[v]" \
  -map "[v]" -map 1:a \
  -c:v libx264 -crf 20 -preset medium \
  -c:a aac -ar 48000 -ac 2 \
  -shortest \
  -movflags +faststart \
  -n "silent.norm.mp4"
```

After every normalized file shares the same streams, concatenate the normalized files with the matching-input command (`-c copy`). Remove the normalized intermediates after the joined file is playable, and only those intermediates.

For two to six clips, one `filter_complex` concat is enough and does not need intermediate files. Scale each input first, then concat. `n` is the number of segments. `a=1` when the result has audio, `a=0` when every clip is silent.

```bash
ffmpeg -i "clip-a.mp4" -i "clip-b.mp4" \
  -filter_complex "[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p[v0];[1:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p[v1];[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 20 -preset medium \
  -c:a aac -ar 48000 -ac 2 \
  -movflags +faststart \
  -n "joined.mp4"
```

Use the intermediate-file path when a clip lacks audio or when there are more than six clips. The one-shot filter above assumes every input already has an audio stream.

Confirm the joined duration with ffprobe before deleting temporary files. It should be close to the sum of the input durations.
