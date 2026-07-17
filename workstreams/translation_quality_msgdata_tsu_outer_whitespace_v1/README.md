# PC-only trailing-whitespace `tsu` reading audit

This isolated workstream recovers static `msgdata` name-label candidates that
the earlier exact-string matcher intentionally skipped because the target keeps
outer ASCII whitespace while its matching PC `strdata` anchor does not.

It reads only:

- pristine PC Japanese `msgdata` and `strdata` resources;
- current PC Korean `msgdata` / `strdata` resources;
- PC EN, SC, and TC context for the candidate coordinate; and
- the committed PC-only quality overlay, only to virtualize already-active
  Korean corrections and prevent duplicate coordinates.

It never opens a Switch resource, historical Korean backup, or game-writing
path.  The private JSONL preserves the candidate target's complete format
profile and outer whitespace.  A row is admitted only when replacing every
Korean `tsu` syllable with `ssu` produces the same visible Korean label as a
same-pristine-Japanese PC `strdata` anchor.

Run:

```powershell
python workstreams/translation_quality_msgdata_tsu_outer_whitespace_v1/build_msgdata_tsu_outer_whitespace_v1.py --write
python workstreams/translation_quality_msgdata_tsu_outer_whitespace_v1/build_msgdata_tsu_outer_whitespace_v1.py --validate
```

The generator writes review material only below `tmp/` and does not apply,
stage, or commit a game-resource change.
