#!/usr/bin/env python3
"""Build Base authoring segment 809 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S809.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s809", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
RAW_TRANSLATIONS: dict[str, str] = {
    "15:349:0": "불러 주시니 황송하기 그지없사옵니다\n이제부터 이",
    "15:349:1": "놈을\n",
    "15:349:2": "의 칼날로 써 주시옵소서",
    "15:350:0": "불초,",
    "15:350:1": "\n제 재주를 펼칠 수 있는 주군을 찾고 있었사옵니다\n",
    "15:350:2": "을(를) 섬기게 되어 영광이옵니다",
    "15:351:0": (
        "(이)라 하옵니다\n"
        "이번에 말석에 들게 되었사오니\n"
        "어떠한 일이라도 맡겨 주시옵소서"
    ),
    "15:352:0": "은(는)",
    "15:352:1": "(이)라 한다\n이 목숨이 다할 때까지\n",
    "15:352:2": "을(를) 위해 싸우겠나이다!",
    "15:353:0": (
        "(이)라고 합니다\n"
        "부족한 점도 많겠지만\n"
        "최선을 다하겠습니다!"
    ),
    "15:354:0": "이름은",
    "15:354:1": (
        "(이)라 한다\n"
        "이제부터 신세 좀 지겠다\n"
        "싸움이라면 내게 맡겨 주시오!"
    ),
    "15:355:0": ",",
    "15:355:1": "(이)라고 합니다\n조금이나마",
    "15:355:2": "의 힘이 될 수 있도록\n정성을 다하겠어요",
    "15:356:0": "이제부터 이",
    "15:356:2": "의 힘이 될 수 있도록 충성을 다하겠습니다\n",
    "15:356:3": "의 활약을 기대해 주시옵소서",
    "15:357:0": "님을 찾아냈",
    "15:357:1": "으나\n사관 권유는 거절당하",
    "15:357:2": "\n설득하지 못해 송구",
}
RECORD_ARITIES = {349: 3, 350: 3, 351: 1, 352: 3, 353: 1, 354: 2, 355: 3, 356: 4, 357: 3}
EXPECTED_GAPS = {
    349: ("", "024635", "014308000000", "050505"),
    350: ("", "024633", "014308000000", "050505"),
    351: ("024633", "050505"),
    352: ("014301000000", "024633", "014308000000", "050505"),
    353: ("024633", "050505"),
    354: ("", "024633", "050505"),
    355: ("014301000000", "024633", "014308000000", "050505"),
    356: ("", "024633", "014308000000", "014301000000", "050505"),
    357: ("024833", "014314020000", "014372040000", "014384010000050505"),
}
EXCLUDED_BLANK = "15:356:1"
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
    "pristine_base_pc_jp_authoritative_dynamic_officer_employment_fragments_"
    "with_base_sc_tc_and_exact_offset_plus_7_pk_jp_en_sc_tc_auxiliary_context_"
    "current_pc_literal_arity_outer_layout_and_opcode_skeleton_preserved_"
    "runtime_assembly_pending_pk_only_insertions_excluded"
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
        raise RuntimeError("segment 809 mapped a PK-only insertion")
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
                f"segment 809 PK {language} exact +7 mappings drifted: {sorted(divergences)}"
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
    for record_id, arity in RECORD_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 809 arity drifted: 15:{record_id}")
        expected_gaps = gaps_from_hex(EXPECTED_GAPS[record_id])
        if record_gaps(source_record) != expected_gaps or record_gaps(current_record) != expected_gaps:
            raise RuntimeError(f"segment 809 dynamic skeleton drifted: 15:{record_id}")
        for literal_id in range(arity):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate == EXCLUDED_BLANK:
                if (
                    source_literals[literal_id].text != "\n"
                    or current_literals[literal_id].text != "\n"
                    or ENGINE.is_visible_translation_candidate(source_literals[literal_id].text)
                    or ENGINE.is_visible_translation_candidate(current_literals[literal_id].text)
                    or coordinate in translations
                ):
                    raise RuntimeError("segment 809 LF-only blank drifted")
                continue
            expected_coordinates.add(coordinate)

    if set(translations) != expected_coordinates or len(translations) != 22:
        raise RuntimeError("segment 809 decision universe drifted")
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"segment 809 layout signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment 809 forbidden script/control drifted: {coordinate}")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"segment 809 retains fullwidth punctuation: {coordinate}")
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment 809 retains an unpaired ellipsis: {coordinate}")

    if source_records[(15, 346)].data == current_records[(15, 346)].data:
        raise RuntimeError("segment 809 expected prior Korean overlay at 15:346")
    prior_346 = ENGINE.parse_record_literals(current_records[(15, 346)])[0].text
    if translations["15:352:0"] != prior_346 or translations["15:352:0"] != "은(는)":
        raise RuntimeError("segment 809 は subject-particle reuse drifted")
    if translations["15:355:0"] != ",":
        raise RuntimeError("segment 809 must replace the Japanese comma with ASCII comma")
    if translations["15:353:0"] != (
        "(이)라고 합니다\n부족한 점도 많겠지만\n최선을 다하겠습니다!"
    ):
        raise RuntimeError("segment 809 young polite introduction voice drifted")
    if not translations["15:354:1"].endswith("싸움이라면 내게 맡겨 주시오!"):
        raise RuntimeError("segment 809 rough retainer hierarchy drifted")
    if not translations["15:355:2"].endswith("정성을 다하겠어요"):
        raise RuntimeError("segment 809 feminine introduction voice drifted")
    joined = "\n".join(translations.values())
    required_terms = ("황송하기 그지없", "불초", "말석에 들", "사관", "칼날")
    if any(term not in joined for term in required_terms):
        raise RuntimeError("segment 809 required diction drifted")
    if any(term in joined for term in ("말석을 더럽", "출사", "、")):
        raise RuntimeError("segment 809 retains forbidden literalism/punctuation")


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
        raise RuntimeError("segment 809 record count drifted from 19152")
    target_records = {(15, record_id) for record_id in RECORD_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 809 changed an out-of-scope record: {key}")
    for key in target_records:
        if record_gaps(rebuilt_records[key]) != record_gaps(current_records[key]):
            raise RuntimeError(f"segment 809 target skeleton drifted: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment 809 UTF-16 round-trip failed: {key}")
    if ENGINE.parse_record_literals(rebuilt_records[(15, 356)])[1].text != "\n":
        raise RuntimeError("segment 809 changed the LF-only blank")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 809 reverse overlay is not byte-exact")


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
        raise RuntimeError("segment 809 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S809",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "excluded_lf_only_blank": 1,
                "contextual_ellipsis_normalized_to_project_pair": 0,
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
