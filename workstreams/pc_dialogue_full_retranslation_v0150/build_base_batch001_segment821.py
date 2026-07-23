#!/usr/bin/env python3
"""Build Base authoring segment 821 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment818 as COMMON


ENGINE = COMMON.ENGINE
source_literals = COMMON.source_literals
PRIOR_RAW_TRANSLATIONS = COMMON.RAW_TRANSLATIONS
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S821.private.v1.jsonl"
SEGMENT = 821
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:0": "큰일이"
        for record_id in range(475, 478)
    },
    **{
        f"15:{record_id}:1": "!\n"
        for record_id in range(475, 478)
    },
    **{
        f"15:{record_id}:2": "의"
        for record_id in range(475, 478)
    },
    **{
        f"15:{record_id}:3": "이(가) 우리 가문을 저버리고\n"
        for record_id in range(475, 478)
    },
    **{
        f"15:{record_id}:4": "에 귀순한 모양"
        for record_id in range(475, 478)
    },
    **{
        f"15:{record_id}:5": "!"
        for record_id in range(475, 478)
    },
    "15:478:0": "큰일이",
    "15:478:1": "!\n",
    "15:478:2": "의",
    "15:478:3": "이(가) 우리 가문을 저버리고\n",
    "15:478:4": "째로",
    "15:478:5": "에 귀순하",
    "15:478:6": "!",
}
RECORD_ARITIES = {475: 6, 476: 6, 477: 6, 478: 7}
EXPECTED_JP = {
    **{
        record_id: (
            "一大事で",
            "！\n",
            "の",
            "が当家を見限り\n",
            "に寝返ったよう",
            "！",
        )
        for record_id in range(475, 478)
    },
    478: (
        "一大事で",
        "！\n",
        "の",
        "が当家を見限り\n",
        "ごと",
        "に寝返",
        "！",
    ),
}
EXPECTED_BASE_GAPS = {
    **{
        record_id: (
            "",
            "014352000000",
            "023c",
            "024833",
            "025032",
            "01431a020000",
            "050505",
        )
        for record_id in range(475, 478)
    },
    478: (
        "",
        "014352000000",
        "023c",
        "024833",
        "026432",
        "025032",
        "0143680200000143fc010000",
        "050505",
    ),
}
EXPECTED_PK_JP_GAPS = {
    **{
        record_id: (
            "",
            "014352000000",
            "023c",
            "024833",
            "025032",
            "014326020000",
            "050505",
        )
        for record_id in range(475, 478)
    },
    478: (
        "",
        "014352000000",
        "023c",
        "024833",
        "026432",
        "025032",
        "014374020000014302020000",
        "050505",
    ),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
DEFAULT_AUXILIARY = (("",), ("", "050505"))
AUXILIARY_OVERRIDES = {
    ("pk", "SC", 478): (
        ("有要事禀报！\n", "的", "抛弃了本家，\n连同", "一起投向了", "！"),
        ("", "023c", "024833", "026432", "025032", "050505"),
    ),
    ("pk", "TC", 478): (
        ("發生大事了！\n", "離棄本家，\n帶著整個", "倒戈投奔", "了！"),
        ("", "023c024833", "026432", "025032", "050505"),
    ),
    ("pk", "EN", 478): (
        (
            "WeÖve an emergency! ",
            " of ",
            " has forsaken our clan and turned ",
            " over to the ",
            "!",
        ),
        ("", "024833", "023c", "026432", "025032", "050505"),
    ),
}
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_house_officer_territory_and_"
    "faction_defection_report_fragments_with_exact_uniform_plus_7_pk_mapping_"
    "pk_en_sc_tc_auxiliary_context_and_known_base_478_context_divergence_"
    "historical_register_cross_segment_defection_terminology_current_pc_"
    "layout_and_opcode_skeleton_preserved_runtime_assembly_pending"
)


def expected_auxiliary(
    side: str,
    language: str,
    record_id: int,
    overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return overrides.get((side, language, record_id), DEFAULT_AUXILIARY)


def assert_context_mapping(
    *,
    segment: int,
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    source_records: dict[tuple[int, int], Any],
    pk_source_records: dict[tuple[int, int], Any],
    base_context: dict[str, dict[tuple[int, int], Any]],
    pk_context: dict[str, dict[tuple[int, int], Any]],
) -> None:
    mapped_ids = {record_id + 7 for record_id in record_arities}
    expected_mapped_ids = set(range(min(record_arities) + 7, max(record_arities) + 8))
    if mapped_ids != expected_mapped_ids or mapped_ids & COMMON.PK_ONLY_RECORD_IDS:
        raise RuntimeError(f"segment {segment} uniform +7 mapping drifted")

    for record_id in record_arities:
        base_record = source_records[(15, record_id)]
        pk_record = pk_source_records[(15, record_id + 7)]
        base_literals = tuple(
            literal.text for literal in ENGINE.parse_record_literals(base_record)
        )
        pk_literals = tuple(
            literal.text for literal in ENGINE.parse_record_literals(pk_record)
        )
        if base_literals != expected_jp[record_id]:
            raise RuntimeError(
                f"segment {segment} Base JP literal array drifted: {record_id}"
            )
        if pk_literals != expected_jp[record_id]:
            raise RuntimeError(
                f"segment {segment} mapped PK JP literal array drifted: {record_id + 7}"
            )
        if COMMON.record_gaps(base_record) != COMMON.gaps_from_hex(base_gaps[record_id]):
            raise RuntimeError(
                f"segment {segment} Base JP token skeleton drifted: {record_id}"
            )
        if COMMON.record_gaps(pk_record) != COMMON.gaps_from_hex(pk_jp_gaps[record_id]):
            raise RuntimeError(
                f"segment {segment} PK JP token skeleton drifted: {record_id + 7}"
            )

        for side, languages, mapped_id in (
            ("base", ("SC", "TC"), record_id),
            ("pk", ("SC", "TC", "EN"), record_id + 7),
        ):
            records_by_language = base_context if side == "base" else pk_context
            for language in languages:
                expected_literals, expected_gaps = expected_auxiliary(
                    side, language, record_id, auxiliary_overrides
                )
                record = records_by_language[language][(15, mapped_id)]
                actual_literals = tuple(
                    literal.text for literal in ENGINE.parse_record_literals(record)
                )
                if actual_literals != expected_literals:
                    raise RuntimeError(
                        f"segment {segment} {side} {language} literal array drifted: "
                        f"{mapped_id}"
                    )
                if COMMON.record_gaps(record) != COMMON.gaps_from_hex(expected_gaps):
                    raise RuntimeError(
                        f"segment {segment} {side} {language} token skeleton drifted: "
                        f"{mapped_id}"
                    )


def assert_scope(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str], dict[str, str]], None
    ],
) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }
    assert_context_mapping(
        segment=segment,
        record_arities=record_arities,
        expected_jp=expected_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        auxiliary_overrides=auxiliary_overrides,
        source_records=source_records,
        pk_source_records=pk_source_records,
        base_context=base_context,
        pk_context=pk_context,
    )

    expected_coordinates = set()
    actual_current_ellipsis = set()
    for record_id, arity in record_arities.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment {segment} source/current arity drifted: 15:{record_id}")
        expected_gaps = COMMON.gaps_from_hex(base_gaps[record_id])
        if (
            COMMON.record_gaps(source_record) != expected_gaps
            or COMMON.record_gaps(current_record) != expected_gaps
        ):
            raise RuntimeError(
                f"segment {segment} Base dynamic skeleton drifted: 15:{record_id}"
            )
        for literal_id, current_literal in enumerate(current_literals):
            coordinate = f"15:{record_id}:{literal_id}"
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(f"segment {segment} unexpected blank literal: {coordinate}")
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_current_ellipsis.add(coordinate)

    if set(raw_translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} raw decision coordinate universe drifted")
    if set(translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} resolved decision coordinate universe drifted")
    if len(translations) != sum(record_arities.values()):
        raise RuntimeError(f"segment {segment} visible decision count drifted")
    if actual_current_ellipsis != ellipsis_coordinates:
        raise RuntimeError(f"segment {segment} current ellipsis coordinates drifted")

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if COMMON.layout_signature(translation) != COMMON.layout_signature(current_text):
            raise RuntimeError(f"segment {segment} layout/outer signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment {segment} forbidden script/control drifted: {coordinate}")
        if COMMON.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(
                f"segment {segment} retains banned fullwidth punctuation: {coordinate}"
            )
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment {segment} retains an unpaired ellipsis: {coordinate}")

    semantic_assertions(source_records, raw_translations, translations)


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    basis: str,
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str], dict[str, str]], None
    ],
) -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    translations = COMMON.resolved_translations(current_records, raw_translations)
    assert_scope(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
        expected_jp=expected_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        ellipsis_coordinates=ellipsis_coordinates,
        auxiliary_overrides=auxiliary_overrides,
        semantic_assertions=semantic_assertions,
    )
    COMMON.assert_isolated_overlay_roundtrip(
        prepared,
        segment=segment,
        translations=translations,
        record_arities=record_arities,
    )
    rows = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": basis,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    source_group = {
        source_literals(source_records, record_id)
        for record_id in range(467, 478)
    }
    if len(source_group) != 1:
        raise RuntimeError("segment 821 repeated defection-report source drifted")
    canonical = tuple(
        raw_translations[f"15:475:{literal_id}"] for literal_id in range(6)
    )
    prior_canonical = tuple(
        PRIOR_RAW_TRANSLATIONS[f"15:467:{literal_id}"] for literal_id in range(6)
    )
    if canonical != prior_canonical:
        raise RuntimeError("segment 821 cross-segment defection translation drifted")
    for record_id in range(475, 478):
        if tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(6)
        ) != canonical:
            raise RuntimeError(
                f"segment 821 repeated defection translation drifted: {record_id}"
            )
        if not translations[f"15:{record_id}:2"].startswith("의"):
            raise RuntimeError(
                f"segment 821 house-name possessive particle drifted: {record_id}"
            )
        if not translations[f"15:{record_id}:3"].startswith(
            "이(가) 우리 가문을 저버리고\n"
        ):
            raise RuntimeError(
                f"segment 821 officer-name particle drifted: {record_id}"
            )
        if not translations[f"15:{record_id}:4"].startswith("에 귀순한 모양"):
            raise RuntimeError(
                f"segment 821 faction-name particle drifted: {record_id}"
            )

    exact_prior_pairs = {
        "15:478:0": "15:467:0",
        "15:478:3": "15:467:3",
        "15:478:5": "15:466:4",
    }
    for coordinate, prior_coordinate in exact_prior_pairs.items():
        _, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        _, prior_record_id, prior_literal_id = (
            int(value) for value in prior_coordinate.split(":")
        )
        if (
            source_literals(source_records, record_id)[literal_id]
            != source_literals(source_records, prior_record_id)[prior_literal_id]
        ):
            raise RuntimeError(
                f"segment 821 exact-source reuse drifted: {coordinate}/{prior_coordinate}"
            )
        if raw_translations[coordinate] != PRIOR_RAW_TRANSLATIONS[prior_coordinate]:
            raise RuntimeError(
                f"segment 821 exact-translation reuse drifted: {coordinate}/{prior_coordinate}"
            )
    if not translations["15:478:2"].startswith("의"):
        raise RuntimeError("segment 821 territory-group house possessive drifted")
    if not translations["15:478:3"].startswith(
        "이(가) 우리 가문을 저버리고\n"
    ):
        raise RuntimeError("segment 821 territory-group officer particle drifted")
    if translations["15:478:4"] != "째로":
        raise RuntimeError("segment 821 entire-territory group boundary drifted")
    if not translations["15:478:5"].startswith("에 귀순하"):
        raise RuntimeError("segment 821 faction-name dynamic stem drifted")
    joined = "\n".join(translations.values())
    if "당가" in joined or "우리 가문" not in joined or "귀순" not in joined:
        raise RuntimeError("segment 821 house/defection terminology drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 821 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S821",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
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
