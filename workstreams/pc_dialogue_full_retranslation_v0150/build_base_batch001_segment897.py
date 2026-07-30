#!/usr/bin/env python3
"""Build Base authoring segment 897 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment896 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S897.private.v1.jsonl"
)
SEGMENT = 897
RONIN_RECRUITMENT_BASE_START = PREVIOUS.RONIN_RECRUITMENT_BASE_START
RONIN_RECRUITMENT_SOURCE_JP = PREVIOUS.RONIN_RECRUITMENT_SOURCE_JP
RONIN_RECRUITMENT_CANONICAL = PREVIOUS.RONIN_RECRUITMENT_CANONICAL
RONIN_RECRUITMENT_BASE_GAPS = PREVIOUS.RONIN_RECRUITMENT_BASE_GAPS
RONIN_RECRUITMENT_PK_GAPS = PREVIOUS.RONIN_RECRUITMENT_PK_GAPS
RONIN_RECRUITMENT_ARITIES = PREVIOUS.RONIN_RECRUITMENT_ARITIES
RONIN_RECRUITMENT_REPEAT_START = PREVIOUS.RONIN_RECRUITMENT_REPEAT_START
ronin_repeat_index = PREVIOUS.ronin_repeat_index
make_auxiliary_overrides = PREVIOUS.make_auxiliary_overrides
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1427:1": "\n"}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id in range(1419, 1428)
    for literal_id, translation in enumerate(
        RONIN_RECRUITMENT_CANONICAL[
            ronin_repeat_index(record_id)
        ]
    )
    if f"15:{record_id}:{literal_id}"
    not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: RONIN_RECRUITMENT_ARITIES[
        ronin_repeat_index(record_id)
    ]
    for record_id in range(1419, 1428)
}
EXPECTED_BASE_JP = {
    record_id: RONIN_RECRUITMENT_SOURCE_JP[
        ronin_repeat_index(record_id)
    ]
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: RONIN_RECRUITMENT_BASE_GAPS[
        ronin_repeat_index(record_id)
    ]
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = {
    record_id: RONIN_RECRUITMENT_PK_GAPS[
        ronin_repeat_index(record_id)
    ]
    for record_id in RECORD_ARITIES
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
SHARED_AUXILIARY = {
    ("SC", 1419): (
        (
            "我叫",
            "。\n既然有缘侍奉",
            "大人，\n我定会为您立下汗马功劳。",
        ),
        ("", "024633", "024735", "050505"),
    ),
    ("TC", 1419): (
        (
            "吾人名為",
            "，\n因緣際會下於此前來效命，\n誓必成為",
            "大人的生力軍。",
        ),
        ("", "024633", "024735", "050505"),
    ),
    ("SC", 1420): (
        (
            "蒙您垂青，不胜荣幸。\n以后我",
            "就是\n",
            "大人的利刃，任您驱驰。",
        ),
        ("", "024635", "024735", "050505"),
    ),
    ("TC", 1420): (
        (
            "多謝大人垂青。\n敝人",
            "今後願做\n",
            "大人的馬前卒，水火不辭。",
        ),
        ("", "024635", "024735", "050505"),
    ),
    ("SC", 1424): (
        (
            "我叫",
            "。\n我知道我有很多不成熟的地方，\n但我会全力以赴的！",
        ),
        ("", "024633", "050505"),
    ),
    ("TC", 1424): (
        (
            "吾人名為",
            "，\n尚有諸多不足之處，\n但必當全力以赴！",
        ),
        ("", "024633", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1419: (
        (
            "My name is ",
            ". It was fate that brought me here. I assure you, I will be "
            "of use.",
        ),
        ("", "024633", "050505"),
    ),
    1420: (
        (
            "IÖm delighted that you would reach out to me. ",
            " will act as your blade from here on.",
        ),
        ("", "024635", "050505"),
    ),
    1424: (
        (
            "IÖm ",
            ". There are still things IÖve yet to master, but I will do "
            "my very best.",
        ),
        ("", "024633", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B108_pristine_base_pc_jp_authoritative_"
    "nine_exact_repeated_ronin_introductions_with_uniform_plus_15_pk_jp_"
    "mapping_actual_pk_en_sc_tc_auxiliary_context_b108_a_twelve_record_"
    "ronin_canonical_object_identity_and_exact_reuse_dynamic_officer_house_"
    "and_speaker_tokens_hidden_lf_excluded_current_layout_and_opcode_"
    "skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if (
        RONIN_RECRUITMENT_SOURCE_JP
        is not PREVIOUS.RONIN_RECRUITMENT_SOURCE_JP
        or RONIN_RECRUITMENT_CANONICAL
        is not PREVIOUS.RONIN_RECRUITMENT_CANONICAL
        or RONIN_RECRUITMENT_BASE_GAPS
        is not PREVIOUS.RONIN_RECRUITMENT_BASE_GAPS
        or RONIN_RECRUITMENT_PK_GAPS
        is not PREVIOUS.RONIN_RECRUITMENT_PK_GAPS
    ):
        raise RuntimeError("segment 897 ronin canonical was copied")
    if (
        "15:1427:1" in raw_translations
        or "15:1427:1" in translations
        or RONIN_RECRUITMENT_CANONICAL[-1][1] != "\n"
    ):
        raise RuntimeError("segment 897 hidden LF received a decision")
    for record_id, arity in RECORD_ARITIES.items():
        index = ronin_repeat_index(record_id)
        if (
            COMMON.CORE.source_literals(source_records, record_id)
            != RONIN_RECRUITMENT_SOURCE_JP[index]
        ):
            raise RuntimeError(
                f"segment 897 repeated ronin source drifted: {record_id}"
            )
        actual = tuple(
            (
                EXCLUDED_NONVISIBLE_COORDINATES[coordinate]
                if coordinate in EXCLUDED_NONVISIBLE_COORDINATES
                else raw_translations[coordinate]
            )
            for literal_id in range(arity)
            for coordinate in (f"15:{record_id}:{literal_id}",)
        )
        if actual != RONIN_RECRUITMENT_CANONICAL[index]:
            raise RuntimeError(
                f"segment 897 repeated ronin canonical drifted: {record_id}"
            )
    if len(raw_translations) != 21:
        raise RuntimeError("segment 897 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
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
    if len(validated) != len(translations):
        raise RuntimeError("segment 897 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S897",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "repeated_ronin_records": len(RECORD_ARITIES),
                "excluded_hidden_newline": "15:1427:1",
                "ronin_canonical_object_identity_preserved": True,
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
