#!/usr/bin/env python3
"""Build Base authoring segment 54 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S54.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s54", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


TRANSLATIONS: dict[str, str] = {
    "6:757:0": "가문 지붕 위의 학이\n울음 한 번으로 만사를 정하듯…",
    "6:758:0": "가문의 황혼도 머지않았다…\n어찌할 도리가 없구나…",
    "6:759:0": "옛 명군들은 가신의 말에\n귀를 기울였거늘",
    "6:760:0": "…잠자코\n가문과 운명을 함께하리라",
    "6:761:0": "조금만 더 모두의 의견을\n들어 주셨더라면…",
    "6:762:0": "이 지경이 되어 버려서는\n이제…",
    "6:763:0": "어디까지든 주군 혼자서\n내달리시면 될 일이지",
    "6:764:0": "하하하, 통쾌하구나!\n정말 어쩔 도리가 없군!",
    "6:765:0": "주군의 위압감이 너무 강해\n…괴롭다",
    "6:766:0": "지금은 그저…\n슬플 뿐…",
    "6:767:0": "주군의 생각에 고개만 끄덕이면 될 뿐\n…편한 일이로다",
    "6:768:0": "그만두자, 그만둬\n이제 와서 뭘 해도 소용없다",
    "6:769:0": "훗, 여기도 제법\n큰 집단이 되었군",
    "6:770:0": "세력이 커져도\n방심해선 안 되지",
    "6:771:0": "세력이 커져\n천하가 보이는구나",
    "6:772:0": "천하태평을 위해\n분골쇄신해야겠군",
    "6:773:0": "가신이 늘었다 한들\n규율은 규율이니라",
    "6:774:0": "우리 가문의 기세를\n막을 자가 있겠는가…",
    "6:775:0": "세력이 커졌기에\n쓸 수 있는 방책도…",
    "6:776:0": "우리 가문의 성장 또한\n내 예상대로…",
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
                "segment": "base_msggame_B001_S54",
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
