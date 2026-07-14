#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 10."""

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


BATCH_ID = "msggame_pk_system_messages_b06r1385_1514.v0.10"
OVERLAY_NAME = "msggame_ko_system_messages_b06r1385_1514.v0.10.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.10.json"
REVIEW_NAME = "translation_review_index.v0.10.json"
VALIDATION_NAME = "translation_validation.v0.10.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 1515, 0)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 1385): ("편성할 수 있는 군단이 없습니다.",),
    (6, 1386): ("해산할 수 있는 군단이 없습니다.",),
    (6, 1387): ("해산할 군단:\n", "입니다. 계속하시겠습니까?"),
    (6, 1388): ("적대 행위를 제한하지 않습니다.",),
    (6, 1389): ("모략은 제한하지 않지만 군사 행동은 금지합니다.",),
    (6, 1390): ("방어 이외의 모든 적대 행위를 금지합니다.",),
    (6, 1391): ("모든 판단을 군단장에게 맡깁니다.",),
    (6, 1392): ("선택한 성을 공격합니다.",),
    (6, 1393): ("선택한 세력을 공격합니다.",),
    (6, 1394): ("이 군단의 모든 구신이 발생합니다.",),
    (6, 1395): ("이 군단에서는 물자 관련 구신만 발생합니다.",),
    (6, 1396): ("이 군단에서는 무장 관련 구신만 발생합니다.",),
    (6, 1397): ("이 군단에서는 어떤 구신도 발생하지 않습니다.",),
    (6, 1398): ("공략한 영토는 이 군단이 지배합니다.",),
    (6, 1399): ("공략한 영토는 다이묘 군단이 지배합니다.",),
    (6, 1400): ("공략한 영토가 인접하면 이 군단이 지배합니다.",),
    (6, 1401): ("군단장을 변경할 수 없습니다.",),
    (6, 1402): ("군단장을 변경합니다.",),
    (6, 1403): ("군단 소속 무장을 변경할 수 없습니다.",),
    (6, 1404): ("군단 소속 무장을 변경합니다.",),
    (6, 1405): ("군단 소속 성을 변경할 수 없습니다.",),
    (6, 1406): ("군단장의 지휘 범위 밖에 있는 성입니다",),
    (6, 1407): ("군단 소속 성을 변경합니다.",),
    (6, 1408): ("지휘 범위 밖이므로 최대 통치율과 소속 무장의\n획득 공훈이 감소합니다. 계속하시겠습니까?",),
    (6, 1409): ("인계 불가 항목:", "."),
    (6, 1410): ("어느 군단도 더 보유할 수 없는 항목:", "."),
    (6, 1413): ("군단 조정 항목:", "."),
    (6, 1417): ("다이묘 군단에 매달 납부할 항목:", ", 수량을 설정합니다."),
    (6, 1418): ("이 군단에 수입이 없는 항목:", "."),
    (6, 1421): ("변경 사항이 없습니다.",),
    (6, 1422): ("군단을 편성할 수 없습니다.",),
    (6, 1423): ("선택한 설정으로 군단을 편성합니다.",),
    (6, 1424): ("군단 설정을 중지합니다.",),
    (6, 1425): ("돌아가면 설정한 내용이 사라집니다\n정말 돌아가시겠습니까?",),
    (6, 1426): ("성이 없어지는 군단이 있습니다\n해당 군단은 해산됩니다\n계속하시겠습니까?",),
    (6, 1427): ("다이묘 군단의 금전 수지가 적자가 됩니다\n계속하시겠습니까?",),
    (6, 1430): ("예, 맡겨 주십시오!\n반드시 기대에 부응하겠습니다.",),
    (6, 1431): ("예, 맡겨 주십시오!\n반드시 기대에 부응하겠습니다.",),
    (6, 1432): ("예, 맡겨 주십시오!\n반드시 기대에 부응하겠습니다.",),
    (6, 1436): ("예, 맡겨 주십시오!\n반드시 기대에 부응하겠습니다.",),
    (6, 1442): ("알겠습니다, 맡겨 주십시오\n이 군단을 훌륭히 이끌겠습니다",),
    (6, 1443): ("알겠습니다, 맡겨 주십시오\n이 군단을 훌륭히 이끌겠습니다",),
    (6, 1444): ("알겠습니다, 맡겨 주십시오\n이 군단을 훌륭히 이끌겠습니다",),
    (6, 1448): ("알겠습니다, 맡겨 주십시오\n이 군단을 훌륭히 이끌겠습니다",),
    (6, 1454): ("알겠습니다……\n본가를 위해서라면 어쩔 수 없지요.",),
    (6, 1455): ("알겠습니다……\n본가를 위해서라면 어쩔 수 없지요.",),
    (6, 1456): ("알겠습니다……\n본가를 위해서라면 어쩔 수 없지요.",),
    (6, 1460): ("알겠습니다……\n본가를 위해서라면 어쩔 수 없지요.",),
    (6, 1464): ("성주 이동 기능은 정책 “", "” LV", "에서 해금됩니다."),
    (6, 1465): ("군단장이 이동할 수 있는 성이 없습니다.",),
    (6, 1466): ("군단장이 출진 중입니다.",),
    (6, 1467): ("군단장의 소속 성을 변경합니다.",),
    (6, 1468): ("통치 범위 밖이 되는 성:", "개\n다이묘 군단 소속이 됩니다. 계속하시겠습니까?"),
    (6, 1469): ("새 군단에 소속시킬 성을 선택하십시오.",),
    (6, 1470): ("편성한 무장이나 성이 임무 또는 구신을\n실행 중이라면 중지됩니다\n계속하시겠습니까?",),
    (6, 1471): ("새 군단장을 선택할 군단:\n", "입니다. 임명할 무장을 선택하십시오."),
    (6, 1472): ("군단장을 임명하지 않으면\n", ": 해산됩니다.\n계속하시겠습니까?"),
    (6, 1473): (": 종속시킬 세력:", "."),
    (6, 1474): (": 종속될 세력:", "."),
    (6, 1475): (": 혼인 동맹 상대:", "."),
    (6, 1476): (": 혼인 동맹 상대:", "."),
    (6, 1477): (": 단교 상대:", "."),
    (6, 1478): (": 단교 상대:", "."),
    (6, 1479): (": 단교 상대:", "."),
    (6, 1480): (": 종속시킬 세력:", "."),
    (6, 1481): (": 정전 상대:", ", 정전 기간:", "개월."),
    (6, 1482): (": 정전 상대:", ", 연장 기간:", "개월."),
    (6, 1483): (": 정전 상대:", ", 정전 기간:", "개월."),
    (6, 1484): (": 정전 상대:", ", 연장 기간:", "개월."),
    (6, 1485): (": 무기한 정전 상대:", "."),
    (6, 1486): (": 무기한 정전 상대:", "."),
    (6, 1487): (": 칙명에 따른 강화 상대:", "."),
    (6, 1488): (": 칙명에 따른 강화 상대:", "."),
    (6, 1489): (": 동맹 상대:", ", 동맹 기간:", "개월."),
    (6, 1490): (": 동맹 상대:", ", 연장 기간:", "개월."),
    (6, 1491): (": 동맹 상대:", ", 동맹 기간:", "개월."),
    (6, 1492): (": 동맹 상대:", ", 연장 기간:", "개월."),
    (6, 1493): (": 공략 원군 요청 달성.",),
    (6, 1494): (": 공략 원군 요청 달성.",),
    (6, 1495): (": 공략 원군 요청 종료.",),
    (6, 1496): (": 공략 원군 요청 대상:", ", 요청 종료."),
    (6, 1497): (": 방어 원군 요청 실패.",),
    (6, 1498): (": 방어 원군 요청 실패.",),
    (6, 1499): (": 공략 원군 요청 실패.",),
    (6, 1500): (": 공략 원군 요청 실패.",),
    (6, 1501): (": 방어 원군 요청 달성.",),
    (6, 1502): (": 방어 원군 요청 달성.",),
    (6, 1503): (": 중지한 원군 요청 상대:", "."),
    (6, 1504): (": 원군 요청 중지.",),
    (6, 1505): (": 공략 원군 파견 대상:", ", 원군 전멸."),
    (6, 1506): (": 공략 원군 파견 세력:", ", 원군 전멸."),
    (6, 1507): (": 방어 원군 파견 대상:", ", 원군 전멸."),
    (6, 1508): (": 방어 원군 파견 세력:", ", 원군 전멸."),
    (6, 1509): (": 동맹 상대:", ", 종료까지 2개월."),
    (6, 1510): ("기한 만료. 동맹 상대:", ", 동맹이 종료되었습니다."),
    (6, 1511): (": 원군 요청 대상:", ", 종료까지 2개월."),
    (6, 1512): ("공성 중 원군 요청 연장 대상:", "."),
    (6, 1513): (": 정전 상대:", ", 종료까지 2개월."),
    (6, 1514): ("기한 만료. 정전 상대:", ", 정전이 종료되었습니다."),
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
    if selected[0] != (6, 1385, 0) or selected[-1] != (6, 1514, 1):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 99:
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
                "selected_sc_literal_ids": list(range(len(replacements))),
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
                raise ValueError(f"unexpected skipped literal at {key}")
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
    if selected[-1] != (6, 1514, 1) or NEXT_COORDINATE not in sc_literals:
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
