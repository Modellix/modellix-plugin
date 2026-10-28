# Choosing the rendering

Recommend one rendering and the aspect. Give the pick a one-line reason from the character. A choice the user already named wins.

| Signals | Rendering |
| --- | --- |
| No strong signal, a modern talent board, a studio portrait | `studio` |
| The user asked for a drawing, a painted board, or a comic-adjacent look that is not itself a comic | `illustrated` |
| A named era, historical costume, or period wardrobe | `period` |

`studio` uses an ivory ground, even soft light, and one layout example. `illustrated` keeps the three zones and uses the drawing style the user named. `period` keeps the three zones and the costume of the era the user named. Neither `illustrated` nor `period` uses the photographic examples.

If the user named no costume, recommend one plain outfit and say which layout example it matches:

| Recommended outfit | Layout example |
| --- | --- |
| Black suit, black shirt | `studio-board-suit.webp` |
| Cream knit top and wide trousers | `studio-board-knit.webp` |
| Light gray shirt and off-white trousers | `studio-board-shirt.webp` |
| Black blazer, white shirt, black trousers | `studio-board-blazer.webp` |

Do not recommend an outfit that contradicts a costume the user already named.

Aspect defaults to 16:9. Offer 3:2 when the user wants a slightly taller board. Do not recommend a portrait aspect. The three zones need width.

One board per character. Recommend at most four boards unless the user names a higher count.
