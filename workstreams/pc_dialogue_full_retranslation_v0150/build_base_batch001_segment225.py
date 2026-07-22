#!/usr/bin/env python3
"""Build Base authoring segment 225 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S225.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s225", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "6:3695:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3695:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3696:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3696:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3697:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3697:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3698:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3698:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3699:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3699:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3700:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3700:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3701:0": "와(과)의 동맹도 2개월이 채 남지 않",
    "6:3701:1": "\n동맹을 이어 갈지 끝낼지\n깊이 생각해 보시기 바랍니다",
    "6:3702:0": "와(과)의 동맹은 끝났다더군\n앞으로 3개월간 정전은 이어지지만\n조심해야겠어",
    "6:3703:0": "와(과)의 동맹은 기한이 끝났다고 하옵니다\n앞으로 3개월간 정전은 이어집니다만\n경계를 늦추어서는 아니 되옵니다",
    "6:3704:0": "와(과)의 동맹은 끝났소이다\n앞으로 3개월간 정전은 이어진다 하나\n부디 방심하지 마시오",
    "6:3705:0": "와(과)의 동맹은 기한이 끝났습니다\n앞으로 3개월간 정전은 이어진다 하나\n배후를 조심하소서",
    "6:3706:0": "와(과)의 동맹은 기한이 끝났다고 하옵니다\n앞으로 3개월간 정전은 이어진다 하나\n빈틈을 보이지 않도록 하시오",
    "6:3707:0": "와(과)의 동맹은 기한이 끝났습니다\n앞으로 3개월간 정전은 이어진다 하나\n동향을 예의 주시하소서",
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
    print(ENGINE.json.dumps({"status": "ok", "segment": "base_msggame_B001_S225", "decision_count": len(rows),
                             "retranslated": len(STATIC_COORDINATES),
                             "dynamic_runtime_review_pending": len(rows) - len(STATIC_COORDINATES),
                             "steam_write_performed": False, "output": str(OUTPUT)}, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
