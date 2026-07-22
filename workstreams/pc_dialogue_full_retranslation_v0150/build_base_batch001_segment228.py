#!/usr/bin/env python3
"""Build Base authoring segment 228 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S228.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s228", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3725:1": "\n정전이 끝나면 상대 영내에 주둔한 병력을 철수시키",
    "6:3725:2": "\n그 뒤에도 화친을 유지할지 깊이 생각해 보시기 바랍니다",
    "6:3726:0": "와(과)의 정전 기한이 끝났",
    "6:3726:1": "\n부디 각별히 주의해 주",
    "6:3727:0": "와(과)의 정전 기한이 되었",
    "6:3727:1": "\n빈틈을 보이지 않도록",
    "6:3727:2": "유의하",
    "6:3728:0": "와(과)의 정전 기한이 끝났다더군\n습격당하지 않도록 조심해야겠어",
    "6:3729:0": "와(과)의 정전 기한이 끝났다고 하옵니다\n각별히 조심해야겠습니다",
    "6:3730:0": "와(과)의 정전은 끝났소이다\n대비를 빈틈없이 갖추셔야 할 듯하오",
    "6:3731:0": "와(과)의 정전 기한이 끝났습니다\n배후를 조심하소서",
    "6:3732:0": "와(과)의 정전 기한이 끝났다고 하오\n상대가 파고들 틈을 보이지 마시오",
    "6:3733:0": "와(과)의 정전 기한이 끝났습니다\n상대의 동향을 예의 주시해야겠습니다",
    "6:3734:0": "와(과)의 정전 기한이 끝났다고 하옵니다\n부디 조심하소서",
    "6:3735:0": "와(과)의 정전 기한이 끝났다더군\n습격당하지 않도록 조심해야 할 게야",
    "6:3736:0": "와(과)의 정전 기한이 끝났습니다\n각별히 조심해야 합니다",
    "6:3737:0": "와(과)의 정전 기한이 끝났다고 하오\n상대가 파고들 틈을 보이지 마시오",
    "6:3738:0": "와(과)의 정전 기한이 끝났습니다\n부디 각별히 조심하십시오",
    "6:3739:0": "와(과)의 정전 기한이 끝났소이다\n각별히 조심하시오",
    "6:3740:0": "교섭을 위해,",
}

STATIC_COORDINATES: set[str] = set()


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(ENGINE.DEFAULT_STEAM_ROOT, ENGINE.DEFAULT_BASE_PRISTINE, ENGINE.DEFAULT_PK_PRISTINE)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append({"schema": ENGINE.DECISION_SCHEMA, "resource": "base_msggame", "coordinate": coordinate,
                     "source_record_raw_sha256": target["source_record_raw_sha256"],
                     "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"], "translation": translation,
                     "semantic_review": "approved", "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                     "layout_review": "unchanged_from_current", "runtime_review": "not_required" if static else "pending",
                     "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
                     "historic_korean_used": False, "switch_korean_used": False})
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S228", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
