# Image Prompt Playbook

Use this playbook when a request needs more than a direct, already-complete
prompt. It turns a vague image idea into one prompt with deliberate visual
decisions.

## 1. Determine the mode

Choose the lightest mode that resolves the uncertainty.

### Explore

Use when the user knows the topic but not the visual direction.

Propose three directions that differ in concept, not merely color:

1. a reference or visual grammar,
2. why it fits the audience and message,
3. the target medium and composition,
4. the cliché or failure risk.

If the user delegated creative control, select one direction and continue. Ask for
a choice only when the directions lead to materially different products.

### Hybrid

Use when the user knows the message and medium but not every design decision.
Lock the subject, hierarchy, primary reference, aspect, exact copy, and likely
failure constraints. Leave secondary scene details to the image model.

### Execute

Use when the user supplied brand rules, layout, copy, references, or an approved
direction. Preserve those decisions. Do not "improve" the brief by adding an
unrequested visual system.

## 2. Define intent

Answer these questions before choosing style:

- Who is the audience?
- Where will the image appear?
- What must viewers notice first?
- What should they understand, feel, or do next?
- Is the deliverable one image, an edit, or a coherent set?

Infer low-risk details from context. Ask only about missing information that
changes the result substantially, such as exact copy, required logo, portrait vs
landscape, or whether a reference image must be preserved.

## 3. Fill the three slots

### Subject

Name the actual subject. Prefer known products, objects, places, or supplied
characters over generic categories. Do not add factual specifications unless the
user supplied them or they were verified.

### Visual system

Choose one primary system with relevant, transferable structure:

- a design movement,
- a designer or studio,
- a brand language,
- a photographic or illustration tradition,
- an explicit grammar of grid, palette, line, lighting, texture, and typography.

Named references are compression devices, not decoration. If the reference is
obscure, atmosphere-driven, or mismatched to the medium, explain the visual
grammar directly.

### Medium

Name the actual deliverable: instruction manual, editorial illustration, campaign
poster, product photograph, packaging family, comparison infographic, app
dashboard, icon sheet, character turnaround, or another concrete format.

## 4. Build the composition

Describe the first read before secondary details:

- dominant subject and approximate frame share,
- placement and direction of attention,
- background and depth relationship,
- reserved space for copy or UI,
- crop, viewpoint, and aspect,
- information hierarchy.

Examples:

- "The product occupies the lower-right third; leave the upper-left half quiet for
  the headline."
- "A top-down comparison with two equal columns and one central difference
  marker."
- "One full-bleed portrait with the eyes above the horizontal center; no small
  decorative panels."

Do not specify coordinates unless they are meaningful and verified. Relative
spatial language is usually more portable across image models.

## 5. Handle text

- Quote exact copy.
- Preserve capitalization, punctuation, and official names.
- State the language of descriptive text.
- Prefer one headline and a short support line over paragraphs.
- Use placeholders rather than invented metrics, testimonials, or specifications.
- Ask for no text when the user needs a flexible background or will typeset later.

## 6. Add narrow constraints

Add only constraints that counter a likely failure:

- no extra wording beyond quoted copy,
- no watermark, signature, unrelated logo, or publication masthead,
- preserve a supplied person's identity,
- preserve product geometry and logo placement,
- keep all essential content inside the central safe area,
- avoid a specific visual cliché.

Do not paste a generic negative prompt. It competes with the intended subject.

## 7. Write one natural prompt

The final prompt should read as coherent prose or a compact sequence of sentences
in the audience's language. Do not write fake sections such as `Subject:`,
`Style:`, or `Constraints:`.

Use this order when useful:

```text
[Medium and purpose] featuring [subject]. [Primary visual system and why it
applies]. [Composition and hierarchy]. [Exact copy and language]. [Narrow
constraints]. [Aspect or verified size].
```

This is an ordering aid, not a literal template. Remove anything that does not
change the image.

## High-value prompt patterns

### Concept transfer

Use when the reference and target share a structural medium:

```text
[Reference visual system] applied to a [subject] [medium].
```

### Model contribution

Use when the user wants a new fictional brand or campaign and factual invention
is acceptable:

```text
Create an original brand name and short slogan that express [principle]. Keep them
clearly fictional and explain the naming rationale outside the image.
```

Never use this pattern when the image represents an existing company, product, or
claim.

### Forced subtraction

Use when the brief is overloaded:

```text
Keep only the four elements that carry the most information; remove decorative
elements that repeat the same idea.
```

### Preserve-first editing

Use for I2I:

```text
Preserve [identity/product geometry/logo/camera viewpoint]. Change only
[background/material/lighting/garment/layout]. Use reference 1 for [role] and
reference 2 for [role].
```

### Infographic structure

Start with the relationship:

```text
A [comparison/sequence/hierarchy/flow/cause-and-effect] infographic showing
[verified content], with [primary insight] as the strongest visual hierarchy.
```

### UI decision screen

Start with the user's decision:

```text
A [screen type] for users who need to [decision/action], with [primary action] as
the dominant control and [supporting information] secondary.
```

## Platform dimensions

Platform specifications change. When the user names a platform:

1. verify current official guidance when lookup tools are available,
2. distinguish canvas size from safe area,
3. keep essential text and faces inside the safe area,
4. record whether the value is verified, user-supplied, or unresolved.

Never silently rely on a memorized pixel table. If verification is unavailable,
use a conventional aspect ratio as a proposal and say that exact pixels remain
unverified.

## Readiness check

The brief is ready when:

- the task is classified as T2I or I2I,
- subject, visual system, and medium are specific,
- hierarchy and aspect are clear,
- exact copy and language are explicit,
- reference images have assigned roles,
- facts are verified, supplied, omitted, or marked as placeholders,
- constraints address real risks,
- the prompt contains no fake section headers,
- the next step says either stop or hand off to `modellix-design`.
