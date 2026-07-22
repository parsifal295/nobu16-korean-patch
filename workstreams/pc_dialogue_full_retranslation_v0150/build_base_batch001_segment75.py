#!/usr/bin/env python3
"""Build Base authoring segment 75 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S75.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s75", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:1161:0": "어떤 거래도 할 수 없습니다",
    "6:1162:0": "병량과 가보를 사고팔 수 있습니다",
    "6:1163:0": "병량, 가보를 구매할 수 있습니다",
    "6:1164:0": "병량, 가보를 매각할 수 있습니다",
    "6:1165:0": "구매할 수 있는 물품이 없습니다",
    "6:1166:0": "매각할 수 있는 물품이 없습니다",
    "6:1167:0": "이번 철에는 구매할 수 있는 병량이 남아 있지 않습니다",
    "6:1168:0": "더 이상 본거지에 병량을 비축할 수 없습니다",
    "6:1169:0": "다른 가문의 방해로 병량을 구매할 수 없습니다",
    "6:1170:0": "이번 철에는 더 이상 병량을 매입하지 않습니다",
    "6:1171:0": "다른 가문의 방해로 병량을 매각할 수 없습니다",
    "6:1172:0": "이번 철에는 구매할 수 있는 군마가 남아 있지 않습니다",
    "6:1173:0": "더 이상 군마를 보유할 수 없습니다",
    "6:1174:0": "다른 가문의 방해로 군마를 구매할 수 없습니다",
    "6:1175:0": "군마를 매각할 수 없습니다",
    "6:1176:0": "이번 철에는 구매할 수 있는 철포가 남아 있지 않습니다",
    "6:1177:0": "더 이상 철포를 보유할 수 없습니다",
    "6:1178:0": "아직 철포가 전래되지 않았습니다",
    "6:1179:0": "다른 가문의 방해로 철포를 구매할 수 없습니다",
    "6:1180:0": "성하 마을에 남만 상관이 없어 철포를 구매할 수 없습니다",
}

DYNAMIC_RUNTIME_COORDINATES: set[str] = set()


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
                "segment": "base_msggame_B001_S75",
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
