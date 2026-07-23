#!/usr/bin/env python3
"""Build Base authoring segment 925 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment923 as COMMON_SEGMENT


COMMON = COMMON_SEGMENT.COMMON
ENGINE = COMMON_SEGMENT.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S925.private.v1.jsonl"
)
SEGMENT = 925
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1677:0": "님,",
    "15:1677:1": "합전",
    "15:1677:2": (
        "의 지휘를 맡아 주십시오!\n"
        "직접 지휘하신다면\n"
        "단기 결착을 기대할 수 있"
    ),
    "15:1678:0": "합전",
    "15:1678:1": "을 지휘할 절호의 기회",
    "15:1678:2": "!\n",
    "15:1678:3": "아군을 승리로 이끌어",
    "15:1679:1": "합전",
    "15:1679:2": "을 지휘",
    "15:1679:3": "인가?\n",
    "15:1679:4": (
        "님의 지휘라면\n"
        "병사들도 용기백배하여 떨쳐 일어날 것이옵니다"
    ),
}
RECORD_ARITIES = {
    1677: 3,
    1678: 4,
    1679: 5,
}
EXPECTED_BASE_JP = {
    1677: (
        "、",
        "合戦",
        "の指揮を！\n直々の指揮であれば\n短期決着が望め",
    ),
    1678: (
        "合戦",
        "指揮の好機",
        "！\n",
        "味方を勝利へと導いて",
    ),
    1679: (
        "",
        "合戦",
        "を指揮",
        "か？\n",
        "の指揮とあらば\n兵たちも勇み奮い立つこと必定かと",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1677: (
        "014308000000",
        "1b434d",
        "1b435a",
        "01431e040000050505",
    ),
    1678: (
        "1b434d",
        "1b435a",
        "01431a020000",
        "014384040000",
        "014342010000050505",
    ),
    1679: (
        "",
        "1b434d",
        "1b435a",
        "0143cc010000",
        "014308000000",
        "050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1677: (
        "014308000000",
        "1b434d",
        "1b435a",
        "01432a040000050505",
    ),
    1678: (
        "1b434d",
        "1b435a",
        "014326020000",
        "014390040000",
        "014342010000050505",
    ),
    1679: (
        "",
        "1b434d",
        "1b435a",
        "0143d2010000",
        "014308000000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    1677: 1707,
    1678: 1708,
    1679: 1709,
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1679:0": ""}

SHARED_AUXILIARY = {
    ("SC", 1677): (
        ("，请指挥", "合战", "！\n如果有您直接指挥，\n我们便有可能速战速决。"),
        ("014308000000", "1b434d", "1b435a", "050505"),
    ),
    ("TC", 1677): (
        ("，請指揮", "會戰", "！\n親自指揮可望\n用短期定勝負。"),
        ("014308000000", "1b434d", "1b435a", "050505"),
    ),
    ("SC", 1678): (
        ("正是指挥", "合战", "的大好时机！\n请带领我方得胜吧。"),
        ("", "1b434d", "1b435a", "050505"),
    ),
    ("TC", 1678): (
        ("現為指揮", "會戰", "的良機！\n引導我方邁向勝利吧！"),
        ("", "1b434d", "1b435a", "050505"),
    ),
    ("SC", 1679): (
        ("指挥", "合战", "吗？\n如果是", "的指挥，\n士兵也定将奋勇作战。"),
        ("", "1b434d", "1b435a", "014308000000", "050505"),
    ),
    ("TC", 1679): (
        ("是否要指揮", "會戰", "？\n若能由", "指揮，\n想必士兵們也會鬥志昂揚。"),
        ("", "1b434d", "1b435a", "014308000000", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1677: (
        (
            "Lead us into ",
            "battle",
            "! WeÖll count on your instructions to settle this quickly.",
        ),
        ("", "1b434d", "1b435a", "050505"),
    ),
    1678: (
        (
            "This is your chance to lead the ",
            "battle",
            "! Show our allies the path to victory!",
        ),
        ("", "1b434d", "1b435a", "050505"),
    ),
    1679: (
        (
            "Would you like to lead this ",
            "battle",
            "? IÖm sure your orders will fill the soldiers with courage.",
        ),
        ("", "1b434d", "1b435a", "050505"),
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
    "review_queue_base_msggame_B111_B_pristine_base_pc_jp_authoritative_"
    "battle_command_advice_with_explicit_base1677_to1679_pk1707_to1709_"
    "plus30_mapping_exact_base_pk_sc_tc_and_pk_en_auxiliary_context_battle_"
    "command_glossary_person_token_honorific_subject_voice_colour_tags_and_"
    "live_inflection_preserved_base1679_leading_nonvisible_literal_excluded"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "합전",
        "지휘",
        "직접 지휘",
        "승리",
        "병사",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 925 required terminology drifted: {required}")
    for forbidden in ("회전", "전투", "。", "、", "！"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 925 retained forbidden terminology: {forbidden}"
            )
    if raw_translations["15:1677:0"] != "님,":
        raise RuntimeError("segment 925 record 1677 person honorific drifted")
    if raw_translations["15:1677:2"].splitlines() != [
        "의 지휘를 맡아 주십시오!",
        "직접 지휘하신다면",
        "단기 결착을 기대할 수 있",
    ]:
        raise RuntimeError("segment 925 record 1677 command meaning drifted")
    if (
        raw_translations["15:1678:0"] + raw_translations["15:1678:1"]
        != "합전을 지휘할 절호의 기회"
    ):
        raise RuntimeError("segment 925 record 1678 colour-boundary assembly drifted")
    if (
        raw_translations["15:1679:1"] + raw_translations["15:1679:2"]
        != "합전을 지휘"
    ):
        raise RuntimeError("segment 925 record 1679 colour-boundary assembly drifted")
    if not raw_translations["15:1679:4"].startswith("님의 지휘라면\n"):
        raise RuntimeError("segment 925 record 1679 person-token relation drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:1679:0": ""}:
        raise RuntimeError("segment 925 leading nonvisible literal exclusion drifted")
    pristine_literals = ENGINE.parse_record_literals(source_records[(15, 1679)])
    if pristine_literals[0].text != "":
        raise RuntimeError("segment 925 pristine leading nonvisible literal drifted")
    if set(PK_RECORD_MAP.items()) != {
        (1677, 1707),
        (1678, 1708),
        (1679, 1709),
    }:
        raise RuntimeError("segment 925 explicit Base-to-PK mapping drifted")


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
    if len(rows) != 11 or len(translations) != 11:
        raise RuntimeError("segment 925 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 925 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S925",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "hidden_leading_literal_excluded": 1,
                "explicit_plus30_pk_mapping": True,
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
