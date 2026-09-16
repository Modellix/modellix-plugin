# Batch and Grid Prompting

Use this reference for small coherent sets: icons, character poses, cards, product
variants, or sprite frames. This skill designs the grid prompt only. It does not
generate, crop, remove backgrounds, or promise transparent files.

## Choose grid generation only when it helps

A single grid image is useful when:

- every item shares one visual system,
- the set is small enough to remain legible,
- relative consistency matters more than per-item resolution,
- the user accepts post-processing after generation.

Prefer separate images when:

- each item needs high resolution,
- the set contains long text,
- exact transparent edges are required,
- each image has a different aspect or environment,
- the model or requested schema supports a native batch more reliably.

## Calculate a compatible canvas

The overall aspect should follow the grid and cell shape:

```text
overall width  = columns × cell width
overall height = rows × cell height
```

Examples:

- 4×4 square icons → square canvas
- 4 columns × 3 rows of 2:3 cards → overall ratio 8:9
- 4 columns × 3 rows of 16:9 frames → overall ratio 64:27

If the execution schema cannot express the ideal ratio, reduce the grid or use
separate batches. Do not force dense portrait cells into a square canvas and
assume the model will preserve every row.

## Describe a semantic grid

Ask the model to imagine equal cells without drawing the grid:

```text
Arrange sixteen distinct icons as an imagined 4×4 grid, one centered icon per
equal square cell, with consistent scale and generous empty separation. Use one
uniform background. Do not draw grid lines, borders, registration marks, cell
numbers, labels, captions, or extra objects.
```

Avoid geometry words that may become visible artifacts, such as "baseline,"
"divider," "bounding box," or "anchor marker." Describe placement semantically:
"centered in each equal cell" and "consistent bottom alignment."

## Icon sets

Define:

- the domain and exact item list,
- one shared silhouette language,
- line or fill treatment,
- consistent stroke weight,
- perspective and lighting,
- background strategy,
- one item per cell.

Example prompt:

```text
A coherent set of sixteen AI-tool icons arranged as an imagined 4×4 grid, one
centered icon per equal square cell: chat, search, code, image, video, audio,
translation, document, database, automation, calendar, analytics, security,
cloud, agent, and settings. Swiss pictogram logic, simple black geometric forms
with one cobalt accent, uniform optical weight and scale, flat front view, warm
white background, generous separation. No words, logos, borders, grid lines,
cell numbers, shadows, or extra symbols. Square canvas.
```

## Character sheets

Define whether cells represent different characters, poses, expressions, or
views. Do not mix those dimensions accidentally.

For one character across poses:

- describe identity once,
- list poses in reading order,
- preserve clothing, proportions, and palette,
- keep one full body per cell,
- use a plain background.

For a turnaround, say front, three-quarter, side, and back views explicitly.
Avoid props that cross cell boundaries.

## Card sets

Card grids are more demanding because each cell has an internal layout.

- Keep to 3×3 or 4×4.
- Match the canvas to card proportions.
- Minimize text; use symbols or short titles.
- Preserve one frame system and one title position.
- Do not ask the model to render fake statistics.
- State whether the user needs the grid only as a concept board or intends to
  crop individual cards.

## Sprite sheets

Specify:

- frame count and reading order,
- action timing,
- camera lock,
- character scale,
- consistent ground position without drawing a baseline,
- transparent or uniform chroma background as a request, not a guarantee.

Example:

```text
A twelve-frame 2D side-view run cycle in an imagined 4×3 frame layout, reading
left to right and top to bottom. The same courier character in every frame,
consistent proportions, outfit, scale, side camera, and bottom alignment. Clear
contact, passing, high-point, and recoil phases. Flat animation-cel rendering on
a uniform cyan background. No frame numbers, labels, borders, grid lines,
registration marks, or overlapping frames.
```

## Handoff additions

For a grid brief, add these details to the normal image handoff:

```text
- Grid: <columns>x<rows>, <cell aspect>
- Item order: <reading order and exact list>
- Separation: <background and spacing>
- Post-processing: <grid-only preview | user/host will crop later>
```

Do not claim that the Modellix prompt skill will crop or validate the cells. After
prompt preparation:

- stop if the user asked only for the prompt,
- otherwise pass the brief to `modellix-design`,
- after generation, use tools available in the host only with the user's request
  and with dependencies clearly disclosed.

## Grid readiness check

- The set size and exact item list are known.
- Grid and cell ratios produce a compatible overall canvas.
- One item occupies each cell.
- Style, scale, viewpoint, and background are consistent.
- Visible grids, labels, and helper marks are prohibited.
- Text and fabricated data are minimized.
- The user understands any cropping or transparency post-processing remains a
  separate step.
