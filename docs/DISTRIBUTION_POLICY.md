# NOBU16 Korean patch distribution policy

This project exists to produce a redistributable Korean patch, not merely a
locally modified game installation.

## Non-negotiable runtime rule

The released patch must not modify a running process. The following are out
of scope:

- `WriteProcessMemory` or equivalent process-memory writes
- DLL injection, proxy-DLL loading, or code caves installed at runtime
- API hooks, detours, breakpoints, trainers, or resident patch launchers
- waiting for protected code to unpack and then changing its instructions

Development proofs that use any of those techniques are not release inputs.

## Allowed installation model

The installer may change files on disk only after all of these conditions are
met:

1. The target file path, size, and SHA-256 match a supported stock version.
2. The patch payload contains only project-owned data and binary deltas, not a
   complete copy of a commercial game file.
3. The original file is backed up or can be recreated byte-for-byte by a
   reverse delta.
4. The patched output hash is known and verified before replacement.
5. Replacement is atomic, and a failed install leaves the stock file intact.
6. Restore verifies the restored stock SHA-256.

Permitted targets are message resources and font resources only. Game
executables are never patch targets: the release may not modify, replace,
decrypt, unpack, or redistribute `NOBU16PK.exe`, `NOBU16PK_EN.exe`, or the
official launcher.

## Release contents

A release must include:

- supported stock hashes and patched output hashes
- forward deltas and a tested restore path
- Korean translation sources and their scope/version
- font source version, source hash, upstream URL, and complete license text
- an install/verify/restore guide
- no Python, Ghidra, font editor, or system-font dependency at runtime
- no game launcher, resident helper, background process, or registry mutation

The retired `releases/mainmenu_v0.1_2026-07-13` memory-patch proof is explicitly
not a distributable release.
