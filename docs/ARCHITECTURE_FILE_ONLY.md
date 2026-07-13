# Korean patch architecture: file-only, distributable release

Status: **layout route reopened / release blocked** (2026-07-14)

## Hard boundary

The Korean patch is an offline file patch. It must never attach to or modify a
running game process. Process-memory writes, DLL injection, hooks, proxy DLLs,
trainers, and resident launchers are forbidden in development candidates and
release packages.

Earlier English-renderer runtime proofs are retained only as research notes.
Their code and payloads are not valid release inputs.

## Candidate renderer route

The official Simplified-Chinese executable path remains the direct-Unicode
candidate because its G1N font tables accept added Korean glyphs and its common
menus render Korean without an executable or runtime patch. It is **not yet an
accepted complete layout route**. Runtime observation on 2026-07-14 showed
that strategic-map castle names still use vertical writing even though the
common UI is horizontal. The earlier blanket statement that the SC/TC path
already provided horizontal CJK layout was therefore incorrect.

Korean text and glyphs may continue to be built against the corresponding
message/font resources for development, but no public release may be marked
eligible until a file-only solution makes strategic-map castle labels
horizontal on the stock executable.

The patch does not change unofficial emulator configuration. The official game
launcher was verified to expose Japanese, Traditional Chinese, Simplified
Chinese, and English in its language selector. Validation and the release guide
will use the official Simplified-Chinese configuration path only if the SC
resource candidate passes boot and the complete screen-layout gate below.

## Mandatory layout gate

Runtime evidence must explicitly record `castle_name_horizontal=true` from an
actual strategic-map screen. Main-menu, officer-edit, and ordinary-window
captures do not satisfy this gate. The same run must also check long Korean
officer names, map overlap/clipping, missing glyphs, and restore of every
modified file to its exact stock hash. Until that evidence exists, release
manifests must declare `release_eligible=false` and a public release ZIP must
not be produced.

## Rejected English workarounds

- The verified English Hangul renderer required five runtime code changes;
  runtime patching is forbidden.
- Mapping composed Korean onto printable ASCII cannot preserve the English
  character set. The main menu alone needs more visual variants than the safe
  spare slots provide.
- Patching English width tables inside the executable would invalidate its
  signature and still would not solve the slot and quality problems.

## Font-resource safety gate

The generic G1N editor's full rebuild path is forbidden for SC/TC resources.
Those files contain palette/header data that the editor does not preserve; an
unchanged save already differs in size.

Any SC/TC font builder must:

1. preserve the original header, complete palette blob, existing glyph records,
   and existing atlas bytes;
2. make only documented surgical additions required for Korean glyphs;
3. prove a no-op build is byte-for-byte identical to the stock input;
4. emit structural offsets/counts plus input/output SHA-256 values; and
5. be rejected before packaging if any invariant fails.

## Release model

- supported stock file sizes and SHA-256 hashes are checked before installation;
- payloads are binary deltas, not complete commercial game resources;
- game executables, the official launcher, and the Windows registry remain
  read-only; the user selects Simplified Chinese in the official launcher;
- patched output hashes are checked before atomic replacement;
- restore recreates and verifies the exact stock bytes;
- Noto Korean font source/version/hash and OFL text ship with the patch; and
- Python, Ghidra, font editors, and locally installed fonts are build-time only.

`tools/file_only_sc_mainmenu_test.ps1` is the local apply/restore harness. It
refuses to operate while the game is running, accepts only locked stock or
candidate hashes, stages each output beside its target, uses atomic file
replacement, and rolls both files back on a partial failure. It contains no
process-memory operation.

Every prospective public bundle must also pass
`tools/audit_file_only_release.py`. The audit fails closed if the manifest does
not declare the file-only contract, or if a bundle contains native executable
payloads, process-memory/hook capabilities, complete game resources, or renamed
copies matching known full-file hashes.

See `DISTRIBUTION_POLICY.md` for the normative distribution rules.
