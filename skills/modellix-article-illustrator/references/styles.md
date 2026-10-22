# Styles and palettes

Describe the confirmed style in ordinary visual language. Do not leave the prompt as the style's name alone.

## Styles

| Style | What it looks like |
| --- | --- |
| `sketch-notes` | Warm cream paper, black hand-drawn lines with a slight wobble, two to six rounded pastel blocks, short keyword labels, a few small doodles. Airy. Not realistic. |
| `vector-illustration` | Flat vector shapes, bold geometry, clear icons, even light, high readability. |
| `notion` | Thin hand-drawn lines, rounded boxes, soft icons, a neutral ground, little decoration. |
| `blueprint` | Pale blue or white ground, fine schematic lines, a light grid, zoned boxes, labels that look technical. |
| `editorial` | Magazine hierarchy, one strong accent, numbers or charts as the focus, generous margins. |
| `warm` | Golden light, soft gradients, a lived place, simplified figures. |
| `watercolor` | Soft edges, a little color bleed, one quiet scene, no hard infographic boxes. |
| `screen-print` | Two to five flat inks, halftone, bold silhouettes, poster contrast. Conceptual, not literal. |
| `ink-notes` | Black ink on white, a lot of empty paper, one sparse accent, short hand-lettered labels. |
| `scientific` | Thin precise lines, labeled parts, muted academic colors, no decoration. |
| `elegant` | Restrained colors, fine dividers, balanced space, letterforms with a serif character. Do not name a commercial typeface. |

`sketch-notes` is the default when the article has no stronger signal.

## Type and style

| Type | Strong styles | Weaker styles |
| --- | --- | --- |
| `infographic` | sketch-notes, vector-illustration, notion, blueprint, editorial, scientific | warm, watercolor, screen-print |
| `scene` | warm, watercolor, screen-print | sketch-notes, blueprint, scientific |
| `flowchart` | sketch-notes, vector-illustration, notion, blueprint | watercolor, screen-print |
| `comparison` | sketch-notes, vector-illustration, notion, ink-notes, elegant | watercolor |
| `framework` | blueprint, vector-illustration, sketch-notes, ink-notes, scientific | watercolor, screen-print |
| `timeline` | elegant, sketch-notes, editorial, warm | blueprint, scientific |

## What each type shows

| Type | Composition |
| --- | --- |
| `infographic` | A title area, two to six blocks, one takeaway line. Facts sit in the blocks. |
| `scene` | One place and one action. No diagram boxes unless the user asked for them. |
| `flowchart` | Ordered steps, arrows in one direction, one icon per step. |
| `comparison` | A clear split. One side per option. Shared labels line up. |
| `framework` | Nodes and links. Hierarchy is visible. Empty space separates levels. |
| `timeline` | A single path with dated or ordered marks. The path is the structure. |

## Palettes

A palette replaces the style's default colors. It does not replace the line, texture, or layout. Omit the palette when the style's own colors are enough.

| Palette | Colors |
| --- | --- |
| `macaron` | Light blue, mint, lavender, and peach blocks on warm cream. |
| `warm` | Orange, terracotta, and gold on soft peach. No cool colors. |
| `neon` | Pink, cyan, and yellow on dark purple. |
| `mono-ink` | Black ink on white, with one sparse accent: coral, muted teal, or dusty lavender. |

`macaron` is the usual palette for `sketch-notes`. `mono-ink` is the usual palette for `ink-notes`.
