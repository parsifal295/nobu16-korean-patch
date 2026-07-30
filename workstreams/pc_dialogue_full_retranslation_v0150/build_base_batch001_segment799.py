#!/usr/bin/env python3
"""Build Base authoring segment 799 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S799.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s799", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
RAW_TRANSLATIONS: dict[str, str] = {
    "15:225:0": "승산은 낮다고 보",
    "15:225:1": "지만…\n맞아도 팔괘, 안 맞아도 팔괘\n한 번 걸어 보는 것도 재미있겠지",
    "15:226:0": "…솔직히 말해, 승산이 낮은 도박입니다.",
    "15:226:1": "\n그다지 권하고 싶지는 않습니다.",
    "15:227:0": "! 뛰어난 성과를\n기대할 수 있",
    "15:228:0": "이 정도면 좋은 성과를\n얻을 수 있",
    "15:229:0": "무난한 성과는\n거둘 수 있",
    "15:230:0": "그리 많은 성과는\n바랄 수 없다",
    "15:230:1": "…",
    "15:231:0": "! 뛰어난 성과를\n기대할 수 있",
    "15:232:0": "이 정도면 좋은 성과를\n얻을 수 있",
    "15:233:0": "무난한 성과는\n거둘 수 있",
    "15:234:0": "그리 많은 성과는\n바랄 수 없다",
    "15:234:1": "…",
    "15:235:0": "! 뛰어난 성과를\n기대할 수 있",
    "15:236:0": "이 정도면 좋은 성과를\n얻을 수 있",
    "15:237:0": "무난한 성과는\n거둘 수 있",
    "15:238:0": "그리 많은 성과는\n바랄 수 없다",
    "15:238:1": "…",
    "15:239:0": "! 뛰어난 성과를\n기대할 수 있",
    "15:240:0": "이 정도면 좋은 성과를\n얻을 수 있",
    "15:241:0": "무난한 성과는\n거둘 수 있",
}
EXPECTED_ARITIES = {
    225: 2,
    226: 2,
    227: 1,
    228: 1,
    229: 1,
    230: 2,
    231: 1,
    232: 1,
    233: 1,
    234: 2,
    235: 1,
    236: 1,
    237: 1,
    238: 2,
    239: 1,
    240: 1,
    241: 1,
}
EXPECTED_SOURCE_GAPS = {
    225: ("", "01433c040000", "01431e010000050505"),
    226: ("", "01431e010000", "0143e4010000050505"),
    227: ("0143d6000000", "01433c0400000143f6010000050505"),
    228: ("", "01431e040000050505"),
    229: ("", "01431e040000050505"),
    230: ("", "01431e010000", "050505"),
    231: ("0143d6000000", "01433c0400000143f6010000050505"),
    232: ("", "01431e040000050505"),
    233: ("", "01431e040000050505"),
    234: ("", "01431e010000", "050505"),
    235: ("0143d6000000", "01433c0400000143f6010000050505"),
    236: ("", "01431e040000050505"),
    237: ("", "01431e040000050505"),
    238: ("", "01431e010000", "050505"),
    239: ("0143d6000000", "01433c0400000143f6010000050505"),
    240: ("", "01431e040000050505"),
    241: ("", "01431e040000050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_SOURCE_GAPS,
    226: ("", "", "050505"),
}
PROTECTED_ELLIPSIS_COORDINATES = {"15:230:1", "15:234:1", "15:238:1"}
BANNED_FULLWIDTH_PUNCTUATION = set("！？，。、「」『』（）【】［］｛｝〈〉《》〔〕：；・…／＜＞＝＋－")
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
        "…": "...",
    }
)
ASCII_PUNCTUATION_PRESERVE_ELLIPSIS = str.maketrans(
    {
        "【": "[",
        "】": "]",
        "「": '"',
        "」": '"',
        "／": "/",
        "，": ",",
        "。": ".",
        "・": "·",
    }
)
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_fragments_with_base_sc_tc_"
    "and_exact_offset_plus_3_pk_jp_en_sc_tc_context_current_pc_outer_"
    "literal_arity_and_opcode_skeleton_preserved_runtime_assembly_pending"
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


def adopt_current_layout(raw: str, current: str, preserve_ellipsis: bool = False) -> str:
    raw_lines = raw.split("\n")
    current_lines = current.split("\n")
    if len(raw_lines) != len(current_lines):
        raise RuntimeError("raw translation LF count differs from current layout")
    rendered = []
    for raw_line, current_line in zip(raw_lines, current_lines):
        leading, trailing = line_edge(current_line)
        punctuation = (
            ASCII_PUNCTUATION_PRESERVE_ELLIPSIS
            if preserve_ellipsis
            else ASCII_PUNCTUATION
        )
        visible = raw_line.strip(" \t\u3000").translate(punctuation)
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
        translations[coordinate] = adopt_current_layout(
            raw,
            current,
            preserve_ellipsis=coordinate in PROTECTED_ELLIPSIS_COORDINATES,
        )
    return translations


def assert_exact_repetitions(translations: dict[str, str]) -> None:
    for coordinates in (
        ("15:227:0", "15:231:0", "15:235:0", "15:239:0"),
        ("15:228:0", "15:232:0", "15:236:0", "15:240:0"),
        ("15:229:0", "15:233:0", "15:237:0", "15:241:0"),
        ("15:230:0", "15:234:0", "15:238:0"),
        ("15:230:1", "15:234:1", "15:238:1"),
    ):
        values = {translations[coordinate] for coordinate in coordinates}
        if len(values) != 1:
            raise RuntimeError(f"segment 799 exact-source repetition drifted: {coordinates}")


def assert_cross_segment_ellipsis(
    source_records: dict[tuple[int, int], Any],
    current_records: dict[tuple[int, int], Any],
    translations: dict[str, str],
) -> None:
    reference_source = ENGINE.parse_record_literals(source_records[(15, 242)])[1].text
    reference_current = ENGINE.parse_record_literals(current_records[(15, 242)])[1].text
    for record_id in (230, 234, 238):
        source = ENGINE.parse_record_literals(source_records[(15, record_id)])[1].text
        current = ENGINE.parse_record_literals(current_records[(15, record_id)])[1].text
        if source != reference_source or current != reference_current:
            raise RuntimeError(
                f"segment 799/800 exact ellipsis source/current drifted: 15:{record_id}:1"
            )
        if translations[f"15:{record_id}:1"] != reference_current:
            raise RuntimeError(
                f"segment 799 protected ellipsis differs from 15:242:1: 15:{record_id}:1"
            )
    segment_800 = OUTPUT.parent / "base_msggame_B001_S800.private.v1.jsonl"
    if not segment_800.is_file():
        return
    for line in segment_800.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = ENGINE.json.loads(line)
        if row.get("coordinate") == "15:242:1":
            if row.get("translation") != reference_current:
                raise RuntimeError("segment 800 15:242:1 exact ellipsis decision drifted")
            return
    raise RuntimeError("segment 800 exact ellipsis decision is missing: 15:242:1")


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
                for literal in ENGINE.parse_record_literals(pk_records[(15, record_id + 3)])
            ]
        }
        if divergences:
            raise RuntimeError(
                f"segment 799 PK {language} exact +3 mappings drifted: {sorted(divergences)}"
            )

    expected_coordinates = set()
    for record_id, arity in EXPECTED_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        if len(ENGINE.parse_record_literals(source_record)) != arity or len(
            ENGINE.parse_record_literals(current_record)
        ) != arity:
            raise RuntimeError(f"segment 799 arity drifted: 15:{record_id}")
        if record_gaps(source_record) != gaps_from_hex(EXPECTED_SOURCE_GAPS[record_id]):
            raise RuntimeError(f"segment 799 source dynamic skeleton drifted: 15:{record_id}")
        if record_gaps(current_record) != gaps_from_hex(EXPECTED_CURRENT_GAPS[record_id]):
            raise RuntimeError(f"segment 799 current dynamic skeleton drifted: 15:{record_id}")
        expected_coordinates.update(f"15:{record_id}:{literal_id}" for literal_id in range(arity))

    if set(translations) != expected_coordinates or len(translations) != 22:
        raise RuntimeError("segment 799 decision/runtime count drifted")
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"segment 799 layout signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment 799 forbidden script/control drifted: {coordinate}")
        banned = BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        if coordinate in PROTECTED_ELLIPSIS_COORDINATES:
            banned.discard("…")
            if current_text != "…" or translation != current_text:
                raise RuntimeError(
                    f"segment 799 protected exact ellipsis glyph drifted: {coordinate}"
                )
        if banned:
            raise RuntimeError(f"segment 799 retains fullwidth punctuation: {coordinate}")
    assert_exact_repetitions(translations)
    assert_cross_segment_ellipsis(source_records, current_records, translations)


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
        raise RuntimeError("segment 799 record count drifted from 19152")
    target_records = {(15, record_id) for record_id in EXPECTED_ARITIES}
    for key, current_record in current_records.items():
        if key not in target_records and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 799 changed an out-of-scope record: {key}")
    for key in target_records:
        if record_gaps(rebuilt_records[key]) != record_gaps(current_records[key]):
            raise RuntimeError(f"segment 799 target skeleton drifted: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment 799 UTF-16 round-trip failed: {key}")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 799 reverse overlay is not byte-exact")


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
        raise RuntimeError("segment 799 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S799",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "steam_write_performed": False,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "dynamic_assembly_basis": {
                    "15:225": "current_pc_middle_and_final_personality_suffix_opcodes_retained",
                    "15:226": "current_pc_flattened_jp_inflection_opcodes_fragments_concatenate",
                    "15:227,231,235,239": "current_pc_prefix_and_final_personality_opcodes_retained",
                    "15:228-229,232-233,236-237,240-241": "current_pc_final_personality_opcode_retained",
                    "15:230,234,238": "current_pc_middle_personality_opcode_retained",
                },
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
