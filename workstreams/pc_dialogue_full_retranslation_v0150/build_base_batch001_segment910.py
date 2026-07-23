#!/usr/bin/env python3
"""Build Base authoring segment 910 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment810 as CANONICAL_S810
import build_base_batch001_segment908 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S910.private.v1.jsonl"
)
SEGMENT = 910
OFFICER_EMPLOYED = tuple(
    CANONICAL_S810.RAW_TRANSLATIONS[f"15:373:{literal_id}"]
    for literal_id in range(2)
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1523:0": (
        "성하의 낭인에게 등용을 권했으나\n"
        "제 힘이 미치지 못하여…\n"
        "성과를 얻지 못했습니다."
    ),
    "15:1524:0": "근방에 유망한 자는 있",
    "15:1524:1": (
        "\n더 넓은 인맥을 지닌 자라면\n"
        "찾아낼 수 있을지도 모르"
    ),
    "15:1525:0": "…",
    "15:1525:1": ", 좋은 정보는 얻",
    "15:1525:3": "의",
    "15:1525:4": (
        "은(는) 주군에게 불만이 있다 하니\n"
        "빼내기 교섭을 시도하고자"
    ),
    "15:1525:5": "만",
    "15:1526:0": "유망한 낭인은 발견할 수 있",
    "15:1526:1": (
        "…\n싸움에서 사로잡은 다른 가문의 자를 설득하는 등\n"
        "다른 길을 모색할 필요가 있"
    ),
    **{
        f"15:1527:{literal_id}": translation
        for literal_id, translation in enumerate(OFFICER_EMPLOYED)
    },
    "15:1528:0": "이(가) 무장 탐색에 실패",
    "15:1529:0": "의 조력을 얻을 수만 있다면\n",
    "15:1529:1": ", 반드시 함락시키",
    "15:1529:2": "\n부디 우리 군단에",
    "15:1529:3": "힘을 보태 주시옵소서!",
}
RECORD_ARITIES = {
    1523: 1,
    1524: 2,
    1525: 6,
    1526: 2,
    1527: 2,
    1528: 1,
    1529: 4,
}
EXPECTED_BASE_JP = {
    1523: (
        "城下の牢人に登用をもちかけたものの\n"
        "我が力及ばず…\n"
        "成果は得られ",
    ),
    1524: (
        "近辺に有望な者はい",
        "\nより広い人脈を持つ者なら\n見つけられるやもし",
    ),
    1525: (
        "…",
        "、良き情報は得られ",
        "\n",
        "の",
        "は主に不満があるとか\n引抜の交渉を試みたく",
        "が",
    ),
    1526: (
        "有望な牢人は発見でき",
        "…\n戦で捕らえた他家の者を説得するなど\n別の道を探る必要がある",
    ),
    1527: ("が", "を登用"),
    1528: ("が武将探索に失敗",),
    1529: (
        "の助太刀さえ頂ければ\n",
        "、必ず攻め落と",
        "\nどうか我が軍団に",
        "力添えを！",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1523: ("", "0143f8020000050505"),
    1524: ("", "0143f8020000", "01434e040000050505"),
    1525: (
        "",
        "014332020000",
        "0143140200000143fc010000",
        "026432",
        "01431d000000",
        "0143e2000000",
        "050505",
    ),
    1526: ("", "0143f8020000", "01431e010000050505"),
    1527: ("024633", "024733", "050505"),
    1528: ("024633", "050505"),
    1529: (
        "014308000000",
        "026432",
        "0143b4010000",
        "014384040000",
        "050505",
    ),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    1523: ("", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1523: ("", "014304030000050505"),
    1524: ("", "014304030000", "01435a040000050505"),
    1525: (
        "",
        "01433e020000",
        "01431a020000014302020000",
        "026432",
        "01431d000000",
        "0143e2000000",
        "050505",
    ),
    1526: ("", "014304030000", "01431e010000050505"),
    1529: (
        "014308000000",
        "026432",
        "0143ba010000",
        "014390040000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1523:0",
    "15:1525:0",
    "15:1526:1",
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1525:2": "\n"}

SHARED_AUXILIARY = {
    ("SC", 1523): (
        ("虽然向城下的浪人提出登用，\n但事与愿违……\n并未获得任何成果。",),
        ("", "050505"),
    ),
    ("TC", 1523): (
        ("雖然向城下的浪人提出登庸，\n可惜事與願違……\n未能獲得成果。 ",),
        ("", "050505"),
    ),
    ("SC", 1524): (
        ("附近并未发现前途无量之人。\n若是人脉很广的话，\n也许还是能找得到。",),
        ("", "050505"),
    ),
    ("TC", 1524): (
        ("附近並未發現前途無量之人。\n若是人脈很廣的話，\n也許還是能找得到。 ",),
        ("", "050505"),
    ),
    ("SC", 1525): (
        ("……然而，得到了不错的信息。\n", "的", "似乎对其主不满，\n我想把他挖角过来。"),
        ("", "026432", "01431d000000", "050505"),
    ),
    ("TC", 1525): (
        ("……不過，我打聽到一個好消息。\n", "的", "對其主心懷不滿，\n或許可嘗試挖角看看。"),
        ("", "026432", "01431d000000", "050505"),
    ),
    ("SC", 1526): (
        ("没发现有前途的浪人。\n……得找别的方法了，\n比如说服在战场中抓到的其他家的人。",),
        ("", "050505"),
    ),
    ("TC", 1526): (
        ("未能發掘有潛力的浪人……\n或許該嘗試其他的管道。\n例如，說服敗戰遭俘的他家臣子等等。",),
        ("", "050505"),
    ),
    ("SC", 1527): (
        ("登用了", "。"),
        ("024633", "024733", "050505"),
    ),
    ("TC", 1527): (
        ("登庸", "。"),
        ("024633", "024733", "050505"),
    ),
    ("SC", 1528): (
        ("搜寻武将失败。",),
        ("024633", "050505"),
    ),
    ("TC", 1528): (
        ("搜尋武將失敗。",),
        ("024633", "050505"),
    ),
    ("SC", 1529): (
        ("若能获得", "相助，\n", "一定能渡过难关。\n请一定助我军一臂之力！"),
        ("", "014308000000", "026432", "050505"),
    ),
    ("TC", 1529): (
        ("若能獲得", "相助，\n必定能攻陷", "。\n還請助我軍團一臂之力！"),
        ("", "014308000000", "026432", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1523: (
        (
            "IÖve made an offer of employment to the rªnin in the castle town, "
            "but IÖm afraid I wasnÖt persuasive enough.",
        ),
        ("", "050505"),
    ),
    1524: (
        (
            "We couldnÖt find any promising prospects in the nearby territory. "
            "Someone with a wider network might be able to do so, though.",
        ),
        ("", "050505"),
    ),
    1525: (
        (
            "But we did obtain some interesting information. It turns out that a "
            "man at ",
            " is dissatisfied with their lord. We could try negotiating an extraction.",
        ),
        ("", "026432", "050505"),
    ),
    1526: (
        (
            "We couldnÖt find any promising rªnin. We may need to try a different "
            "method, like persuading people weÖve captured from other clans.",
        ),
        ("", "050505"),
    ),
    1527: (
        (" has employed ", "."),
        ("024633", "024733", "050505"),
    ),
    1528: (
        (" failed to find an officer.",),
        ("024633", "050505"),
    ),
    1529: (
        ("I could seize ", " with your help! Please, lend my province your aid!"),
        ("", "026432", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, language, record_id): expected
        for (language, record_id), expected in SHARED_AUXILIARY.items()
        for side in ("base", "pk")
    },
    **{
        ("pk", "EN", record_id): expected
        for record_id, expected in PK_EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B109_pristine_base_pc_jp_authoritative_"
    "ronin_recruitment_officer_search_extraction_and_corps_aid_with_"
    "explicit_plus_15_pk_mapping_base_pk_sc_tc_and_pk_en_auxiliary_"
    "context_s810_base373_officer_employed_canonical_exact_reuse_"
    "nangin_officer_search_joryeok_our_clan_terminology_hidden_lf_"
    "excluded_current1523_flattened_runtime_skeleton_recorded_source_"
    "opcode_stems_and_current_layout_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    canonical_source = tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, 373)])
    )
    if EXPECTED_BASE_JP[1527] != canonical_source:
        raise RuntimeError("segment 910 S810 Base373 source canonical drifted")
    if (
        EXPECTED_BASE_GAPS[1527]
        != CANONICAL_S810.EXPECTED_GAPS[373]
    ):
        raise RuntimeError("segment 910 S810 Base373 gap canonical drifted")
    if tuple(
        raw_translations[f"15:1527:{literal_id}"]
        for literal_id in range(2)
    ) != OFFICER_EMPLOYED:
        raise RuntimeError("segment 910 S810 Base373 Korean canonical drifted")

    joined = "\n".join(translations.values())
    for required in (
        "낭인",
        "무장 탐색",
        "조력",
        "다른 가문",
        "등용",
        "빼내기 교섭",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 910 required terminology drifted: {required}")
    for forbidden in ("뢰인", "무장 수색", "조태도", "타가"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 910 retained forbidden terminology: {forbidden}"
            )
    for coordinate, ending in {
        "15:1524:0": "있",
        "15:1524:1": "모르",
        "15:1525:1": "얻",
        "15:1525:4": "시도하고자",
        "15:1526:0": "있",
        "15:1526:1": "있",
        "15:1529:1": "함락시키",
    }.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 910 live inflection stem drifted: {coordinate}"
            )
    if raw_translations["15:1525:5"] != "만":
        raise RuntimeError("segment 910 extraction adversative bridge drifted")
    if raw_translations["15:1529:0"] != "의 조력을 얻을 수만 있다면\n":
        raise RuntimeError(
            "segment 910 助太刀さえ focus relation drifted"
        )
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:1525:2": "\n"}:
        raise RuntimeError("segment 910 hidden LF exclusion drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 910 ellipsis seed/pair drifted: {coordinate}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows_with_current_gaps(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 17 or len(translations) != 17:
        raise RuntimeError("segment 910 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 910 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S910",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "hidden_lf_excluded": 1,
                "canonical_s810_base373_reuse": True,
                "explicit_pk_mapping": True,
                "current_flattened_opcode_records": [1523],
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
