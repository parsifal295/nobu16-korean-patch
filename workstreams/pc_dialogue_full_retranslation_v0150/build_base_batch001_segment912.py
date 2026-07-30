#!/usr/bin/env python3
"""Build Base authoring segment 912 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment911 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S912.private.v1.jsonl"
)
SEGMENT = 912
make_auxiliary_overrides = PREVIOUS.make_auxiliary_overrides
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1537:0": "전국의 과반수는 제압했으",
    "15:1537:1": "\n기나이 제패까지 남은",
    "15:1537:2": "성",
    "15:1537:3": "\n기나이에 우리 가문의 성은 없",
    "15:1538:0": "적성 제압, 훌륭하오",
    "15:1538:1": "\n이 기세로",
    "15:1538:2": "통일을\n노려 보심이",
    "15:1538:3": "인가",
    "15:1539:0": (
        "우리 가문이야말로 이 나라에 둘도 없는 무가\n"
        "천하에 패권을 떨쳐\n"
        "천하 평정을 이루"
    ),
    "15:1539:1": "다",
    "15:1540:0": "이제",
    "15:1540:1": "야말로 천하인\n전국 통일의 비원을,",
    "15:1540:2": "의 야망을\n이루",
    "15:1540:3": "다",
    "15:1541:0": "취임, 경사로다",
    "15:1541:1": "\n전국 통일의 비원을,",
    "15:1541:2": "의 야망을\n이루",
    "15:1541:3": "다",
    "15:1542:0": "우선",
    "15:1542:1": "의 상황을",
    "15:1542:2": "확인",
    "15:1542:4": "을(를) 제압하려면\n그 땅을 알아야 하",
}
RECORD_ARITIES = {
    1537: 4,
    1538: 4,
    1539: 2,
    1540: 4,
    1541: 4,
    1542: 5,
}
EXPECTED_BASE_JP = {
    1537: (
        "全国の過半数は制してお",
        "\n畿内制覇まで残り",
        "城",
        "\n畿内に当家の城は",
    ),
    1538: (
        "敵城制圧、お見事",
        "\nこの勢いで",
        "統一を\n目指してみては",
        "か",
    ),
    1539: (
        "当家こそ日の本に二つ無き武家\n"
        "天下に覇を唱え\n"
        "天下平定を成し遂げ",
        "ぞ",
    ),
    1540: (
        "いまや",
        "こそが天下人\n全国統一の悲願を、",
        "の野望を\n果た",
        "ぞ",
    ),
    1541: (
        "就任、めでたきこと",
        "\n全国統一の悲願を、",
        "の野望を\n果た",
        "ぞ",
    ),
    1542: (
        "まずは",
        "の状況を",
        "確認",
        "\n",
        "を制するには\nその地を知らねば",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    1539: (
        "当家こそ日の本に二つと無き武家\n"
        "天下に覇を唱え\n"
        "天下平定を成し遂げ",
        "ぞ",
    ),
}
EXPECTED_BASE_GAPS = {
    1537: (
        "",
        "014336040000",
        "0232",
        "01432C020000",
        "014384010000050505",
    ),
    1538: (
        "",
        "01433E020000",
        "023C",
        "0143B0020000014356020000",
        "050505",
    ),
    1539: ("", "01431E040000", "050505"),
    1540: (
        "",
        "0143D0040000",
        "025032",
        "01437E040000",
        "050505",
    ),
    1541: (
        "023C",
        "01431A020000",
        "025032",
        "01437E040000",
        "050505",
    ),
    1542: (
        "",
        "023C",
        "01438A040000",
        "014396010000",
        "023C",
        "01431C030000050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1537: (
        "",
        "014342040000",
        "0232",
        "014338020000",
        "01438A010000050505",
    ),
    1538: (
        "",
        "01434A020000",
        "023C",
        "0143BC020000014362020000",
        "050505",
    ),
    1539: ("", "01432A040000", "050505"),
    1540: (
        "",
        "014306050000",
        "025032",
        "01438A040000",
        "050505",
    ),
    1541: (
        "023C",
        "014326020000",
        "025032",
        "01438A040000",
        "050505",
    ),
    1542: (
        "",
        "023C",
        "014396040000",
        "01439C010000",
        "023C",
        "014328030000050505",
    ),
}
PK_RECORD_MAP = {
    1537: 1567,
    1538: 1568,
    1539: 1569,
    1540: 1570,
    1541: 1571,
    1542: 1572,
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1542:3": "\n"}
SHARED_AUXILIARY = {
    ("SC", 1537): (
        (
            "已控制全国的大半部分。\n距离称霸畿内还剩",
            "城。\n在畿内还没有本家的城。",
        ),
        ("", "0232", "050505"),
    ),
    ("TC", 1537): (
        (
            "對全國的控制已過半數。\n距稱霸畿內尚餘",
            "城。\n畿內已無本家的城。",
        ),
        ("", "0232", "050505"),
    ),
    ("SC", 1538): (
        (
            "漂亮地压制了敌城。\n以此气势，\n把目标定为统一",
            "如何？",
        ),
        ("", "023C", "050505"),
    ),
    ("TC", 1538): (
        ("已成功壓制敵城。不妨乘勝追擊，\n達成", "統一如何？"),
        ("", "023C", "050505"),
    ),
    ("SC", 1539): (
        (
            "本家才是日本无人匹敌的武家。\n"
            "向天下宣告霸业，\n"
            "完成天下平定吧。",
        ),
        ("", "050505"),
    ),
    ("TC", 1539): (
        (
            "本家才是天下無雙的武家。\n"
            "務必主張稱霸天下，\n"
            "並且平定天下。",
        ),
        ("", "050505"),
    ),
    ("SC", 1540): (
        (
            "如今大人您才是天下。\n请达成统一全国的夙愿和\n",
            "的野心吧。",
        ),
        ("", "025032", "050505"),
    ),
    ("SC", 1541): (
        ("恭喜就任", "。\n请达成统一全国的夙愿和\n", "的野心吧。"),
        ("", "023C", "025032", "050505"),
    ),
    ("TC", 1541): (
        ("就任，真是可喜可賀。\n務必一償統一全國的宿願，\n實現", "的野望。"),
        ("023C", "025032", "050505"),
    ),
    ("SC", 1542): (
        (
            "首先，先确认下",
            "的情况。\n要想控制",
            "的话，\n必须要对此地有所了解。",
        ),
        ("", "023C", "023C", "050505"),
    ),
    ("TC", 1542): (
        ("首先將前往確認", "的狀況。\n欲控制", "就必須先了解該地。"),
        ("", "023C", "023C", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1537: (
        (
            "WeÖve conquered half of the nation. ",
            " castles must be seized to control the capital. We already have "
            "some castles in the area.",
        ),
        ("", "0232", "050505"),
    ),
    1538: (
        (
            "Well done conquering the enemy castle. Why donÖt you use that "
            "momentum to try and unify all of ",
            "?",
        ),
        ("", "023C", "050505"),
    ),
    1539: (
        (
            "Our clan is one of the two remaining houses in Japan. LetÖs "
            "set our sights on the ultimate conquest and unify the country.",
        ),
        ("", "050505"),
    ),
    1540: (
        ("LetÖs fulfill the ", "Ös ambition of uniting the country!"),
        ("", "025032", "050505"),
    ),
    1541: (
        (
            "You did well getting appointed as ",
            ". LetÖs fulfill the ",
            "Ös ambition of uniting the country!",
        ),
        ("", "023C", "025032", "050505"),
    ),
    1542: (
        (
            "We should first check on the situation in ",
            ". We must know what the place is like before we begin our conquest.",
        ),
        ("", "023C", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
AUXILIARY_OVERRIDES.update(
    {
        ("base", "TC", 1540): (
            (
                "只有",
                "才是真正的天下人。\n務必一償統一全國的宿願，\n實現",
                "的野望。",
            ),
            ("", "0143D0040000", "025032", "050505"),
        ),
        ("pk", "TC", 1540): (
            (
                "只有",
                "才是真正的天下人。\n務必一償統一全國的宿願，\n實現",
                "的野望。",
            ),
            ("", "014306050000", "025032", "050505"),
        ),
    }
)
BASIS = (
    "review_queue_base_msggame_B110_pristine_base_pc_jp_authoritative_"
    "kinai_and_national_unification_tutorial_with_directly_verified_base_"
    "1537_1542_to_pk_1567_1572_mapping_exact_sc_tc_and_actual_pk_en_context_"
    "explicit_1539_base_pk_jp_particle_wording_exception_and_1540_tc_side_"
    "opcode_difference_畿内_as_기나이_天下平定_as_천하_평정_天下人_as_"
    "천하인_当家_as_우리_가문_日の本_and_覇を唱える_naturalized_as_이_나라_"
    "and_패권_dynamic_region_title_house_tokens_one_hidden_lf_live_0143_"
    "stems_current_layout_and_protected_skeleton_preserved_runtime_fragment_"
    "pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if PK_RECORD_MAP != {
        1537: 1567,
        1538: 1568,
        1539: 1569,
        1540: 1570,
        1541: 1571,
        1542: 1572,
    }:
        raise RuntimeError("segment 912 direct Base/PK mapping drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_JP[record_id] != EXPECTED_PK_JP[record_id]
    } != {1539}:
        raise RuntimeError("segment 912 Base/PK JP exception set drifted")
    if "15:1542:3" in raw_translations or "15:1542:3" in translations:
        raise RuntimeError("segment 912 hidden LF received a decision")
    joined = "\n".join(translations.values())
    for required in (
        "기나이",
        "통일",
        "천하 평정",
        "천하인",
        "우리 가문",
        "이 나라",
        "패권",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 912 terminology drifted: {required}"
            )
    if any(term in joined for term in ("당가", "일본", "패를 외치")):
        raise RuntimeError(
            "segment 912 retained a forbidden or literalized expression"
        )
    stem_expectations = {
        "15:1537:0": "제압했으",
        "15:1537:3": "성은 없",
        "15:1538:2": "보심이",
        "15:1539:0": "이루",
        "15:1540:2": "이루",
        "15:1541:2": "이루",
        "15:1542:4": "알아야 하",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 912 live inflection stem drifted: {coordinate}"
            )
    if (
        AUXILIARY_OVERRIDES[("base", "TC", 1540)]
        == AUXILIARY_OVERRIDES[("pk", "TC", 1540)]
    ):
        raise RuntimeError("segment 912 1540 TC opcode difference collapsed")
    if len(raw_translations) != 22:
        raise RuntimeError("segment 912 visible decision count drifted")


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
    if len(rows) != 22 or len(translations) != 22:
        raise RuntimeError("segment 912 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 912 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 912 dynamic classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S912",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "hidden_lf_excluded": 1,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_exception_records": [1539],
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
