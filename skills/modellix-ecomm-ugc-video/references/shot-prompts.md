# Shot prompts

The deliverable is one prompt per shot. Each prompt is one clip, one action, and one spoken line. A single prompt that stacks a hook, a try-on, and a close loses the person and the product between cuts. Separate shots keep the cast lock repeated so `modellix-design` can generate them one at a time.

When the user explicitly asks for one clip, write one prompt that covers the hook and one proof. Say in the brief that the video is a single shot. Do not compress a six-beat film into that paragraph.

## Cast lock

Write the cast lock in ordinary words from what the user said: age range, hair, clothes, room or street, and the product's silhouette, color, and material. Paste that same paragraph into every shot prompt.

If the user did not describe a person, ask once who is on camera. Do not borrow a face, a celebrity, or a default creator.

A product still replaces invented packaging. The prompt says to match the still's color and shape, and to keep packaging text unreadable or out of frame.

## Prompt contents

Every shot prompt includes:

- Vertical phone video, 9:16, unless the user named another aspect.
- A duration of about four seconds for a 15-second, four-shot video, or about five seconds for a 30-second, six-shot video.
- The cast lock, copied, not summarized into a pronoun.
- The light and place for this beat: window light in a lived-in room, a sidewalk, a gym, a car, or a porch.
- One camera: a selfie, a phone on a stand left in frame, or a hands close-up.
- One action.
- The spoken line in quotation marks, introduced as the words the person says. A maker-story line is voiceover over the hands.
- The product, described from the user's facts.
- A closing instruction: do not render captions, subtitles, logos, watermarks, or writing on the product.

`modellix-design` owns whether the chosen model's schema carries speech, and which body field receives a reference image. This skill names the still and the spoken line. It does not pick the field.

## Duration

| Length | Shots | Each shot |
| --- | --- | --- |
| 15 seconds | 4 | about 4 seconds |
| 30 seconds | 6 | about 5 seconds |
| listicle | hook + one per variant + close | about 4 seconds; length is the sum |

A maker-story the user asked to run longer can add process shots. The brief states that length. Do not stretch a 15-second ad into a 45-second film on your own.

## Captions stay out of the prompt

The shot prompt tells the model to leave writing out of the frame. The brief's caption list quotes the exact on-screen lines, in order, in the audience language. After `modellix-design` downloads the files, `modellix-ffmpeg` burns that list. A misspelled word inside a generated frame is fixed by regenerating the shot without those words, not by asking the video model to spell a sentence.

## After a miss

Change only the shot that failed. Repeat the cast lock and the "no writing in frame" line. Hand that shot's new prompt to `modellix-design`. Leave the shots that already match the brief unchanged in the new brief so the next pass is easy to see.
