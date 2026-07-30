#!/usr/bin/env python3
"""Build Base authoring segment 812 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment809 as SUPPORT


ENGINE = SUPPORT.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S812.private.v1.jsonl"
SEGMENT = 812
RAW_TRANSLATIONS: dict[str, str] = {
    "15:384:0": "의",
    "15:384:1": "을(를)\n권유하고자 하옵니다\n무언가 큰 불만을 품고 있다 하옵니다",
    "15:385:0": "의",
    "15:385:1": (
        "은(는)\n"
        "우리 가문에 권유하면 귀순할지도 모르오\n"
        "한 번 시도해 보고 싶구려…"
    ),
    "15:386:0": "의",
    "15:386:1": "은(는)\n알고 계십니까?　",
    "15:386:2": "이(가)\n권유하면 귀순할지도…",
    "15:387:0": "에서 큰 불만을 품은\n",
    "15:387:1": "에게 권유를\n해 볼 수는 없겠습니까…",
    "15:388:0": "가엾게도",
    "15:388:1": "안에서\n",
    "15:388:2": "은(는) 입지가 없다 하옵니다…\n우리 가문으로 오시면 좋으련만",
    "15:389:0": "의",
    "15:389:1": (
        "이(가)\n"
        "큰 불만을 품고 있사옵니다\n"
        "권유하면 귀순할지도 모르옵니다"
    ),
    "15:390:0": (
        "다른 가문의 이야기다만\n"
        "크게 불만을 품은 무장이 있는 듯하다\n"
        "귀순을 권해 볼까?"
    ),
    "15:391:0": (
        "다른 가문의 무장을 우리 가문에 귀순시키면\n"
        "일석이조라 할 수 있겠습니다\n"
        "불만을 품은 무장이 있다면…"
    ),
    "15:392:0": (
        "다른 가문의 무장을 우리 가문에 귀순시키려면\n"
        "현재 처지에 불만을 품은 자가\n"
        "적당할 것이옵니다. 이를테면…"
    ),
    "15:393:0": (
        "우리 가문에 귀순하고 싶다고\n"
        "남몰래 생각하는 무장이 다른 가문에\n"
        "있다는 소문이 돌고 있사옵니다…"
    ),
    "15:394:0": (
        "주변 다이묘 가문에서 귀순해\n"
        "올 만한 자는 없느냐!\n"
        "음? 그러고 보니…"
    ),
    "15:395:0": (
        "주변 다이묘 가문에서\n"
        "귀순할 만한 무장을 찾고 있었는데\n"
        "이제 후보가 좁혀졌습니다…"
    ),
    "15:396:0": (
        "다른 가문 무장의 권유라면 맡겨 주시옵소서\n"
        "현재 처지에 큰 불만을 품은 무장 중\n"
        "짐작 가는 자가 있사옵니다"
    ),
    "15:397:0": (
        "우리 가문에 귀순하고 싶다는\n"
        "서신이 은밀히 도착했다 하니\n"
        "과연 거짓일지 참일지…"
    ),
}
RECORD_ARITIES = {
    384: 2,
    385: 2,
    386: 3,
    387: 2,
    388: 3,
    389: 2,
    **{record_id: 1 for record_id in range(390, 398)},
}
EXPECTED_GAPS = {
    384: ("02483e", "014315000000", "050505"),
    385: ("02483e", "014315000000", "050505"),
    386: ("02483e", "014315000000", "014301000000", "050505"),
    387: ("02483e", "014315000000", "050505"),
    388: ("", "02483e", "014315000000", "050505"),
    389: ("02483e", "014315000000", "050505"),
    **{record_id: ("", "050505") for record_id in range(390, 398)},
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:385:1",
    "15:386:2",
    "15:387:1",
    "15:388:2",
    "15:391:0",
    "15:392:0",
    "15:393:0",
    "15:394:0",
    "15:395:0",
    "15:397:0",
}
BASE_CONTEXT_ARITIES = {
    "SC": {record_id: 1 for record_id in RECORD_ARITIES},
    "TC": {record_id: 1 for record_id in RECORD_ARITIES},
}
PK_EN_ARITIES = {record_id: 1 for record_id in RECORD_ARITIES}
MAPPING_TEXT_DIVERGENCES = {"JP": set(), "SC": set(), "TC": set()}
MAPPING_GAP_DIVERGENCES = {"JP": set(), "SC": set(), "TC": set()}
PK_ONLY_RECORD_IDS = {317, 319, 324, 326}
BASIS = (
    "pristine_base_pc_jp_authoritative_with_uniform_plus7_mapped_pk_jp_"
    "en_sc_tc_auxiliary_context_current_pc_layout_and_opcode_skeleton_"
    "preserved_runtime_assembly_pending_pk_only_insertions_excluded"
)


def gaps_from_hex(values: tuple[str, ...]) -> tuple[bytes, ...]:
    return tuple(bytes.fromhex(value) for value in values)


def resolved_translations(current_records: dict[tuple[int, int], Any]) -> dict[str, str]:
    translations = {}
    for coordinate, raw in RAW_TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        translations[coordinate] = SUPPORT.adopt_current_layout(raw, current)
    return translations


def text_array(record: Any) -> list[str]:
    return [literal.text for literal in ENGINE.parse_record_literals(record)]


def assert_common_scope(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
    expected_gaps: dict[int, tuple[str, ...]],
    current_ellipsis_coordinates: set[str],
    base_context_arities: dict[str, dict[int, int]],
    pk_en_arities: dict[int, int],
    mapping_text_divergences: dict[str, set[int]],
    mapping_gap_divergences: dict[str, set[int]],
    semantic_assertions: Callable[[dict[tuple[int, int], Any], dict[str, str]], None],
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

    mapped_ids = {record_id + 7 for record_id in record_arities}
    if mapped_ids & PK_ONLY_RECORD_IDS:
        raise RuntimeError(f"segment {segment} mapped through a PK-only insertion")
    if mapped_ids != set(range(min(record_arities) + 7, max(record_arities) + 8)):
        raise RuntimeError(f"segment {segment} Base-to-PK +7 mapping drifted")

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context["SC"], pk_context["SC"]),
        ("TC", base_context["TC"], pk_context["TC"]),
    ):
        text_divergences = {
            record_id
            for record_id in record_arities
            if text_array(base_records[(15, record_id)])
            != text_array(mapped_records[(15, record_id + 7)])
        }
        gap_divergences = {
            record_id
            for record_id in record_arities
            if SUPPORT.record_gaps(base_records[(15, record_id)])
            != SUPPORT.record_gaps(mapped_records[(15, record_id + 7)])
        }
        if text_divergences != mapping_text_divergences[language]:
            raise RuntimeError(
                f"segment {segment} mapped PK {language} text divergence drifted: "
                f"{sorted(text_divergences)}"
            )
        if gap_divergences != mapping_gap_divergences[language]:
            raise RuntimeError(
                f"segment {segment} mapped PK {language} token divergence drifted: "
                f"{sorted(gap_divergences)}"
            )

    actual_current_ellipsis = set()
    expected_coordinates = set()
    for record_id, arity in record_arities.items():
        source = source_records[(15, record_id)]
        current = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source)
        current_literals = ENGINE.parse_record_literals(current)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment {segment} JP/current arity drifted: 15:{record_id}")
        expected = gaps_from_hex(expected_gaps[record_id])
        if SUPPORT.record_gaps(source) != expected or SUPPORT.record_gaps(current) != expected:
            raise RuntimeError(f"segment {segment} Base token skeleton drifted: 15:{record_id}")
        if len(ENGINE.parse_record_literals(pk_source_records[(15, record_id + 7)])) != arity:
            raise RuntimeError(f"segment {segment} mapped PK JP arity drifted: 15:{record_id}")
        for language in ("SC", "TC"):
            expected_arity = base_context_arities[language][record_id]
            if len(ENGINE.parse_record_literals(base_context[language][(15, record_id)])) != expected_arity:
                raise RuntimeError(
                    f"segment {segment} Base {language} context arity drifted: 15:{record_id}"
                )
            if len(
                ENGINE.parse_record_literals(pk_context[language][(15, record_id + 7)])
            ) != expected_arity:
                raise RuntimeError(
                    f"segment {segment} mapped PK {language} context arity drifted: "
                    f"15:{record_id}"
                )
        if len(
            ENGINE.parse_record_literals(pk_context["EN"][(15, record_id + 7)])
        ) != pk_en_arities[record_id]:
            raise RuntimeError(f"segment {segment} mapped PK EN arity drifted: 15:{record_id}")
        for literal_id, literal in enumerate(current_literals):
            coordinate = f"15:{record_id}:{literal_id}"
            expected_coordinates.add(coordinate)
            if "…" in literal.text:
                actual_current_ellipsis.add(coordinate)

    if actual_current_ellipsis != current_ellipsis_coordinates:
        raise RuntimeError(f"segment {segment} current ellipsis coordinates drifted")
    if set(raw_translations) != expected_coordinates or set(translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} decision coordinate set drifted")
    if len(translations) != sum(record_arities.values()):
        raise RuntimeError(f"segment {segment} decision count drifted")

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        if SUPPORT.layout_signature(translation) != SUPPORT.layout_signature(current_text):
            raise RuntimeError(f"segment {segment} layout signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment {segment} forbidden script/control: {coordinate}")
        if SUPPORT.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"segment {segment} fullwidth punctuation drifted: {coordinate}")
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment {segment} unpaired ellipsis drifted: {coordinate}")

    semantic_assertions(source_records, translations)


def assert_isolated_overlay_roundtrip(
    prepared: Any,
    *,
    segment: int,
    translations: dict[str, str],
    record_arities: dict[int, int],
) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements = {}
    reverse_replacements = {}
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse_replacements[key] = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
    rebuilt = ENGINE.rebuild_packed_with_literals(base.current_blob, replacements)
    rebuilt_records = ENGINE.archive_records(ENGINE.parse_packed_msggame(rebuilt).archive)
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError(f"segment {segment} record count drifted from 19152")
    target_records = {(15, record_id) for record_id in record_arities}
    outside_exact = 0
    for key, current_record in current_records.items():
        if key not in target_records:
            if rebuilt_records[key].data != current_record.data:
                raise RuntimeError(f"segment {segment} changed out-of-scope record: {key}")
            outside_exact += 1
    if outside_exact != 19152 - len(target_records):
        raise RuntimeError(f"segment {segment} outside-scope exact count drifted")
    for key in target_records:
        if SUPPORT.record_gaps(rebuilt_records[key]) != SUPPORT.record_gaps(current_records[key]):
            raise RuntimeError(f"segment {segment} target skeleton drifted: {key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(f"segment {segment} UTF-16 round-trip failed: {key}")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError(f"segment {segment} reverse overlay is not byte-exact")


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    expected_gaps: dict[int, tuple[str, ...]],
    current_ellipsis_coordinates: set[str],
    base_context_arities: dict[str, dict[int, int]],
    pk_en_arities: dict[int, int],
    mapping_text_divergences: dict[str, set[int]],
    mapping_gap_divergences: dict[str, set[int]],
    semantic_assertions: Callable[[dict[tuple[int, int], Any], dict[str, str]], None],
) -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    translations = {}
    for coordinate, raw in raw_translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        translations[coordinate] = SUPPORT.adopt_current_layout(raw, current)
    assert_common_scope(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
        expected_gaps=expected_gaps,
        current_ellipsis_coordinates=current_ellipsis_coordinates,
        base_context_arities=base_context_arities,
        pk_en_arities=pk_en_arities,
        mapping_text_divergences=mapping_text_divergences,
        mapping_gap_divergences=mapping_gap_divergences,
        semantic_assertions=semantic_assertions,
    )
    assert_isolated_overlay_roundtrip(
        prepared,
        segment=segment,
        translations=translations,
        record_arities=record_arities,
    )
    rows = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets[("base_msggame", block_id, record_id, literal_id)]
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
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows


def assert_semantics(
    source_records: dict[tuple[int, int], Any], translations: dict[str, str]
) -> None:
    if len({text_array(source_records[(15, record_id)])[0] for record_id in range(390, 398)}) != 8:
        raise RuntimeError("segment 812 distinct static recruitment sources collapsed")
    joined = "\n".join(translations.values())
    for term in ("우리 가문", "다른 가문", "귀순", "권유", "다이묘 가문"):
        if term not in joined:
            raise RuntimeError(f"segment 812 required terminology drifted: {term}")
    if any(term in joined for term in ("당가", "타가", "배반", "출사", "다이묘가", "、")):
        raise RuntimeError("segment 812 retains forbidden terminology/punctuation")
    if translations["15:384:0"] != translations["15:385:0"]:
        raise RuntimeError("segment 812 repeated clan possessive fragment drifted")
    if translations["15:384:0"] != translations["15:386:0"]:
        raise RuntimeError("segment 812 repeated clan possessive fragment drifted")
    if translations["15:384:0"] != translations["15:389:0"]:
        raise RuntimeError("segment 812 repeated clan possessive fragment drifted")
    if not translations["15:385:1"].endswith("싶구려……"):
        raise RuntimeError("segment 812 elder proposal voice drifted")
    if "한 번 시도해" not in translations["15:385:1"]:
        raise RuntimeError("segment 812 one-time spacing drifted")
    if "\u3000" not in translations["15:386:1"]:
        raise RuntimeError("segment 812 U+3000 runtime spacing drifted")
    if not translations["15:388:2"].endswith("좋으련만"):
        raise RuntimeError("segment 812 sympathetic voice drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_gaps=EXPECTED_GAPS,
        current_ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        base_context_arities=BASE_CONTEXT_ARITIES,
        pk_en_arities=PK_EN_ARITIES,
        mapping_text_divergences=MAPPING_TEXT_DIVERGENCES,
        mapping_gap_divergences=MAPPING_GAP_DIVERGENCES,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 812 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S812",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "steam_write_performed": False,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
