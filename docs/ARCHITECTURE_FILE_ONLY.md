# Korean patch architecture: file-only, distributable release

Status: **SC route accepted with a documented vertical-map-label limitation** (2026-07-14)

## Hard boundary

The Korean patch is an offline file patch. It must never attach to or modify a
running game process. Process-memory writes, DLL injection, hooks, proxy DLLs,
trainers, and resident launchers are forbidden in development candidates and
release packages.

Earlier English-renderer runtime proofs are retained only as research notes.
Their code and payloads are not valid release inputs.

## Candidate renderer route

The official Simplified-Chinese executable path is the accepted direct-Unicode
route because its G1N font tables accept added Korean glyphs and its common
menus render Korean without an executable or runtime patch. Runtime observation
on 2026-07-14 showed that strategic-map castle names still use vertical writing
even though the common UI is horizontal. This is a documented display
limitation, not a release blocker. The user explicitly accepted vertical castle
labels on 2026-07-14 so translation coverage and a distributable patch can take
priority.

The patch does not change unofficial emulator configuration. The official game
launcher was verified to expose Japanese, Traditional Chinese, Simplified
Chinese, and English in its language selector. Validation and the release guide
will use the official Simplified-Chinese configuration path after the SC
resource candidate passes the runtime and restoration gates below.

## Mandatory runtime gate

Runtime evidence must record successful boot on the SC route, visible Korean UI,
missing-glyph and clipping checks on representative screens, normal exit, and
restoration of every modified file to its exact stock hash. Strategic-map castle
names must be checked and recorded as `vertical_known_limitation=true`; they do
not need to be horizontal. Long Korean officer names and map overlap remain QA
items, but a vertical castle label alone must not force `release_eligible=false`.

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
