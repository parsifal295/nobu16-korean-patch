#!/usr/bin/env python3
"""Build Base authoring segment 973 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment972 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S973.private.v1.jsonl"
)
SEGMENT = 973
CASTLE_TOKEN = PREVIOUS.CASTLE_TOKEN
FORCE_TOKEN = "025032"
PERSON_TOKEN = "024833"
OFFICER_TOKEN = PREVIOUS.OFFICER_TOKEN
UNIT_TOKEN = "029632"
VALUE_TOKEN = "0232"
COUNT_TOKEN = "0233"
TRANSLATIONS_BY_RECORD = {
    2184: (
        "의 병량을 ",
        " 회복, 농촌 ",
        "개 지배 해제",
    ),
    2185: (
        "의 병량을 ",
        " 회복, 농촌의 지배 해제",
    ),
    2186: (
        "이(가)",
        "에게서\n조략을 받고 있는 듯",
        "\n출병하여 방해하",
    ),
    2187: (
        "이(가)\n",
        "에게 걸어 둔 조략을\n출진하여 밝혀내",
    ),
    2188: (
        "은(는) 지금 병사를 내지 않으면\n",
        "에게 피해를 입",
        "\n부디 결단을",
    ),
    2189: (
        "이(가)\n",
        "의 ",
        "에게서\n조략을 받",
    ),
    2190: (
        "이(가)",
        "의 ",
        "에게서 조략을 받음",
    ),
    2191: (
        "고마운",
        "지휘로다!\n반드시",
        "기대에 부응해 보이",
    ),
    2192: (
        "에게",
        "\n훌륭히 해내 보이",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2184: ("の兵糧を", "回復、農村", "個の支配解除"),
    2185: ("の兵糧を", "回復、農村の支配解除"),
    2186: ("が", "から\n調略を受けているよう", "\n出兵し、妨害して"),
    2187: ("が\n", "に仕掛けている調略を\n出陣して暴いて"),
    2188: (
        "は、今、兵を出さねば\n",
        "からの害を被",
        "\nどうか、ご決断を",
    ),
    2189: ("が\n", "の", "から\n調略を受け"),
    2190: ("が", "の", "から調略を受けた"),
    2191: ("ありがたき", "采配！\n必ず", "期待に応えてみせ"),
    2192: ("に", "\n見事成し遂げてみせ"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2184: (CASTLE_TOKEN, VALUE_TOKEN, COUNT_TOKEN, "050505"),
    2185: (CASTLE_TOKEN, VALUE_TOKEN, "050505"),
    2186: (
        UNIT_TOKEN,
        FORCE_TOKEN,
        "01431A020000",
        "014300040000050505",
    ),
    2187: (FORCE_TOKEN, UNIT_TOKEN, "014300040000050505"),
    2188: (UNIT_TOKEN, FORCE_TOKEN, "014336040000", "050505"),
    2189: (UNIT_TOKEN, FORCE_TOKEN, PERSON_TOKEN, "014314020000050505"),
    2190: (UNIT_TOKEN, FORCE_TOKEN, OFFICER_TOKEN, "050505"),
    2191: ("", "01438A040000", "01438A040000", "01433C040000050505"),
    2192: ("014301000000", "01437C030000", "01431E040000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2186: (
        UNIT_TOKEN,
        FORCE_TOKEN,
        "014326020000",
        "01430C040000050505",
    ),
    2187: (FORCE_TOKEN, UNIT_TOKEN, "01430C040000050505"),
    2188: (UNIT_TOKEN, FORCE_TOKEN, "014342040000", "050505"),
    2189: (UNIT_TOKEN, FORCE_TOKEN, PERSON_TOKEN, "01431A020000050505"),
    2191: ("", "014396040000", "014396040000", "014348040000050505"),
    2192: ("014301000000", "014388030000", "01432A040000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2184): (
        ("的军粮恢复", "，解除对", "个农村的支配。"),
        (CASTLE_TOKEN, VALUE_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("TC", 2184): (
        ("將", "的軍糧恢復", "，解除", "個農村的支配。"),
        ("", CASTLE_TOKEN, VALUE_TOKEN, COUNT_TOKEN, "050505"),
    ),
    ("SC", 2185): (
        ("的军粮恢复", "，解除对农村的支配。"),
        (CASTLE_TOKEN, VALUE_TOKEN, "050505"),
    ),
    ("TC", 2185): (
        ("將", "的軍糧恢復", "，解除農村的支配。"),
        ("", CASTLE_TOKEN, VALUE_TOKEN, "050505"),
    ),
    ("SC", 2186): (
        ("好像遭到了来自\n", "的谋略，\n立即出兵，进行妨害吧。"),
        (UNIT_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("TC", 2186): (
        ("獲", "指示計謀，\n出兵並予以阻撓。"),
        (UNIT_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("SC", 2187): (
        ("向\n", "所用之谋略，\n出阵将其揭穿吧。"),
        (FORCE_TOKEN, UNIT_TOKEN, "050505"),
    ),
    ("TC", 2187): (
        ("向\n", "施展計謀，\n出征予以痛擊。"),
        (FORCE_TOKEN, UNIT_TOKEN, "050505"),
    ),
    ("SC", 2188): (
        ("若现在不出兵，\n将会蒙受来自", "的重大损失，\n还请做出决定。"),
        (UNIT_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("TC", 2188): (
        ("，現在若不出兵，\n勢必將遭到", "的迫害。\n還請大人裁奪。"),
        (UNIT_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("SC", 2189): (
        ("中了\n来自", "的", "\n的谋略。"),
        (UNIT_TOKEN, FORCE_TOKEN, PERSON_TOKEN, "050505"),
    ),
    ("TC", 2189): (
        ("遭受", "的\n", "之謀略。"),
        (UNIT_TOKEN, FORCE_TOKEN, PERSON_TOKEN, "050505"),
    ),
    ("SC", 2190): (
        ("遭受了", "的\n", "之谋略。"),
        (UNIT_TOKEN, FORCE_TOKEN, OFFICER_TOKEN, "050505"),
    ),
    ("TC", 2190): (
        ("遭受", "的", "之謀略。"),
        (UNIT_TOKEN, FORCE_TOKEN, OFFICER_TOKEN, "050505"),
    ),
    ("SC", 2191): (
        ("感激不尽，\n必竭尽全力完成任务。",),
        ("", "050505"),
    ),
    ("TC", 2191): (
        ("真是感激不盡！\n必當全力以赴，\n達成使命！",),
        ("", "050505"),
    ),
    ("SC", 2192): (
        ("交给我吧，\n一定会完成。",),
        ("", "050505"),
    ),
    ("TC", 2192): (
        ("交給", "來吧。\n必將達成任務。"),
        ("", "014301000000", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2184: (
        (" restored ", " supplies. Control over ", " farm(s) has been removed."),
        (CASTLE_TOKEN, VALUE_TOKEN, COUNT_TOKEN, "050505"),
    ),
    2185: (
        (" restored ", " supplies. Control over the farm has been removed."),
        (CASTLE_TOKEN, VALUE_TOKEN, "050505"),
    ),
    2186: (
        (
            "It appears that ",
            " has been the victim of the ",
            "Ös schemes. LetÖs deploy our soldiers to put a stop to it.",
        ),
        ("", UNIT_TOKEN, FORCE_TOKEN, "050505"),
    ),
    2187: (
        (
            "Let us march our soldiers and disrupt the covert action the ",
            " are hatching against ",
            ".",
        ),
        ("", FORCE_TOKEN, UNIT_TOKEN, "050505"),
    ),
    2188: (
        (
            " will suffer harm at the ",
            "Ös hands if we do not deploy our soldiers now. "
            "Please make a decision.",
        ),
        (UNIT_TOKEN, FORCE_TOKEN, "050505"),
    ),
    2189: (
        (" has suffered covert action from ", " of the ", "."),
        (UNIT_TOKEN, PERSON_TOKEN, FORCE_TOKEN, "050505"),
    ),
    2190: (
        (" has suffered covert action from ", " of the ", "."),
        (UNIT_TOKEN, OFFICER_TOKEN, FORCE_TOKEN, "050505"),
    ),
    2191: (
        (
            "I am well pleased to receive your command! "
            "I will certainly meet your expectations.",
        ),
        ("", "050505"),
    ),
    2192: (
        ("You can count on me! My accomplishments shall be a marvel to behold!",),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B116_C_pristine_base_pc_jp_authoritative_"
    "provision_recovery_settlement_release_counter_subversion_reports_and_"
    "command_responses_with_explicit_base2184_2192_to_pk2214_2222_mapping_"
    "exact_base_pk_jp_sc_tc_literals_dynamic_castle_value_count_force_"
    "person_officer_and_unit_token_direction_兵糧_as_byengnyang_賦課_as_"
    "bugwa_調略_as_joryak_出兵_as_chulbyeong_出陣_as_chuljin_采配_as_"
    "jihwi_historical_register_and_current_korean_morphology_terminal_"
    "corpora_all_base_pk_opcode_divergences_recorded_ascii_punctuation_"
    "current_line_counts_and_protected_skeleton_preserved_runtime_fragment_"
    "pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    1: ("소승", "나", "저", "소인", "이 몸"),
    532: ("했습니다", "다"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    892: ("맡겨 주시오", "맡겨 주게", "맡겨라", "맡겨 주십시오"),
    1024: ("드리겠습니다", "하자", "내리겠노라", "드리겠소"),
    1054: ("합시다", "듯"),
    1078: ("합니다", "다"),
    1084: ("합니다", "다", "하옵니다"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    1: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1],
    538: EXPECTED_BASE_MORPHOLOGY_TERMINALS[532],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    904: EXPECTED_BASE_MORPHOLOGY_TERMINALS[892],
    1036: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1024],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1090: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1078],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 973 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 973 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2186, 2187, 2188, 2189, 2191, 2192}:
        raise RuntimeError("segment 973 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 973 pristine/current gap drifted")
    if EXPECTED_BASE_GAPS[2184] != (
        CASTLE_TOKEN,
        VALUE_TOKEN,
        COUNT_TOKEN,
        "050505",
    ) or EXPECTED_BASE_GAPS[2185] != (
        CASTLE_TOKEN,
        VALUE_TOKEN,
        "050505",
    ):
        raise RuntimeError("segment 973 provision recovery token direction drifted")
    if (
        any(
            EXPECTED_BASE_GAPS[record_id][0] != UNIT_TOKEN
            for record_id in (2186, 2188, 2189, 2190)
        )
        or EXPECTED_BASE_GAPS[2187][:2] != (FORCE_TOKEN, UNIT_TOKEN)
    ):
        raise RuntimeError("segment 973 unit-token subject direction drifted")
    if (
        EXPECTED_BASE_GAPS[2189][2] != PERSON_TOKEN
        or EXPECTED_BASE_GAPS[2190][2] != OFFICER_TOKEN
    ):
        raise RuntimeError("segment 973 person/officer token distinction drifted")
    if any(
        OFFICER_TOKEN in gap
        for gap in EXPECTED_BASE_GAPS[2191]
    ):
        raise RuntimeError("segment 973 Base2191 invented an officer-name token")
    if (
        not raw_translations["15:2184:0"].endswith(" ")
        or not raw_translations["15:2184:1"].startswith(" ")
        or not raw_translations["15:2184:1"].endswith(" ")
        or not raw_translations["15:2185:0"].endswith(" ")
        or not raw_translations["15:2185:1"].startswith(" ")
    ):
        raise RuntimeError("segment 973 numeric-token spacing drifted")
    joined = "\n".join(translations.values())
    for required in ("병량", "농촌", "조략", "출병", "출진", "지휘"):
        if required not in joined:
            raise RuntimeError(
                f"segment 973 historical terminology drifted: {required}"
            )
    for forbidden in ("식량", "계략", "출동", "。", "！"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 973 forbidden wording retained: {forbidden}"
            )
    if (
        "출병하여 방해하" not in TRANSLATIONS_BY_RECORD[2186][2]
        or "출진하여 밝혀내" not in TRANSLATIONS_BY_RECORD[2187][1]
        or TRANSLATIONS_BY_RECORD[2190][2] != "에게서 조략을 받음"
        or TRANSLATIONS_BY_RECORD[2192][0] != "에게"
    ):
        raise RuntimeError("segment 973 action or dative distinction drifted")
    if len(raw_translations) != 24 or len(translations) != 24:
        raise RuntimeError("segment 973 visible decision count drifted")


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
    SUPPORT.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 24 or len(validated) != len(translations):
        raise RuntimeError("segment 973 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 973 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S973",
                "source_literal_count": 24,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    2186,
                    2187,
                    2188,
                    2189,
                    2191,
                    2192,
                ],
                "pristine_current_gap_divergence_records": [],
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": {
                    line_count: sum(
                        text.count("\n") + 1 == line_count
                        for text in translations.values()
                    )
                    for line_count in (1, 2, 3)
                },
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
