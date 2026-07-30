#!/usr/bin/env python3
"""Build Base authoring segment 818 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S818.private.v1.jsonl"
SEGMENT = 818


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s818", ENGINE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
RAW_TRANSLATIONS: dict[str, str] = {
    "15:460:0": "을(를) 권유하고자 적지로 향하던 도중\n적의 습격을 받은",
    "15:460:1": "님께서 돌아가셨사옵니다\n그 자리에서는 벗어나셨으나 상처가 깊었사옵니다…",
    "15:461:0": "을(를) 권유하고자 적지로 향하던 도중\n적의 습격을 받은",
    "15:461:1": "님께서 돌아가셨사옵니다\n그 자리에서는 벗어나셨으나 상처가 깊었사옵니다…",
    "15:462:0": "을(를) 권유하고자 적지로 향하던 도중\n적의 습격을 받은",
    "15:462:1": "님께서 돌아가셨사옵니다\n그 자리에서는 벗어나셨으나 상처가 깊었사옵니다…",
    "15:463:0": "을(를) 권유하고자 적지로 향하던 도중\n적의 습격을 받은",
    "15:463:1": "님께서 돌아가셨사옵니다\n그 자리에서는 벗어나셨으나 상처가 깊었사옵니다…",
    "15:464:0": "·",
    "15:464:1": "을(를) 회유하는 데 실패",
    "15:465:0": "·",
    "15:465:1": "을(를) 회유하는 데 실패",
    "15:466:0": "큰일",
    "15:466:1": "!\n",
    "15:466:2": "의",
    "15:466:3": "이(가)\n",
    "15:466:4": "에 귀순하",
    "15:466:5": "!",
    "15:467:0": "큰일이",
    "15:467:1": "!\n",
    "15:467:2": "의",
    "15:467:3": "이(가) 우리 가문을 저버리고\n",
    "15:467:4": "에 귀순한 모양",
    "15:467:5": "!",
}
RECORD_ARITIES = {460: 2, 461: 2, 462: 2, 463: 2, 464: 2, 465: 2, 466: 6, 467: 6}
EXPECTED_BASE_GAPS = {
    460: ("024833", "024933", "050505"),
    461: ("024833", "024933", "050505"),
    462: ("024833", "024933", "050505"),
    463: ("024833", "024933", "050505"),
    464: ("", "024633", "050505"),
    465: ("", "024633", "050505"),
    466: (
        "",
        "014326020000",
        "023c",
        "024833",
        "025032",
        "014368020000",
        "050505",
    ),
    467: (
        "",
        "014352000000",
        "023c",
        "024833",
        "025032",
        "01431a020000",
        "050505",
    ),
}
EXPECTED_PK_JP_GAPS = {
    **{record_id: gaps for record_id, gaps in EXPECTED_BASE_GAPS.items() if record_id <= 465},
    466: (
        "",
        "014332020000",
        "023c",
        "024833",
        "025032",
        "014374020000",
        "050505",
    ),
    467: (
        "",
        "014352000000",
        "023c",
        "024833",
        "025032",
        "014326020000",
        "050505",
    ),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:460:1",
    "15:461:1",
    "15:462:1",
    "15:463:1",
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
        "！": "!",
        "？": "?",
    }
)
BASIS = (
    "pristine_base_pc_jp_authoritative_dynamic_defection_and_poaching_fragments_"
    "with_exact_uniform_plus_7_pk_jp_mapping_and_pk_en_sc_tc_auxiliary_context_"
    "runtime_person_lord_house_and_faction_tokens_with_safe_korean_particles_"
    "historical_register_current_pc_layout_and_opcode_skeleton_preserved_"
    "runtime_assembly_pending_and_no_steam_write"
)

SC_AUXILIARY = ["有要事禀报！\n", "的", "放弃本家，\n投靠", "去了！"]
TC_AUXILIARY = ["有要事稟報！\n", "的", "放棄本家，\n投靠", "去了！"]
EN_AUXILIARY = ["I have dire news! ", "Ös ", " has betrayed us and joined the ", "!"]
AUXILIARY_NONEMPTY_RECORD_IDS = {468, 469, 470, 474}
AUXILIARY_NONEMPTY_GAPS = ("", "023c", "024833", "025032", "050505")
AUXILIARY_EMPTY_GAPS = ("", "050505")


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


def resolved_translations(
    current_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
) -> dict[str, str]:
    translations = {}
    for coordinate, raw in raw_translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        translations[coordinate] = adopt_current_layout(raw, current)
    return translations


def expected_auxiliary(language: str, record_id: int) -> tuple[list[str], tuple[str, ...]]:
    if record_id not in AUXILIARY_NONEMPTY_RECORD_IDS:
        return [""], AUXILIARY_EMPTY_GAPS
    arrays = {"SC": SC_AUXILIARY, "TC": TC_AUXILIARY, "EN": EN_AUXILIARY}
    return arrays[language], AUXILIARY_NONEMPTY_GAPS


def assert_context_mapping(
    *,
    segment: int,
    record_arities: dict[int, int],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    source_records: dict[tuple[int, int], Any],
    pk_source_records: dict[tuple[int, int], Any],
    base_context: dict[str, dict[tuple[int, int], Any]],
    pk_context: dict[str, dict[tuple[int, int], Any]],
) -> None:
    mapped_ids = {record_id + 7 for record_id in record_arities}
    expected_mapped_ids = set(range(min(record_arities) + 7, max(record_arities) + 8))
    if mapped_ids != expected_mapped_ids or mapped_ids & PK_ONLY_RECORD_IDS:
        raise RuntimeError(f"segment {segment} uniform +7 mapping drifted")

    for record_id in record_arities:
        base_record = source_records[(15, record_id)]
        pk_record = pk_source_records[(15, record_id + 7)]
        base_literals = [literal.text for literal in ENGINE.parse_record_literals(base_record)]
        pk_literals = [literal.text for literal in ENGINE.parse_record_literals(pk_record)]
        if base_literals != pk_literals:
            raise RuntimeError(f"segment {segment} mapped PK JP literal array drifted: {record_id}")
        if record_gaps(base_record) != gaps_from_hex(base_gaps[record_id]):
            raise RuntimeError(f"segment {segment} Base JP token skeleton drifted: {record_id}")
        if record_gaps(pk_record) != gaps_from_hex(pk_jp_gaps[record_id]):
            raise RuntimeError(f"segment {segment} PK JP token skeleton drifted: {record_id + 7}")

        for language in ("SC", "TC"):
            expected_literals, expected_gaps = expected_auxiliary(language, record_id)
            for label, records, mapped_id in (
                ("Base", base_context[language], record_id),
                ("PK", pk_context[language], record_id + 7),
            ):
                record = records[(15, mapped_id)]
                actual_literals = [
                    literal.text for literal in ENGINE.parse_record_literals(record)
                ]
                if actual_literals != expected_literals:
                    raise RuntimeError(
                        f"segment {segment} {label} {language} literal array drifted: {mapped_id}"
                    )
                if record_gaps(record) != gaps_from_hex(expected_gaps):
                    raise RuntimeError(
                        f"segment {segment} {label} {language} token skeleton drifted: {mapped_id}"
                    )

        expected_en_literals, expected_en_gaps = expected_auxiliary("EN", record_id)
        pk_en_record = pk_context["EN"][(15, record_id + 7)]
        if [
            literal.text for literal in ENGINE.parse_record_literals(pk_en_record)
        ] != expected_en_literals:
            raise RuntimeError(f"segment {segment} PK EN literal array drifted: {record_id + 7}")
        if record_gaps(pk_en_record) != gaps_from_hex(expected_en_gaps):
            raise RuntimeError(f"segment {segment} PK EN token skeleton drifted: {record_id + 7}")


def assert_scope(
    prepared: Any,
    *,
    segment: int,
    translations: dict[str, str],
    record_arities: dict[int, int],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str]], None
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
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
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
        expected_gaps = gaps_from_hex(base_gaps[record_id])
        if record_gaps(source_record) != expected_gaps or record_gaps(current_record) != expected_gaps:
            raise RuntimeError(f"segment {segment} Base dynamic skeleton drifted: 15:{record_id}")
        for literal_id, current_literal in enumerate(current_literals):
            coordinate = f"15:{record_id}:{literal_id}"
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(f"segment {segment} unexpected blank literal: {coordinate}")
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_current_ellipsis.add(coordinate)

    if set(translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} decision coordinate universe drifted")
    if len(translations) != sum(record_arities.values()):
        raise RuntimeError(f"segment {segment} visible decision count drifted")
    if actual_current_ellipsis != ellipsis_coordinates:
        raise RuntimeError(f"segment {segment} current ellipsis coordinates drifted")

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        current_text = ENGINE.parse_record_literals(current_records[(block_id, record_id)])[literal_id].text
        if layout_signature(translation) != layout_signature(current_text):
            raise RuntimeError(f"segment {segment} layout/outer signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment {segment} forbidden script/control drifted: {coordinate}")
        if BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(
                f"segment {segment} retains banned fullwidth punctuation: {coordinate}"
            )
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment {segment} retains an unpaired ellipsis: {coordinate}")

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
    reverse = {}
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (int(value) for value in coordinate.split(":"))
        key = (block_id, record_id, literal_id)
        replacements[key] = translation
        reverse[key] = ENGINE.parse_record_literals(current_records[key[:2]])[literal_id].text
    rebuilt = ENGINE.rebuild_packed_with_literals(base.current_blob, replacements)
    rebuilt_records = ENGINE.archive_records(ENGINE.parse_packed_msggame(rebuilt).archive)
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError(f"segment {segment} Base record count drifted")
    targets = {(15, record_id) for record_id in record_arities}
    for key, current_record in current_records.items():
        if key not in targets and rebuilt_records[key].data != current_record.data:
            raise RuntimeError(f"segment {segment} changed an out-of-scope record: {key}")
    for key in targets:
        if record_gaps(rebuilt_records[key]) != record_gaps(current_records[key]):
            raise RuntimeError(f"segment {segment} changed target skeleton: {key}")
    for key, translation in replacements.items():
        if ENGINE.parse_record_literals(rebuilt_records[key[:2]])[key[2]].text != translation:
            raise RuntimeError(f"segment {segment} UTF-16 round-trip failed: {key}")
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse)
    if reversed_blob != base.current_blob:
        raise RuntimeError(f"segment {segment} reverse overlay is not byte-exact")


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str]], None
    ],
) -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(prepared.resources["base_msggame"].current_archive)
    translations = resolved_translations(current_records, raw_translations)
    assert_scope(
        prepared,
        segment=segment,
        translations=translations,
        record_arities=record_arities,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        ellipsis_coordinates=ellipsis_coordinates,
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


def source_literals(
    records: dict[tuple[int, int], Any], record_id: int
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[(15, record_id)])
    )


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    translations: dict[str, str],
) -> None:
    if len({source_literals(source_records, record_id) for record_id in range(460, 464)}) != 1:
        raise RuntimeError("segment 818 fatal-poaching report source repeat drifted")
    if source_literals(source_records, 460) != source_literals(source_records, 452):
        raise RuntimeError("segment 818 fatal-poaching source drifted from the 12-record group")
    if len({source_literals(source_records, record_id) for record_id in (464, 465)}) != 1:
        raise RuntimeError("segment 818 poaching-failure source repeat drifted")
    if len({source_literals(source_records, record_id) for record_id in range(467, 475)}) != 1:
        raise RuntimeError("segment 818 defection-report source repeat drifted")
    for literal_id in range(2):
        if len(
            {
                translations[f"15:{record_id}:{literal_id}"]
                for record_id in range(460, 464)
            }
        ) != 1:
            raise RuntimeError("segment 818 fatal-poaching translation repeat drifted")
        if len(
            {
                translations[f"15:{record_id}:{literal_id}"]
                for record_id in (464, 465)
            }
        ) != 1:
            raise RuntimeError("segment 818 poaching-failure translation repeat drifted")

    particle_expectations = {
        **{f"15:{record_id}:0": "을(를)" for record_id in range(460, 464)},
        **{f"15:{record_id}:1": "님께서 " for record_id in range(460, 464)},
        "15:464:1": "을(를)",
        "15:465:1": "을(를)",
        "15:466:2": "의",
        "15:466:3": "이(가)\n",
        "15:466:4": "에 귀순하",
        "15:467:2": "의",
        "15:467:3": "이(가) 우리 가문을 저버리고\n",
        "15:467:4": "에 귀순한 모양",
    }
    for coordinate, prefix in particle_expectations.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(f"segment 818 dynamic name particle drifted: {coordinate}")
    for record_id in range(460, 464):
        if not translations[f"15:{record_id}:0"].endswith("적의 습격을 받은"):
            raise RuntimeError(
                f"segment 818 actor-name attributive boundary drifted: 15:{record_id}:0"
            )
    prior_3937 = ENGINE.parse_record_literals(source_records[(6, 3937)])[0].text
    if source_literals(source_records, 466)[0] != prior_3937:
        raise RuntimeError("segment 818 15:466:0 prior exact-source lookup drifted")
    if translations["15:466:0"] != "큰일":
        raise RuntimeError("segment 818 15:466:0 must reuse the prior exact translation")
    joined = "\n".join(translations.values())
    for required in (
        "권유하고자",
        "적의 습격",
        "돌아가셨사옵니다",
        "상처가 깊었사옵니다",
        "회유",
        "우리 가문",
        "귀순",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 818 historical/semantic diction drifted: {required}")
    if any(
        forbidden in joined
        for forbidden in ("당가", "꾀어내", "숨을 거두", "돌아선 모양", "의 편으로")
    ):
        raise RuntimeError("segment 818 retains a forbidden literalism")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 818 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S818",
                "decision_count": len(rows),
                "retranslated": 0,
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
