#!/usr/bin/env python3
"""Build Base authoring segment 820 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment818 as COMMON
import build_base_batch001_segment819 as PRIOR


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S820.private.v1.jsonl"
SEGMENT = 820
RAW_TRANSLATIONS: dict[str, str] = {
    "15:472:0": "큰일이",
    "15:472:1": "!\n",
    "15:472:2": "의",
    "15:472:3": "이(가) 우리 가문을 저버리고\n",
    "15:472:4": "에 귀순한 모양",
    "15:472:5": "!",
    "15:473:0": "큰일이",
    "15:473:1": "!\n",
    "15:473:2": "의",
    "15:473:3": "이(가) 우리 가문을 저버리고\n",
    "15:473:4": "에 귀순한 모양",
    "15:473:5": "!",
    "15:474:0": "큰일이",
    "15:474:1": "!\n",
    "15:474:2": "의",
    "15:474:3": "이(가) 우리 가문을 저버리고\n",
    "15:474:4": "에 귀순한 모양",
    "15:474:5": "!",
}
RECORD_ARITIES = {472: 6, 473: 6, 474: 6}
EXPECTED_BASE_GAPS = {
    record_id: (
        "",
        "014352000000",
        "023c",
        "024833",
        "025032",
        "01431a020000",
        "050505",
    )
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = {
    record_id: (
        "",
        "014352000000",
        "023c",
        "024833",
        "025032",
        "014326020000",
        "050505",
    )
    for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    translations: dict[str, str],
) -> None:
    source_group = range(467, 475)
    if len({COMMON.source_literals(source_records, record_id) for record_id in source_group}) != 1:
        raise RuntimeError("segment 820 defection-report source repeat drifted")
    canonical = tuple(PRIOR.RAW_TRANSLATIONS[f"15:468:{literal_id}"] for literal_id in range(6))
    for record_id in RECORD_ARITIES:
        raw_group = tuple(
            RAW_TRANSLATIONS[f"15:{record_id}:{literal_id}"] for literal_id in range(6)
        )
        if raw_group != canonical:
            raise RuntimeError(f"segment 820 defection translation repeat drifted: {record_id}")
        if not translations[f"15:{record_id}:2"].startswith("의"):
            raise RuntimeError(f"segment 820 house-name possessive drifted: {record_id}")
        if not translations[f"15:{record_id}:3"].startswith(
            "이(가) 우리 가문을 저버리고\n"
        ):
            raise RuntimeError(f"segment 820 officer-name particle drifted: {record_id}")
        if not translations[f"15:{record_id}:4"].startswith("에 귀순한 모양"):
            raise RuntimeError(f"segment 820 faction-name particle drifted: {record_id}")
    joined = "\n".join(translations.values())
    if "당가" in joined or "우리 가문" not in joined or "귀순" not in joined:
        raise RuntimeError("segment 820 house terminology drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 820 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S820",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
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
