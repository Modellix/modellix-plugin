# Choosing the style

Recommend one preset, or one art style, one tone, and one layout. Give the pick a one-line reason from the source. A choice the user already named wins.

Compatibility is a recommendation. If the user asks for a weaker pairing, use it and say so. Do not refuse the combination.

## Content signals

| Signals in the source | Recommendation |
| --- | --- |
| Tutorial, how-to, programming, a technical explanation | preset `ohmsha` |
| Psychology, self-help, a business idea told as a story, personal growth | preset `concept-story` |
| A fable, a parable, a one-beat insight, 四格 | preset `four-panel` |
| Martial arts, wuxia, xianxia, when the user asked for that comic | preset `wuxia` |
| Romance or school-life feelings, when the user asked for that comic | preset `shoujo` |
| Biography, a balanced life story | `ligne-claire` + `neutral` + `mixed` |
| Pre-1950 history, a classical subject | `realistic` + `vintage` + `cinematic` |
| A personal story or a mentor relationship, not a tutorial | `ligne-claire` + `warm` + `standard` |
| Food, craft, or a lifestyle process | `realistic` + `neutral` + `cinematic` |
| Conflict or a breakthrough inside another recommendation | keep the art, shift tone to `dramatic` and layout to `splash` for that page only |

If two rows match, choose the one that matches the comic's job, and say so.

## Preset bases

Load `presets.md` when a preset is recommended. The base is the default art, tone, and layout. The preset's special rules still apply if the user changes one base dimension.

| Preset | Base |
| --- | --- |
| `ohmsha` | `manga` + `neutral` + `webtoon` |
| `concept-story` | `manga` + `warm` + `standard` |
| `four-panel` | `minimalist` + `neutral` + `four-panel` |
| `wuxia` | `ink-brush` + `action` + `splash` |
| `shoujo` | `manga` + `romantic` + `standard` |

## Art and tone

| Art | Strong tones | Weaker tones |
| --- | --- | --- |
| `ligne-claire` | neutral, warm | romantic, action |
| `manga` | neutral, romantic, energetic, action | vintage |
| `realistic` | neutral, warm, dramatic, vintage | romantic, energetic |
| `ink-brush` | neutral, dramatic, action, vintage | romantic, energetic |
| `chalk` | neutral, warm, energetic | dramatic, action, romantic |
| `minimalist` | neutral | dramatic, vintage, romantic, action |

## Pages, aspect, and text

| Form | Pages | Aspect |
| --- | --- | --- |
| `four-panel` | 1, and no character sheet | 3:4 |
| `webtoon`, including `ohmsha` | a cover plus at most six story pages, unless the user named a count | 9:16 |
| Any other multi-page comic | a cover plus at most six story pages, unless the user named a count | 3:4 |
| A single scene the user already limited to one page | 1, and no character sheet | the aspect they named, otherwise 3:4 |

Each page is a separate image. Do not raise the recommendation to fill a long source. Shorten the story instead.

Text level:

| Signals | Text level |
| --- | --- |
| The user asked for no words, or the page should be read without lettering | `silent` |
| A story, tutorial, or biography that needs speech or captions | `bubbles` |

`bubbles` is the usual recommendation. On-image language follows the source.
