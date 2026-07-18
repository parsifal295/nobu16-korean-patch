# &#xD604;&#xC7AC; Steam PC &#xC774;&#xBCA4;&#xD2B8; &#xB808;&#xC774;&#xC544;&#xC6C3; &#xBB34;&#xBCC0;&#xACBD; Ledger v1

This workstream proves the accepted current Steam-PC event-layout state without
changing it.  Its only inputs are the current Steam Base event resource
`MSG/JP/ev_strdata.bin`, PK event resource `MSG_PK/JP/msgev.bin`, and the
current event font in `RES_JP/res_lang.bin`.

## Why this is a no-op ledger

The earlier PK full-layout v2 overlay is stale: it was prepared against an
older input state.  Although 3,700 of its 3,774 target literals already match
the current PK text, its remaining 74 coordinates are not safe to write back.
This ledger never reads the old v2 target-overlay payload and never injects it.

It reads only the historic v2 audit's coordinate metadata, then proves the
current state in memory.  The build result is explicitly the same current PK
resource, with an effective change count of zero.

## What is pinned and checked

- Current Steam packed and raw SHA-256 profiles for Base, PK, and the event
  font; the font is read for metrics only.
- Seven Wave13 Base event anchors.
- The current PK hard-line-break coordinate domain: 6,681 rows.
- The three current-only runtime rows: `10837`, `10840`, and `10905`.
- Runtime-name reservation data: 58 token spellings across 29 name IDs.
- 4,002 bounded historic review rows: every row remains within three lines and
  912 px after runtime-name reservation.  ID `16402` remains a preserved
  printf-width-unknown hold, not an automatic reflow target.
- Reconciliation of the stale v2 overlay: 3,700 exact current no-ops and 74
  non-exact IDs.  The 74 all remain in the historic hard-break domain; 11 are
  verified as historic `v1_reused` rows outside the old review subset.

## Commands

```powershell
$py='C:\\Users\\melse\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe'
& $py -B workstreams/pc_event_current_rebase_ledger_v1/build_pc_event_current_rebase_ledger_v1.py verify
& $py -B workstreams/pc_event_current_rebase_ledger_v1/build_pc_event_current_rebase_ledger_v1.py build
& $py -B -m unittest discover -s workstreams/pc_event_current_rebase_ledger_v1 -p test_pc_event_current_rebase_ledger_v1.py -v
```

`verify` and `build` emit JSON only to stdout.  They do not create a
candidate file, modify Steam files, touch font assets, stage or commit Git
changes, push, or create a release.

## Follow-up rule

The 74 non-exact coordinates are a current-text quality/review queue, not
permission to restore old v2 literals.  If a real PK layout correction is
needed later, it must be authored from the current PK text and current font
metrics in a separate, explicit overlay.
