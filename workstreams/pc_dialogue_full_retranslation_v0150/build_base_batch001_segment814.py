#!/usr/bin/env python3
"""Build Base authoring segment 814 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment812 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S814.private.v1.jsonl"
SEGMENT = 814
RAW_TRANSLATIONS: dict[str, str] = {
    "15:414:0": (
        "우리 쪽으로 귀순할 만한 무장이라…\n"
        "짐작 가는 자가 없진 않아\n"
        "잠깐 알아볼까"
    ),
    "15:415:0": (
        "다른 가문 무장의 권유라면 맡겨 주시옵소서\n"
        "짐작 가는 자가 있사옵니다\n"
        "잘되면 귀순시킬 수 있을 듯하옵니다"
    ),
    "15:416:0": (
        "무장을 빼 오는 일이라면 짐작 가는 자가 있소\n"
        "아무래도 대우에 불만이 있는 듯하니\n"
        "권유하면 우리 가문에 귀순할지도 모르오"
    ),
    "15:417:0": (
        "다른 가문의 무장을 권유하는 일은 맡겨 주시옵소서\n"
        "섬기는 가문에 불만을 품은 무장이라면\n"
        "짐작 가는 자가 몇 있사옵니다"
    ),
    "15:418:0": (
        "무장을 늘리는 일이라면 맡겨 주시옵소서\n"
        "귀순할 만한 자를\n"
        "마침 찾아냈사옵니다"
    ),
    "15:419:0": (
        "무장을 빼 오는 일이라면 맡겨 주시오\n"
        "이익에 밝은 무장을 찾고 있었는데\n"
        "마침내 후보가 좁혀졌소이다…"
    ),
    "15:420:0": (
        "다른 가문의 무장을 권유하는 일은 맡겨 주시옵소서\n"
        "섬기는 가문에 불만을 품은 무장이라면\n"
        "짐작 가는 자가 몇 있사옵니다"
    ),
    "15:421:0": (
        "무장을 빼 오는 일이라면 맡겨 주시오\n"
        "이익에 밝은 무장을 찾고 있었는데\n"
        "마침내 후보가 좁혀졌소이다…"
    ),
    "15:422:0": (
        "다른 가문 무장의 권유라면 맡겨 주시옵소서\n"
        "짐작 가는 자가 있사옵니다\n"
        "잘되면 귀순시킬 수 있을 듯하옵니다"
    ),
    "15:423:0": (
        "큰 불만을 품은 무장이\n"
        "다른 가문에 있다는 소문이 돌고 있사옵니다\n"
        "권유하면 귀순할지도 모르옵니다"
    ),
    "15:424:0": (
        "큰 불만을 품은 무장이\n"
        "다른 가문에 있다는 소문이 돌고 있사옵니다\n"
        "권유하면 귀순할지도 모르옵니다"
    ),
    "15:425:0": (
        "큰 불만을 품은 무장이\n"
        "다른 가문에 있다는 소문이 돌고 있사옵니다\n"
        "권유하면 귀순할지도 모르옵니다"
    ),
    "15:426:0": (
        "은(는) 우리가 퍼뜨린 유언비어로\n"
        "거취를 두고 갈피를 못 잡는 모양\n"
        "우리 가문으로 오도록 권유하면 순순히 귀순할지도…"
    ),
    "15:427:0": "을(를) 설득하여\n우리 가문에 귀순시켜 보이",
    "15:427:1": "!\n당장 그자를",
    "15:427:2": "알현시키",
    "15:428:0": "은(는)",
    "15:428:1": "을(를) 거두어 주셨다\n이",
    "15:428:2": ", 입은 은혜는 절대 잊지 않아\n반드시 도움이 되고 말겠어!",
    "15:429:0": "제 힘을 인정해 주신\n",
    "15:429:1": "을(를) 위해\n이",
    "15:429:2": "의 목숨을 맡기겠소이다",
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(414, 427)},
    427: 3,
    428: 3,
    429: 3,
}
EXPECTED_GAPS = {
    **{record_id: ("", "050505") for record_id in range(414, 426)},
    426: ("024833", "050505"),
    427: (
        "014322000000",
        "0143140200000143f6010000",
        "014384040000",
        "01433c040000050505",
    ),
    428: ("014311000000", "014301000000", "024633", "050505"),
    429: ("", "014311000000", "024633", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:414:0",
    "15:419:0",
    "15:421:0",
    "15:426:0",
}
BASE_CONTEXT_ARITIES = {
    "SC": {
        record_id: 2 if record_id == 427 else 1
        for record_id in RECORD_ARITIES
    },
    "TC": {
        record_id: 2 if record_id in {426, 427} else 1
        for record_id in RECORD_ARITIES
    },
}
PK_EN_ARITIES = {
    record_id: 2 if record_id == 426 else 1
    for record_id in RECORD_ARITIES
}
MAPPING_TEXT_DIVERGENCES = {"JP": set(), "SC": set(), "TC": {417}}
MAPPING_GAP_DIVERGENCES = {"JP": {427}, "SC": set(), "TC": set()}


def resolved_translations(current_records: dict[tuple[int, int], Any]) -> dict[str, str]:
    translations = {}
    for coordinate, raw in RAW_TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        translations[coordinate] = COMMON.SUPPORT.adopt_current_layout(raw, current)
    return translations


def assert_semantics(
    source_records: dict[tuple[int, int], Any], translations: dict[str, str]
) -> None:
    exact_groups = ((415, 422), (417, 420), (419, 421), (423, 424, 425))
    for group in exact_groups:
        if len({source_records[(15, record_id)].data for record_id in group}) != 1:
            raise RuntimeError(f"segment 814 exact-source group drifted: {group}")
        if len({translations[f"15:{record_id}:0"] for record_id in group}) != 1:
            raise RuntimeError(f"segment 814 exact-translation group drifted: {group}")

    joined = "\n".join(translations.values())
    for term in ("우리 가문", "다른 가문", "귀순", "권유", "유언비어", "알현"):
        if term not in joined:
            raise RuntimeError(f"segment 814 required terminology drifted: {term}")
    if any(term in joined for term in ("당가", "타가", "배반", "출사", "다이묘가", "、")):
        raise RuntimeError("segment 814 retains forbidden terminology/punctuation")
    if not translations["15:426:0"].startswith("은(는)"):
        raise RuntimeError("segment 814 dynamic officer subject boundary drifted")
    if not translations["15:427:0"].endswith("보이"):
        raise RuntimeError("segment 814 live persuasion morphology stem drifted")
    if not translations["15:427:2"].endswith("알현시키"):
        raise RuntimeError("segment 814 live audience morphology stem drifted")
    if translations["15:428:2"].startswith("、"):
        raise RuntimeError("segment 814 Japanese comma survived")
    if not translations["15:428:2"].startswith(", "):
        raise RuntimeError("segment 814 officer-name comma bridge drifted")
    if not translations["15:428:2"].endswith("도움이 되고 말겠어!"):
        raise RuntimeError("segment 814 rough wasurenee/miseruze voice drifted")
    if not translations["15:429:1"].endswith("\n이"):
        raise RuntimeError("segment 814 officer-name demonstrative bridge drifted")
    if not translations["15:429:2"].startswith("의 목숨을"):
        raise RuntimeError("segment 814 dynamic officer genitive life phrase drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_gaps=EXPECTED_GAPS,
        current_ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        base_context_arities=BASE_CONTEXT_ARITIES,
        pk_en_arities=PK_EN_ARITIES,
        mapping_text_divergences=MAPPING_TEXT_DIVERGENCES,
        mapping_gap_divergences=MAPPING_GAP_DIVERGENCES,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 814 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S814",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "steam_write_performed": False,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
