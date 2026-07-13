# Third-party inputs

Only redistributable build inputs and source references belong in this repository.
Complete game resources and unlicensed third-party archives are excluded.

## Noto Korean fonts

- Files: `vendor/noto/NotoSansKR-wght.ttf`, `vendor/noto/NotoSerifKR-wght.ttf`
- License: SIL Open Font License 1.1
- Local license copies: `vendor/noto/OFL-NotoSansKR.txt`,
  `vendor/noto/OFL-NotoSerifKR.txt`
- Use: deterministic Korean glyph rasterization for public font recipes

## G1N Font Editor research reference

- Upstream: <https://github.com/lehieugch68/G1N-Font-Editor.git>
- Reviewed revision: `62d5468a5bc12f777e531be8bfd38f391009d0a1`
- License: MIT
- Use: format research reference only; the upstream checkout and build outputs are not
  vendored or required by the patch build.

## Excluded historical reference

The locally obtained `NOBU15_msg_editor_v0.13` archive had no sufficiently clear
redistribution license. It is neither tracked nor required by the current NOBU16
file-only pipeline.
