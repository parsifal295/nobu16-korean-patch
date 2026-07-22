#!/usr/bin/env python3
"""Build Base authoring segment 12 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S12.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s12", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:272:0": "노리는 자는 「",
    "2:272:1": "」 단 한 명!\n죽는 한이 있어도 그 목을 베겠다!",
    "2:273:0": "무가라 해도 풍류를 빼놓을 수 없지.\n풍류를 아는 마음이야말로 교섭의 요체다.",
    "2:274:0": "무가라 해도 풍류를 빼놓을 수 없지.\n풍류를 아는 마음이야말로 교섭의 요체……\n",
    "2:274:1": "에게도 가르쳐야겠군.",
    "2:275:0": "싸우지 않고도 목적을 이룰 수 있다면 그만이지……\n머리는 제대로 써야 하는 법이야.",
    "2:276:0": "시코쿠를 제패할 영웅은\n",
    "2:276:1": "조소카베",
    "2:276:2": "밖에 없다!",
    "2:277:0": "의 강함은 병력의 수에 있지 않다.\n자, 적진을 꿰뚫어 주마!",
    "2:278:0": "나의 힘을 똑똑히 보아라!",
    "2:279:0": "적군을 격파했다!\n가메와리",
    "2:279:1": "를 당해 낼 자는 없다!",
    "2:280:0": "나의 힘을 똑똑히 보아라!",
    "2:281:0": "나의 힘을 똑똑히 보아라!",
    "2:282:0": "나의 힘을 똑똑히 보아라!",
    "2:283:0": "출진하겠습니다.",
    "2:283:1": "한베에",
    "2:283:2": "의 병법을\n똑똑히 보여 드리지요.",
    "2:284:0": "나의 힘을 똑똑히 보아라!",
    "2:285:0": "적과 아군은 시세에 따라 달라지는 법.\n다시 손잡을 날도 있을 테니 섭섭해하지 마시오.",
    "2:286:0": "나의 힘을 똑똑히 보아라!",
    "2:287:0": "의 무용을 여기서 보이리라!\n자, 모두 기운을 내시오!",
    "2:288:0": "나의 힘을 똑똑히 보아라!",
    "2:289:0": "나의 힘을 똑똑히 보아라!",
    "2:290:0": "올 수 있거든 와 보아라!\n",
    "2:290:1": "가이",
    "2:290:2": "의 활로 되받아쳐 주마!",
    "2:291:0": "나의 힘을 똑똑히 보아라!",
    "2:292:0": "성을 지키지 못한 것은 불찰!\n이리된 이상 적병에게 일격을 돌려주리라!",
    "2:294:0": "적의 모략은 모두 「",
    "2:294:1": "한조",
    "2:294:2": "」가\n막을 테니 걱정하지 마시오……",
    "2:297:0": "협격 따위 얄팍한 수작은 내게 통하지 않는다!",
    "2:300:0": "에게",
    "2:300:1": ".\n이 땅의 기리시탄을 힘으로",
}

NON_DISPLAY_COORDINATES = {
    "2:293:0",
    "2:295:0",
    "2:296:0",
    "2:298:0",
    "2:299:0",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {272, 274, 276, 277, 279, 283, 287, 290, 294, 300}
}


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    rows: list[dict[str, object]] = []
    coordinates = sorted(
        set(TRANSLATIONS) | NON_DISPLAY_COORDINATES,
        key=lambda value: tuple(int(part) for part in value.split(":")),
    )
    for coordinate in coordinates:
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = ("base_msggame", block_id, record_id, literal_id)
        target = prepared.visible_targets.get(key)
        if target is None:
            raise RuntimeError(f"decision target is absent from the current Base universe: {coordinate}")
        non_display = coordinate in NON_DISPLAY_COORDINATES
        dynamic = coordinate in DYNAMIC_RUNTIME_COORDINATES
        row: dict[str, object] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "base_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
            "semantic_review": "approved",
            "scope_classification": (
                "confirmed_non_display"
                if non_display
                else "runtime_fragment_pending" if dynamic else "retranslated"
            ),
            "layout_review": "not_needed" if non_display else "unchanged_from_current",
            "runtime_review": "not_required" if non_display or not dynamic else "pending",
            "basis": (
                "explicit_unused_trait_dummy_slot_structural_evidence"
                if non_display
                else "pristine_pc_jp_with_same_record_pc_sc_tc_context_where_available"
            ),
            "historic_korean_used": False,
            "switch_korean_used": False,
        }
        if not non_display:
            row["translation"] = TRANSLATIONS[coordinate]
        rows.append(row)
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    expected_count = len(TRANSLATIONS) + len(NON_DISPLAY_COORDINATES)
    if len(validated) != expected_count:
        raise RuntimeError("validated decision count differs from the segment decision count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S12",
                "decision_count": len(rows),
                "retranslated": len(TRANSLATIONS) - len(DYNAMIC_RUNTIME_COORDINATES),
                "dynamic_runtime_review_pending": len(DYNAMIC_RUNTIME_COORDINATES),
                "confirmed_non_display": len(NON_DISPLAY_COORDINATES),
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
