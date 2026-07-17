# PC base `msggame` semantic re-audit v1

This workstream performs an independent PC-only pass over all 24,262 literal
coordinates in the base `msggame` resource.  It compares pristine PC Japanese,
the current PC Korean resource, and same-coordinate Steam PC SC/TC only.
The Steam PC installation does not contain a same-resource EN file, and no PK
EN table is substituted.

The Switch Korean translation and historical Korean translations are excluded.
`F:\Games\NOBU16\MSG_PK\SC` is also excluded; only
`F:\SteamLibrary\steamapps\common\NOBU16\MSG\SC\msggame.bin` is used as
Chinese corroboration.

Existing generic-overlay coordinates are excluded only by IDs and dispositions
from the source-free PC coverage ledger.  The generic-overlay Korean text and
generic builder are not read.  Candidate text is emitted only to a private
`tmp` output; this workstream never writes a Steam game resource, changes a
generic builder, stages files, commits, pushes, or releases.

Candidate gates preserve the protected string profile, newline vector,
per-line visible codepoint counts, literal width, and raw byte-change surface.
No new line-break/reflow candidate is made here.  Passing this resource-only
pass does not claim complete in-game-context semantic completion.

Run:

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B workstreams\translation_quality_base_msggame_pc_reaudit_v1\build_base_msggame_pc_reaudit_v1.py --write
& $py -B workstreams\translation_quality_base_msggame_pc_reaudit_v1\build_base_msggame_pc_reaudit_v1.py --validate
```
