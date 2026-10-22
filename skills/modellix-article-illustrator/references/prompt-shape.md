# Prompt shape

The deliverable is one prompt per illustration. Say the aspect as a ratio. Omit pixel sizes. Repeat the same style lock in every prompt.

## Order inside the prompt

1. Type and composition: where the blocks, path, split, or scene sit, and how much of the frame is empty.
2. The idea: one sentence for what the picture shows. A metaphor names the underlying concept, not the literal object, unless the article is about that object.
3. Exact labels: only words copied from the article. Say which line is largest. If the illustration needs no words, say the image contains no text.
4. Style lock: line, fill, ground, accent, and texture, in color words. A named palette replaces the style's default colors and keeps the line and texture.
5. Figure lock, when this illustration includes a recurring figure. Use the same sentence as the other prompts.
6. Constraint: copy the quoted labels and do not add captions, logos, watermarks, footnotes, or claims the article does not contain.

## Labels

Quote numbers, terms, and short quotations the picture must show. Do not paraphrase a statistic into a new number. Do not invent a percentage, a date, or a citation.

A Chinese article keeps Chinese labels inside an English prompt. Do not translate a label the reader must see in the original language.

## References

When the user supplied images, add a short section per file:

- direct: match the supplied picture's subject and layout, and say which parts are required.
- style: match line, texture, and composition. Do not copy its words.
- palette: match its colors. Do not copy its subject.

Describe concrete parts: a cream ground, a wobble in the ink, a three-stroke mark. "Clean style" is not a description. Tell `modellix-design` the file path. Do not invent an upload flag.

## After a miss

Write a new prompt that repeats the style lock and names the miss: extra words, a literal metaphor, an invented number, or a figure that drifted. Hand that prompt to `modellix-design`. Do not paint corrected type onto the bitmap.
