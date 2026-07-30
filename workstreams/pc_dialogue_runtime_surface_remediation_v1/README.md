# PC dialogue runtime-surface remediation

This workstream rebuilds literal text only. It preserves `msggame.bin` VM
opcodes, calls, jumps, selectors, control bytes, and line topology. Generated
resources and private audits stay under `tmp/`; tracked overlays and
source-free evidence stay in this directory.

## Base build

Run:

```powershell
python -B workstreams/pc_dialogue_runtime_surface_remediation_v1/base_build_runtime_surface_remediation_v1.py
python -B workstreams/pc_dialogue_runtime_surface_remediation_v1/base_build_runtime_surface_remediation_v1.py --check
python -B workstreams/pc_dialogue_runtime_surface_remediation_v1/base_test_runtime_surface_remediation_v1.py
```

The Base builder applies the six user-reported priority coordinates first and
then builds the 4,291-coordinate bulk overlay against that predecessor. It
requires both independent runtime-surface and terminal-boundary audits to
report zero issues.

Base layout is not assigned the PK event-dialogue 912px limit. The tracked
relative-layout audit uses the established raw G1N model (48px for
Hangul/Hanja and 24px for other visible characters) and requires:

- no line-count change;
- no ordinary changed line wider by more than 24px;
- a +24px line may not exceed the predecessor maximum for its block;
- only `2:142:0` and `8:1020:1` are approved priority exceptions, with their
  exact line widths, final literal hashes, and reasons pinned in
  `base_layout_risk.source_free.v1.json`.

The Base quality gates also reject newly introduced generic `대상`, `인물`,
or `분`. The sole new `장수` occurrence at `15:1642:1` is pinned as an
explicit role classifier rather than an automatic dynamic-name carrier.
They additionally compare the final candidate with the source and reject
new dynamic-boundary `도` or 조사처럼 쓰인 `및`, as well as fixed honorific
particles following mixed-register calls.

The same gate rejects `본인`/`자신` and other unreviewed person carriers
immediately after dynamic person selectors. The Base overlay reconstructs all
264 such boundaries by context (for example merit, recruitment, capture,
battle target, betrayal, appointment, and status-log relations). Four
foreign-trader lines also replace the malformed repeated `요오` spelling with
stiff but natural `하십시오체`, with exact output regressions.

No command in this workstream writes to the Steam installation.
