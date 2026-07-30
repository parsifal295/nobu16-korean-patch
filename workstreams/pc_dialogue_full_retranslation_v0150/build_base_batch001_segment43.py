#!/usr/bin/env python3
"""Build Base authoring segment 43 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S43.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s43", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:552:0": "사전 조율을\n게을리해서는 안 된다",
    "6:553:0": "의 제안을\n받아들여 주지 않겠나",
    "6:554:0": "…",
    "6:554:1": "의 제안\n잊힌 건가…",
    "6:555:0": "나의 헌언이\n받아들여지기를",
    "6:556:0": "건의에 대한 재가를 기다리니\n시간이 더디게 가는군…",
    "6:557:0": "자, 나의 진언이\n받아들여질지 어떨지",
    "6:558:0": "헌책을 들으실 생각이 없나…\n가볍게 보인 모양이군",
    "6:559:0": "헌언을 한시라도 빨리\n살펴 주었으면 하네만",
    "6:560:0": "언제쯤",
    "6:560:1": "의 건의를\n들어 주시려나…",
    "6:561:0": "건의에 아무 소식이 없군…",
    "6:562:0": "진언은 필요 없다\n…그런 것인가?",
    "6:563:0": "혼신을 다한 제안…\n꼭 들어주셔야 하는데",
    "6:564:0": "채택 소식이 없군…\n건의가 전해지긴 한 건가",
    "6:565:0": "건의가 받아들여지기를\n기다립시다",
    "6:566:0": "엉뚱한 제안을\n해 버린 건가…?",
    "6:567:0": "나의 진언이\n아직 눈에 들지 않았나",
    "6:568:0": "내가 살아 있는 동안\n건의를 알아봐 주시려나…",
    "6:569:0": "주군께 마음을 보내자\n",
    "6:569:1": "은(는) 건의 중입니다…",
    "6:570:0": "그렇게 득의양양하게\n건의했는데 방치라니",
    "6:571:0": "내 계책… 보시기만 하면\n채택될 터인데…",
}

DYNAMIC_RUNTIME_COORDINATES = {
    coordinate
    for coordinate in TRANSLATIONS
    if int(coordinate.split(":")[1]) in {552, 553, 554, 560, 569}
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
                "segment": "base_msggame_B001_S43",
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
