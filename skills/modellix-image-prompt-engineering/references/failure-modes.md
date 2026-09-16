# Image Prompt Failure Modes

Use this reference after an image result fails. Diagnose the layer that failed,
change the prompt deliberately, and return a revised handoff. Do not repeat the
same paid request merely to seek random variation.

## Triage order

Check failures in this order:

1. intent and message,
2. composition and hierarchy,
3. subject or identity fidelity,
4. visual-system transfer,
5. text and factual content,
6. unwanted artifacts,
7. batch consistency.

Fix the earliest failed layer first. Surface-level color changes cannot rescue the
wrong concept or hierarchy.

## Generic, polished, and forgettable

**Signal:** The output is attractive but interchangeable with many AI images.

**Likely cause:** The prompt used broad adjectives, conflicting references, or no
specific medium.

**Repair:**

- replace adjective piles with one relevant named system or an explicit visual
  grammar,
- name the medium,
- state the first-read message,
- remove secondary references that average the result.

## Correct style, wrong message

**Signal:** The image resembles the reference but communicates the wrong thing.

**Likely cause:** The prompt started with surface style instead of audience and
purpose.

**Repair:**

- rewrite the intent in one sentence,
- identify what viewers notice first,
- make the visual metaphor support that message,
- keep the style secondary to hierarchy.

## Overcrowded composition

**Signal:** Every idea appears at once; there is no focal point or text-safe area.

**Likely cause:** The prompt rewarded addition and listed too many equal elements.

**Repair:**

- select one focal subject,
- keep at most three or four supporting elements,
- state what must remain empty,
- define foreground/background and scale,
- remove repeated symbols.

## Weak or cropped text

**Signal:** Text is illegible, too small, incomplete, or outside the frame.

**Likely cause:** Too much copy, unclear exact wording, low hierarchy, or missing
safe-area instructions.

**Repair:**

- reduce the copy,
- quote every exact string,
- move the headline earlier in the prompt,
- state the text language,
- reserve a large quiet region,
- request no extra text.

If exact typography is mission-critical, generate the visual without text and
typeset it later rather than fabricating reliability.

## Fabricated data or product facts

**Signal:** The image contains plausible but false figures, specifications,
testimonials, dates, or claims.

**Likely cause:** The brief asked the model to make the layout look complete
without supplying content.

**Repair:**

- remove unsupplied facts,
- insert explicit placeholders,
- provide verified content,
- separate fictional naming exercises from real products and organizations.

## Publication masthead, watermark, or unrelated logo

**Signal:** A style reference appears as a visible publication name, logo,
nameplate, signature, or English filler.

**Likely cause:** The named reference is strongly associated with its masthead or
brand mark.

**Repair:**

1. Remove the risky name and translate it into layout, type, palette, and material
   attributes.
2. Add a narrow exclusion: no masthead, publication name, logo, watermark,
   signature, or unrelated copy.
3. Use a visual reference image for grammar only when the execution path supports
   it, and assign that role explicitly.

## Style drift

**Signal:** The result captures a superficial color palette but not the intended
system.

**Likely cause:** The reference is atmosphere-driven, obscure, or has a native
medium unlike the target.

**Repair:**

- describe structure: grid, line, palette, typography, lighting, texture,
  materials, and density,
- select a reference from the same medium,
- assign a supplied image the role "style only,"
- preserve the subject separately.

## Subject, face, or product drift

**Signal:** Identity, geometry, controls, packaging, or proportions change.

**Likely cause:** The edit prompt described the desired result before stating what
must remain unchanged, or reference roles were ambiguous.

**Repair:**

- lead with preservation requirements,
- assign each reference a single role,
- say "change only" before listing edits,
- remove style instructions that imply structural transformation,
- use a simpler camera angle when hands or geometry remain unstable.

## Hands or anatomy fail

**Signal:** Fingers, limbs, pose, or body overlap is malformed.

**Likely cause:** Complex occlusion, a small subject, or too many simultaneous
actions.

**Repair:**

- simplify the pose,
- increase subject size,
- reduce occlusion,
- move hands away from detailed objects,
- use a crop or viewpoint that does not depend on finger precision.

## Composition ignores the requested aspect

**Signal:** Essential information is cropped or compressed.

**Likely cause:** The content density conflicts with the canvas, or exact platform
safe areas were assumed.

**Repair:**

- verify the platform dimensions and safe area,
- reduce content,
- describe relative placement,
- keep essential elements central,
- state the aspect once, clearly.

## Grid lines and labels appear in a batch

**Signal:** The model draws cell borders, numbers, captions, or registration
marks.

**Likely cause:** The prompt described a literal table or emphasized grid
mechanics.

**Repair:**

- describe an imagined grid,
- prohibit visible lines, borders, labels, and cell numbers,
- use a uniform background,
- ask for generous separation between items.

## Last row is compressed or cells vary

**Signal:** A dense grid squeezes the last row or changes item proportions.

**Likely cause:** Overall canvas ratio does not match the grid and cell ratio, or
the grid is too large.

**Repair:**

- match canvas ratio to columns × cell width by rows × cell height,
- reduce 5×5 or larger grids to 4×4 batches,
- keep one item per cell,
- remove secondary props,
- generate smaller coherent batches when quality matters more than throughput.

## Revision note

When returning a revised brief, include one sentence:

```text
Diagnosis: <failed layer>. Change: <specific prompt decision revised>.
```

This makes the next result comparable and prevents arbitrary prompt growth.
