# Prompt shape

The deliverable is one prompt for one flat raster image. The image model has to place the sections and paint the words. A later overlay, SVG, or HTML page is a different artifact.

## Facts

Copy numbers, names, and quotations from the source into quotation marks. Say which line is the title and which lines are labels. Tell the model to copy the quoted text and not add captions, logos, watermarks, footnotes, or extra statistics.

If the source says "240 signups" and does not state a rate, the prompt does not display a percentage. Derived figures belong in the prompt only when the user asks for them and the arithmetic is shown in the brief.

## Aspect

Use the ratio the user confirmed.

- landscape: 16:9
- portrait: 9:16
- square: 1:1
- any other ratio the user names, written as W:H

Put the ratio in the prompt in words and as a fraction. Pixel sizes are optional. If a pixel size was not checked, omit it.

## One image

Describe the structure so the model knows where each section sits: left and right for a comparison, top to bottom for a sequence, center and spokes for a hub. Repeat the exact label beside the section it belongs to.

Keep the text short enough to read. A section that needs a paragraph should become a shorter label, with the nuance left out of the image.

## After a miss

When a generated image misspells a label or invents a number, write a new prompt that quotes the correct text again and names the mistake to avoid. Hand that prompt to `modellix-design`. Do not cover the bitmap with new type from this skill.
