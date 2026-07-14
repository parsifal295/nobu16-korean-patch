#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 14."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
WORKSPACE_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_translation_batch1 as previous  # noqa: E402


BATCH_ID = "msggame_pk_system_messages_b06r1993_2139.v0.14"
OVERLAY_NAME = "msggame_ko_system_messages_b06r1993_2139.v0.14.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.14.json"
REVIEW_NAME = "translation_review_index.v0.14.json"
VALIDATION_NAME = "translation_validation.v0.14.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 2139, 2)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 1993): ("월경지가 되는 군은 선택할 수 없습니다.",),
    (6, 1994): ("성은 군으로 선택할 수 없습니다.",),
    (6, 1995): ("전쟁에 휘말릴 가능성이 있어 선택할 수 없습니다.",),
    (6, 1996): ("이미 선택한 군입니다.",),
    (6, 1997): ("이미 선택한 성의 지배하에 있습니다.",),
    (6, 1998): ("선택할 수 있는 성이 없습니다.",),
    (6, 1999): ("이미 성을 선택했습니다.",),
    (6, 2001): ("월경지가 되는 성은 선택할 수 없습니다.",),
    (6, 2002): ("전쟁에 휘말릴 가능성이 있어 선택할 수 없습니다.",),
    (6, 2003): ("원군 요청 대상인 성은 선택할 수 없습니다.",),
    (6, 2004): ("상대의 영지를 분단하게 되므로 선택할 수 없습니다.",),
    (6, 2005): ("선택할 수 있는 관직이 없습니다.",),
    (6, 2006): ("교전 중인 상대는 관직을 제안해도 정전에 응하지 않을 것입니다.",),
    (6, 2007): ("이미 관직을 선택했습니다.",),
    (6, 2008): ("맹약 파기 대상으로 선택할 수 있는 세력이 없습니다.",),
    (6, 2009): ("우호도가 「친밀」에 이르지 않아 맹약 파기를 선택할 수 없습니다.",),
    (6, 2010): ("종속 세력에는 맹약 파기를 교섭 재료로 제시할 수 없습니다.",),
    (6, 2011): ("상대가 맹약 파기 교섭을 거부하고 있습니다.",),
    (6, 2012): ("본가와 상대 양쪽의 아군입니다.",),
    (6, 2013): ("혼인 동맹 중인 세력은 선택할 수 없습니다.",),
    (6, 2014): ("종속 세력과는 단교할 수 없습니다.",),
    (6, 2015): ("칙명 강화를 맺은 세력은 선택할 수 없습니다.",),
    (6, 2016): ("원군을 주고받는 세력은 선택할 수 없습니다.",),
    (6, 2017): ("아무 관계가 없는 세력입니다.",),
    (6, 2018): ("대상 세력에는 우호도 상승만 요청합니다.",),
    (6, 2019): ("대상 세력에 금전을 요청합니다.",),
    (6, 2020): ("대상 세력에 군량을 요청합니다.",),
    (6, 2021): ("대상 세력에 군마를 요청합니다.",),
    (6, 2022): ("대상 세력에 철포를 요청합니다.",),
    (6, 2023): ("대상 세력의 다이묘가 보유한 가보를 최대 5개까지 요청합니다.",),
    (6, 2024): ("대상 세력에 군을 최대 5개까지 요청합니다.\n외교 관계가 없을 때 군을 교환하면 6개월 정전이 맺어집니다.",),
    (6, 2025): ("대상 세력에 성을 요청합니다.\n외교 관계가 없을 때 성을 교환하면 6개월 정전이 맺어집니다.",),
    (6, 2026): ("대상 세력에 6개월 정전 체결 또는 연장을 요청합니다.",),
    (6, 2027): ("대상 세력에 본가로의 종속을 요청합니다.",),
    (6, 2028): ("대상 세력에 종속을 청합니다.",),
    (6, 2029): ("대상 세력에 6~60개월 동맹 체결 또는 연장을 제안합니다.",),
    (6, 2030): ("대상 세력에 혼인 동맹 체결을 제안합니다.",),
    (6, 2031): ("대상 세력에 다른 세력과 단교하도록 의뢰합니다.",),
    (6, 2032): ("대상 세력에 다른 세력을 목표로 삼도록 의뢰합니다.",),
    (6, 2033): ("성과 병력을 지정해 대상 세력에 공략 또는 방어 원군을 요청합니다.",),
    (6, 2034): ("대상 세력과의 외교 관계를 해소합니다.",),
    (6, 2035): ("대상 세력으로의 주가 변경을 청합니다.",),
    (6, 2036): ("모든 요청 내용을 일단 철회합니다.",),
    (6, 2037): ("모든 제안 내용을 일단 철회합니다.",),
    (6, 2038): ("요청 내용의 대가를 자동으로 설정합니다.",),
    (6, 2039): ("대상 세력에 금전 양도를 제안합니다.",),
    (6, 2040): ("대상 세력에 군량 양도를 제안합니다.",),
    (6, 2041): ("대상 세력에 군마 양도를 제안합니다.",),
    (6, 2042): ("대상 세력에 철포 양도를 제안합니다.",),
    (6, 2043): ("대상 세력에 다이묘 보유 가보를 최대 5개까지 양도하겠다고 제안합니다.",),
    (6, 2044): ("대상 세력에 군을 최대 5개까지 양도하겠다고 제안합니다.\n외교 관계가 없을 때 군을 교환하면 6개월 정전이 맺어집니다.",),
    (6, 2045): ("대상 세력에 성을 양도하겠다고 제안합니다.\n외교 관계가 없을 때 성을 교환하면 6개월 정전이 맺어집니다.",),
    (6, 2046): ("대상 세력에 다이묘가 보유한 관직을 양도하겠다고 제안합니다.",),
    (6, 2047): ("대상 세력에 다른 세력과 단교하겠다고 제안합니다.",),
    (6, 2048): ("대상 세력에 금전을 요청합니다.",),
    (6, 2049): ("대상 세력에 군량을 요청합니다.",),
    (6, 2050): ("대상 세력에 군마를 요청합니다.",),
    (6, 2051): ("대상 세력에 철포를 요청합니다.",),
    (6, 2052): ("대상 세력의 다이묘가 보유한 가보를 최대 5개까지 요청합니다.",),
    (6, 2053): ("대상 세력에 군을 최대 5개까지 요청합니다.",),
    (6, 2054): ("대상 세력에 성을 요청합니다.",),
    (6, 2055): ("대상 세력의 다이묘가 보유한 관직을 요청합니다.",),
    (6, 2056): ("대상 세력에 다른 세력과 단교하도록 의뢰합니다.",),
    (6, 2057): ("의 지행 지급량에 불만　충성-",),
    (6, 2058): ("의 지행 지급량에 만족　충성+",),
    (6, 2059): ("계속할 수 없음. 대상:", "의 방침 「", "」."),
    (6, 2062): ("유감입니다. 대상:", "의 방침\n「", "」을 중단했습니다.\n새 방침을 정해 주십시오."),
    (6, 2063): ("의 방침 「", "」을\n계속하기 어려워졌습니다.\n새 방침을 지시해 주시겠습니까?"),
    (6, 2064): ("의 「", "」은\n더 이상 유지할 수 없습니다.\n방침을 다시 검토해 주십시오!"),
    (6, 2068): ("의 방침 「", "」을\n계속하기 어려워졌습니다.\n새 방침을 지시해 주시겠습니까?"),
    (6, 2072): ("의 방침 「", "」을\n계속하기 어려워졌습니다.\n새 방침을 지시해 주시겠습니까?"),
    (6, 2073): ("의 「", "」을 포함해 계속할 수 없는 방침 수:", "개입니다."),
    (6, 2076): ("유감입니다. 대상:", "의 중단 방침 수:", "개.\n「", "」 등을 중단했습니다.\n새 방침을 정해 주십시오."),
    (6, 2077): ("의 방침 「", "」 등을 포함해 계속하기 어려운 방침 수:\n", "개입니다.\n새 방침을 지시해 주시겠습니까?"),
    (6, 2078): ("다음 대상:", "의 방침 「", "」을 포함해 계속할 수 없는 방침 수:\n", "개입니다.\n방침을 다시 검토해 주십시오!"),
    (6, 2082): ("의 방침 「", "」 등을 포함해 계속하기 어려운 방침 수:\n", "개입니다. 새 방침을\n지시해 주시겠습니까?"),
    (6, 2086): ("봉기가 진정된 지역:", "에서 발생한 봉기가 진정되었습니다."),
    (6, 2089): ("다음 성을 함락했습니다:", ".\n원군을 보내 준 세력:", ". 감사합니다."),
    (6, 2090): ("다음 성을 함락했습니다:", ".\n원군을 보내 준 세력:", ". 감사합니다."),
    (6, 2091): ("다음 성을 함락했습니다:", ".\n원군을 보내 준 세력:", ". 감사합니다."),
    (6, 2095): ("다음 성을 함락했습니다:", ".\n원군을 보내 준 세력:", ". 감사합니다."),
    (6, 2101): ("원군 파견 요청을 받아들였습니다.\n양도 대상:", "\n양도받은 세력:", "."),
    (6, 2102): ("원군 파견 요청을 받아들였습니다.\n양도 대상:", "\n양도받은 세력:", "."),
    (6, 2103): ("원군 파견 요청을 받아들였습니다.\n양도 대상:", "\n양도받은 세력:", "."),
    (6, 2107): ("원군 파견 요청을 받아들였습니다.\n양도 대상:", "\n양도받은 세력:", "."),
    (6, 2113): ("이번 일은 이것으로 끝났습니다.\n원군에 감사할 세력:", "."),
    (6, 2114): ("이번 일은 이것으로 끝났습니다.\n원군에 감사할 세력:", "."),
    (6, 2115): ("이번 일은 이것으로 끝났습니다.\n원군에 감사할 세력:", "."),
    (6, 2119): ("이번 일은 이것으로 끝났습니다.\n원군에 감사할 세력:", "."),
    (6, 2125): ("지키지 못한 성:", ".\n그래도 원군에 감사할 세력:", "."),
    (6, 2126): ("지키지 못한 성:", ".\n그래도 원군에 감사할 세력:", "."),
    (6, 2127): ("지키지 못한 성:", ".\n그래도 원군에 감사할 세력:", "."),
    (6, 2131): ("지키지 못한 성:", ".\n그래도 원군에 감사할 세력:", "."),
    (6, 2137): ("함락하지 못한 성:", ".\n그래도 원군에 감사할 세력:", "."),
    (6, 2138): ("함락하지 못한 성:", ".\n그래도 원군에 감사할 세력:", "."),
    (6, 2139): ("함락하지 못한 성:", ".\n그래도 원군에 감사할 세력:", None),
}

SKIPPED_CANDIDATES: dict[tuple[int, int, int], str] = {}
EXPECTED_RECORD_KEYS = tuple(TRANSLATIONS)


def selected_record_keys() -> list[tuple[int, int]]:
    return sorted(TRANSLATIONS)


def selected_coordinates() -> list[tuple[int, int, int]]:
    return [
        (block_id, record_id, literal_id)
        for (block_id, record_id), replacements in sorted(TRANSLATIONS.items())
        for literal_id, replacement in enumerate(replacements)
        if replacement is not None
    ]


def validate_static_scope() -> None:
    keys = selected_record_keys()
    selected = selected_coordinates()
    if keys != sorted(EXPECTED_RECORD_KEYS):
        raise ValueError("translation scan record set changed")
    if selected[0] != (6, 1993, 0) or selected[-1] != (6, 2139, 1):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 96:
        raise ValueError("translation batch scope changed")
    if SKIPPED_CANDIDATES:
        raise ValueError("translation batch unexpectedly contains skips")


def _uncertainty_flags(
    coordinate: tuple[int, int, int],
    record_counts: dict[str, int],
    sc_literal_count: int,
) -> list[str]:
    flags = ["runtime_line_wrap_review"]
    if len(set(record_counts.values())) != 1:
        flags.append("cross_language_literal_shape_diff")
    if sc_literal_count > 1:
        flags.append("runtime_dynamic_join_review")
    if coordinate[:2] in {(4, 83), (4, 107)}:
        flags.append("runtime_fragment_join_review")
    return flags


def _assert_public_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    scans: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = previous.script_counts(path.read_text(encoding="utf-8"))
        scans[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise ValueError(f"source-script text leaked into {path}")
    return scans


def build(args: argparse.Namespace) -> dict[str, Any]:
    validate_static_scope()
    paths = {
        language: Path(getattr(args, f"stock_{language.lower()}")).resolve()
        for language in LANGUAGES
    }
    installed_before = {
        language: previous.sha256(path.read_bytes()) for language, path in paths.items()
    }
    loaded = previous.load_sources(paths)
    archives = {
        language: loaded[language]["parsed"].archive for language in LANGUAGES
    }
    records = {
        language: previous._record_map(archive)
        for language, archive in archives.items()
    }
    sc_literals = previous._literal_map(archives["SC"])

    overlay_entries: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    invariant_failures: list[dict[str, Any]] = []
    record_evidence: list[dict[str, Any]] = []
    replacement_map: dict[tuple[int, int, int], str] = {}

    for block_id, record_id in selected_record_keys():
        key = (block_id, record_id)
        source_record_literals = previous.parse_record_literals(records["SC"][key])
        replacements = TRANSLATIONS[key]
        if len(source_record_literals) != len(replacements):
            raise ValueError(
                f"translation literal count mismatch at {key}: "
                f"source={len(source_record_literals)}, ko={len(replacements)}"
            )
        if not all(
            previous.is_visible_translation_candidate(literal.text)
            for literal in source_record_literals
        ):
            raise ValueError(f"scanned record contains a non-visible literal: {key}")
        language_references = {
            language: previous.record_reference(records[language][key])
            for language in LANGUAGES
        }
        literal_counts = {
            language: language_references[language]["literal_count"]
            for language in LANGUAGES
        }
        record_evidence.append(
            {
                "block_id": block_id,
                "record_id": record_id,
                "selected_sc_literal_ids": [
                    literal_id
                    for literal_id, replacement in enumerate(replacements)
                    if replacement is not None
                ],
                "skipped_sc_literal_ids": [],
                "references": language_references,
                "literal_shape_aligned_across_languages": len(set(literal_counts.values()))
                == 1,
                "cross_language_literal_id_alignment_used": False,
                "manual_same_record_semantic_crosscheck": True,
            }
        )
        for literal, replacement in zip(
            source_record_literals, replacements, strict=True
        ):
            if replacement is None:
                continue
            coordinate = (block_id, record_id, literal.literal_id)
            problems = previous.common.invariant_mismatches(literal.text, replacement)
            if previous.bracket_sequence(literal.text) != previous.bracket_sequence(
                replacement
            ):
                problems.append(
                    "bracket_sequence: "
                    f"source={previous.bracket_sequence(literal.text)!r}, "
                    f"ko={previous.bracket_sequence(replacement)!r}"
                )
            if problems:
                invariant_failures.append(
                    {"coordinate": list(coordinate), "problems": problems}
                )
            replacement_map[coordinate] = replacement
            overlay_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "source_sc_utf16le_sha256": previous.text_hash(literal.text),
                    "ko": replacement,
                }
            )
            review_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "status": "translated",
                    "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en_tc_record_context",
                    "automated_draft": True,
                    "human_review_required": True,
                    "runtime_reviewed": False,
                    "uncertainty_flags": _uncertainty_flags(
                        coordinate, literal_counts, len(source_record_literals)
                    ),
                }
            )
    if invariant_failures:
        raise ValueError(f"replacement invariants failed: {invariant_failures}")

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": previous.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "packed_size": len(sc_packed),
            "packed_sha256": previous.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": previous.sha256(sc_raw),
            "record_count": archives["SC"].record_count,
            "literal_slot_count": len(sc_literals),
        },
        "entries": overlay_entries,
    }
    rebuilt, binary_manifest = previous.apply_overlay_blob(sc_packed, overlay)
    _target_header, target_raw = previous.decompress_wrapper(rebuilt)
    target = previous.parse_packed_msggame(rebuilt)
    target_literals = previous._literal_map(target.archive)
    target_records = previous._record_map(target.archive)
    if set(target_literals) != set(sc_literals):
        raise ValueError("literal coordinates changed after rebuild")
    for coordinate, source_literal in sc_literals.items():
        expected = replacement_map.get(coordinate, source_literal.text)
        if target_literals[coordinate].text != expected:
            raise ValueError(f"rebuilt literal mismatch at {coordinate}")
    if set(target_records) != set(records["SC"]):
        raise ValueError("record coordinates changed after rebuild")
    if any(
        previous.record_skeleton(records["SC"][key])
        != previous.record_skeleton(target_records[key])
        for key in target_records
    ):
        raise ValueError("opaque record bytecode changed outside literal text")
    if previous.rebuild_raw_msggame(target.archive) != target_raw:
        raise ValueError("rebuilt target raw parse/rebuild is not byte-identical")
    if [len(block.records) for block in archives["SC"].blocks] != [
        len(block.records) for block in target.archive.blocks
    ]:
        raise ValueError("top-level block record counts changed")
    if any(block.offset % 4 for block in target.archive.blocks):
        raise ValueError("rebuilt top-level block offset is not four-byte aligned")

    selected = selected_coordinates()
    actual_coordinates = [
        tuple(entry[key] for key in ("block_id", "record_id", "literal_id"))
        for entry in overlay_entries
    ]
    if actual_coordinates != selected:
        raise ValueError("overlay coordinate order is not deterministic")
    if selected[-1] != (6, 2139, 1) or NEXT_COORDINATE not in sc_literals:
        raise ValueError("batch continuation boundary changed")

    record_keys = selected_record_keys()
    evidence = {
        "schema": "nobu16.kr.msggame-translation-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "scanned_visible_candidate_count": len(selected),
            "skipped_candidates": [],
        },
        "alignment_basis": [
            "same_pk_resource_role",
            "same_18_block_shape",
            "same_block_and_record_coordinates",
            "manual_same_record_semantic_crosscheck",
            "language_literal_shapes_may_differ",
            "cross_language_literal_id_alignment_not_used",
        ],
        "source_files": {
            language: {
                "logical_path": SOURCE_PATHS[language],
                **previous.SOURCE_PINS[SOURCE_PATHS[language]],
            }
            for language in LANGUAGES
        },
        "record_count": len(record_evidence),
        "records": record_evidence,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msggame-translation-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(review_entries),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts["overlay"] = previous.write_json(overlay_path, overlay)
    artifacts["alignment_evidence"] = previous.write_json(evidence_path, evidence)
    artifacts["review_index"] = previous.write_json(review_path, review)
    source_free_scan = _assert_public_source_free(
        (overlay_path, evidence_path, review_path)
    )
    installed_after = {
        language: previous.sha256(path.read_bytes()) for language, path in paths.items()
    }
    if installed_before != installed_after:
        raise ValueError("installed game source changed during read-only batch build")

    validation = {
        "schema": "nobu16.kr.msggame-translation-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "selected_coordinates_sha256": previous.sha256(
                json.dumps(selected, separators=(",", ":")).encode("utf-8")
            ),
        },
        "selection": {
            "stable_sc_coordinate_order": True,
            "natural_scan_record_boundaries": True,
            "all_linguistic_literals_in_scanned_records_selected": True,
            "scanned_visible_candidate_count": len(selected),
            "nonlinguistic_visible_candidate_skips": 0,
            "skipped_candidates": [],
        },
        "source_alignment": {
            "languages": list(LANGUAGES),
            "record_coordinates_aligned": True,
            "literal_shapes_assumed_aligned": False,
            "manual_same_record_semantic_crosschecks": len(record_keys),
            "record_reference_count": len(record_keys) * len(LANGUAGES),
        },
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "escape_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_sequence_in_order",
            ],
        },
        "offline_binary_validation": {
            "entry_count": binary_manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": previous.sha256(rebuilt),
            "target_raw_size": len(target_raw),
            "target_raw_sha256": previous.sha256(target_raw),
            "literal_coordinates_preserved": True,
            "record_coordinates_preserved": True,
            "opaque_record_bytecode_preserved": True,
            "top_level_offsets_recomputed_and_aligned": True,
            "raw_parse_rebuild_byte_exact": True,
            "skipped_candidates_unchanged": True,
            "installed_game_file_written": False,
        },
        "translation_status": {
            "translated_draft": len(selected),
            "human_review_required": len(selected),
            "runtime_reviewed": 0,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": previous.sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "byte_identical_offline_binary_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_modified": False,
            "progress_manifest_modified": False,
            "other_workstreams_modified": False,
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    artifacts["generation_validation"] = previous.write_json(
        validation_path, validation
    )
    if previous.script_counts(validation_path.read_text(encoding="utf-8")) != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise ValueError("source-script text leaked into validation artifact")
    return {
        "out_root": out_root,
        "entry_count": len(selected),
        "record_count": len(record_keys),
        "skipped_count": 0,
        "next_coordinate": NEXT_COORDINATE,
        "target_packed_sha256": previous.sha256(rebuilt),
        "artifacts": artifacts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for language in LANGUAGES:
        parser.add_argument(
            f"--stock-{language.lower()}",
            type=Path,
            default=WORKSPACE_ROOT / Path(SOURCE_PATHS[language]),
        )
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"records={result['record_count']}")
    print(f"entries={result['entry_count']}")
    print(f"skipped={result['skipped_count']}")
    print("next_coordinate=" + ",".join(map(str, result["next_coordinate"])))
    print(f"target_packed_sha256={result['target_packed_sha256']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
