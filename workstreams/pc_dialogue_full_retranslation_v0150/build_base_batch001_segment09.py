#!/usr/bin/env python3
"""Build Base authoring segment 09 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S09.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s09", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "2:201:0": "「",
    "2:201:1": "」 등",
    "2:201:2": "정책 발령 준비를 시작",
    "2:202:0": "우리 가문 위신:",
    "2:202:1": "으로 상승",
    "2:203:0": "우리 가문 위신:",
    "2:203:1": "으로 하락",
    "2:204:0": "을 제압 ",
    "2:204:1": "+",
    "2:205:0": "이 함락 ",
    "2:206:0": "세력 분단으로 위신 변동",
    "2:207:0": "역직 「",
    "2:207:1": "」 취임 ",
    "2:207:2": "+",
    "2:208:0": "관직 「",
    "2:208:1": "」 취임 ",
    "2:208:2": "+",
    "2:209:0": "에 건설 가능 구획이 증가",
    "2:210:0": "의 건설 가능 구획이 감소",
    "2:211:0": "나의 힘을 똑똑히 보아라!",
    "2:212:0": "백성을 다스리는 요체는 오직 진심뿐.\n이 군의 장악은 제게 ",
    "2:212:1": "맡겨 주십시오!",
    "2:213:0": "이(가) 쌓아 온 인맥을\n우리 가문에 보탤 때가 온 듯",
    "2:214:0": "이 일은",
    "2:214:1": "에게 맡겨 주시오.\n평소 쌓아 온 인맥으로\n",
    "2:214:2": "의",
    "2:214:3": "활약을 든든히 뒷받침",
    "2:215:0": "사람을 쓰는 데는 조금\n자신이 있지……\n부하 지휘는 내게 맡겨라.",
    "2:216:0": "자랑하는 언변으로 반드시 신용을\n얻어 ",
    "2:216:1": "오겠습니다!",
    "2:217:0": "의 차례인 듯",
    "2:217:1": "\n이 자랑하는 언변으로",
    "2:217:2": "을(를) 보좌하여\n반드시 신용을 얻어 오겠",
    "2:218:0": "나의 힘을 똑똑히 보아라!",
    "2:219:0": "내 영지는 한 치도 침범하게 두지 ",
    "2:219:1": "않겠다!\n철통같이 지키는 데 ",
    "2:219:2": "전념하겠다!",
    "2:220:0": "수세는 내가 가장 자신 있는 분야다.\n철벽의 방비를 보여 주마!",
}


DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1])
    in {201, 202, 203, 204, 205, 207, 208, 209, 210, 212, 213, 214, 216, 217, 219}
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
                "segment": "base_msggame_B001_S09",
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
