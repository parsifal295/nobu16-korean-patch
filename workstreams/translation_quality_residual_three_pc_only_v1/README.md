# Residual Three PC-Only Candidate Evidence

This isolated workstream prepares exactly three high-confidence translation
quality candidates:

1. base msggame 8:937:2: immediate preparation wording.
2. PK msggame 8:949:2: the same immediate preparation wording.
3. MS GEV 7256: a punitive command wording correction.

The builder reads pristine PC Japanese and installed PC EN/SC/TC only for
meaning.  Installed PC Korean is a current-text hash gate only.  It does not
open Switch Korean or historical Korean backups.  Its only output is a
private JSONL under tmp.  It never writes a game resource, changes a generic
builder, applies Steam files, creates a commit, or creates a release.

Run:

    python build_residual_three_pc_only_candidates_v1.py --write --validate
