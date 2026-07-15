# PK msggame UI-priority B05

This batch adds 300 source-free Korean replacements for high-exposure PK
management reports, menu guidance, advice, prompts, confirmations, and result
messages in blocks 8, 13, and 15.

- B04's 250 coordinates are pinned and treated as a read-only predecessor.
- The 300 coordinates are disjoint from every registered predecessor and B04.
- Every entry preserves leading/trailing whitespace, newline structure,
  placeholders, escape sequences, control codes, and PUA structure exactly.
- Every Korean line fits the largest official multilingual line width plus 12.
- Repeated identical source literals use one consistent Korean replacement.
- Offline reconstruction and the full registered-overlay candidate both parse
  successfully without changing non-overlay literal coordinates.

Build and test:

```powershell
python workstreams/msggame_pk_ui_priority_b05/build_msggame_pk_ui_priority_b05.py
python -m unittest workstreams/msggame_pk_ui_priority_b05/test_msggame_pk_ui_priority_b05.py -v
```
