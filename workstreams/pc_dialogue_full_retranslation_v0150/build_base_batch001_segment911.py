#!/usr/bin/env python3
"""Build Base authoring segment 911 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment881 as AUXILIARY
import build_base_batch001_segment910 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S911.private.v1.jsonl"
)
SEGMENT = 911
make_auxiliary_overrides = AUXILIARY.make_auxiliary_overrides
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1530:0": "통일까지\n남은",
    "15:1530:1": "성",
    "15:1530:3": "성은 우리 가문의 지배하에 있",
    "15:1531:0": (
        "지방 통일에 필요한 성을 우호 세력이\n"
        "제압하고 있다면, 외교 관계를\n"
        "해소한 뒤 공략해야 하"
    ),
    "15:1532:0": "기나이는 모두 우리 가문의 지배하에 있",
    "15:1532:1": "\n천하 평정까지 남은",
    "15:1532:2": "성",
    "15:1532:4": "성은 우리 가문의 지배하에 있",
    "15:1533:0": (
        "천하 평정에 필요한 성을 우호 세력이\n"
        "제압하고 있다면, 외교 관계를\n"
        "해소한 뒤 공략해야 하"
    ),
    "15:1534:0": "전국의 과반수는 제압했으",
    "15:1534:1": "\n기나이 제패까지 남은",
    "15:1534:2": "성",
    "15:1534:4": "성은 우리 가문의 지배하에 있",
    "15:1535:0": "모든 성의 완전 제패까지\n남은",
    "15:1535:1": "성",
    "15:1535:3": "성은 우리 가문의 지배하에 있",
    "15:1536:0": "천하 평정까지 남은",
    "15:1536:1": "성\n기나이를 제압할 필요가 있",
    "15:1536:2": "\n기나이 제패까지 남은",
    "15:1536:3": "성",
}
RECORD_ARITIES = {
    1530: 4,
    1531: 1,
    1532: 5,
    1533: 1,
    1534: 5,
    1535: 4,
    1536: 4,
}
EXPECTED_BASE_JP = {
    1530: (
        "統一まで\n残り",
        "城",
        "\n",
        "城は当家が統治してお",
    ),
    1531: (
        "地方統一に必要な城を友好勢力が\n"
        "制圧している場合、外交関係を\n"
        "解消して攻め取る必要が",
    ),
    1532: (
        "畿内はすべて制してお",
        "\n天下平定まで残り",
        "城",
        "\n",
        "城は当家が統治してお",
    ),
    1533: (
        "天下平定に必要な城を友好勢力が\n"
        "制圧している場合、外交関係を\n"
        "解消して攻めとる必要が",
    ),
    1534: (
        "全国の過半数は制してお",
        "\n畿内制覇まで残り",
        "城",
        "\n",
        "城は当家が統治してお",
    ),
    1535: (
        "全城の完全制覇まで\n残り",
        "城",
        "\n",
        "城は当家が統治してお",
    ),
    1536: (
        "天下平定まで残り",
        "城\n畿内を制する必要が",
        "\n畿内制覇まで残り",
        "城",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    1530: (
        "統一まで\n残り",
        "城",
        "\n",
        "城は当家に従ってお",
    ),
    1531: (
        "地方統一に必要な城を同盟勢力が\n"
        "制圧している場合、外交関係を\n"
        "解消して攻め取る必要が",
    ),
    1532: (
        "畿内はすべて当家に従ってお",
        "\n天下平定まで残り",
        "城",
        "\n",
        "城は当家が統治してお",
    ),
    1533: (
        "天下平定に必要な城を同盟勢力が\n"
        "制圧している場合、外交関係を\n"
        "解消して攻めとる必要が",
    ),
}
EXPECTED_BASE_GAPS = {
    1530: (
        "023C",
        "0232",
        "01432C020000",
        "0233",
        "014336040000050505",
    ),
    1531: ("", "014352000000050505"),
    1532: (
        "",
        "014336040000",
        "0232",
        "01432C020000",
        "0233",
        "014336040000050505",
    ),
    1533: ("", "014352000000050505"),
    1534: (
        "",
        "014336040000",
        "0232",
        "01432C020000",
        "0233",
        "014336040000050505",
    ),
    1535: (
        "",
        "0232",
        "01432C020000",
        "0233",
        "014336040000050505",
    ),
    1536: (
        "",
        "0232",
        "014352000000",
        "0233",
        "01432C020000050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1530: (
        "023C",
        "0232",
        "014338020000",
        "0233",
        "014342040000050505",
    ),
    1531: EXPECTED_BASE_GAPS[1531],
    1532: (
        "",
        "014342040000",
        "0232",
        "014338020000",
        "0233",
        "014342040000050505",
    ),
    1533: EXPECTED_BASE_GAPS[1533],
    1534: (
        "",
        "014342040000",
        "0232",
        "014338020000",
        "0233",
        "014342040000050505",
    ),
    1535: (
        "",
        "0232",
        "014338020000",
        "0233",
        "014342040000050505",
    ),
    1536: (
        "",
        "0232",
        "014352000000",
        "0233",
        "014338020000050505",
    ),
}
PK_RECORD_MAP = {
    1530: 1560,
    1531: 1561,
    1532: 1562,
    1533: 1563,
    1534: 1564,
    1535: 1565,
    1536: 1566,
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:1530:2": "\n",
    "15:1532:3": "\n",
    "15:1534:3": "\n",
    "15:1535:2": "\n",
}
SHARED_AUXILIARY = {
    ("SC", 1530): (
        ("距离统一", "\n还剩", "城。\n", "城已在本家的统治之下。"),
        ("", "023C", "0232", "0233", "050505"),
    ),
    ("TC", 1530): (
        ("距", "統一成功尚餘", "城。\n本家統治著", "城。"),
        ("", "023C", "0232", "0233", "050505"),
    ),
    ("SC", 1531): (
        (
            "若出现地区统一所必要的城\n"
            "被友好势力压制的情况时，\n"
            "需要解除外交关系再进行攻占。",
        ),
        ("", "050505"),
    ),
    ("TC", 1531): (
        (
            "當友好勢力壓制統一地方必須的城池時，\n"
            "必須先解除外交關係後攻奪。",
        ),
        ("", "050505"),
    ),
    ("SC", 1532): (
        (
            "已经完全控制了畿内。\n距离天下平定还剩",
            "城。\n",
            "城已在本家的统治之下。",
        ),
        ("", "0232", "0233", "050505"),
    ),
    ("TC", 1532): (
        (
            "已完全控制畿內。\n距平定天下尚餘",
            "城。\n本家統治著",
            "城。",
        ),
        ("", "0232", "0233", "050505"),
    ),
    ("SC", 1533): (
        (
            "若出现天下平定所必要的城\n"
            "被友好势力压制的情况时，\n"
            "需要解除外交关系再进行攻占。",
        ),
        ("", "050505"),
    ),
    ("TC", 1533): (
        (
            "當友好勢力壓制平定天下必須的城池時，\n"
            "必須先解除外交關係後攻奪。",
        ),
        ("", "050505"),
    ),
    ("SC", 1534): (
        (
            "已控制全国的大半部分。\n距离称霸畿内还剩",
            "城。\n",
            "城已在本家统治之下。",
        ),
        ("", "0232", "0233", "050505"),
    ),
    ("TC", 1534): (
        (
            "對全國的控制已過半數。\n距稱霸畿內尚餘",
            "城。\n本家統治著",
            "城。",
        ),
        ("", "0232", "0233", "050505"),
    ),
    ("SC", 1535): (
        ("距离称霸全城还剩", "城。\n", "城已在本家的统治之下。"),
        ("", "0232", "0233", "050505"),
    ),
    ("TC", 1535): (
        ("距全城的完全稱霸\n尚餘", "城。\n本家統治著", "城。"),
        ("", "0232", "0233", "050505"),
    ),
    ("SC", 1536): (
        (
            "距离天下平定还剩",
            "城。\n必须先控制畿内，\n距离称霸畿内还剩",
            "城。",
        ),
        ("", "0232", "0233", "050505"),
    ),
    ("TC", 1536): (
        (
            "距平定天下尚餘",
            "城。\n必須壓制畿內。\n距稱霸畿內尚餘",
            "城。",
        ),
        ("", "0232", "0233", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1530: (
        (
            "Only ",
            " castle(s) must still be taken to unify ",
            ". Our clan rules over ",
            " castle(s).",
        ),
        ("", "0232", "023C", "0233", "050505"),
    ),
    1531: (
        (
            "When a friendly clan controls a castle standing in the way of "
            "regional unity, we ought to try a diplomatic approach before "
            "turning to violence.",
        ),
        ("", "050505"),
    ),
    1532: (
        (
            "WeÖve conquered all of the area surrounding the capital. Only ",
            " castles still stand in the way of unifying the land. Our clan "
            "rules over ",
            " castles.",
        ),
        ("", "0232", "0233", "050505"),
    ),
    1533: (
        (
            "When a friendly clan controls a castle standing in the way of "
            "national unity, we ought to try a diplomatic approach before "
            "turning to violence.",
        ),
        ("", "050505"),
    ),
    1534: (
        (
            "WeÖve conquered half of the nation. ",
            " castles must be seized to control the capital. Our clan rules "
            "over ",
            " castles.",
        ),
        ("", "0232", "0233", "050505"),
    ),
    1535: (
        (
            "Only ",
            " castles remain until all castles have been conquered. Our "
            "clan rules over ",
            " castles.",
        ),
        ("", "0232", "0233", "050505"),
    ),
    1536: (
        (
            "We still need to conquer ",
            " castles to rule the nation. ",
            " castles must be seized to control the capital.",
        ),
        ("", "0232", "0233", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B110_pristine_base_pc_jp_authoritative_"
    "regional_and_national_unification_progress_with_directly_verified_"
    "base_1530_1536_to_pk_1560_1566_mapping_exact_sc_tc_and_actual_pk_en_"
    "context_explicit_base_pk_jp_exceptions_for_governed_subordinate_and_"
    "friendly_allied_wording_統一_as_통일_天下平定_as_천하_평정_畿内_as_"
    "기나이_当家_as_우리_가문_dynamic_region_and_two_count_token_directions_"
    "four_hidden_lf_slots_live_0143_stems_current_layout_and_protected_"
    "skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if PK_RECORD_MAP != {
        1530: 1560,
        1531: 1561,
        1532: 1562,
        1533: 1563,
        1534: 1564,
        1535: 1565,
        1536: 1566,
    }:
        raise RuntimeError("segment 911 direct Base/PK mapping drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_JP[record_id] != EXPECTED_PK_JP[record_id]
    } != {1530, 1531, 1532, 1533}:
        raise RuntimeError("segment 911 Base/PK JP exception set drifted")
    for coordinate in EXCLUDED_NONVISIBLE_COORDINATES:
        if coordinate in raw_translations or coordinate in translations:
            raise RuntimeError(
                f"segment 911 hidden LF received a decision: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in ("통일", "천하 평정", "기나이", "우리 가문"):
        if required not in joined:
            raise RuntimeError(
                f"segment 911 terminology drifted: {required}"
            )
    if any(term in joined for term in ("당가", "평정 천하", "키나이")):
        raise RuntimeError("segment 911 forbidden terminology retained")
    stem_expectations = {
        "15:1530:3": "지배하에 있",
        "15:1531:0": "공략해야 하",
        "15:1532:0": "지배하에 있",
        "15:1532:4": "지배하에 있",
        "15:1533:0": "공략해야 하",
        "15:1534:0": "제압했으",
        "15:1534:4": "지배하에 있",
        "15:1535:3": "지배하에 있",
        "15:1536:1": "필요가 있",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 911 live inflection stem drifted: {coordinate}"
            )
    if len(raw_translations) != 20:
        raise RuntimeError("segment 911 visible decision count drifted")


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
    if len(rows) != 20 or len(translations) != 20:
        raise RuntimeError("segment 911 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 911 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 911 dynamic classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S911",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "hidden_lf_excluded": len(
                    EXCLUDED_NONVISIBLE_COORDINATES
                ),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_exception_records": [1530, 1531, 1532, 1533],
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
