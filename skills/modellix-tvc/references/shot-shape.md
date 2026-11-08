# Shot shape

The deliverable is one prompt per shot. Each prompt is one clip, one action, and one camera move. A prompt that stacks the open, the use, and the end card loses the product between cuts.

## Order inside the prompt

1. Aspect and duration. Say 16:9 or 9:16, and the seconds for this shot.
2. The product lock, copied, not replaced with "it" or "the item."
3. The person lock, when this shot includes the person. Copy it again.
4. The place and the light, in ordinary visual words.
5. One camera move: a slow push, a lateral move, a static frame, or a close view. One move.
6. One action.
7. Constraint: no speech to camera, no captions, no logos, no watermarks, and no writing on the package.

For `sculpture`, omit the person lock. For a product-only end shot, omit it even when earlier shots had a person.

## References

When the user supplied a product still, add it on every shot that shows the product:

- `direct`: match the still's shape, material, and color. Keep packaging text out of frame or unreadable.

Tell `modellix-design` the path. Do not invent an upload flag.

## Words that stay out of the picture

An end line the user supplied is listed in the brief for `modellix-moviepy`. It is not part of the shot prompt.

A music mood is a short phrase in the brief, such as "sparse, no vocal." It is not part of the shot prompt. Write a separate audio description only when the user asked for a soundtrack, and hand that description to `modellix-design` apart from the pictures.

## After a miss

Change the shot that failed. Repeat the product lock and the line that keeps writing out of the frame. Hand that prompt to `modellix-design`. Leave matching shots unchanged in the new brief.
