#!/usr/bin/env python3
"""Build Base authoring segment 806 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S806.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s806", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "15:310:0": "낭인이었던 자,",
    "15:310:1": (
        "이(가)\n"
        "우리 가문을 섬기고 싶다 하옵니다\n"
        "맞아들일 채비를 갖추"
    ),
    "15:310:2": "까?",
    "15:311:0": (
        "이(가) 우리 가문에 몸을 의탁해\n"
        "사관하고 싶다고 한다는데...\n"
        "기꺼이 맞아들여야 할 줄로 아옵니다"
    ),
    "15:312:0": "에게서 사관하고 싶다는\n서신이 도착한 듯",
    "15:312:1": "\n회답을 서둘러",
    "15:313:0": (
        "라는 낭인이\n"
        "우리 가문의 승전보를 듣고 꼭 섬기고 싶다 하니\n"
        "한 번 만나 보시는 것도"
    ),
    "15:313:1": "까 하옵니다",
    "15:314:0": "사관을 청하러 온 낭인이",
    "15:314:2": "라는 자, 우리 가문의 승전 소식을\n벌써 전해 들은 모양입니다",
    "15:315:0": "라는 자가 성하에 찾아와\n",
    "15:315:1": "인",
    "15:315:2": "을(를) 섬기고 싶다 하니\n한 번",
    "15:315:3": "인견",
    "15:315:4": "는 것이 어떠실지요",
    "15:316:0": "라는 자가 성하에 찾아와\n",
    "15:316:1": "인",
    "15:316:2": "을(를) 섬기고 싶다 하니\n한 번",
    "15:316:3": "인견",
    "15:316:4": "는 것이 어떠실지요",
}
EXPECTED_ARITIES = {310: 3, 311: 1, 312: 2, 313: 2, 314: 3, 315: 5, 316: 5}
EXPECTED_GAPS = {
    310: ("", "024833", "01431e040000", "050505"),
    311: ("024833", "0143e2000000050505"),
    312: ("024833", "01432c020000", "014304030000050505"),
    313: ("024833", "01430c040000", "050505"),
    314: ("", "0143b2000000", "024833", "0143c8020000050505"),
    315: ("024833", "023c", "014308000000", "01438a040000", "014310030000", "050505"),
    316: ("024833", "023c", "014308000000", "01438a040000", "014310030000", "050505"),
}
PK_ONLY_RECORD_IDS = {317, 319, 324, 326}
BLANK_NON_DISPLAY_COORDINATE = "15:314:1"
PROTECTED_GLYPHS: set[str] = set()
BANNED_FULLWIDTH_PUNCTUATION = set(
    "！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－＆"
)
BASIS = (
    "pristine_base_pc_jp_authoritative_with_base_sc_tc_and_explicit_"
    "mapped_pk_jp_en_sc_tc_auxiliary_context_current_pc_runtime_name_"
    "inflection_and_outer_opcode_skeleton_preserved"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    mapping = {310: 313, 311: 314, 312: 315, 313: 316, 314: 318, 315: 320, 316: 321}
    try:
        return mapping[base_record_id]
    except KeyError as exc:
        raise RuntimeError(f"segment 806 record has no PK mapping: {base_record_id}") from exc


def record_gaps_hex(record: Any) -> tuple[str, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gap.hex() for gap in gaps)


def line_edge(text: str) -> tuple[str, str]:
    return (
        text[: len(text) - len(text.lstrip(" \t\u3000"))],
        text[len(text.rstrip(" \t\u3000")) :],
    )


def layout_signature(text: str) -> tuple[object, ...]:
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line_edge(line) for line in text.split("\n")),
        tuple(line.count("\u3000") for line in text.split("\n")),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in PROTECTED_GLYPHS]


def assert_context_mappings(prepared: Any) -> tuple[dict[tuple[int, int], Any], dict[tuple[int, int], Any]]:
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
    mapped_ids = {mapped_pk_record_id(record_id) for record_id in EXPECTED_ARITIES}
    if mapped_ids & PK_ONLY_RECORD_IDS:
        raise RuntimeError("segment 806 mapped through a PK-only insertion")
    if mapped_ids != {313, 314, 315, 316, 318, 320, 321}:
        raise RuntimeError("segment 806 explicit Base-to-PK mapping drifted")
    for language, base_records, pk_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context["SC"], pk_context["SC"]),
        ("TC", base_context["TC"], pk_context["TC"]),
    ):
        divergences = {
            record_id
            for record_id in EXPECTED_ARITIES
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(15, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    pk_records[(15, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences:
            raise RuntimeError(
                f"segment 806 PK {language} mapped divergence drifted: {sorted(divergences)}"
            )
    return source_records, current_records


def assert_scope(prepared: Any) -> None:
    source_records, current_records = assert_context_mappings(prepared)
    expected_coordinates = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 806 source/current arity drifted: 15:{record_id}")
        if record_gaps_hex(source_record) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 806 source opcode skeleton drifted: 15:{record_id}")
        if record_gaps_hex(current_record) != EXPECTED_GAPS[record_id]:
            raise RuntimeError(f"segment 806 current opcode skeleton drifted: 15:{record_id}")
        for literal_id, current_literal in enumerate(current_literals):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate == BLANK_NON_DISPLAY_COORDINATE:
                if source_literals[literal_id].text != "\n" or current_literal.text != "\n":
                    raise RuntimeError("segment 806 LF-only blank drifted: 15:314:1")
                if coordinate in TRANSLATIONS:
                    raise RuntimeError("segment 806 LF-only blank must remain excluded")
                continue
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(f"segment 806 unexpected blank literal: {coordinate}")
            expected_coordinates.add(coordinate)
            translation = TRANSLATIONS.get(coordinate)
            if translation is None:
                raise RuntimeError(f"segment 806 decision is missing: {coordinate}")
            if layout_signature(translation) != layout_signature(current_literal.text):
                raise RuntimeError(f"segment 806 layout/outer signature drifted: {coordinate}")
            if glyph_skeleton(translation) != glyph_skeleton(current_literal.text):
                raise RuntimeError(f"segment 806 protected ellipsis drifted: {coordinate}")
            if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
                raise RuntimeError(f"segment 806 forbidden script/control drifted: {coordinate}")
            if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
                raise RuntimeError(f"segment 806 retains banned fullwidth punctuation: {coordinate}")
    if set(TRANSLATIONS) != expected_coordinates or len(TRANSLATIONS) != 20:
        raise RuntimeError("segment 806 decision universe drifted")

    source_315 = ENGINE.parse_record_literals(source_records[(15, 315)])
    source_316 = ENGINE.parse_record_literals(source_records[(15, 316)])
    if [literal.text for literal in source_315] != [literal.text for literal in source_316]:
        raise RuntimeError("segment 806 15:315/316 exact source repetition drifted")
    for literal_id in range(5):
        if TRANSLATIONS[f"15:315:{literal_id}"] != TRANSLATIONS[f"15:316:{literal_id}"]:
            raise RuntimeError(f"segment 806 15:315/316 translation drifted: literal {literal_id}")

    joined = "\n".join(TRANSLATIONS.values())
    for required in ("우리 가문", "낭인", "사관", "성하", "인견"):
        if required not in joined:
            raise RuntimeError(f"segment 806 required terminology drifted: {required}")
    if any(term in joined for term in ("당가", "임관", "접견", "、")):
        raise RuntimeError("segment 806 retains a forbidden legacy term")


def assert_isolated_overlay_roundtrip(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements = {}
    reverse = {}
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse[key] = ENGINE.parse_record_literals(current_records[key[:2]])[literal_id].text
    rebuilt = ENGINE.rebuild_packed_with_literals(base.current_blob, replacements)
    rebuilt_records = ENGINE.archive_records(ENGINE.parse_packed_msggame(rebuilt).archive)
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError("segment 806 Base record count drifted")
    targets = {(15, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in targets and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 806 changed out-of-scope record: {key}")
    for key in targets:
        if record_gaps_hex(rebuilt_records[key]) != record_gaps_hex(current_records[key]):
            raise RuntimeError(f"segment 806 changed target skeleton: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment 806 UTF-16 round-trip failed: {key}")
    if ENGINE.parse_record_literals(rebuilt_records[(15, 314)])[1].text != "\n":
        raise RuntimeError("segment 806 changed LF-only blank")
    if ENGINE.rebuild_packed_with_literals(rebuilt, reverse) != base.current_blob:
        raise RuntimeError("segment 806 reverse overlay is not byte-exact")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_scope(prepared)
    assert_isolated_overlay_roundtrip(prepared)
    rows = []
    for coordinate, translation in TRANSLATIONS.items():
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
    return prepared, rows


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("segment 806 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S806",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "excluded_non_display": 1,
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
