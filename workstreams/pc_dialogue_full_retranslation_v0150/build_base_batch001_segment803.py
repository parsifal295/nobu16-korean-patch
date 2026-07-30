#!/usr/bin/env python3
"""Build Base authoring segment 803 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S803.private.v1.jsonl"
SEGMENT = 803


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s803", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
TRANSLATIONS: dict[str, str] = {
    "15:271:0": "효과는 다소 떨어지지만\n신속히 끝낼 수 있는 계책입니다",
    "15:272:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:272:1": "\n비용은 늘어나",
    "15:272:2": "지만\n착실히 진행할 수 있",
    "15:273:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:273:1": "\n비용은 늘어나",
    "15:273:2": "지만\n착실히 진행할 수 있",
    "15:274:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:274:1": "\n시간은 걸리",
    "15:274:2": "지만\n착실히 진행할 수 있",
    "15:275:0": "더 성공하기 쉬운 계책이라 할 수 있",
    "15:275:1": "\n시간은 걸리",
    "15:275:2": "지만\n착실히 진행할 수 있",
    "15:276:0": "더 성공하기 쉬운 계책이라 할 수 있습니다",
    "15:276:1": "\n실행할 곳을 좁히는 만큼\n착실히 진행할 수 있습니다",
    "15:277:0": "\n모 아니면 도인 계책",
    "15:277:1": "이지만\n큰 효과를 기대할 수 있을 것입니다",
    "15:278:0": "채비에는 시간이 걸리지만\n넓은 범위에 계책을 펼칠 수 있습니다",
    "15:279:0": "\n비용은 늘어나",
    "15:279:1": "지만\n효과는 막대하다고 할 수 있",
}

EXPECTED_ARITIES = {
    271: 1,
    272: 3,
    273: 3,
    274: 3,
    275: 3,
    276: 2,
    277: 2,
    278: 1,
    279: 2,
}
EXPECTED_SOURCE_GAPS = {
    271: ("0143f6490200", "014326020000050505"),
    272: ("", "01431e040000", "0143a0030000", "01433c040000050505"),
    273: ("", "01431e040000", "0143a0030000", "01433c040000050505"),
    274: ("", "01431e040000", "014336040000", "01433c040000050505"),
    275: ("", "01431e040000", "014336040000", "01433c040000050505"),
    276: ("", "01431e040000", "01433c040000050505"),
    277: ("0143f6490200", "01432c020000", "050505"),
    278: ("0143f6490200", "01431e040000050505"),
    279: ("0143f6490200", "0143a0030000", "01431e040000050505"),
}
EXPECTED_CURRENT_GAPS = {
    271: ("", "050505"),
    272: ("", "01431e040000", "0143a0030000", "01433c040000050505"),
    273: ("", "01431e040000", "0143a0030000", "01433c040000050505"),
    274: ("", "01431e040000", "014336040000", "01433c040000050505"),
    275: ("", "01431e040000", "014336040000", "01433c040000050505"),
    276: ("", "", "050505"),
    277: ("0143f6490200", "01432c020000", "050505"),
    278: ("", "050505"),
    279: ("0143f6490200", "0143a0030000", "01431e040000050505"),
}

PK_ONLY_RECORD_IDS = {271, 272, 273}
BASE_PK_DIVERGENCES = {"JP": set(), "SC": set(), "TC": set()}
PROTECTED_GLYPHS = {"…"}
BANNED_FULLWIDTH_PUNCTUATION = set("。、！？：；（）［］｛｝〈〉《》「」『』【】")
BASIS = (
    "pristine_base_pc_jp_authoritative_with_exact_plus3_mapped_"
    "pk_jp_en_sc_tc_auxiliary_context_and_current_runtime_fragment_skeleton"
)


def mapped_pk_record_id(base_record_id: int) -> int:
    return base_record_id + 3


def record_gaps_hex(record: Any) -> tuple[str, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps = [record.data[: literals[0].marker_offset]]
    gaps.extend(
        record.data[left.marker_end : right.marker_offset]
        for left, right in zip(literals, literals[1:])
    )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gap.hex() for gap in gaps)


def glyph_skeleton(text: str) -> list[str]:
    return [character for character in text if character in PROTECTED_GLYPHS]


def layout_signature(text: str) -> tuple[object, ...]:
    protected = ENGINE.protected_signature(text)
    return (
        text.count("\n"),
        tuple(line.count("\u3000") for line in text.split("\n")),
        tuple(ENGINE.ESC_TAG_RE.findall(text)),
        tuple(ENGINE.PRINTF_RE.findall(text)),
        tuple(ENGINE.BRACKET_TOKEN_RE.findall(text)),
        tuple(protected["non_layout_controls"]),
        protected["leading_whitespace"],
        protected["trailing_whitespace"],
    )


def source_text(records: dict[tuple[int, int], Any], record_id: int, literal_id: int) -> str:
    return ENGINE.parse_record_literals(records[(15, record_id)])[literal_id].text


def assert_common_scope(
    prepared: Any,
    *,
    segment: int,
    translations: dict[str, str],
    arities: dict[int, int],
    source_gaps: dict[int, tuple[str, ...]],
    current_gaps: dict[int, tuple[str, ...]],
    semantic_assertions: Callable[[dict[tuple[int, int], Any]], None],
) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context_records = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }

    mapped_ids = {mapped_pk_record_id(record_id) for record_id in arities}
    if mapped_ids & PK_ONLY_RECORD_IDS:
        raise RuntimeError(f"segment {segment} mapped through a PK-only insertion record")
    expected_mapped_ids = set(range(min(arities) + 3, max(arities) + 4))
    if mapped_ids != expected_mapped_ids:
        raise RuntimeError(f"segment {segment} Base-to-PK +3 mapping drifted")

    for language, base_records, mapped_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context_records["SC"], pk_context_records["SC"]),
        ("TC", base_context_records["TC"], pk_context_records["TC"]),
    ):
        divergences = {
            record_id
            for record_id in arities
            if [
                literal.text
                for literal in ENGINE.parse_record_literals(base_records[(15, record_id)])
            ]
            != [
                literal.text
                for literal in ENGINE.parse_record_literals(
                    mapped_records[(15, mapped_pk_record_id(record_id))]
                )
            ]
        }
        if divergences != BASE_PK_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment {segment} mapped PK {language} divergences drifted: "
                f"{sorted(divergences)}"
            )

    for record_id, arity in arities.items():
        source_literals = ENGINE.parse_record_literals(source_records[(15, record_id)])
        current_literals = ENGINE.parse_record_literals(current_records[(15, record_id)])
        if len(source_literals) != arity:
            raise RuntimeError(f"segment {segment} source literal arity drifted: 15:{record_id}")
        if len(current_literals) != arity:
            raise RuntimeError(f"segment {segment} current literal arity drifted: 15:{record_id}")
        if record_gaps_hex(source_records[(15, record_id)]) != source_gaps[record_id]:
            raise RuntimeError(
                f"segment {segment} pristine opaque gaps drifted: 15:{record_id}"
            )
        if record_gaps_hex(current_records[(15, record_id)]) != current_gaps[record_id]:
            raise RuntimeError(
                f"segment {segment} current opaque gaps drifted: 15:{record_id}"
            )
        if any(not literal.text.strip() for literal in source_literals + current_literals):
            raise RuntimeError(
                f"segment {segment} contains an unexpected blank literal: 15:{record_id}"
            )

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[
            literal_id
        ].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"{coordinate} line/U+3000/outer/token signature drifted")
        if glyph_skeleton(translation) != glyph_skeleton(current_text):
            raise RuntimeError(f"{coordinate} protected ellipsis skeleton drifted")
        if "\r" in translation:
            raise RuntimeError(f"{coordinate} must not add CR")
        if ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"{coordinate} retains kana or CJK Han text")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"{coordinate} retains banned fullwidth punctuation")

    expected_coordinates = {
        f"15:{record_id}:{literal_id}"
        for record_id, arity in arities.items()
        for literal_id in range(arity)
    }
    if set(translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} decision coordinate set drifted")
    if len(translations) != sum(arities.values()):
        raise RuntimeError(f"segment {segment} decision count drifted")

    semantic_assertions(source_records)


def assert_isolated_overlay_roundtrip(
    prepared: Any,
    *,
    segment: int,
    translations: dict[str, str],
    arities: dict[int, int],
) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements: dict[tuple[int, int, int], str] = {}
    reverse_replacements: dict[tuple[int, int, int], str] = {}
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
        raise RuntimeError(f"segment {segment} Base record count drifted from 19152")

    target_records = {(15, record_id) for record_id in arities}
    outside_exact = 0
    for key, current_record in current_records.items():
        if key not in target_records:
            if rebuilt_records[key].data != current_record.data:
                raise RuntimeError(f"segment {segment} changed an out-of-scope record: {key}")
            outside_exact += 1
    if outside_exact != 19152 - len(target_records):
        raise RuntimeError(f"segment {segment} outside-scope byte-exact count drifted")
    for record_key in target_records:
        if record_gaps_hex(rebuilt_records[record_key]) != record_gaps_hex(
            current_records[record_key]
        ):
            raise RuntimeError(
                f"segment {segment} changed a target opaque skeleton: {record_key}"
            )
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text
        if actual != translation:
            raise RuntimeError(
                f"segment {segment} literal failed UTF-16 round-trip: {key}"
            )

    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse_replacements)
    if reversed_blob != base.current_blob:
        raise RuntimeError(f"segment {segment} reverse overlay is not byte-exact")


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    translations: dict[str, str],
    arities: dict[int, int],
    source_gaps: dict[int, tuple[str, ...]],
    current_gaps: dict[int, tuple[str, ...]],
    semantic_assertions: Callable[[dict[tuple[int, int], Any]], None],
) -> tuple[Any, list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_common_scope(
        prepared,
        segment=segment,
        translations=translations,
        arities=arities,
        source_gaps=source_gaps,
        current_gaps=current_gaps,
        semantic_assertions=semantic_assertions,
    )
    assert_isolated_overlay_roundtrip(
        prepared,
        segment=segment,
        translations=translations,
        arities=arities,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets.get(("base_msggame", block_id, record_id, literal_id))
        if target is None:
            raise RuntimeError(
                f"decision target is absent from the current Base universe: {coordinate}"
            )
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


def assert_semantics(source_records: dict[tuple[int, int], Any]) -> None:
    group_0 = (272, 273, 274, 275, 276, 280)
    if len({source_text(source_records, record_id, 0) for record_id in group_0}) != 1:
        raise RuntimeError("proposal-success exact-source group drifted")
    group_1 = ((272, 1), (273, 1), (279, 0), (280, 1))
    if len({source_text(source_records, record_id, literal_id) for record_id, literal_id in group_1}) != 1:
        raise RuntimeError("proposal-cost exact-source group drifted")
    group_2 = ((272, 2), (273, 2), (274, 2), (275, 2), (280, 2))
    if len({source_text(source_records, record_id, literal_id) for record_id, literal_id in group_2}) != 1:
        raise RuntimeError("proposal-steady-progress exact-source group drifted")
    if source_text(source_records, 274, 1) != source_text(source_records, 275, 1):
        raise RuntimeError("proposal-time exact-source pair drifted")

    if TRANSLATIONS["15:272:0"] != TRANSLATIONS["15:273:0"]:
        raise RuntimeError("15:272/273 success translation exactness drifted")
    if TRANSLATIONS["15:272:1"] != TRANSLATIONS["15:273:1"]:
        raise RuntimeError("15:272/273 cost translation exactness drifted")
    if TRANSLATIONS["15:272:2"] != TRANSLATIONS["15:273:2"]:
        raise RuntimeError("15:272/273 progress translation exactness drifted")
    if TRANSLATIONS["15:274:0"] != TRANSLATIONS["15:275:0"]:
        raise RuntimeError("15:274/275 success translation exactness drifted")
    if TRANSLATIONS["15:274:1"] != TRANSLATIONS["15:275:1"]:
        raise RuntimeError("15:274/275 time translation exactness drifted")
    if TRANSLATIONS["15:274:2"] != TRANSLATIONS["15:275:2"]:
        raise RuntimeError("15:274/275 progress translation exactness drifted")
    if TRANSLATIONS["15:272:0"] != TRANSLATIONS["15:274:0"]:
        raise RuntimeError("same proposal-success source must reuse one Korean fragment")
    if TRANSLATIONS["15:272:2"] != TRANSLATIONS["15:274:2"]:
        raise RuntimeError("same steady-progress source must reuse one Korean fragment")
    if TRANSLATIONS["15:272:1"] != TRANSLATIONS["15:279:0"]:
        raise RuntimeError("same proposal-cost source must reuse one Korean fragment")

    joined = "\n".join(TRANSLATIONS.values())
    if any(term not in joined for term in ("계책", "비용", "시간", "모 아니면 도")):
        raise RuntimeError("segment 803 required proposal terminology drifted")
    if any(term in joined for term in ("책략", "이(가)", "절대적")):
        raise RuntimeError("segment 803 retains a forbidden proposal mistranslation")
    if "효과는 막대하다고" not in TRANSLATIONS["15:279:1"]:
        raise RuntimeError("15:279 lost the increased-cost/large-effect contrast")


def build_rows() -> tuple[Any, list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        translations=TRANSLATIONS,
        arities=EXPECTED_ARITIES,
        source_gaps=EXPECTED_SOURCE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(TRANSLATIONS):
        raise RuntimeError("validated decision count differs from the segment translation count")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S803",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
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
