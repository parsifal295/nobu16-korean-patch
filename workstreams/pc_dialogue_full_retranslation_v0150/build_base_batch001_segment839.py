#!/usr/bin/env python3
"""Build Base authoring segment 839 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment838 as PRIOR


COMMON = PRIOR.COMMON
LOW_LEVEL = COMMON.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S839.private.v1.jsonl"
SEGMENT = 839
REPEATED_INVASION_718_729 = (
    "에 적이 진군 중입니다!\n"
    "맞아 싸우기 위해서라도\n"
    "무리해서라도 병사를 모읍시다"
)
REPEATED_WARNING_730_741 = (
    "병사를 서둘러 모을 수는 있으나\n"
    "한동안 민심을 잃게 될 것이옵니다\n"
    "신중히 판단하시옵소서"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:715:0": "을(를) 등용",
    "15:716:0": "의 병력이",
    "15:716:1": "→",
    "15:716:2": "으로(로)",
    "15:717:0": "이(가)",
    "15:717:1": "의 편입에 실패",
    **{
        f"15:{record_id}:0": REPEATED_INVASION_718_729
        for record_id in range(718, 730)
    },
    **{
        f"15:{record_id}:0": REPEATED_WARNING_730_741
        for record_id in range(730, 734)
    },
}
RECORD_ARITIES = {
    715: 1,
    716: 3,
    717: 2,
    **{record_id: 1 for record_id in range(718, 734)},
}
REPEATED_INVASION_JP = (
    "に敵が進軍中！\n"
    "迎え撃つためにも\n"
    "無理にでも兵を集めましょう",
)
REPEATED_WARNING_JP = (
    "兵を急ぎ集められますが\n"
    "しばらくの間、民心を失うでしょう\n"
    "慎重にご判断ください",
)
EXPECTED_JP = {
    715: ("を登用",),
    716: ("の兵力が", "→", "に"),
    717: ("が", "の取込に失敗"),
    **{record_id: REPEATED_INVASION_JP for record_id in range(718, 730)},
    **{record_id: REPEATED_WARNING_JP for record_id in range(730, 734)},
}
EXPECTED_PK_JP = dict(EXPECTED_JP)
EXPECTED_BASE_GAPS = {
    715: ("024633", "050505"),
    716: ("026432", "0232", "0233", "050505"),
    717: ("024633", "028c32", "050505"),
    **{record_id: ("026432", "050505") for record_id in range(718, 730)},
    **{record_id: ("", "050505") for record_id in range(730, 734)},
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
SC_AUXILIARY = {
    715: (("登用了", "。"), ("", "024633", "050505")),
    716: (("的兵力由", "→", "。"), ("026432", "0232", "0233", "050505")),
    717: (("拉拢", "失败。"), ("024633", "028c32", "050505")),
}
TC_AUXILIARY = {
    715: (("登庸", "。"), ("", "024633", "050505")),
    716: (("的兵力", "→", "。"), ("026432", "0232", "0233", "050505")),
    717: (("對", "懷柔失敗。"), ("024633", "028c32", "050505")),
}
EN_AUXILIARY = {
    715: ((" has been employed.",), ("024633", "050505")),
    716: (
        ("Ös soldiers changed from ", " to ", "."),
        ("026432", "0232", "0233", "050505"),
    ),
    717: (
        (" failed to assimilate the ", "."),
        ("024633", "028c32", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): value
        for side in ("base", "pk")
        for record_id, value in SC_AUXILIARY.items()
    },
    **{
        (side, "TC", record_id): value
        for side in ("base", "pk")
        for record_id, value in TC_AUXILIARY.items()
    },
    **{
        ("pk", "EN", record_id): value
        for record_id, value in EN_AUXILIARY.items()
    },
}
BASIS = (
    "pristine_base_pc_jp_authoritative_incorporation_result_and_emergency_"
    "levy_warning_fragments_with_explicit_plus_7_pk_jp_variant_validation_"
    "exact_pc_sc_tc_and_pk_en_auxiliary_context_dynamic_officer_territory_"
    "force_count_and_kunishu_tokens_historical_register_current_pc_layout_"
    "and_opcode_skeleton_preserved_runtime_assembly_pending"
)


def assert_extended_context_mapping(
    *,
    segment: int,
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    expected_pk_jp: dict[int, tuple[str, ...]],
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
    if mapped_ids != expected_mapped_ids or mapped_ids & LOW_LEVEL.PK_ONLY_RECORD_IDS:
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
        if pk_literals != expected_pk_jp[record_id]:
            raise RuntimeError(
                f"segment {segment} mapped PK JP literal array drifted: {record_id + 7}"
            )
        if LOW_LEVEL.record_gaps(base_record) != LOW_LEVEL.gaps_from_hex(
            base_gaps[record_id]
        ):
            raise RuntimeError(
                f"segment {segment} Base JP token skeleton drifted: {record_id}"
            )
        if LOW_LEVEL.record_gaps(pk_record) != LOW_LEVEL.gaps_from_hex(
            pk_jp_gaps[record_id]
        ):
            raise RuntimeError(
                f"segment {segment} PK JP token skeleton drifted: {record_id + 7}"
            )

        for side, languages, mapped_id in (
            ("base", ("SC", "TC"), record_id),
            ("pk", ("SC", "TC", "EN"), record_id + 7),
        ):
            records_by_language = base_context if side == "base" else pk_context
            for language in languages:
                expected_literals, expected_gaps = COMMON.expected_auxiliary(
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
                if LOW_LEVEL.record_gaps(record) != LOW_LEVEL.gaps_from_hex(
                    expected_gaps
                ):
                    raise RuntimeError(
                        f"segment {segment} {side} {language} token skeleton drifted: "
                        f"{mapped_id}"
                    )


def assert_extended_scope(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    expected_pk_jp: dict[int, tuple[str, ...]],
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
    assert_extended_context_mapping(
        segment=segment,
        record_arities=record_arities,
        expected_jp=expected_jp,
        expected_pk_jp=expected_pk_jp,
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
        expected_gaps = LOW_LEVEL.gaps_from_hex(base_gaps[record_id])
        if (
            LOW_LEVEL.record_gaps(source_record) != expected_gaps
            or LOW_LEVEL.record_gaps(current_record) != expected_gaps
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
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if LOW_LEVEL.layout_signature(translation) != LOW_LEVEL.layout_signature(
            current_text
        ):
            raise RuntimeError(f"segment {segment} layout/outer signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment {segment} forbidden script/control drifted: {coordinate}")
        if LOW_LEVEL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(
                f"segment {segment} retains banned fullwidth punctuation: {coordinate}"
            )
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment {segment} retains an unpaired ellipsis: {coordinate}")

    semantic_assertions(source_records, raw_translations, translations)


def build_extended_segment_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    expected_pk_jp: dict[int, tuple[str, ...]],
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
    translations = LOW_LEVEL.resolved_translations(current_records, raw_translations)
    assert_extended_scope(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
        expected_jp=expected_jp,
        expected_pk_jp=expected_pk_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        ellipsis_coordinates=ellipsis_coordinates,
        auxiliary_overrides=auxiliary_overrides,
        semantic_assertions=semantic_assertions,
    )
    LOW_LEVEL.assert_isolated_overlay_roundtrip(
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
    invasion_source = COMMON.source_literals(source_records, 718)
    if any(
        COMMON.source_literals(source_records, record_id) != invasion_source
        for record_id in range(719, 730)
    ):
        raise RuntimeError("segment 839 718-729 exact invasion source drifted")
    if any(
        raw_translations[f"15:{record_id}:0"] != REPEATED_INVASION_718_729
        for record_id in range(718, 730)
    ):
        raise RuntimeError("segment 839 718-729 exact invasion translation drifted")
    warning_source = COMMON.source_literals(source_records, 730)
    if any(
        COMMON.source_literals(source_records, record_id) != warning_source
        for record_id in range(731, 734)
    ):
        raise RuntimeError("segment 839 730-733 warning source drifted")
    if any(
        raw_translations[f"15:{record_id}:0"] != REPEATED_WARNING_730_741
        for record_id in range(730, 734)
    ):
        raise RuntimeError("segment 839 730-733 warning translation drifted")

    if translations["15:715:0"] != "을(를) 등용":
        raise RuntimeError("segment 839 officer employment particle drifted")
    if translations["15:716:2"] != "으로(로)":
        raise RuntimeError("segment 839 force-change result particle drifted")
    if translations["15:717:0"] != "이(가)":
        raise RuntimeError("segment 839 actor subject particle drifted")
    if not translations["15:718:0"].startswith("에 적이 진군 중"):
        raise RuntimeError("segment 839 destination invasion particle drifted")
    if "민심" not in translations["15:730:0"]:
        raise RuntimeError("segment 839 popular-support warning drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_extended_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        expected_pk_jp=EXPECTED_PK_JP,
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
        raise RuntimeError("segment 839 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S839",
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
