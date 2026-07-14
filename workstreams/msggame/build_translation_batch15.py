#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 15."""

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


BATCH_ID = "msggame_pk_system_messages_b06r2139_2436.v0.15"
OVERLAY_NAME = "msggame_ko_system_messages_b06r2139_2436.v0.15.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.15.json"
REVIEW_NAME = "translation_review_index.v0.15.json"
VALIDATION_NAME = "translation_validation.v0.15.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 2436, 1)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 2139): (None, None, "."),
    (6, 2143): ("함락하지 못한 성:", ".\n그래도 원군에 감사할 세력:", "."),
    (6, 2149): ("지켜 낸 성:", ".\n도움을 준 원군 세력: ", "의 원군 덕분입니다……\n진심으로 감사드립니다."),
    (6, 2150): ("지켜 낸 성:", ".\n도움을 준 원군 세력: ", "의 원군 덕분입니다……\n진심으로 감사드립니다."),
    (6, 2151): ("지켜 낸 성:", ".\n도움을 준 원군 세력: ", "의 원군 덕분입니다……\n진심으로 감사드립니다."),
    (6, 2155): ("지켜 낸 성:", ".\n도움을 준 원군 세력: ", "의 원군 덕분입니다……\n진심으로 감사드립니다."),
    (6, 2161): ("원군 지원 대상:", ". 지원은 여기까지입니다.\n이제 철수하겠습니다."),
    (6, 2162): ("원군 지원 대상:", ". 지원은 여기까지입니다.\n이제 철수하겠습니다."),
    (6, 2163): ("원군 지원 대상:", ". 지원은 여기까지입니다.\n이제 철수하겠습니다."),
    (6, 2167): ("원군 지원 대상:", ". 지원은 여기까지입니다.\n이제 철수하겠습니다."),
    (6, 2171): ("공략 목표:", ". 함락 전에 부대가 괴멸했습니다……\n면목 없지만 원군 파견을 중단하겠습니다.\n남은 전투의 무운을 빕니다."),
    (6, 2172): ("방어 목표:", ". 지켜 내기 전에 부대가 괴멸했습니다……\n면목 없지만 원군 파견을 중단하겠습니다.\n남은 전투의 무운을 빕니다."),
    (6, 2173): ("예상치 못한 사태가 발생한 듯합니다.\n죄송하지만 원군 파견을 더 이어갈 수 없습니다……\n무운을 빕니다.",),
    (6, 2174): ("이 내용으로 교섭을 제안하시겠습니까?\n성공하면 이 내용으로 교섭이 확정됩니다.\n실패하면 상대가 노하여 교섭이 어려워집니다.",),
    (6, 2175): ("정말 외교 화면에서 나가시겠습니까?",),
    (6, 2176): ("정말 교섭을 거부하시겠습니까?",),
    (6, 2177): ("좋은 교섭이었습니다!",),
    (6, 2178): ("이 세력과 외교합니다.",),
    (6, 2179): ("교섭할 세력을 선택하십시오.",),
    (6, 2182): ("약속한 날짜가 지났지만 원군이 아직 성을 공격 중입니다.\n어쩔 수 없군요.\n공성이 끝나면 철수시키겠습니다.",),
    (6, 2183): ("장병을 돌려받지 못하면 곤란하지만\n공성 중이라면\n계속 빌려줄 수밖에 없습니다.",),
    (6, 2184): ("흠, 공성 중에 병력을 물리면\n겁쟁이라는 비난을 받겠지요.\n전투가 끝날 때까지 파견하겠습니다.",),
    (6, 2188): ("공성 중인 병력을 돌려보내라고 하면\n상대도 곤란할 것입니다.\n끝나는 대로 철수시키겠습니다.",),
    (6, 2194): ("오, 잘 오셨습니다!",),
    (6, 2195): ("오, 잘 오셨습니다!",),
    (6, 2196): ("오, 잘 오셨습니다!",),
    (6, 2200): ("오, 잘 오셨습니다!",),
    (6, 2206): ("오, 찾아오신 분:", "님이시군요?"),
    (6, 2207): ("오, 찾아오신 분:", "님이시군요?"),
    (6, 2208): ("오, 찾아오신 분:", "님이시군요?"),
    (6, 2212): ("오, 찾아오신 분:", "님이시군요?"),
    (6, 2218): ("님,\n오늘은 무슨 용무입니까?",),
    (6, 2219): ("님,\n오늘은 무슨 용무입니까?",),
    (6, 2220): ("님,\n오늘은 무슨 용무입니까?",),
    (6, 2224): ("님,\n오늘은 무슨 용무입니까?",),
    (6, 2230): ("무슨 용무입니까?",),
    (6, 2231): ("무슨 용무입니까?",),
    (6, 2232): ("무슨 용무입니까?",),
    (6, 2236): ("무슨 용무입니까?",),
    (6, 2242): ("누구신가 했더니:", "님이군요."),
    (6, 2243): ("누구신가 했더니:", "님이군요."),
    (6, 2244): ("누구신가 했더니:", "님이군요."),
    (6, 2248): ("누구신가 했더니:", "님이군요."),
    (6, 2254): ("님,\n무슨 낯으로 찾아오셨습니까?",),
    (6, 2255): ("님,\n무슨 낯으로 찾아오셨습니까?",),
    (6, 2256): ("님,\n무슨 낯으로 찾아오셨습니까?",),
    (6, 2260): ("님,\n무슨 낯으로 찾아오셨습니까?",),
    (6, 2264): ("모든 요청 내용을 일단 철회합니다.\n계속하시겠습니까?",),
    (6, 2267): ("우리와 친해지고 싶으시다고요……\n그 대가로 무엇을 주시겠습니까?",),
    (6, 2268): ("우리와 친해지고 싶으시다고요……\n그 대가로 무엇을 주시겠습니까?",),
    (6, 2269): ("우리와 친해지고 싶으시다고요……\n그 대가로 무엇을 주시겠습니까?",),
    (6, 2273): ("우리와 친해지고 싶으시다고요……\n그 대가로 무엇을 주시겠습니까?",),
    (6, 2279): ("간단한 부탁이니 들어줄 수도 있습니다.\n대가로 무엇을 주시겠습니까?",),
    (6, 2280): ("간단한 부탁이니 들어줄 수도 있습니다.\n대가로 무엇을 주시겠습니까?",),
    (6, 2281): ("간단한 부탁이니 들어줄 수도 있습니다.\n대가로 무엇을 주시겠습니까?",),
    (6, 2285): ("간단한 부탁이니 들어줄 수도 있습니다.\n대가로 무엇을 주시겠습니까?",),
    (6, 2291): ("꽤 큰 부탁이군요.\n그만한 대가를 기대해도 되겠습니까?",),
    (6, 2292): ("꽤 큰 부탁이군요.\n그만한 대가를 기대해도 되겠습니까?",),
    (6, 2293): ("꽤 큰 부탁이군요.\n그만한 대가를 기대해도 되겠습니까?",),
    (6, 2297): ("꽤 큰 부탁이군요.\n그만한 대가를 기대해도 되겠습니까?",),
    (6, 2303): ("이 요청의 대가는 큽니다.\n상응하는 보답을 준비하셨겠지요?",),
    (6, 2304): ("이 요청의 대가는 큽니다.\n상응하는 보답을 준비하셨겠지요?",),
    (6, 2305): ("이 요청의 대가는 큽니다.\n상응하는 보답을 준비하셨겠지요?",),
    (6, 2309): ("이 요청의 대가는 큽니다.\n상응하는 보답을 준비하셨겠지요?",),
    (6, 2313): ("모든 제안 내용을 일단 철회합니다.\n계속하시겠습니까?",),
    (6, 2316): ("이 대가로 설득할 상대:", "님.\n아직 받아들이지 않을 것입니다……"),
    (6, 2317): ("이 대가로 설득할 상대:", "님.\n아직 받아들이지 않을 것입니다……"),
    (6, 2318): ("이 대가로 설득할 상대:", "님.\n아직 받아들이지 않을 것입니다……"),
    (6, 2322): ("이 대가로 설득할 상대:", "님.\n아직 받아들이지 않을 것입니다……"),
    (6, 2328): ("이 대가의 수락 여부를 정할 상대:", "님.\n결과는 운에 맡겨야 합니다."),
    (6, 2329): ("이 대가의 수락 여부를 정할 상대:", "님.\n결과는 운에 맡겨야 합니다."),
    (6, 2330): ("이 대가의 수락 여부를 정할 상대:", "님.\n결과는 운에 맡겨야 합니다."),
    (6, 2334): ("이 대가의 수락 여부를 정할 상대:", "님.\n결과는 운에 맡겨야 합니다."),
    (6, 2340): ("이 정도 대가라면 만족할 상대:", "님.\n기꺼이 부탁을 들어줄 것입니다."),
    (6, 2341): ("이 정도 대가라면 만족할 상대:", "님.\n기꺼이 부탁을 들어줄 것입니다."),
    (6, 2342): ("이 정도 대가라면 만족할 상대:", "님.\n기꺼이 부탁을 들어줄 것입니다."),
    (6, 2346): ("이 정도 대가라면 만족할 상대:", "님.\n기꺼이 부탁을 들어줄 것입니다."),
    (6, 2352): ("이 조건이라면 부탁을 듣겠습니다.\n상대:", "님.\n교섭을 계속하시지요."),
    (6, 2353): ("이 조건이라면 부탁을 듣겠습니다.\n상대:", "님.\n교섭을 계속하시지요."),
    (6, 2354): ("이 조건이라면 부탁을 듣겠습니다.\n상대:", "님.\n교섭을 계속하시지요."),
    (6, 2358): ("이 조건이라면 부탁을 듣겠습니다.\n상대:", "님.\n교섭을 계속하시지요."),
    (6, 2364): ("이제 마무리합시다. 상대:", "님.\n이번이 마지막입니다."),
    (6, 2365): ("이제 마무리합시다. 상대:", "님.\n이번이 마지막입니다."),
    (6, 2366): ("이제 마무리합시다. 상대:", "님.\n이번이 마지막입니다."),
    (6, 2370): ("이제 마무리합시다. 상대:", "님.\n이번이 마지막입니다."),
    (6, 2400): ("그 요구는 받아들일 수 없습니다……",),
    (6, 2401): ("그 요구는 받아들일 수 없습니다……",),
    (6, 2402): ("그 요구는 받아들일 수 없습니다……",),
    (6, 2406): ("그 요구는 받아들일 수 없습니다……",),
    (6, 2412): ("이제 그만합시다. 상대:", "님.\n다른 용건이 없다면 마치겠습니다."),
    (6, 2413): ("이제 그만합시다. 상대:", "님.\n다른 용건이 없다면 마치겠습니다."),
    (6, 2414): ("이제 그만합시다. 상대:", "님.\n다른 용건이 없다면 마치겠습니다."),
    (6, 2418): ("이제 그만합시다. 상대:", "님.\n다른 용건이 없다면 마치겠습니다."),
    (6, 2424): ("더는 교섭하고 싶지 않은 상대:\n", "님과의 교섭은 끝입니다.\n어서 돌아가십시오."),
    (6, 2425): ("더는 교섭하고 싶지 않은 상대:\n", "님과의 교섭은 끝입니다.\n어서 돌아가십시오."),
    (6, 2426): ("더는 교섭하고 싶지 않은 상대:\n", "님과의 교섭은 끝입니다.\n어서 돌아가십시오."),
    (6, 2430): ("더는 교섭하고 싶지 않은 상대:\n", "님과의 교섭은 끝입니다.\n어서 돌아가십시오."),
    (6, 2436): ("이런 조건은 받아들일 수 없습니다.\n교섭 상대:", None),
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
    if selected[0] != (6, 2139, 2) or selected[-1] != (6, 2436, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 98:
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
    if selected[-1] != (6, 2436, 0) or NEXT_COORDINATE not in sc_literals:
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
