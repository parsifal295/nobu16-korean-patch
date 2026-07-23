#!/usr/bin/env python3
"""Build Base authoring segment 804 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment803 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S804.private.v1.jsonl"
SEGMENT = 804
TRANSLATIONS: dict[str, str] = {
    "15:280:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:280:1": "\n비용은 늘어나",
    "15:280:2": "지만\n착실히 진행할 수 있",
    "15:281:0": "좋은 방안이라 생각했",
    "15:281:1": "지만…\n조금 궁리가 부족했던 것일",
    "15:281:2": "까",
    "15:282:0": "그쪽 방안이 채택될 줄이야…\n제 제안은 때를 못 맞춘",
    "15:282:1": " 셈이군요",
    "15:283:0": "의 방안이 채택되",
    "15:283:1": "다니…\n아직 정진이 부족하다는 뜻",
    "15:284:0": "을(를) 승인하시겠습니까?",
    "15:285:0": "화면을 나가면",
    "15:285:1": "이(가) 제안하는\n",
    "15:285:2": "을(를) 채택할 수 없게 됩니다\n괜찮겠습니까?",
    "15:286:0": "이(라)는 낭인이\n성하에 있는 모양이다!\n등용해 와도 되겠지!?",
    "15:287:0": "성하에서",
    "15:287:1": "을(를)\n보았다는 소식이 들어왔습니다…\n등용해도 되겠습니까?",
    "15:288:0": "낭인·",
    "15:288:1": "이라는 자를\n성하에서 보았다고 하옵니다\n등용해도 되겠사옵니까",
    "15:289:0": "이(라)는 낭인을…\n성하에서 발견하였습니다\n등용해도 되겠습니까",
}

EXPECTED_ARITIES = {
    280: 3,
    281: 3,
    282: 2,
    283: 2,
    284: 1,
    285: 3,
    286: 1,
    287: 2,
    288: 2,
    289: 1,
}
EXPECTED_SOURCE_GAPS = {
    280: ("", "01431e040000", "0143a0030000", "01433c040000050505"),
    281: ("", "01432c020000", "0143f8020000", "050505"),
    282: ("", "0143ec020000", "014300010000050505"),
    283: ("014301000000", "0143ec020000", "014300010000050505"),
    284: ("023c", "050505"),
    285: ("", "024633", "023c", "050505"),
    286: ("024833", "050505"),
    287: ("", "024833", "050505"),
    288: ("", "024833", "050505"),
    289: ("024833", "050505"),
}
EXPECTED_CURRENT_GAPS = {
    280: ("", "01431e040000", "0143a0030000", "01433c040000050505"),
    281: ("", "01432c020000", "0143f8020000", "050505"),
    282: ("", "", "050505"),
    283: ("014301000000", "0143ec020000", "014300010000050505"),
    284: ("023c", "050505"),
    285: ("", "024633", "023c", "050505"),
    286: ("024833", "050505"),
    287: ("", "024833", "050505"),
    288: ("", "024833", "050505"),
    289: ("024833", "050505"),
}


def assert_semantics(source_records: dict[tuple[int, int], Any]) -> None:
    for literal_id in range(3):
        if COMMON.source_text(source_records, 280, literal_id) != COMMON.source_text(
            source_records, 272, literal_id
        ):
            raise RuntimeError("15:280/15:272 exact-source proposal repeat drifted")
        if TRANSLATIONS[f"15:280:{literal_id}"] != COMMON.TRANSLATIONS[
            f"15:272:{literal_id}"
        ]:
            raise RuntimeError("15:280 must reuse the exact 15:272 Korean fragments")

    if COMMON.source_text(source_records, 281, 2) != COMMON.source_text(
        source_records, 372, 2
    ):
        raise RuntimeError("15:281:2/15:372:2 same-source observation drifted")
    if EXPECTED_SOURCE_GAPS[281] == COMMON.record_gaps_hex(source_records[(15, 372)]):
        raise RuntimeError("15:281 and 15:372 context/gap distinction unexpectedly collapsed")

    if len(
        {
            COMMON.source_text(source_records, record_id, 0)
            for record_id in (287, 295, 297, 321)
        }
    ) != 1:
        raise RuntimeError("castle-town sighting exact-source group drifted")
    if len(
        {
            COMMON.source_text(source_records, record_id, 0)
            for record_id in (288, 290, 296, 322, 330)
        }
    ) != 1:
        raise RuntimeError("ronin-name exact-source group drifted")

    if not TRANSLATIONS["15:281:0"].endswith("했"):
        raise RuntimeError("15:281:0 must connect to its live morphology command")
    if not TRANSLATIONS["15:281:1"].endswith("것일"):
        raise RuntimeError("15:281:1 must connect to its live question morphology")
    if TRANSLATIONS["15:281:2"] != "까":
        raise RuntimeError("15:281:2 context-specific question ending drifted")
    if "제 제안은 때를 못 맞춘" not in TRANSLATIONS["15:282:0"]:
        raise RuntimeError("15:282 lost the source/auxiliary ill-timed-own-proposal meaning")
    if not TRANSLATIONS["15:283:0"].endswith("채택되"):
        raise RuntimeError("15:283:0 must leave the negative live morphology intact")
    if not TRANSLATIONS["15:283:1"].startswith("다니…"):
        raise RuntimeError("15:283:1 negative-result assembly drifted")

    joined = "\n".join(TRANSLATIONS.values())
    required_terms = ("계책", "방안", "제안", "정진", "낭인", "성하", "등용")
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 804 required terminology drifted")
    if any(term in joined for term in ("책략", "채용할", "낭인의")):
        raise RuntimeError("segment 804 retains a forbidden mistranslation")
    if "을(를)" not in TRANSLATIONS["15:284:0"]:
        raise RuntimeError("15:284 proposal token lost its batchim-safe particle")
    if not TRANSLATIONS["15:285:1"].endswith("\n"):
        raise RuntimeError("15:285:1 proposal-name bridge layout drifted")
    if not TRANSLATIONS["15:286:0"].endswith("되겠지!?"):
        raise RuntimeError("15:286 energetic proposal voice drifted")
    if TRANSLATIONS["15:288:0"] != "낭인·":
        raise RuntimeError("15:288 ronin/name runtime separator drifted")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        translations=TRANSLATIONS,
        arities=EXPECTED_ARITIES,
        source_gaps=EXPECTED_SOURCE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        semantic_assertions=assert_semantics,
    )


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
                "segment": "base_msggame_B001_S804",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
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
