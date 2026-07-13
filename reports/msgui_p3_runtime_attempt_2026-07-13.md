# MSGUI P3 runtime attempt — 2026-07-13

## Scope

This was a runtime QA attempt for the file-only P3 candidate:

- 279 translated `MSG_PK/SC/msgui.bin` records
- Font-v3 with 226 generated Hangul glyphs
- no process-memory access, DLL injection, hook, proxy DLL, EXE edit, or registry write

## Preflight and apply

PowerShell parsing of `tools/file_only_sc_mainmenu_test.ps1` passed. Both installed
targets and both verified backups started at the pinned stock hashes.

The development QA apply completed with the expected target hashes:

- `MSG_PK/SC/msgui.bin`: `B3203C89A99840AEC736936268803F685A7F2575E766AFB4C9D6E052383E86E6`
- `RES_SC/res_lang.bin`: `73E3759BF1886E95C769A95EB212F7ED34B7546E9A3DFA1EB49F542A7018E6B7`

The game was launched from `F:\Games\NOBU16` as its working directory. It did
not produce error 9001.

## Runtime observation

The game ran through the Japanese language path, not the Simplified Chinese
path containing the P3 files. Visible menu labels included:

- `初めから`
- `武将編集`
- `追加コンテンツ`
- `鑑賞`
- `設定`
- `ライセンス`

Screenshot evidence:

- `reports/screenshots/msgui_p3_blocked_japanese_path_2026-07-13.png`
- SHA-256: `6DED3ADBAF9CB382F19704320679B90EEE008D64F3D09126336201DF2F513B8B`

Therefore this run cannot be counted as a Korean-glyph or Korean-text pass or
failure: `MSG_PK/SC/msgui.bin` and `RES_SC/res_lang.bin` were not the active
language resources.

No automatic registry or launcher-language change was made. The next runtime
attempt requires the user to select Simplified Chinese (`简体中文`) through the
official launcher.

## Exit and restoration

The game was closed through its own exit confirmation. The P3 candidate was
then restored immediately. Final installed hashes:

- `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

Final running `NOBU16PK` process count: zero.

## QA disposition

- offline apply/hash verification: PASS
- no error 9001 with correct working directory: PASS
- exact stock restoration: PASS
- SC/Korean runtime rendering: NOT TESTED (official launcher was set to Japanese)
- Font-v3 `runtime_verified`: remains `false`
- public release eligibility: remains `false`
