# Prompt shape

The deliverable is one prompt for one flat raster cover. Say the aspect as a ratio. Omit pixel sizes.

## Words

Quote the exact title. For title-subtitle, quote one short subtitle taken from the source. For text-rich, quote at most two extra labels, each a few words. For none, say the image contains no text.

Tell the model to copy those words and not add captions, logos, watermarks, footnotes, or a second headline. Say which line is largest.

## Style in sentences

Do not leave the prompt as a list of dimension names. Translate each confirmed choice:

- Type: where the focal object sits, and how much of the frame is empty.
- Palette: ground, main color, and accent, in color words.
- Rendering: line, fill, and texture.
- Mood: low, medium, or high contrast.
- Font character: the letterforms, not a brand name.

The metaphor comes from the article. One object. Name it.

## References

When the user supplied images, add a short section per file:

- direct: match the supplied picture's subject and layout, and say which parts are required.
- style: match line, texture, and composition. Do not copy its words.
- palette: match its colors. Do not copy its subject.

Describe concrete parts: a bottom band, a woven line pattern, hair color, a logo built from three strokes. "Clean style" is not a description. Tell `modellix-design` the file path. Do not invent an upload flag.

## After a miss

Write a new prompt that repeats the quoted title and names the miss: extra words, a photographic face, a second metaphor, or a crowded frame. Hand that prompt to `modellix-design`. Do not paint corrected type onto the bitmap.
