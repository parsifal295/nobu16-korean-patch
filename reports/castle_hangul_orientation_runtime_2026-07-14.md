# Direct Hangul Castle-Name Runtime Result — 2026-07-14

## Result

`castle_name_horizontal=false`

The direct-Hangul hypothesis failed. On the live strategic map, message-table ID `9168`
was changed from `小田原` to `오다성` using only offline SC resource replacements.
The label rendered successfully, but each Hangul syllable was stacked vertically in the
same non-English castle-label layout used for Chinese text.

## Test boundary

- Executable modification: none
- Process-memory access or patching: none
- DLL injection, hook, or proxy DLL: none
- Registry modification by the patch: none
- Files changed for the probe:
  - `MSG_PK/SC/msgdata.bin`
  - `RES_SC/res_lang.bin`
- Test ID: `9168`
- Test text: `오다성`

## Post-test restoration

The game was closed normally and the probe harness restored both files. Final installed hashes:

- `MSG_PK/SC/msgdata.bin`:
  `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- `RES_SC/res_lang.bin`:
  `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

The temporary in-game screen-edge scrolling option was also returned from `High` to its
original `Disabled` value before exit.

## Consequence

Direct Korean strings cannot solve strategic-map orientation on the stock SC route.
The next permitted file-only experiment is the single-wide-glyph proxy candidate: encode an
entire horizontal Korean castle name into one glyph so the vertical renderer receives only one
logical character. This remains a workaround and must pass live-map and cross-screen QA.
