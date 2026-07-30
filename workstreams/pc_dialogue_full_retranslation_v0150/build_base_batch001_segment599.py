#!/usr/bin/env python3
"""Build Base authoring segment 599 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S599.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s599", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1056:0": "빗나가지는 않습니다!\n각오하십시오!",
    "9:1057:0": "끝장내 주마!\n이 일격을 받아라!",
    "9:1058:0": "이것으로 끝을\n내도록 하지요!",
    "9:1059:0": "승리의 함성을 올릴 이는\n우리다!",
    "9:1060:0": "요충지를 확보해\n줬다!",
    "9:1061:0": "요충지, 이",
    "9:1061:1": "이(가)\n차지했다!",
    "9:1062:0": "요충지는",
    "9:1062:1": "이(가)\n점령했다!",
    "9:1063:0": "요충지를 제압했습니다",
    "9:1064:0": "요충지를 탈취했노라!",
    "9:1065:0": "요충지는 우리가 차지했다",
    "9:1066:0": "이제 요충지는\n우리 것이다",
    "9:1067:0": "요충지는\n우리 것이로다!",
    "9:1068:0": "요충지를 제압했습니다!",
    "9:1069:0": "요충지는 우리가 차지했다!",
    "9:1070:0": "요충지를 차지했습니다",
    "9:1071:0": "요충지, 이",
    "9:1071:1": "이(가)\n차지했다!",
    "9:1072:0": "멋대로 빼앗지 마라!",
    "9:1073:0": "큭, 당했는가!",
    "9:1074:0": "빼앗겼는가……\n어쩔 수 없군",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1061:0",
    "9:1061:1",
    "9:1062:0",
    "9:1062:1",
    "9:1071:0",
    "9:1071:1",
}
STATIC_COORDINATES = set(TRANSLATIONS) - DYNAMIC_RUNTIME_COORDINATES


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        static = coordinate in STATIC_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "retranslated" if static else "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required" if static else "pending",
                "basis": (
                    "pristine_base_pc_jp_with_base_sc_tc_and_corresponding_pk_en_sc_tc_context_where_available"
                ),
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S599",
                "decision_count": len(rows),
                "retranslated": len(STATIC_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
