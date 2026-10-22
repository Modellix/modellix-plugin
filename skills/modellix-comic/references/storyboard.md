# Storyboard and prompt shape

Plan in this order: one-sentence message, cast lock, page roles, then prompts. The brief is the deliverable. Do not require a `comic/` directory on disk.

## What to keep

Before the panels, decide:

- One sentence the reader should remember.
- The few facts, names, and quotations that must stay. Quote them. Do not upgrade a vague source into a precise date or a statistic.
- What becomes a picture, and what is cut because it does not change the story.

A concept needs a concrete picture:

| Idea | Picture |
| --- | --- |
| A model learning | A ball rolling down a valley until it rests |
| A network of parts | A room of glowing nodes the character walks through |
| A repeated process | A staircase or a loop of doors |
| A proof | Blocks that lock together |
| A misunderstanding | A foggy fork, then one cleared path |
| A breakthrough | A barrier splitting, with the character still in the frame |

## Cast lock

Write the lock once, then paste that same paragraph into the character sheet and every page. Include only characters who appear.

For each character: role, age range, face, hair, build, default costume, and two or three color names. Add one line for how they look when thinking and when they understand.

Age that changes across a biography gets named variants in the lock, such as "youth, school coat" and "later, worn jacket." Use the variant the page needs. Keep the face plan consistent inside a variant.

A historical person gets the era, the role, and the costume, drawn in the confirmed art style. Do not ask for a photographic likeness, a celebrity face, or a real child's portrait. Do not sexualize any character.

## Character sheet

Write this prompt only when more than one page uses the same characters. Omit it for a four-panel strip and for any other single page.

The sheet shows, on a plain background:

- Front view and three-quarter view of each recurring character.
- A short row of expressions: neutral, thinking, and the feeling the story needs.
- The costume and color names from the lock.

If the text level is `bubbles`, the only words on the sheet are the character names, quoted from the cast. If the text level is `silent`, the sheet has no words. The prompt still says who stands where.

Tell `modellix-design` to generate this image first and pass the saved file as a reference on every later page, including the cover when the cover shows those characters.

## Page prompt

One prompt is one page. Number the pages. Give each page a role in a short scene sentence.

Include, in this order:

1. Comic page, confirmed art, tone, layout, and aspect.
2. Panel count, panel sizes, and reading order.
3. For each panel: who does what, where, and what the camera sees. Name the cast with the lock's identifying features.
4. The cast-lock paragraph, unchanged.
5. Text instruction. For `bubbles`, quote the exact line, name the speaker, and say it sits in a bubble or a caption box. Tell the model to copy those words and not add a title, a logo, a watermark, or another claim. For `silent`, say the image contains no letters, numbers, or captions.
6. Consistency line: same faces, hair, costumes, and colors as the character sheet.

The cover, when there is one, is page 0. It shows the title only when the text level is `bubbles`, quoted exactly. A `silent` cover has no title lettering; the title stays in the brief.

Do not put a second explanation under the page. The prompt is the page.

## Text

Keep a bubble to one short sentence. A caption is shorter than a bubble. If a page needs more words than that, cut the copy or move the page to `silent` and list the lines beside it in the brief.

Those listed lines stay in the brief. This skill does not burn them onto the image afterward.

When lettering comes back wrong, shorten the quote or drop the words, then hand the revised prompt to `modellix-design`. Do not cover the bitmap with new type.
