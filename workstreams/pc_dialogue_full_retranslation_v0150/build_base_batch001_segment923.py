#!/usr/bin/env python3
"""Build Base authoring segment 923 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment908 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S923.private.v1.jsonl"
)
SEGMENT = 923
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1657:0": (
        "이(가) 우리 가문에 품은 인상은 충분히 좋으니\n"
        "동맹 체결을 제안해 보시는 것이\n"
    ),
    "15:1658:0": (
        "와(과)의 친선으로\n"
        "동맹에 필요한 신용을 얻어"
    ),
    "15:1658:1": "\n교섭을 통해 제안하",
    "15:1659:0": (
        "이(가) 우리 가문에 품은 인상은 충분히 좋으니\n"
        "동맹 연장을 제안해 보시는 것이\n"
    ),
    "15:1660:0": (
        "와(과)의 친선으로\n"
        "동맹 연장에 필요한 신용을 얻어"
    ),
    "15:1660:1": "\n교섭을 통해 제안하",
    "15:1661:0": (
        "이(가) 우리 가문에 품은 인상은 충분히 좋으니\n"
        "혼인 동맹 체결을 제안해 보시는 것이\n"
    ),
    "15:1662:0": (
        "와(과)의 친선으로\n"
        "혼인 동맹에 필요한 신용을 얻어"
    ),
    "15:1662:1": "\n교섭을 통해 제안하",
    "15:1663:0": "을(를) 맞아 싸우기보다\n",
    "15:1663:1": (
        "을(를) 중개자로 세워\n"
        "정전을 교섭해 보는 것은 어떻겠습니까?"
    ),
    "15:1664:0": "우리의 적,",
    "15:1664:1": (
        "에게\n"
        "정전을 제의해 보시는 것이"
    ),
    "15:1664:3": "이(가) 중개를 맡",
    "15:1665:0": "와(과)의 정전…\n",
    "15:1665:1": (
        "에게 중개를 부탁하면\n"
        "성사될지도 모르"
    ),
    "15:1666:0": "싸우면 많은 병사를 잃게 됩니다\n",
    "15:1666:1": "와(과) 정전을 맺고자\n",
    "15:1666:2": "에게 중개를 의뢰해 보시면 어떻겠습니까",
    "15:1667:0": (
        "막부의 신용을 얻은 지금\n"
        "막부 역직을 교섭으로\n"
        "요구해 보는 것은 어떻겠습니까?"
    ),
    "15:1668:0": (
        "막부와의 친선이 결실을 맺어\n"
        "역직에 필요한 신용을 얻어"
    ),
    "15:1668:1": "\n교섭해야 할 듯하옵니다",
}
RECORD_ARITIES = {
    1657: 1,
    1658: 2,
    1659: 1,
    1660: 2,
    1661: 1,
    1662: 2,
    1663: 2,
    1664: 4,
    1665: 2,
    1666: 3,
    1667: 1,
    1668: 2,
}
EXPECTED_BASE_JP = {
    1657: ("の心証は十分\n同盟の締結を持ちかけては\n",),
    1658: (
        "との親善により\n同盟に足る信用を得",
        "\n交渉にて持ちかけ",
    ),
    1659: ("の心証は十分\n同盟の延長を持ちかけては\n",),
    1660: (
        "との親善により\n同盟延長に足る信用を得",
        "\n交渉にて持ちかけ",
    ),
    1661: ("の心証は十分\n婚姻同盟の締結を持ちかけては\n",),
    1662: (
        "との親善により\n婚姻同盟に足る信用を得",
        "\n交渉にて持ちかけ",
    ),
    1663: (
        "を迎え撃つのではなく\n",
        "を仲介に立て\n停戦を交渉してみては？",
    ),
    1664: (
        "我らが敵、",
        "に対し\n停戦を申し出ては",
        "\n",
        "が仲介とな",
    ),
    1665: (
        "との停戦…\n",
        "に仲介を頼めば\n成し遂げられるやもしれ",
    ),
    1666: (
        "戦えば、多くの兵を失うこととなります\n",
        "と停戦すべく、\n",
        "に仲介を依頼してはいかがでしょう",
    ),
    1667: ("幕府よりの信用がある今\n幕府役職を交渉にて\n要求してみては？",),
    1668: (
        "幕府との親善が実を結び\n役職に足る信用を得",
        "\n交渉すべきかと",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1657: ("025032", "0143b0020000014356020000050505"),
    1658: ("025032", "014314020000", "01431e040000050505"),
    1659: ("025032", "0143b0020000014356020000050505"),
    1660: ("025032", "014314020000", "01431e040000050505"),
    1661: ("025032", "0143b0020000014356020000050505"),
    1662: ("025032", "014314020000", "01431e040000050505"),
    1663: ("025032", "025132", "050505"),
    1664: (
        "",
        "025032",
        "0143b0020000014356020000",
        "025132",
        "01435a040000050505",
    ),
    1665: ("025032", "025132", "0143e0020000050505"),
    1666: ("", "025032", "025032", "050505"),
    1667: ("", "050505"),
    1668: ("", "014314020000", "0143e2000000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1657: ("025032", "0143bc020000014362020000050505"),
    1658: ("025032", "01431a020000", "01432a040000050505"),
    1659: ("025032", "0143bc020000014362020000050505"),
    1660: ("025032", "01431a020000", "01432a040000050505"),
    1661: ("025032", "0143bc020000014362020000050505"),
    1662: ("025032", "01431a020000", "01432a040000050505"),
    1664: (
        "",
        "025032",
        "0143bc020000014362020000",
        "025132",
        "014366040000050505",
    ),
    1665: ("025032", "025132", "0143ec020000050505"),
    1668: ("", "01431a020000", "0143e2000000050505"),
}
PK_RECORD_MAP = {
    1657: 1687,
    1658: 1688,
    1659: 1689,
    1660: 1690,
    1661: 1691,
    1662: 1692,
    1663: 1693,
    1664: 1694,
    1665: 1695,
    1666: 1696,
    1667: 1697,
    1668: 1698,
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1665:0"}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1664:2": "\n"}
STATIC_RECORD_IDS = {1667}

SHARED_AUXILIARY = {
    ("SC", 1657): (
        ("足以信赖，\n提出缔结同盟一事如何？",),
        ("025032", "050505"),
    ),
    ("TC", 1657): (
        ("足以信賴，\n提出締結同盟一事如何？",),
        ("025032", "050505"),
    ),
    ("SC", 1658): (
        ("因与", "的亲善，\n已获足以同盟的信赖，\n进行交涉，斡旋同盟吧。"),
        ("", "025032", "050505"),
    ),
    ("TC", 1658): (
        ("因與", "的親善，\n已獲足以同盟的信賴，\n進行交涉，斡旋同盟吧。"),
        ("", "025032", "050505"),
    ),
    ("SC", 1659): (
        ("足以信赖，\n提出延长同盟一事如何？",),
        ("025032", "050505"),
    ),
    ("TC", 1659): (
        ("足以信賴，\n提出延長同盟一事如何？",),
        ("025032", "050505"),
    ),
    ("SC", 1660): (
        ("因与", "的亲善，\n已获足以延长同盟的信赖，\n进行交涉，斡旋延长吧。"),
        ("", "025032", "050505"),
    ),
    ("TC", 1660): (
        ("因與", "的親善，\n已獲足以延長同盟的信賴，\n進行交涉，斡旋延長吧。"),
        ("", "025032", "050505"),
    ),
    ("SC", 1661): (
        ("足以信赖，\n提出缔结联姻一事如何？",),
        ("025032", "050505"),
    ),
    ("TC", 1661): (
        ("足以信賴，\n提出締結聯姻一事如何？",),
        ("025032", "050505"),
    ),
    ("SC", 1662): (
        ("因与", "的亲善，\n已获足以联姻的信赖，\n进行交涉，斡旋联姻吧。"),
        ("", "025032", "050505"),
    ),
    ("TC", 1662): (
        ("因與", "的親善，\n已獲足以聯姻的信賴，\n進行交涉，斡旋聯姻吧。"),
        ("", "025032", "050505"),
    ),
    ("SC", 1664): (
        ("向", "提出停战请求如何？\n就让", "来调停吧。"),
        ("", "025032", "025132", "050505"),
    ),
    ("SC", 1667): (
        ("如今已拥有幕府的信赖，\n进行交涉，要求\n幕府官职如何？",),
        ("", "050505"),
    ),
    ("TC", 1667): (
        ("如今已擁有幕府的信賴，\n進行交涉，要求\n幕府官職如何？",),
        ("", "050505"),
    ),
    ("SC", 1668): (
        ("与幕府的亲善已有成果，\n已获足以就任官职的信赖，\n应进行交涉吧。",),
        ("", "050505"),
    ),
    ("TC", 1668): (
        ("與幕府的親善已有成果，\n已獲足以就任官職的信賴，\n應進行交涉吧。",),
        ("", "050505"),
    ),
}
SIDE_AUXILIARY = {
    ("base", "TC", 1664): (
        ("向", "提議停戰如何？\n就由", "來調解吧。"),
        ("", "025032", "025132", "050505"),
    ),
    ("pk", "TC", 1664): (
        ("向", "提議停戰如何？\n就由", "來調停吧。"),
        ("", "025032", "025132", "050505"),
    ),
    ("base", "SC", 1663): (
        ("非迎击", "，\n请", "进行仲裁，\n交涉停战如何？"),
        ("", "025032", "025132", "050505"),
    ),
    ("base", "TC", 1663): (
        ("非迎擊", "，\n請", "進行仲裁，\n交涉停戰如何？"),
        ("", "025032", "025132", "050505"),
    ),
    ("pk", "SC", 1663): (
        ("非迎击", "，\n请", "进行调停，\n交涉停战如何？"),
        ("", "025032", "025132", "050505"),
    ),
    ("pk", "TC", 1663): (
        ("非迎擊", "，\n請", "進行調停，\n交涉停戰如何？"),
        ("", "025032", "025132", "050505"),
    ),
    ("base", "SC", 1665): (
        ("与", "停战……\n委托", "仲裁的话，\n或许能达成协议吧。"),
        ("", "025032", "025132", "050505"),
    ),
    ("base", "TC", 1665): (
        ("與", "停戰……\n委託", "仲裁的話，\n或許能達成協議吧。"),
        ("", "025032", "025132", "050505"),
    ),
    ("pk", "SC", 1665): (
        ("与", "停战……\n委托", "调停的话，\n或许能达成协议吧。"),
        ("", "025032", "025132", "050505"),
    ),
    ("pk", "TC", 1665): (
        ("與", "停戰……\n委託", "調停的話，\n或許能達成協議吧。"),
        ("", "025032", "025132", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1657: (
        ("The ", " have a good opinion of us, so why donÖt we form an alliance?"),
        ("", "025032", "050505"),
    ),
    1658: (
        (
            "The goodwill between us and the ",
            " has produced sufficient trust to form an alliance. Shall we begin negotiations?",
        ),
        ("", "025032", "050505"),
    ),
    1659: (
        ("The ", " have a good opinion of us, so why donÖt we extend our alliance?"),
        ("", "025032", "050505"),
    ),
    1660: (
        (
            "The goodwill between us and the ",
            " has produced sufficient trust to extend our alliance. Shall we begin negotiations?",
        ),
        ("", "025032", "050505"),
    ),
    1661: (
        (
            "The ",
            " have a good opinion of us, so why donÖt we form a marriage alliance?",
        ),
        ("", "025032", "050505"),
    ),
    1662: (
        (
            "The goodwill between us and the ",
            " has produced sufficient trust to form a marriage alliance. Shall we begin negotiations?",
        ),
        ("", "025032", "050505"),
    ),
    1663: (
        (
            "Instead of attacking the ",
            ", why donÖt we mediate a truce through the ",
            "?",
        ),
        ("", "025032", "025132", "050505"),
    ),
    1664: (
        (
            "Why donÖt we offer a truce to our enemy, the ",
            "? The ",
            " could act as intermediary.",
        ),
        ("", "025032", "025132", "050505"),
    ),
    1665: (
        (
            "A truce with the ",
            "? If we asked ",
            " to mediate, it might just be possible.",
        ),
        ("", "025032", "025132", "050505"),
    ),
    1667: (
        (
            "Why not negotiate for a shªgunate title now that youÖve gained the governmentÖs trust?",
        ),
        ("", "050505"),
    ),
    1668: (
        (
            "The goodwill with the shªgunate is paying off. It might be time to negotiate for a title.",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, language, record_id): expected
        for (language, record_id), expected in SHARED_AUXILIARY.items()
        for side in ("base", "pk")
    },
    **SIDE_AUXILIARY,
    **{
        ("pk", "EN", record_id): expected
        for record_id, expected in PK_EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B111_B_pristine_base_pc_jp_authoritative_"
    "alliance_extension_marriage_alliance_mediated_truce_and_shogunate_"
    "office_requests_with_explicit_base1657_to1668_pk1687_to1698_plus30_"
    "mapping_exact_base_pk_sc_tc_and_pk_en_auxiliary_context_base_pk1666_"
    "blank_auxiliary_exception_impression_trust_alliance_marriage_alliance_"
    "truce_intermediary_shogunate_office_glossary_runtime_token_subject_"
    "target_voice_and_live_inflection_preserved_hidden1664_lf_excluded"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "인상",
        "신용",
        "동맹",
        "혼인 동맹",
        "정전",
        "중개",
        "막부",
        "역직",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 923 required terminology drifted: {required}")
    for forbidden in (
        "호감",
        "의 인상은 충분",
        "막부 직책",
        "관직",
        "仲介",
        "停戦",
        "。",
        "、",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 923 retained forbidden terminology: {forbidden}"
            )
    opinion_actions = {
        "15:1657:0": "동맹 체결",
        "15:1659:0": "동맹 연장",
        "15:1661:0": "혼인 동맹 체결",
    }
    for coordinate, action in opinion_actions.items():
        expected = (
            "이(가) 우리 가문에 품은 인상은 충분히 좋으니\n"
            f"{action}을 제안해 보시는 것이\n"
        )
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 923 心証 wording drifted: {coordinate}"
            )
    for coordinate, ending in {
        "15:1658:0": "얻어",
        "15:1658:1": "제안하",
        "15:1660:0": "얻어",
        "15:1660:1": "제안하",
        "15:1662:0": "얻어",
        "15:1662:1": "제안하",
        "15:1664:1": "것이",
        "15:1664:3": "맡",
        "15:1665:1": "모르",
        "15:1668:0": "얻어",
    }.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 923 live inflection stem drifted: {coordinate}"
            )
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:1664:2": "\n"}:
        raise RuntimeError("segment 923 hidden LF exclusion drifted")
    if tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, 1664)])
    )[2] != "\n":
        raise RuntimeError("segment 923 pristine hidden LF drifted")
    blank_exception = {1666}
    if any(
        key in AUXILIARY_OVERRIDES
        for key in (
            ("base", "SC", 1666),
            ("base", "TC", 1666),
            ("pk", "SC", 1666),
            ("pk", "TC", 1666),
            ("pk", "EN", 1666),
        )
    ):
        raise RuntimeError("segment 923 blank auxiliary exception drifted")
    if blank_exception != {1666}:
        raise RuntimeError("segment 923 blank auxiliary record set drifted")
    if set(PK_RECORD_MAP.items()) != {
        (1657, 1687),
        (1658, 1688),
        (1659, 1689),
        (1660, 1690),
        (1661, 1691),
        (1662, 1692),
        (1663, 1693),
        (1664, 1694),
        (1665, 1695),
        (1666, 1696),
        (1667, 1697),
        (1668, 1698),
    }:
        raise RuntimeError("segment 923 explicit Base-to-PK mapping drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows = COMMON.build_segment_rows_with_current_gaps(
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
    for row in rows:
        record_id = int(str(row["coordinate"]).split(":")[1])
        if record_id in STATIC_RECORD_IDS:
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 22 or len(translations) != 22:
        raise RuntimeError("segment 923 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 923 validated count drifted")
    retranslated = sum(
        row["scope_classification"] == "retranslated" for row in rows
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S923",
                "decision_count": len(rows),
                "retranslated": retranslated,
                "runtime_fragment_pending": len(rows) - retranslated,
                "hidden_lf_excluded": 1,
                "explicit_plus30_pk_mapping": True,
                "blank_auxiliary_records": [1666],
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
