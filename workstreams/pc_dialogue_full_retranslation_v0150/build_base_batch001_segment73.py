#!/usr/bin/env python3
"""Build Base authoring segment 73 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S73.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s73", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1121:0": "어머, 슬슬\n끝인가요",
    "6:1122:0": "…조금 배가\n고프군요",
    "6:1123:0": "…끝인가",
    "6:1124:0": "돌아가도 되는가?",
    "6:1125:0": "어머, 슬슬\n끝인가요",
    "6:1126:0": "우후후, 즐거운\n모임이었답니다",
    "6:1127:0": "평정도 막을 내리는군",
    "6:1128:0": "자, 돌아갈 채비다",
    "6:1129:0": "이번에야말로\n",
    "6:1129:1": "도…!",
    "6:1130:0": "절로 자세가\n바로잡히는군",
    "6:1131:0": "훈공 1위는\n누구인가?",
    "6:1132:0": "슬슬 논공행상을 할\n시기군",
    "6:1133:0": "어서 승진하고\n싶구나",
    "6:1134:0": "배후를 기습당하면\n곤란",
    "6:1134:1": "까닭에",
    "6:1135:0": "어쩔 수 없는 지출",
    "6:1136:0": "밖으로 눈을 돌리는 것도\n잊어서는 안 된다",
    "6:1137:0": "가는 정이 있어야 오는 정이 있는 법\n그렇지",
    "6:1137:1": "은가",
    "6:1138:0": "동맹 관계라면\n안심할 수 있겠군",
    "6:1139:0": "늘 고맙습니다\n오늘은 무슨 용건이십니까",
    "6:1140:0": "늘 고맙습니다\n수확철이라 쌀을 싸게 팔고 있습니다",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "6:1129:0",
    "6:1129:1",
    "6:1130:0",
    "6:1131:0",
    "6:1132:0",
    "6:1133:0",
    "6:1134:0",
    "6:1134:1",
    "6:1135:0",
    "6:1136:0",
    "6:1137:0",
    "6:1137:1",
    "6:1138:0",
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending" if dynamic else "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending" if dynamic else "not_required",
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available",
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
                "segment": "base_msggame_B001_S73",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
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
