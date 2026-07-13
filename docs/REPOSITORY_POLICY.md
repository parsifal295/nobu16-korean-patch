# Repository and Cleanup Policy

## Purpose

This repository records the reproducible source of the file-only Korean patch.
It is not a mirror of the installed game and not an archive of experimental binary outputs.

## Tracked material

- Source code for extraction, rebuilding, validation, installation, and restoration
- Translation mappings and review metadata
- Public font recipes and OFL-licensed pinned font inputs
- Architecture, safety, reverse-engineering, and runtime-QA reports
- Tests and small deterministic fixtures that do not contain complete commercial resources
- Public release recipes and manifests

## Never tracked or redistributed

- Complete KOEI TECMO game resources, executables, archives, or backups
- Rebuilt `msg*.bin`, `res_lang.bin`, G1N/G1T payloads, or full extracted string tables
- Ghidra project databases, caches, unpacked executables, or local application state
- Runtime memory patchers, injectors, hooks, proxy DLLs, or process-attach tooling
- Private runtime candidates that are useful only for local verification

## Local cleanup rules

1. Preserve the frozen P3/P4 release evidence and the latest candidate reports.
2. Preserve source recipes before deleting generated candidates.
3. Delete superseded failed probes, captured frame sets, duplicated rebuilds, and stale backups
   only after the installed files have passed stock-hash verification.
4. A local complete-resource candidate may remain under an ignored directory only while its
   runtime test is pending; delete it after the recipe and evidence are sufficient.
5. Run `git status --ignored` before each release to make sure no commercial resource is staged.

## Commit discipline

- Keep safety policy, tooling, translations, and generated release metadata in separate commits.
- Record runtime pass/fail evidence before changing architecture status.
- Do not rewrite a published frozen release; create a new versioned release instead.
