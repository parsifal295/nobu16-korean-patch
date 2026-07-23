#!/usr/bin/env python3
"""Build Base authoring segment 895 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment894 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S895.private.v1.jsonl"
)
SEGMENT = 895
RONIN_RECRUITMENT_BASE_START = PREVIOUS.RONIN_RECRUITMENT_BASE_START
RONIN_RECRUITMENT_SOURCE_JP = PREVIOUS.RONIN_RECRUITMENT_SOURCE_JP
RONIN_RECRUITMENT_CANONICAL = PREVIOUS.RONIN_RECRUITMENT_CANONICAL
RONIN_RECRUITMENT_BASE_GAPS = PREVIOUS.RONIN_RECRUITMENT_BASE_GAPS
RONIN_RECRUITMENT_PK_GAPS = PREVIOUS.RONIN_RECRUITMENT_PK_GAPS
RONIN_RECRUITMENT_ARITIES = PREVIOUS.RONIN_RECRUITMENT_ARITIES
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1409:1": "\n"}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id in range(1400, 1410)
    for literal_id, translation in enumerate(
        RONIN_RECRUITMENT_CANONICAL[
            record_id - RONIN_RECRUITMENT_BASE_START
        ]
    )
    if f"15:{record_id}:{literal_id}"
    not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: RONIN_RECRUITMENT_ARITIES[
        record_id - RONIN_RECRUITMENT_BASE_START
    ]
    for record_id in range(1400, 1410)
}
EXPECTED_BASE_JP = {
    record_id: RONIN_RECRUITMENT_SOURCE_JP[
        record_id - RONIN_RECRUITMENT_BASE_START
    ]
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    record_id: RONIN_RECRUITMENT_BASE_GAPS[
        record_id - RONIN_RECRUITMENT_BASE_START
    ]
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = {
    record_id: RONIN_RECRUITMENT_PK_GAPS[
        record_id - RONIN_RECRUITMENT_BASE_START
    ]
    for record_id in RECORD_ARITIES
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
SHARED_AUXILIARY = {
    ("SC", 1400): (
        ("叫", "。\n我愿为协助", "大人的霸业\n粉身碎骨，誓死效力。"),
        ("014301000000", "024633", "024735", "050505"),
    ),
    ("TC", 1400): (
        ("名叫", "。\n願助", "大人達成霸業，\n粉身碎骨，在所不惜。"),
        ("014301000000", "024633", "024735", "050505"),
    ),
    ("SC", 1401): (
        ("我叫", "。\n既然有缘侍奉", "大人，\n我定会为您立下汗马功劳。"),
        ("", "024633", "024735", "050505"),
    ),
    ("TC", 1401): (
        ("吾人名為", "，\n因緣際會下於此前來效命，\n誓必成為", "大人的生力軍。"),
        ("", "024633", "024735", "050505"),
    ),
    ("SC", 1402): (
        ("蒙您垂青，不胜荣幸。\n以后我", "就是\n", "大人的利刃，任您驱驰。"),
        ("", "024635", "024735", "050505"),
    ),
    ("TC", 1402): (
        ("多謝大人垂青。\n敝人", "今後願做\n", "大人的馬前卒，水火不辭。"),
        ("", "024635", "024735", "050505"),
    ),
    ("SC", 1406): (
        ("我叫", "。\n我知道我有很多不成熟的地方，\n但我会全力以赴的！"),
        ("", "024633", "050505"),
    ),
    ("TC", 1406): (
        ("吾人名為", "，\n尚有諸多不足之處，\n但必當全力以赴！"),
        ("", "024633", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1400: (
        (
            "The nameÖs ",
            ". I will do everything within my power to help you achieve "
            "supremacy.",
        ),
        ("", "024633", "050505"),
    ),
    1401: (
        (
            "My name is ",
            ". It was fate that brought me here. I assure you, I will be "
            "of use.",
        ),
        ("", "024633", "050505"),
    ),
    1402: (
        (
            "IÖm delighted that you would reach out to me. ",
            " will act as your blade from here on.",
        ),
        ("", "024635", "050505"),
    ),
    1406: (
        (
            "IÖm ",
            ". There are still things IÖve yet to master, but I will do "
            "my very best.",
        ),
        ("", "024633", "050505"),
    ),
}
AUXILIARY_OVERRIDES = PREVIOUS.AUXILIARY.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B108_pristine_base_pc_jp_authoritative_"
    "ten_ronin_recruitment_introductions_with_uniform_plus_15_exact_pk_jp_"
    "sc_tc_mapping_actual_pk_en_auxiliary_context_b080_s808_s809_canonical_"
    "exact_reuse_and_b108_twelve_record_canonical_export_牢人_as_historically_"
    "contextualized_낭인_gendered_and_hierarchical_speaker_register_"
    "恐悦至極_humble_gratitude_不肖_self_deprecation_末席を汚す_idiomatic_"
    "retainer_service_dynamic_officer_house_and_speaker_tokens_hidden_lf_"
    "excluded_current_layout_and_opcode_skeleton_preserved_runtime_fragment_"
    "pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    PREVIOUS.assert_ronin_canonical_sources(source_records)
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
        raise RuntimeError("segment 895 ronin canonical was copied")
    if (
        "15:1409:1" in raw_translations
        or "15:1409:1" in translations
        or RONIN_RECRUITMENT_CANONICAL[-1][1] != "\n"
    ):
        raise RuntimeError("segment 895 hidden LF received a decision")
    for record_id, arity in RECORD_ARITIES.items():
        index = record_id - RONIN_RECRUITMENT_BASE_START
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
                f"segment 895 ronin canonical drifted: {record_id}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "패업",
        "몸이 부서져라",
        "인연이 닿아",
        "황송하기 그지없",
        "칼날",
        "불초",
        "말석에 들",
        "목숨이 다할 때까지",
        "최선을 다하겠습니다",
        "싸움이라면",
        "정성을 다하겠어요",
        "충성을 다하겠습니다",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 895 meaning or speaker register drifted: {required}"
            )
    if any(
        term in joined
        for term in ("末席", "말석을 더럽", "불초한", "牢人", "浪人", "、")
    ):
        raise RuntimeError(
            "segment 895 retained a literalism, source term, or Japanese comma"
        )


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
        raise RuntimeError("segment 895 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S895",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "excluded_hidden_newline": "15:1409:1",
                "ronin_recruitment_canonical_size": len(
                    RONIN_RECRUITMENT_CANONICAL
                ),
                "ronin_recruitment_canonical_reexported": True,
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
