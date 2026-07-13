# Public translation overlay

## Why it exists

Translator work packs contain official multilingual strings for review and therefore stay in
the ignored `data/translations/` directory. Public Git and release packages use a compact
overlay containing only:

- a stable numeric message ID;
- the SHA-256 of the stock SC string encoded as UTF-16LE;
- project-owned Korean text;
- optional review status, priority, and explicit invariant override.

The hash prevents a translation from being applied to a different game revision without
redistributing the original string.

## Export from a private development workspace

```powershell
$Python = (Get-Command python).Source
& $Python tools/export_public_translation_overlay.py `
  --meta workstreams/msgui_full/catalog_v2/msgui.meta.json `
  --catalog workstreams/msgui_full/catalog_v2/msgui.catalog.jsonl `
  --translations data/translations `
  --max-id 3300 `
  --overlay-id msgui_ko_0001_3300.v0.1 `
  --output data/public/msgui_ko_0001_3300.v0.1.json
```

The exporter verifies any development `source_en` text and supplied SC hash against the
private catalog before removing source text from the output. Repeating the command with the
same inputs must produce the same SHA-256.

## Merge in a clean workspace

First run `msgui_catalog_v2.py init` against a supported stock installation. This creates a
local ignored catalog. Then merge the public overlay:

```powershell
& $Python tools/msgui_catalog_v2.py merge-overlay `
  --meta workstreams/msgui_full/catalog_v2/msgui.meta.json `
  --catalog workstreams/msgui_full/catalog_v2/msgui.catalog.jsonl `
  --overlay data/public/msgui_ko_0001_3300.v0.1.json `
  --output tmp/msgui.catalog.ko.jsonl `
  --game-root ..
```

`merge-overlay` checks the packed and raw stock hashes, every per-ID SC hash, native printf
token order, escape sequences, PUA icons, line breaks, edge whitespace, and review-only
overrides before writing a separate catalog. It never edits the installed game.
