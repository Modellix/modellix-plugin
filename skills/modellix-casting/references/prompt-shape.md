# Prompt shape

The deliverable is one prompt for one board. Repeat the identity lock in the hero, the grid, and the turnaround. Say the aspect as a ratio.

## Order inside the prompt

1. The board: ivory ground for `studio`, two rounded cards, no text.
2. Identity lock: age range, face, hair, build, costume, and two or three color names. Say this person is the only person in the image.
3. Center: the chest-up portrait, gaze slightly off the lens, largest element.
4. Left card: nine head-and-shoulders cells, same distance, different expressions and small head turns.
5. Right card: full-body front, three-quarter, and back, feet visible, neutral stance.
6. Constraint: copy no face, hair, age, build, or costume from a layout example. Add no letters, numbers, logos, watermarks, or extra people.

For `illustrated` or `period`, replace the ivory studio sentence with the confirmed drawing style or era, and do not mention the photographic examples.

## References

- `direct`: the user's picture of the person. Match that face and body. The confirmed costume still wins if the user asked for different clothes.
- `layout`: one file under `references/examples/`. Match the board, the cards, and the studio light. Do not match the person in that file.

Name both paths when both are used. Tell `modellix-design` the paths. Do not invent an upload flag.

## Extra views

Add a separate prompt only for a view the user named. That prompt repeats the identity lock, shows one full-body view, and contains no text. Keep the board prompt as well.

## After a miss

Write a new prompt that repeats the identity lock and names the miss: a second face, a copied example, a missing back view, or letters in the grid. Hand that prompt to `modellix-design`. Do not paint corrections onto the bitmap.
