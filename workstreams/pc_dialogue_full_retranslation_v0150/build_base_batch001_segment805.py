#!/usr/bin/env python3
"""Build Base authoring segment 805 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment804 as PRIOR


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S805.private.v1.jsonl"
SEGMENT = 805
TRANSLATIONS: dict[str, str] = {
    "15:290:0": "낭인·",
    "15:290:1": "이(라)는 자를\n성하에서 찾아냈다!\n어서 등용해도 되겠나?!",
    "15:291:0": "이(라)는 이름의 낭인을\n성하까지 불러냈습니다\n등용해도 되겠지요?",
    "15:292:0": "이(라)고 자칭하는 낭인이\n사관할 곳을 찾고 있다 합니다…\n말을 걸어도 되겠습니까?",
    "15:293:0": "이(라)는 낭인을\n성하에서 찾았소이다\n등용해도 되겠소이까?",
    "15:294:0": "성하에서",
    "15:294:1": "이(라)는\n낭인을 보았다는 소문이…\n찾아 등용하오리까",
    "15:295:0": "성하에서",
    "15:295:1": "을(를)\n보았다는 소식이 들어왔사옵니다\n등용해도 되겠사옵니까",
    "15:296:0": "낭인·",
    "15:296:1": "입니다만\n아무래도 성하에 있는 듯합니다\n등용해도 되겠습니까?",
    "15:297:0": "성하에서",
    "15:297:1": "이(라)는\n낭인을 보았다는 소문이…\n등용하오리까",
    "15:298:0": (
        "재미있어 보이는 낭인이 없나\n"
        "찾아보다가 마침내 발견했습니다!\n"
        "딱 한 번이면 된다, 만나 주지 않겠나?"
    ),
    "15:299:0": (
        "유능해 보이는 낭인을 발견해\n"
        "이야기해 보니 제법 훌륭한 인물이었습니다\n"
        "한 번 만나 보시지 않겠습니까?"
    ),
    "15:300:0": (
        "눈여겨볼 만한 낭인을 찾고 있었는데\n"
        "마침내 마음에 드는 자를 찾았사옵니다\n"
        "한 번 만나 보시지 않겠사옵니까"
    ),
    "15:301:0": (
        "실력 있는 낭인을 찾던 중\n"
        "마침내 한 명을 찾아냈습니다\n"
        "만나 보시지 않겠습니까?"
    ),
    "15:302:0": (
        "여기저기 알아보던 중\n"
        "마음이 맞는 낭인을 찾아냈습니다!\n"
        "어떤가, 만나 보지 않겠나?"
    ),
    "15:303:0": (
        "쓸 만한 낭인을\n"
        "남몰래 찾던 중 발견했습니다\n"
        "만나 보시지 않겠습니까?"
    ),
    "15:304:0": (
        "떠돌아다니는 이름난 낭인의 소문을 듣고\n"
        "마침내 찾아냈습니다\n"
        "만나 보시지 않겠습니까?"
    ),
    "15:305:0": (
        "재기 넘치는 낭인을 찾았소이다\n"
        "이 늙은이의 눈을 믿고\n"
        "한 번 만나 보아 주시구려"
    ),
    "15:306:0": (
        "우리 가문의 버팀목이 될 낭인을 찾던 중\n"
        "한 명을 찾아냈습니다\n"
        "만나 보시겠습니까?"
    ),
    "15:307:0": (
        "재능 있는 자를 찾고 있었습니다만\n"
        "마침내 찾아냈습니다\n"
        "만나 보시지 않겠습니까?"
    ),
    "15:308:0": (
        "각지의 낭인을 찾던 중\n"
        "훌륭한 인물을 찾아냈습니다\n"
        "한 번 만나 보시지 않겠습니까?"
    ),
    "15:309:0": (
        "남몰래 낭인의 소문을 여러 번 알아본 끝에\n"
        "마침내 눈여겨볼 만한 자를 찾았사옵니다…\n"
        "부디 만나 보시옵소서"
    ),
}

EXPECTED_ARITIES = {
    290: 2,
    291: 1,
    292: 1,
    293: 1,
    294: 2,
    295: 2,
    296: 2,
    297: 2,
    298: 1,
    299: 1,
    300: 1,
    301: 1,
    302: 1,
    303: 1,
    304: 1,
    305: 1,
    306: 1,
    307: 1,
    308: 1,
    309: 1,
}
EXPECTED_SOURCE_GAPS = {
    290: ("", "024833", "050505"),
    291: ("024833", "050505"),
    292: ("024833", "050505"),
    293: ("024833", "050505"),
    294: ("", "024833", "050505"),
    295: ("", "024833", "050505"),
    296: ("", "024833", "050505"),
    297: ("", "024833", "050505"),
    298: ("", "050505"),
    299: ("", "050505"),
    300: ("", "050505"),
    301: ("", "050505"),
    302: ("", "050505"),
    303: ("", "050505"),
    304: ("", "050505"),
    305: ("", "050505"),
    306: ("", "050505"),
    307: ("", "050505"),
    308: ("", "050505"),
    309: ("", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_SOURCE_GAPS)


def assert_semantics(source_records: dict[tuple[int, int], Any]) -> None:
    castle_group = (287, 295, 297, 321)
    if len(
        {COMMON.source_text(source_records, record_id, 0) for record_id in castle_group}
    ) != 1:
        raise RuntimeError("castle-town sighting exact-source group drifted")
    if not (
        PRIOR.TRANSLATIONS["15:287:0"]
        == TRANSLATIONS["15:295:0"]
        == TRANSLATIONS["15:297:0"]
        == "성하에서"
    ):
        raise RuntimeError("same castle-town source/gap must reuse exact Korean")

    ronin_group = (288, 290, 296, 322, 330)
    if len(
        {COMMON.source_text(source_records, record_id, 0) for record_id in ronin_group}
    ) != 1:
        raise RuntimeError("ronin-name exact-source group drifted")
    if not (
        PRIOR.TRANSLATIONS["15:288:0"]
        == TRANSLATIONS["15:290:0"]
        == TRANSLATIONS["15:296:0"]
        == "낭인·"
    ):
        raise RuntimeError("same ronin-name source/gap must reuse exact Korean")

    joined = "\n".join(TRANSLATIONS.values())
    for term in ("낭인", "사관", "등용", "성하", "우리 가문"):
        if term not in joined:
            raise RuntimeError(f"segment 805 required term drifted: {term}")
    if any(term in joined for term in ("당가", "채용", "사관처")):
        raise RuntimeError("segment 805 retains a forbidden mistranslation")

    if not TRANSLATIONS["15:290:1"].endswith("되겠나?!"):
        raise RuntimeError("15:290 energetic-but-respectful proposal voice drifted")
    if "되겠지요?" not in TRANSLATIONS["15:291:0"]:
        raise RuntimeError("15:291 confident polite proposal voice drifted")
    if "되겠소이까?" not in TRANSLATIONS["15:293:0"]:
        raise RuntimeError("15:293 elder proposal voice drifted")
    if "되겠사옵니까" not in TRANSLATIONS["15:295:1"]:
        raise RuntimeError("15:295 high-formality proposal voice drifted")
    if "딱 한 번이면 된다" not in TRANSLATIONS["15:298:0"]:
        raise RuntimeError("15:298 energetic colloquial proposal voice drifted")
    if "찾았사옵니다" not in TRANSLATIONS["15:300:0"]:
        raise RuntimeError("15:300 archaic respectful proposal voice drifted")
    if "주시구려" not in TRANSLATIONS["15:305:0"]:
        raise RuntimeError("15:305 elder proposal voice drifted")
    if not TRANSLATIONS["15:302:0"].endswith("만나 보지 않겠나?"):
        raise RuntimeError("15:302 rough colloquial proposal voice drifted")
    if any(
        "한번" in TRANSLATIONS[coordinate]
        for coordinate in ("15:299:0", "15:300:0", "15:305:0", "15:308:0")
    ):
        raise RuntimeError("one-time adverb spacing drifted")
    if "부디" not in TRANSLATIONS["15:309:0"]:
        raise RuntimeError("15:309 deferential proposal voice drifted")
    if "여러 번" not in TRANSLATIONS["15:309:0"]:
        raise RuntimeError("15:309 lost the repeated-search source detail")


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
                "segment": "base_msggame_B001_S805",
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
