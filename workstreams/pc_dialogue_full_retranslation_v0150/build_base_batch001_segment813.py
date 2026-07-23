#!/usr/bin/env python3
"""Build Base authoring segment 813 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S813.private.v1.jsonl"
SEGMENT = 813
RAW_TRANSLATIONS: dict[str, str] = {
    "15:398:0": (
        "우리 가문에 귀순하고 싶다는 자가\n"
        "주변 다이묘 가문에도 있다 하옵니다\n"
        "이를테면…"
    ),
    "15:399:0": (
        "어느 무장이 우리 가문에 귀순하겠다고\n"
        "나섰다더군… 사실이라면\n"
        "더할 나위 없는 일이다만…"
    ),
    "15:400:0": (
        "지금은 다른 가문에 계시지만\n"
        "이쪽으로 귀순하고 싶다는 분이\n"
        "계신 듯합니다만…"
    ),
    "15:401:0": (
        "큰 불만을 품은 무장이 다른 가문에\n"
        "있다는 소문이 돌고 있사옵니다\n"
        "권유하면 귀순할지도 모르겠사옵니다"
    ),
    "15:402:0": "에서 무장을 빼 오자고\n권유하면 따라올 만한 녀석이 있어",
    "15:403:0": (
        "에서 무장을 데려옵시다\n"
        "조략을 걸면 우리 가문에 귀순할 만한 자를 알고 있사옵니다"
    ),
    "15:404:0": "조략의 표적은",
    "15:404:1": "이옵니다\n우리 가문으로 귀순을 꾀하는 자가 있기 때문이옵니다",
    "15:405:0": "다른 가문에서 무장을 빼 오지 않으시겠습니까…\n",
    "15:405:1": "의 누군가가\n우리 가문에 귀순할지도 모르옵니다…",
    "15:406:0": "조략으로 무장을 빼 오고자 하옵니다…\n",
    "15:406:1": "에\n우리 가문으로 귀순할 만한 무장이 있사오니…",
    "15:407:0": (
        "무장을 귀순시키려면\n"
        "상대를 잘 가려야 하옵니다… 이를테면\n"
    ),
    "15:407:1": "의 그자라든가",
    "15:408:0": (
        "에서 무장을 빼 오고자 하옵니다\n"
        "주군에게 큰 불만을 품은 자가 있다 합니다"
    ),
    "15:409:0": "의 무장을 빼 올 수는 없을까\n한 번 시도해 보고 싶구려…",
    "15:410:0": (
        "에서 무장을 빼 오는 건 어떻습니까?\n"
        "불만을 품은 자가 있다고 하니\n"
        "분명 설득에 응해 줄 것입니다"
    ),
    "15:411:0": "의 무장을 빼 와 보이겠다\n이",
    "15:411:1": "이(가) 설득한다면\n싫다고는 하지 못할 것이다",
    "15:412:0": (
        "의 무장을 빼 옵시다\n"
        "주군에게 불만을 품은 자에게 말을 걸면\n"
        "분명 우리 가문에 귀순할 것입니다"
    ),
    "15:413:0": (
        "에서 무장을 빼 오자고 제안드리옵니다\n"
        "푸대접받는 자를 권유하면\n"
        "우리 가문으로 귀순할지도 모르옵니다"
    ),
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(398, 404)},
    404: 2,
    405: 2,
    406: 2,
    407: 2,
    408: 1,
    409: 1,
    410: 1,
    411: 2,
    412: 1,
    413: 1,
}
EXPECTED_GAPS = {
    **{record_id: ("", "050505") for record_id in range(398, 402)},
    402: ("02483e", "050505"),
    403: ("02483e", "050505"),
    404: ("", "02483e", "050505"),
    405: ("", "02483e", "050505"),
    406: ("", "02483e", "050505"),
    407: ("", "02483e", "050505"),
    408: ("02483e", "050505"),
    409: ("02483e", "050505"),
    410: ("02483e", "050505"),
    411: ("02483e", "014304000000", "050505"),
    412: ("02483e", "050505"),
    413: ("02483e", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:398:0",
    "15:399:0",
    "15:400:0",
    "15:405:0",
    "15:405:1",
    "15:406:0",
    "15:406:1",
    "15:407:0",
    "15:409:0",
}
CONTEXT_ARITY_TWO = {404, 405, 406, 410}
BASE_CONTEXT_ARITIES = {
    language: {
        record_id: 2 if record_id in CONTEXT_ARITY_TWO else 1
        for record_id in RECORD_ARITIES
    }
    for language in ("SC", "TC")
}
PK_EN_ARITIES = {
    record_id: 2 if record_id in CONTEXT_ARITY_TWO else 1
    for record_id in RECORD_ARITIES
}
MAPPING_TEXT_DIVERGENCES = {"JP": set(), "SC": set(), "TC": set()}
MAPPING_GAP_DIVERGENCES = {"JP": set(), "SC": set(), "TC": set()}


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
    joined = "\n".join(translations.values())
    for term in ("우리 가문", "다른 가문", "귀순", "권유", "조략"):
        if term not in joined:
            raise RuntimeError(f"segment 813 required terminology drifted: {term}")
    if any(term in joined for term in ("당가", "타가", "배반", "출사", "다이묘가", "、")):
        raise RuntimeError("segment 813 retains forbidden terminology/punctuation")
    if translations["15:404:0"] != "조략의 표적은":
        raise RuntimeError("segment 813 stratagem target fragment drifted")
    if not translations["15:404:1"].startswith("이옵니다\n"):
        raise RuntimeError("segment 813 clan-token predicate boundary drifted")
    if not translations["15:406:1"].startswith("에\n"):
        raise RuntimeError("segment 813 target-clan locative boundary drifted")
    if "에\n우리 가문으로 귀순할 만한 무장" not in translations["15:406:1"]:
        raise RuntimeError("segment 813 source-clan/destination-clan roles drifted")
    if not translations["15:407:0"].endswith("이를테면\n"):
        raise RuntimeError("segment 813 example-clan bridge drifted")
    if not translations["15:411:0"].endswith("\n이"):
        raise RuntimeError("segment 813 self-name demonstrative bridge drifted")
    if not translations["15:411:1"].startswith("이(가)"):
        raise RuntimeError("segment 813 self-name subject particle drifted")
    if "한 번 시도해" not in translations["15:409:0"]:
        raise RuntimeError("segment 813 one-time spacing drifted")
    if not translations["15:401:0"].endswith("모르겠사옵니다"):
        raise RuntimeError("segment 813 mase-nu-na archaic polite voice drifted")
    if COMMON.text_array(source_records[(15, 404)])[0] == COMMON.text_array(
        source_records[(15, 407)]
    )[0]:
        raise RuntimeError("segment 813 unrelated stratagem sources collapsed")


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
        raise RuntimeError("segment 813 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S813",
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
