#!/usr/bin/env python3
"""Build Base authoring segment 10 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S10.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s10", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:221:0": "나의 힘을 똑똑히 보아라!",
    "2:222:0": "성 공략이야말로 나의 본분이다.\n적병들아, 똑똑히 깨달아라!",
    "2:223:0": "나의 힘을 똑똑히 보아라!",
    "2:224:0": "싸움이야말로 무가의 본분! 내 활약을\n기대해도 ",
    "2:224:1": "좋다!",
    "2:225:0": "적의 공격을 신속히 물리치도록\n엄중히 경계하며 전진하자.",
    "2:226:0": "나의 힘을 똑똑히 보아라!",
    "2:227:0": "강공 따위는 두려워할 것 없다.",
    "2:227:1": "\n지금이야말로 반격할 ",
    "2:227:2": "때다!",
    "2:228:0": "나의 힘을 똑똑히 보아라!",
    "2:229:0": "나의 힘을 똑똑히 보아라!",
    "2:230:0": "여러 공격로에서 협격한다……\n이것이 바로 용병의 묘리",
    "2:231:0": "나의 힘을 똑똑히 보아라!",
    "2:232:0": "나의 힘을 똑똑히 보아라!",
    "2:233:0": "나의 힘을 똑똑히 보아라!",
    "2:234:0": "나의 힘을 똑똑히 보아라!",
    "2:235:0": "그늘에서 할 일은 ",
    "2:235:1": "내게 맡겨라……\n머리 쓰는 방식이 다르기",
    "2:235:2": " 때문이지……",
    "2:236:0": "아무래도",
    "2:236:1": "의 차례인 듯하군……\n무슨 수를 써서라도\n",
    "2:236:2": "의 소임을 든든히 받쳐 보이겠",
    "2:237:0": "나의 힘을 똑똑히 보아라!",
    "2:238:0": "수상전에서는 결코 질 수 없다.",
    "2:238:1": "\n우리에게 해신의 가호가 있기를.",
    "2:239:0": "나의 힘을 똑똑히 보아라!",
    "2:240:0": "나의 힘을 똑똑히 보아라!",
}


DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {224, 225, 227, 230, 235, 236, 238}
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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": (
                    "runtime_fragment_pending"
                    if coordinate in DYNAMIC_RUNTIME_COORDINATES
                    else "retranslated"
                ),
                "layout_review": "unchanged_from_current",
                "runtime_review": (
                    "pending" if coordinate in DYNAMIC_RUNTIME_COORDINATES else "not_required"
                ),
                "basis": "pristine_pc_jp_with_same_record_pc_sc_tc_context",
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
                "segment": "base_msggame_B001_S10",
                "decision_count": len(rows),
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
