# Choosing the set

Recommend one preset, or one type, one style, and an optional palette. Give the pick a one-line reason from the article. A choice the user already named wins.

Compatibility is a recommendation. If the user asks for a weaker pairing, use it and say so. Do not refuse the combination.

## Content signals

| Signals in the article | Recommendation |
| --- | --- |
| No strong signal, a general explainer, onboarding | preset `hand-drawn-edu` |
| A how-to, a workflow, steps | preset `hand-drawn-edu-flow` |
| API, metrics, a technical deep dive | preset `tech-explainer` |
| Architecture, a system, a model of parts | preset `system-design` |
| A setup guide that should look like flat vector steps | preset `tutorial` |
| A versus, a review, two or more options | preset `versus` |
| A personal essay, a journey, a reflection | preset `storytelling` |
| History, milestones, an evolution | preset `history` |
| A manifesto, a before/after mindset, a professional note | preset `ink-notes-compare` |
| A paper, a lab result, a scientific explanation | preset `science-paper` |

If two rows match, choose the one that matches the article's job, and say so.

`mixed` is for an article whose sections need different types, such as a scene beside a flowchart. Recommend it only when one type would hide a section. Style, palette, and aspect stay shared.

## Density

| Density | Count |
| --- | --- |
| `minimal` | 1–2, on the sections that carry the article |
| `balanced` | 3–5 |
| `per-section` | one picture after each major section, and at most 6 |

`per-section` is the usual recommendation. Do not raise the count to illustrate every paragraph. Shorten the list instead.

Go past six only when the user names a higher count. State the count in the brief. Each illustration is a separate generation later.

## Aspect and language

Aspect defaults to 16:9. Offer 1:1 for a square embed and 4:3 for a taller figure. On-image language follows the article. A Chinese article keeps Chinese labels inside an English prompt.
