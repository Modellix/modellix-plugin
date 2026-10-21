# Platforms

Use this file when the user names a network or a placement. Record the aspect in the brief. Pixel sizes below are working assumptions gathered from public size guides. When a docs or web lookup is available, check the platform's current help page before treating a pixel size as fact. If you cannot check, keep the aspect ratio and say the exact pixels are unverified.

This skill covers content cards, covers, and carousels. Profile photos, personal banners, and paid-ad specs are out of scope.

## Ratio families

| Aspect | Working pixels | Placements |
| --- | --- | --- |
| 3:4 | 1080×1440 | Xiaohongshu cover. Threads post (often prepared at 1440×1920). Instagram, TikTok, and YouTube Shorts profile grids crop the center of a taller frame to about 3:4. |
| 4:5 | 1080×1350 | Instagram feed portrait. LinkedIn and Facebook portrait posts. |
| 1:1 | 1080×1080 | Instagram square, Xiaohongshu square note, WeChat Official Account secondary cover, Weibo multi-image cell, LinkedIn square. |
| 16:9 | 1280×720 | YouTube thumbnail. Also a Bilibili cover and an X post image (X is often prepared at 1600×900). |
| 1.91:1 | 1200×630 | LinkedIn feed image (often 1200×627), Facebook feed image, X link card, Open Graph preview used by Slack and Discord. |
| ~2.35:1 | 900×383 | WeChat Official Account headline cover. Pair it with a separately composed 1:1 card. |
| 9:16 | 1080×1920 | Instagram and Facebook Stories and Reels, TikTok, Douyin, YouTube Shorts, Snapchat, WhatsApp Status. |
| 2:3 | 1000×1500 | Pinterest Pin. |

## How a placement is chosen

- Xiaohongshu: the first image sets the ratio for the note. Prefer 3:4 for a cover in the discovery feed. A 4:3 landscape cover occupies less of that feed.
- WeChat Official Account: compose the headline cover and the square secondary cover as two images. Do not crop the wide cover down to a square.
- Weibo: a single image can keep its ratio. A multi-image grid displays cells as squares, so keep the subject near the center.
- X: the timeline shows a single image across roughly 2:1 to 3:4. A link card uses 1.91:1. Bluesky follows the same post and header habits as X; use 16:9 or 1:1 for a Bluesky post unless the user names another ratio.
- Instagram: 4:5 fills the feed. The profile grid crops toward the center at about 3:4, so keep the claim inside that center band. Carousel frames follow the first image's ratio.
- YouTube: a thumbnail is 16:9. Leave the lower-right corner clear for the duration badge. A Shorts cover is 9:16, and the channel grid shows its center.
- TikTok and Douyin: the full frame is 9:16. The profile grid shows the center at about 3:4. Keep the claim inside that center band.
- LinkedIn: a standard post image is 1.91:1. An article cover is 16:9. Square and 4:5 are acceptable when the user asks for a portrait.
- Facebook: a feed image is 1.91:1, with 1:1 and 4:5 also accepted. Stories and Reels are 9:16.
- Pinterest: a standard pin is 2:3.
- Reddit link previews use about 1.91:1.
- Telegram post images are flexible. Use the ratio of the nearest family the user named, or 1:1 when they did not.

## Safe areas

Interface chrome covers type that sits on the edge.

- 9:16 stories, reels, and short-video covers: keep words in the middle. The top band holds the account and progress, the bottom band holds the caption, and the right edge holds actions.
- YouTube thumbnail: keep words out of the lower-right duration badge.
- Xiaohongshu 3:4: keep the last line of the claim above the bottom of the discovery thumbnail.
- Instagram grid: the saved thumbnail crops a 4:5 or 9:16 frame toward a center 3:4. Put the claim in that center.
- WeChat headline: the wide cover is a thin band. Use one short line, not a paragraph.

## One placement, one prompt

A set that ships to two networks gets two prompts. Changing only the pixel size of the same composition is not enough when the aspect changes. Rewrite the crop, the line breaks, and the safe area for the second placement.
