#!/usr/bin/env python3
"""Build Base authoring segment 815 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S815.private.v1.jsonl"


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s815", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
RAW_TRANSLATIONS: dict[str, str] = {
    "15:430:0": "이",
    "15:430:1": "을(를) 막하에 거두시다니\n",
    "15:430:2": (
        "은(는) 사람을 보는 눈이 있으신 듯하니\n"
        "반드시 기대에 부응해 보이겠사옵니다"
    ),
    "15:431:0": "이",
    "15:431:1": "\n어리석은 옛 주군을 버리고 왔사옵니다\n부디",
    "15:431:2": "께 힘이 되고자 하옵니다",
    "15:432:0": "이제부터 신세를 지겠사옵니다\n",
    "15:432:1": "은(는) 제 솜씨를 알아봐 주신 분\n이",
    "15:432:2": ", 반드시 보탬이 되겠사옵니다",
    "15:433:0": "영명하신 주군을 찾아왔사옵니다\n",
    "15:433:1": "(이)라 하옵니다\n",
    "15:433:2": "께서 중히 써 주시기를 바라옵니다…",
    "15:434:0": "불러 주시니 참으로 감사하옵니다\n",
    "15:434:1": "께 힘이 될 수 있도록\n분골쇄신하여 힘쓰겠사옵니다",
    "15:435:0": "이제부터 신세를 질",
    "15:435:1": "(이)라네\n",
    "15:435:2": "을(를) 위해\n몸이 부서져라 일하겠네!",
    "15:436:0": "을(를) 뵙고 싶었사옵니다\n앞으로 신세를 지겠사오며 이름은",
    "15:436:1": "(이)라 하옵니다\n앞으로 잘 부탁드리옵니다",
    "15:437:0": "(이)다\n",
    "15:437:1": "을(를) 위해 목숨을 걸겠다\n기대해 다오",
}
RECORD_ARITIES = {430: 3, 431: 3, 432: 3, 433: 3, 434: 2, 435: 3, 436: 2, 437: 2}
EXPECTED_GAPS = {
    430: ("", "024633", "014311000000", "050505"),
    431: ("", "024633", "014311000000", "050505"),
    432: ("", "014311000000", "024633", "050505"),
    433: ("", "024633", "014311000000", "050505"),
    434: ("", "014311000000", "050505"),
    435: ("", "024633", "014311000000", "050505"),
    436: ("014311000000", "024633", "050505"),
    437: ("024633", "014311000000", "050505"),
}
EXPECTED_PK_EN_ARITIES = {430: 2, 431: 2, 432: 2, 433: 1, 434: 1, 435: 1, 436: 2, 437: 1}
EXPECTED_PK_EN_GAPS = {
    430: ("", "024633", "050505"),
    431: ("", "024633", "050505"),
    432: ("", "024633", "050505"),
    433: ("", "050505"),
    434: ("", "050505"),
    435: ("", "050505"),
    436: ("", "024633", "050505"),
    437: ("", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {"15:433:2"}
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
    "pristine_base_pc_jp_authoritative_dynamic_retainer_recruitment_fragments_"
    "with_base_sc_tc_and_exact_offset_plus_7_pk_jp_en_sc_tc_auxiliary_context_"
    "speaker_lord_name_particles_person_voice_and_historical_register_verified_"
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
    if mapped_ids != set(range(437, 445)) or mapped_ids & PK_ONLY_RECORD_IDS:
        raise RuntimeError("segment 815 uniform +7 mapping drifted")
    for language, base_records, pk_records in (
        ("JP", source_records, pk_source_records),
        ("SC", base_context["SC"], pk_context["SC"]),
        ("TC", base_context["TC"], pk_context["TC"]),
    ):
        divergences = set()
        for record_id in RECORD_ARITIES:
            base_record = base_records[(15, record_id)]
            pk_record = pk_records[(15, record_id + 7)]
            base_literals = [literal.text for literal in ENGINE.parse_record_literals(base_record)]
            pk_literals = [literal.text for literal in ENGINE.parse_record_literals(pk_record)]
            if (
                base_record.data != pk_record.data
                or base_literals != pk_literals
                or record_gaps(base_record) != record_gaps(pk_record)
            ):
                divergences.add(record_id)
        if divergences:
            raise RuntimeError(
                f"segment 815 PK {language} exact +7 arrays/tokens drifted: {sorted(divergences)}"
            )
    for record_id, expected_arity in EXPECTED_PK_EN_ARITIES.items():
        record = pk_context["EN"][(15, record_id + 7)]
        if len(ENGINE.parse_record_literals(record)) != expected_arity:
            raise RuntimeError(f"segment 815 PK EN arity drifted: {record_id + 7}")
        if record_gaps(record) != gaps_from_hex(EXPECTED_PK_EN_GAPS[record_id]):
            raise RuntimeError(f"segment 815 PK EN token skeleton drifted: {record_id + 7}")


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
    assert_context_mapping(source_records, pk_source_records, base_context, pk_context)

    expected_coordinates = set()
    actual_current_ellipsis = set()
    for record_id, arity in RECORD_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 815 source/current arity drifted: 15:{record_id}")
        expected_gaps = gaps_from_hex(EXPECTED_GAPS[record_id])
        if record_gaps(source_record) != expected_gaps or record_gaps(current_record) != expected_gaps:
            raise RuntimeError(f"segment 815 dynamic skeleton drifted: 15:{record_id}")
        for literal_id, current_literal in enumerate(current_literals):
            coordinate = f"15:{record_id}:{literal_id}"
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(f"segment 815 unexpected blank literal: {coordinate}")
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_current_ellipsis.add(coordinate)

    if set(translations) != expected_coordinates or len(translations) != 21:
        raise RuntimeError("segment 815 decision universe drifted")
    if actual_current_ellipsis != CURRENT_ELLIPSIS_COORDINATES:
        raise RuntimeError("segment 815 current contextual ellipsis coordinates drifted")
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"segment 815 layout/outer signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment 815 forbidden script/control drifted: {coordinate}")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"segment 815 retains banned fullwidth punctuation: {coordinate}")
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment 815 retains an unpaired ellipsis: {coordinate}")

    particle_expectations = {
        "15:430:1": "을(를)",
        "15:430:2": "은(는)",
        "15:431:2": "께 ",
        "15:432:1": "은(는)",
        "15:433:1": "(이)라",
        "15:433:2": "께서 ",
        "15:434:1": "께 ",
        "15:435:1": "(이)라",
        "15:435:2": "을(를)",
        "15:436:0": "을(를)",
        "15:436:1": "(이)라",
        "15:437:0": "(이)다",
        "15:437:1": "을(를)",
    }
    for coordinate, prefix in particle_expectations.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(f"segment 815 dynamic name particle drifted: {coordinate}")
    if not translations["15:436:0"].endswith("앞으로 신세를 지겠사오며 이름은"):
        raise RuntimeError("segment 815 care-and-self-introduction boundary drifted")
    joined = "\n".join(translations.values())
    for required in (
        "막하",
        "옛 주군",
        "영명하신 주군",
        "분골쇄신",
        "신세를 지겠사오며",
        "목숨을 걸겠다",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 815 historical/person-voice diction drifted: {required}")


def assert_isolated_overlay_roundtrip(prepared: Any, translations: dict[str, str]) -> None:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements = {}
    reverse = {}
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse[key] = ENGINE.parse_record_literals(current_records[key[:2]])[literal_id].text
    rebuilt = ENGINE.rebuild_packed_with_literals(base.current_blob, replacements)
    rebuilt_records = ENGINE.archive_records(ENGINE.parse_packed_msggame(rebuilt).archive)
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError("segment 815 Base record count drifted")
    targets = {(15, record_id) for record_id in RECORD_ARITIES}
    for key, current_record in current_records.items():
        if key not in targets and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment 815 changed an out-of-scope record: {key}")
    for key in targets:
        if record_gaps(rebuilt_records[key]) != record_gaps(current_records[key]):
            raise RuntimeError(f"segment 815 changed target skeleton: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment 815 UTF-16 round-trip failed: {key}")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse)
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 815 reverse overlay is not byte-exact")


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
        raise RuntimeError("segment 815 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S815",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "protected_ellipsis": 0,
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
