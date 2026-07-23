#!/usr/bin/env python3
"""Build Base authoring segment 627 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S627.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("pc_dialogue_full_retranslation_v0150_engine_s627", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS = {
    "9:1655:0": "이(가) 가겠다!\n조금만 더 버텨라",
    "9:1656:0": "곧 가겠습니다!\n기다려 주십시오!",
    "9:1657:0": "잠시 기다리시오!",
    "9:1658:0": "곧바로 가겠습니다!",
    "9:1659:0": "기다리고 있거라!\n지금 간다!",
    "9:1660:0": "지원인가! 살았군!",
    "9:1661:0": "●●●● 공인가! 지원에 감사하오!",
    "9:1662:0": "지원, 참으로 고맙소이다",
    "9:1663:0": "지원해 주셔서 감사드립니다!",
    "9:1664:0": "원호 덕분이오, 교대는 끝났소",
    "9:1665:0": "원호 덕에 교대를 마쳤구나",
    "9:1666:0": "무사히 교대를 마쳤소, 이 또한 원호 덕분이오",
    "9:1667:0": "잘 풀렸구나, 이 또한 원호 덕분이로다",
    "9:1668:0": "지원해 주셔서 살았습니다!",
    "9:1669:0": "배려에 감사하오!",
    "9:1670:0": "지원해 주셔서 감사합니다",
    "9:1671:0": "덕분에 살았소이다!",
    "9:1672:0": "나머지는 맡겨 두라고!",
    "9:1673:0": "감사는 필요 없소!\n무운을 비오!",
    "9:1674:0": "잘 버텨 주었다\n나머지는 내가 맡으마",
    "9:1675:0": "나머지는 우리에게\n맡겨 주시오!",
    "9:1676:0": "알겠소, 맡기시오!",
}

DYNAMIC_RUNTIME_COORDINATES = {
    "9:1655:0",
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
                "segment": "base_msggame_B001_S627",
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
