# NOBU16 Korean main-menu file-only release — final report

Date: 2026-07-13

## Outcome

The canonical main-menu v0.1 release is an offline file patch. It does not
attach to the game, read or write game-process memory, inject a DLL, install a
hook, modify an executable, launch the game, or write the registry.

- public folder: `KR_PATCH_WORK/releases/mainmenu_file_only_v0.1_2026-07-13`
- public ZIP: `KR_PATCH_WORK/releases/mainmenu_file_only_v0.1_2026-07-13.zip`
- ZIP size: 45,138 bytes
- ZIP SHA-256: `2BDA22F979303D10F30F55E5E7FB5AD03D5DCA6C2DAEBC219A44A1AFF7240412`
- release manifest SHA-256: `53D6A589DCD1DE6C8B116C6D87354A7CF057B31005425644981CD3553543A422`
- files: 15
- unpacked size: 212,576 bytes

The ZIP contents and public folder were compared file by file. All 15 relative
paths, sizes, and SHA-256 values matched exactly.

## Runtime result

The v2 font candidate uses larger scratch-canvas rasterization while preserving
the stock SC record advance and cell dimensions. The SC game path booted without
error 9001. These seven labels rendered as nonblank Korean and the game exited
normally from the menu:

- 새 게임
- 무장 편집
- 추가 콘텐츠
- 갤러리
- 설정
- 라이선스
- 게임 종료

The verified target hashes were:

- `MSG_PK/SC/msgui.bin`: `45DD6DA6EA2BF924350E67FD3B5922410C6798477CA10F795327E1AD4239E3AA`
- `RES_SC/res_lang.bin`: `F186049EF380B75AC9FF89ED746C98338E9D880FB920EBB040DEE65497EF8651`

## Distribution and recovery validation

- public package `Verify`: PASS
- stock Apply to both targets: PASS
- exact Restore of both stock files: PASS
- wrong-stock refusal without modifying the other target: PASS
- interrupted/mixed pair recovery through the durable journal: PASS
- refusal while a game process is running: PASS
- Python files in public bundle: 0
- PE/native executables or DLLs in public bundle: 0
- complete commercial game resources in public bundle: 0
- strict file-only audit: PASS, zero issues

Independent final recheck report:
`KR_PATCH_WORK/reports/mainmenu_file_only_v0.1_2026-07-13_AUDIT.recheck.json`

## Post-test installed state

The test installation was restored after validation:

- SC message stock SHA-256:
  `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- SC font-resource stock SHA-256:
  `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- registry `LANGUAGE`: restored to the pre-test value `3`
- running NOBU16 processes: none

Users select Simplified Chinese in the official launcher themselves after
applying the patch. The installer deliberately does not change that setting or
start the game.
