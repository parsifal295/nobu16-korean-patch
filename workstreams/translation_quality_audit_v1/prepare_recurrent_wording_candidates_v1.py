#!/usr/bin/env python3
"""Extract high-confidence recurrent Korean wording fixes from the private audit.

This is deliberately narrow: it only emits a candidate when the exact Korean
wording and its Japanese meaning both match a reviewed rule.  It never edits a
game file and writes source-bearing data only below ``tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
DEFAULT_INPUT = REPO / "tmp" / "translation_quality_audit_v1" / "semantic_inventory_v3" / "private_full_pairs.jsonl"
DEFAULT_OUTPUT = REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "recurrent_wording_candidates.v1.jsonl"

# Japanese 自主的に in these tutorial messages means an actor operates on its
# own initiative.  Korean "자주적으로" is a literal but unnatural formation;
# "자율적으로" is the established UI wording for autonomous operation.
SOURCE_FRAGMENT = "\u81ea\u4e3b\u7684"
TARGET_FRAGMENT = "\uc790\uc8fc\uc801\uc73c\ub85c"
REPLACEMENT_FRAGMENT = "\uc790\uc728\uc801\uc73c\ub85c"
SUPPORTED_RESOURCES = {"base_msggame", "pk_msggame"}


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    private_root = (REPO / "tmp").resolve()
    output = args.output.resolve()
    if output == private_root or private_root not in output.parents:
        raise SystemExit("output must remain below tmp")
    candidates: list[dict[str, str]] = []
    for line in args.input.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["resource"] not in SUPPORTED_RESOURCES or TARGET_FRAGMENT not in row["ko"]:
            continue
        if SOURCE_FRAGMENT not in row["jp"]:
            raise SystemExit(f"unexpected Japanese source at {row['resource']}:{row['coordinate']}")
        proposed = row["ko"].replace(TARGET_FRAGMENT, REPLACEMENT_FRAGMENT)
        if proposed == row["ko"]:
            raise SystemExit("replacement did not change the target")
        candidates.append({
            "resource": row["resource"],
            "coordinate": row["coordinate"],
            "issue_type": "literal_wording_autonomous_operation",
            "proposed_ko": proposed,
            "source_current_hash": text_hash(row["ko"]),
            "format_invariants": {
                "runtime": row["ko"].count("[") == proposed.count("["),
                "printf": row["ko"].count("%") == proposed.count("%"),
                "escape": row["ko"].count("\x1b") == proposed.count("\x1b"),
                "linebreak": row["ko"].count("\n") == proposed.count("\n"),
                "edge_whitespace": (row["ko"][:1], row["ko"][-1:]) == (proposed[:1], proposed[-1:]),
            },
        })
    candidates.sort(key=lambda item: (item["resource"], tuple(int(part) for part in item["coordinate"].split(":"))))
    if len(candidates) != 24 or any(not all(entry["format_invariants"].values()) for entry in candidates):
        raise SystemExit(f"candidate contract failed: {len(candidates)} entries")
    atomic_write(output, "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in candidates))
    print(json.dumps({"entry_count": len(candidates), "output": str(output), "game_files_written": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
