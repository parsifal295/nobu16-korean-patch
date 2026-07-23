#!/usr/bin/env python3
"""Build Base authoring segment 811 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S811.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s811", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
RAW_TRANSLATIONS: dict[str, str] = {
    "15:377:0": "창칼을 휘두르는 것만이 전쟁은 아니옵니다\n",
    "15:377:1": "의 공략을 위해서라도\n",
    "15:377:2": "의 실행을",
    "15:377:3": "허가해 주시옵소서",
    "15:378:0": "의",
    "15:378:1": (
        "은(는)\n"
        "지금 지위에 불만인 모양이야!\n"
        "권유하면 이쪽으로 귀순할지도 몰라"
    ),
    "15:379:0": "의",
    "15:379:1": (
        "이(가)\n"
        "불만을 크게 토로하고 있다 하옵니다\n"
        "조략을 걸 때인지도 모르겠사옵니다"
    ),
    "15:380:0": "에 변고가 생긴 모양\n불만을 품은",
    "15:380:1": "에게\n조략을 걸면 귀순할지도…",
    "15:381:0": "솔깃한 소식이 있사옵니다…\n",
    "15:381:1": "의",
    "15:381:2": "이(가)\n우리 가문에 귀순할지도 모른다고…",
    "15:382:0": (
        "귀순할 듯한 무장이 있다는 소문이오\n"
        "조략을 걸어 보는 것이 어떻겠소\n"
    ),
    "15:382:1": "의",
    "15:382:2": "에게…",
    "15:383:0": (
        "귀순을 권하려면 상대를\n"
        "잘 가려야 하오… 이를테면\n"
    ),
    "15:383:1": "의",
    "15:383:2": "(이)라든가",
}
RECORD_ARITIES = {377: 4, 378: 2, 379: 2, 380: 2, 381: 3, 382: 3, 383: 3}
EXPECTED_GAPS = {
    377: ("", "026432", "1b434d023c1b435a", "01438a040000", "050505"),
    378: ("02483e", "01431d000000", "050505"),
    379: ("02483e", "014315000000", "050505"),
    380: ("02483e", "014315000000", "050505"),
    381: ("", "02483e", "014315000000", "050505"),
    382: ("", "02483e", "014315000000", "050505"),
    383: ("", "02483e", "014315000000", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:380:1",
    "15:381:0",
    "15:381:2",
    "15:382:2",
    "15:383:0",
}
POSSESSIVE_COORDINATES = {
    "15:378:0",
    "15:379:0",
    "15:381:1",
    "15:382:1",
    "15:383:1",
}
PK_ONLY_RECORD_IDS = {317, 319, 324, 326}
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－"
) - {"…"}
ASCII_PUNCTUATION = str.maketrans(
    {
        "【": "[",
        "】": "]",
        "「": '"',
        "」": '"',
        "／": "/",
        "，": ",",
        "。": ".",
        "・": "·",
        "…": "……",
        "、": ",",
    }
)
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_stratagem_proposal_and_"
    "defection_fragments_with_base_sc_tc_and_exact_offset_plus_7_pk_jp_en_"
    "sc_tc_auxiliary_context_runtime_clan_officer_genitive_subject_and_"
    "dative_boundaries_verified_current_pc_literal_arity_outer_layout_and_"
    "opcode_skeleton_preserved_runtime_assembly_pending_pk_only_insertions_excluded"
)


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def gaps_from_hex(values: tuple[str, ...]) -> tuple[bytes, ...]:
    return tuple(bytes.fromhex(value) for value in values)


def line_edge(text: str) -> tuple[str, str]:
    return (
        text[: len(text) - len(text.lstrip(" \t\u3000"))],
        text[len(text.rstrip(" \t\u3000")) :],
    )


def adopt_current_layout(raw: str, current: str) -> str:
    raw_lines = raw.split("\n")
    current_lines = current.split("\n")
    if len(raw_lines) != len(current_lines):
        raise RuntimeError("raw translation LF count differs from current layout")
    rendered = []
    for raw_line, current_line in zip(raw_lines, current_lines):
        leading, trailing = line_edge(current_line)
        visible = raw_line.strip(" \t\u3000").translate(ASCII_PUNCTUATION)
        rendered.append(leading + visible + trailing)
    return "\n".join(rendered)


def layout_signature(text: str) -> tuple[object, ...]:
    lines = text.split("\n")
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line_edge(line) for line in lines),
        tuple(line.count("\u3000") for line in lines),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


def resolved_translations(current_records: dict[tuple[int, int], Any]) -> dict[str, str]:
    translations = {}
    for coordinate, raw in RAW_TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        translations[coordinate] = adopt_current_layout(raw, current)
    return translations


def assert_context_mapping(
    source_records: dict[tuple[int, int], Any],
    pk_source_records: dict[tuple[int, int], Any],
    base_context: dict[str, dict[tuple[int, int], Any]],
    pk_context: dict[str, dict[tuple[int, int], Any]],
) -> None:
    mapped_ids = {record_id + 7 for record_id in RECORD_ARITIES}
    if mapped_ids & PK_ONLY_RECORD_IDS:
        raise RuntimeError("segment 811 mapped a PK-only insertion")
    for language, base_records, pk_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context["SC"], pk_context["SC"]),
        ("TC", base_context["TC"], pk_context["TC"]),
    ):
        divergences = {
            record_id
            for record_id in RECORD_ARITIES
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(15, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(pk_records[(15, record_id + 7)])
            ]
        }
        if divergences:
            raise RuntimeError(
                f"segment 811 PK {language} exact +7 mappings drifted: {sorted(divergences)}"
            )


def assert_scope(prepared: Any, translations: dict[str, str]) -> None:
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
        source_records, pk_source_records, base_context, pk_context
    )

    expected_coordinates = set()
    actual_current_ellipsis = set()
    for record_id, arity in RECORD_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 811 arity drifted: 15:{record_id}")
        expected_gaps = gaps_from_hex(EXPECTED_GAPS[record_id])
        if record_gaps(source_record) != expected_gaps or record_gaps(current_record) != expected_gaps:
            raise RuntimeError(f"segment 811 dynamic skeleton drifted: 15:{record_id}")
        for literal_id, literal in enumerate(current_literals):
            coordinate = f"15:{record_id}:{literal_id}"
            expected_coordinates.add(coordinate)
            if "…" in literal.text:
                actual_current_ellipsis.add(coordinate)

    if actual_current_ellipsis != CURRENT_ELLIPSIS_COORDINATES:
        raise RuntimeError("segment 811 current contextual ellipsis coordinates drifted")
    if set(translations) != expected_coordinates or len(translations) != 19:
        raise RuntimeError("segment 811 decision universe drifted")
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"segment 811 layout signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment 811 forbidden script/control drifted: {coordinate}")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"segment 811 retains fullwidth punctuation: {coordinate}")
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment 811 retains an unpaired ellipsis: {coordinate}")

    if {translations[coordinate] for coordinate in POSSESSIVE_COORDINATES} != {"의"}:
        raise RuntimeError("segment 811 clan/officer possessive boundaries drifted")
    if translations["15:380:1"].split("\n", 1)[0] != "에게":
        raise RuntimeError("segment 811 15:380 officer dative boundary drifted")
    if translations["15:382:2"] != "에게……":
        raise RuntimeError("segment 811 15:382 officer dative boundary drifted")
    if translations["15:383:2"] != "(이)라든가":
        raise RuntimeError("segment 811 15:383 example-name particle drifted")
    if not translations["15:378:1"].endswith("이쪽으로 귀순할지도 몰라"):
        raise RuntimeError("segment 811 rough defection proposal voice drifted")
    if "우리 가문에 귀순할지도" not in translations["15:381:2"]:
        raise RuntimeError("segment 811 defection destination drifted")
    if not translations["15:382:0"].startswith("귀순할 듯한 무장"):
        raise RuntimeError("segment 811 stratagem target semantics drifted")
    joined = "\n".join(translations.values())
    required_terms = ("조략", "귀순", "우리 가문", "공략")
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 811 required terminology drifted")
    if any(term in joined for term in ("당가", "、")):
        raise RuntimeError("segment 811 retains forbidden terminology/punctuation")


def assert_isolated_overlay_roundtrip(
    prepared: Any, translations: dict[str, str]
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
        raise RuntimeError("segment 811 record count drifted from 19152")
    target_records = {(15, record_id) for record_id in RECORD_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 811 changed an out-of-scope record: {key}")
    for key in target_records:
        if record_gaps(rebuilt_records[key]) != record_gaps(current_records[key]):
            raise RuntimeError(f"segment 811 target skeleton drifted: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment 811 UTF-16 round-trip failed: {key}")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 811 reverse overlay is not byte-exact")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    translations = resolved_translations(current_records)
    assert_scope(prepared, translations)
    assert_isolated_overlay_roundtrip(prepared, translations)
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


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 811 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S811",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "protected_ellipsis": 0,
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
