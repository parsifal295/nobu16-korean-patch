# NOBU16 Korean font suitability review (2026-07-13)

## Decision

Use a two-family Noto CJK KR profile for the production patch:

| G1N role | Recommended face | Raster target |
|---|---|---:|
| 32px cell / small menu | Noto Sans KR Bold | 22px, grayscale |
| 40px cell / ordinary UI and names | Noto Sans KR Medium | 27px, grayscale |
| 48px cell / ordinary large UI | Noto Sans KR Medium or SemiBold | 33px, grayscale |
| 48px decorative serif table | Noto Serif KR Bold | 33px, grayscale |

Keep the game's full-width layout advances (`23 / 29 / 35px`) separate from
the slightly smaller raster sizes (`22 / 27 / 33px`).  This preserves one to
two pixels of breathing room without changing the English horizontal layout.

The small main-menu proof was run with Noto Sans KR Bold at 94% raster scale.
It is the recommended default for the current demo.

## Real game comparison

The following image is assembled from actual game captures, not a desktop font
preview:

`KR_PATCH_WORK/tmp/font_review_ingame_compare.png`

SHA-256:

`42FC3B9748C3B37F74E5AF1C77D753620AE90A7C9F427C11302FF4D10C826446`

Observed ranking:

1. **Noto Sans KR Bold, grayscale, 94%**: best balance of historical-neutral
   tone, small-cell clarity, coverage, and redistribution simplicity.
2. **Pretendard JP SemiBold, grayscale, 110%**: excellent small UI clarity,
   but visibly more modern and subject to several Reserved Font Names.
3. **Noto Serif KR Bold, grayscale, 94%**: best period tone, but too delicate
   for the 32px cell.  Reserve it for the existing 48px decorative table.
4. **Malgun Gothic Regular**: readable but too heavy, visually Windows-like,
   tight against the cell, and unsuitable for public redistribution.

## Rasterizer defect found during review

The external G1N editor hard-codes ClearType rendering and its 4bpp converter
keeps only the red channel.  With Noto this discarded entire hinted strokes,
which looked like severe vertical clipping in the game.  It was not a bad Noto
outline or a renderer-codepoint failure.

`tools/build_hangul_phrase_probe.ps1` now supports:

```powershell
-Rasterizer Grayscale
```

That path renders white text on black with `AntiAliasGridFit`, then stores the
result as the single 4-bit coverage channel expected by G1N.  The successful
Noto captures were built with this path.  ClearType must not be used for the
production atlas.

## Licensing and packaging

The official Noto CJK Sans and Serif packages are under SIL OFL 1.1.  The
license permits modification, embedding, bundling, and redistribution when
the copyright and license are retained and the font component remains under
the OFL.  A G1N atlas is conservatively treated as Modified Font Software.

Production packaging should include:

```text
THIRD_PARTY_FONTS/
  OFL-1.1.txt
  UPSTREAM_COPYRIGHT.txt
  SOURCE_URL.txt
  FONTLOG.txt
```

Use a neutral derived resource name such as `N16KR UI` and `N16KR Serif` even
though the current official Noto CJK license files do not declare a Reserved
Font Name.  Record upstream version and SHA-256 and generate the shipping G1N
from a pinned official release rather than a user's Windows font installation.

Official sources:

- https://github.com/notofonts/noto-cjk
- https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE
- https://github.com/notofonts/noto-cjk/blob/main/Serif/LICENSE
- https://github.com/orioncactus/pretendard/blob/main/LICENSE

Detailed licensing matrix:

`KR_PATCH_WORK/reports/korean_font_redistribution_review_2026-07-13.md`

## Tested artifacts

Recommended small-menu font asset:

`KR_PATCH_WORK/tmp/font_review_noto_sans_bold_gray94/res_lang.phrase.bin`

SHA-256:

`1BC5E14669493D2601157703D84673B890BA650289AEAE7F0DA8BF38B4D90507`

Successful full-window capture:

`KR_PATCH_WORK/tmp/runtime_latin_entry7_EN_FontNotoSansBoldGray94_frames/entry7_EN_FontNotoSansBoldGray94_final.png`

Every automated run restored the installed English resources to these hashes:

- `MSG_PK/EN/msgui.bin`: `FB9C4698989319AE9A9BF138F6DC963DC106124FC60D19308D0BF1AD35BE3965`
- `RES_EN/res_lang.bin`: `CA05180FD6EE9F2877649716B34B61F056B222BC893711E68B39C500E94E8F80`

## Remaining font QA

Before generating the complete atlas:

1. Build the actual translated-character corpus, including punctuation and
   officer names.
2. Apply the Noto profile per G1N table instead of one font to every table.
3. Test dense 받침 syllables, counters, numerals, brackets, and mixed Latin.
4. Capture dialogue, tooltips, officer lists, map labels, and battle UI at the
   original game resolution.
5. Check long names for widget clipping separately from glyph rendering.
