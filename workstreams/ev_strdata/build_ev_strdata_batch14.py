#!/usr/bin/env python3
"""Build source-free ev_strdata event-label batch v0.14 artifacts."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_ev_strdata_batch1 as shared  # noqa: E402


BATCH_ID = "ev-strdata-event-labels-2407-2580-v0.14"
OVERLAY_NAME = "ev_strdata_ko_event_labels_2407_2580.v0.14.json"
EVIDENCE_NAME = "alignment_evidence.v0.14.json"
REVIEW_NAME = "review_index.v0.14.json"
VALIDATION_NAME = "validation.v0.14.json"

SCOPE_START = 2407
SCOPE_END = 2580
TRANSLATED_COUNT = SCOPE_END - SCOPE_START + 1
SEQUENTIAL_NEXT_ID = 2581
NEXT_PLACEHOLDER_START = 2581
NEXT_PLACEHOLDER_END = 2779
NEXT_PLACEHOLDER_COUNT = NEXT_PLACEHOLDER_END - NEXT_PLACEHOLDER_START + 1
NEXT_DISPLAY_ID = 2780

INPUT_MAP_SHA256 = "E96B7F48466E92F55B480D8A9A96BAF35F1DF4D070EFD4F99F2C79C466581BFD"
SOURCE_SC_HASHES_SHA256 = "05F6A51D9F033862E180B39F99863BF570729E4A850FFC575BE9EBD40999AAE5"
ALL_REFERENCE_HASHES_SHA256 = "77AEB9AF67105F4D05F96F0FC22BE8950732EFA8EC99BB9D9D23C18046E618D7"
PLACEHOLDER_REFERENCE_HASHES = {
    "SC": "2AB80B631AD896118B57262A7756C480D2BC0733C95357BC5EC1F4AD4A21CFAB",
    "JP": "143A3833C55A7B51DBBEB8B0E0475770C90A4756005D69FCBB117DDBF4611BFC",
    "TC": "2AB80B631AD896118B57262A7756C480D2BC0733C95357BC5EC1F4AD4A21CFAB",
}

TRANSLATIONS: dict[int, str] = {
    2407: "와가중 두령",
    2408: "가시야마중 두령",
    2409: "이시노마키중 두령",
    2410: "구마가네중 두령",
    2411: "이시카와중 두령",
    2412: "하나와중 두령",
    2413: "가타히라중 두령",
    2414: "시로이시중 두령",
    2415: "와타리중 두령",
    2416: "나라하중 두령",
    2417: "오바마중 두령",
    2418: "야나토리중 두령",
    2419: "시오노중 두령",
    2420: "돗코중 두령",
    2421: "도시마중 두령",
    2422: "니카호중 두령",
    2423: "가바야마중 두령",
    2424: "히노키나이중 두령",
    2425: "사케노베중 두령",
    2426: "야치중 두령",
    2427: "아라토중 두령",
    2428: "오구니중 두령",
    2429: "후쿠로다중 두령",
    2430: "마카베중 두령",
    2431: "미토중 두령",
    2432: "시모사중 두령",
    2433: "모리야마중 두령",
    2434: "마리야쓰중 두령",
    2435: "아와노중 두령",
    2436: "이오노중 두령",
    2437: "시오바라중 두령",
    2438: "오야마중 두령",
    2439: "사루가쿄중 두령",
    2440: "우스이중 두령",
    2441: "요코세중 두령",
    2442: "지치부중 두령",
    2443: "아라카와중 두령",
    2444: "가쓰누마중 두령",
    2445: "나루세중 두령",
    2446: "네고야중 두령",
    2447: "마쓰야마중 두령",
    2448: "우라가중 두령",
    2449: "후마 일당 두령",
    2450: "가와치중 두령",
    2451: "군나이중 두령",
    2452: "사쿠중 두령",
    2453: "나가누마중 두령",
    2454: "이야마중 두령",
    2455: "오미중 두령",
    2456: "하타야마중 두령",
    2457: "네즈중 두령",
    2458: "마쓰오카중 두령",
    2459: "아가키타중 두령",
    2460: "미나미아가키타중 두령",
    2461: "야스다중 두령",
    2462: "마쓰시로중 두령",
    2463: "가키자키중 두령",
    2464: "네치중 두령",
    2465: "모리데라중 두령",
    2466: "네이중 두령",
    2467: "마쓰쿠라중 두령",
    2468: "유사중 두령",
    2469: "와지마중 두령",
    2470: "시라미네중 두령",
    2471: "도리고에중 두령",
    2472: "호리에중 두령",
    2473: "유노중 두령",
    2474: "이시야마중 두령",
    2475: "도이중 두령",
    2476: "고가와중 두령",
    2477: "가쓰라야마중 두령",
    2478: "후지노미야중 두령",
    2479: "이누이중 두령",
    2480: "미쓰케중 두령",
    2481: "쓰쿠데중 두령",
    2482: "가마가타중 두령",
    2483: "가리야중 두령",
    2484: "가와나미중 두령",
    2485: "이와쿠라중 두령",
    2486: "나루미중 두령",
    2487: "도코나메중 두령",
    2488: "나에기중 두령",
    2489: "우호중 두령",
    2490: "기타가타중 두령",
    2491: "후와중 두령",
    2492: "다카하라중 두령",
    2493: "나카지마중 두령",
    2494: "고즈쿠리중 두령",
    2495: "간베중 두령",
    2496: "구키중 두령",
    2497: "이누카미중 두령",
    2498: "고카중 두령",
    2499: "이시베중 두령",
    2500: "오미조중 두령",
    2501: "아사즈마중 두령",
    2502: "마키시마중 두령",
    2503: "엔랴쿠지중 두령",
    2504: "다케베야마중 두령",
    2505: "히카미중 두령",
    2506: "슈치중 두령",
    2507: "가타노중 두령",
    2508: "도키중 두령",
    2509: "아리마중 두령",
    2510: "요노중 두령",
    2511: "이가중 두령",
    2512: "오치중 두령",
    2513: "도치중 두령",
    2514: "신구중 두령",
    2515: "네고로중 두령",
    2516: "조즈이중 두령",
    2517: "고데라중 두령",
    2518: "니시와키중 두령",
    2519: "나카무라중 두령",
    2520: "고토중 두령",
    2521: "고쿠라중 두령",
    2522: "오사후네중 두령",
    2523: "니이미중 두령",
    2524: "기비중 두령",
    2525: "와치중 두령",
    2526: "시토미야마중 두령",
    2527: "구마가이중 두령",
    2528: "히라가중 두령",
    2529: "세노중 두령",
    2530: "시시도중 두령",
    2531: "도쿠야마중 두령",
    2532: "니호중 두령",
    2533: "헤키중 두령",
    2534: "우베중 두령",
    2535: "만바중 두령",
    2536: "가시마중 두령",
    2537: "요시오카중 두령",
    2538: "쓰쓰미중 두령",
    2539: "오다카중 두령",
    2540: "아카나중 두령",
    2541: "마쓰에중 두령",
    2542: "오치중 두령",
    2543: "다카쓰중 두령",
    2544: "시와쿠 수군 두령",
    2545: "고자이중 두령",
    2546: "우시키중 두령",
    2547: "시노하라중 두령",
    2548: "무라카미 수군 두령",
    2549: "사기노모리중 두령",
    2550: "오즈중 두령",
    2551: "스쿠모중 두령",
    2552: "하타중 두령",
    2553: "게라중 두령",
    2554: "구몬중 두령",
    2555: "아카하타중 두령",
    2556: "우사군중 두령",
    2557: "마쓰무레중 두령",
    2558: "미나미군중 두령",
    2559: "기즈키중 두령",
    2560: "무나카타중 두령",
    2561: "쓰쿠시중 두령",
    2562: "아소중 두령",
    2563: "다카오중 두령",
    2564: "나가이와중 두령",
    2565: "미쓰세중 두령",
    2566: "가시마중 두령",
    2567: "다카시로중 두령",
    2568: "사세보중 두령",
    2569: "조중 두령",
    2570: "아카호시중 두령",
    2571: "야쓰시로중 두령",
    2572: "다카치호중 두령",
    2573: "마쓰오중 두령",
    2574: "이노중 두령",
    2575: "쓰루다중 두령",
    2576: "구시키노중 두령",
    2577: "게도인중 두령",
    2578: "다네가시마중 두령",
    2579: "이지치중 두령",
    2580: "네지메중 두령",
}

INPUT_CORRECTION_IDS = frozenset({2450})
UNCERTAIN_READING_IDS = frozenset(
    {
        2419,
        2466,
        2473,
        2482,
        2489,
        2506,
        2513,
        2516,
        2526,
        2529,
        2533,
        2536,
        2542,
        2546,
        2553,
        2554,
        2558,
        2563,
        2567,
        2569,
    }
)
CLASS_COUNTS = {
    "fuma_party_leader_label": 1,
    "naval_group_leader_label": 2,
    "regional_group_leader_label": 171,
}


def classify(entry_id: int) -> str:
    if entry_id == 2449:
        return "fuma_party_leader_label"
    if entry_id in {2544, 2548}:
        return "naval_group_leader_label"
    return "regional_group_leader_label"


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if sorted(TRANSLATIONS) != ids or len(TRANSLATIONS) != TRANSLATED_COUNT:
        raise shared.EvStrDataError("v0.14 map is not the exact contiguous 174-id range")
    if TRANSLATIONS[2450] != "가와치중 두령":
        raise shared.EvStrDataError("v0.14 reviewed input correction changed")

    source_sc_hashes: list[str] = []
    all_reference_hashes: list[str] = []
    replacement_by_source_hash: dict[str, str] = {}
    class_counts = {name: 0 for name in CLASS_COUNTS}
    for entry_id in ids:
        class_counts[classify(entry_id)] += 1
        source_sc = loaded["SC"]["table"].texts[entry_id]
        if any(
            not loaded[language]["table"].texts[entry_id].strip()
            for language in shared.LANGUAGES
        ):
            raise shared.EvStrDataError(f"id {entry_id}: empty aligned display label")
        source_hash = common.text_hash(source_sc)
        source_sc_hashes.append(source_hash)
        all_reference_hashes.extend(
            common.text_hash(loaded[language]["table"].texts[entry_id])
            for language in shared.LANGUAGES
        )
        replacement = TRANSLATIONS[entry_id]
        failures = shared.replacement_failures(source_sc, replacement)
        if failures:
            raise shared.EvStrDataError(f"id {entry_id}: invariant mismatch: {failures}")
        prior = replacement_by_source_hash.setdefault(source_hash, replacement)
        if prior != replacement:
            raise shared.EvStrDataError(
                f"id {entry_id}: repeated SC source has inconsistent Korean translations"
            )

    if class_counts != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.14 functional classification counts changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.14 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.14 ordered SC/JP/TC source hashes changed")
    if len(set(source_sc_hashes)) != TRANSLATED_COUNT:
        raise shared.EvStrDataError("v0.14 reviewed SC source uniqueness changed")

    for entry_id in range(NEXT_PLACEHOLDER_START, NEXT_PLACEHOLDER_END + 1):
        for language in shared.LANGUAGES:
            source_hash = common.text_hash(loaded[language]["table"].texts[entry_id])
            if source_hash != PLACEHOLDER_REFERENCE_HASHES[language]:
                raise shared.EvStrDataError(
                    f"id {entry_id} {language}: next placeholder range hash mismatch"
                )
    return ids


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    ids = validate_batch_sources(loaded)

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = loaded["SC"]["table"].texts[entry_id]
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": TRANSLATIONS[entry_id],
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "classification": classify(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            loaded[language]["table"].texts[entry_id]
                        ),
                        "structure": shared.text_structure(
                            loaded[language]["table"].texts[entry_id]
                        ),
                    }
                    for language in shared.LANGUAGES
                },
                "translation_origin": (
                    "reviewed_input_map_obvious_typo_corrected"
                    if entry_id in INPUT_CORRECTION_IDS
                    else "reviewed_input_map_exact"
                ),
            }
        )

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": shared.RESOURCE,
        "base_language": "SC",
        "entry_count": len(ids),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": shared.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": shared.sha256(sc_raw),
            "string_count": shared.STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
    try:
        common.validate_overlay_shape(overlay)
    finally:
        common.ALLOWED_RESOURCES = original_allowlist

    source_files = {
        language: {
            **shared.SOURCE_PINS[language],
            "relative_path": loaded[language]["relative"],
            "string_count": shared.STRING_COUNT,
        }
        for language in shared.LANGUAGES
    }
    boundary_ids = (
        SCOPE_START - 1,
        SCOPE_START,
        2448,
        2449,
        2450,
        2543,
        2544,
        2548,
        SCOPE_END,
        NEXT_PLACEHOLDER_START,
        NEXT_PLACEHOLDER_END,
        NEXT_DISPLAY_ID,
    )
    next_placeholder_range = {
        "start_id": NEXT_PLACEHOLDER_START,
        "end_id": NEXT_PLACEHOLDER_END,
        "count": NEXT_PLACEHOLDER_COUNT,
        "status": "deferred",
        "classification": "code_placeholder",
        "reason": "repeated_internal_placeholder_not_a_display_translation_target",
        "reference_utf16le_sha256": PLACEHOLDER_REFERENCE_HASHES,
        "excluded_from_overlay_and_translation_progress": True,
    }
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v14",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "sequential_next_id": SEQUENTIAL_NEXT_ID,
            "next_display_id": NEXT_DISPLAY_ID,
            "functional_section": "regional_naval_and_fuma_leader_labels_completion",
            "functional_class_counts": CLASS_COUNTS,
        },
        "input_mapping": {
            "relative_path": "tmp/evstr_v014_ko_map.json",
            "sha256": INPUT_MAP_SHA256,
            "entry_count": TRANSLATED_COUNT,
            "embedded_in_distribution": False,
            "obvious_typo_correction_count": len(INPUT_CORRECTION_IDS),
            "corrected_ids_sha256": shared.hash_json(sorted(INPUT_CORRECTION_IDS)),
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17868_string_count",
            "same_numeric_string_ids",
            "sc_jp_tc_semantic_review",
            "exact_sc_hash_for_every_overlay_entry",
            "ordered_sc_jp_tc_hash_set_pin",
            "repeated_source_requires_identical_korean_translation",
        ],
        "reference_language_note": (
            "The installed MSG tree has no EN ev_strdata resource; TC is the third "
            "reference alongside SC and JP. Official strings are represented only by hashes."
        ),
        "source_files": source_files,
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(
                        loaded[language]["table"].texts[entry_id]
                    )
                    for language in shared.LANGUAGES
                },
            }
            for entry_id in boundary_ids
        ],
        "entry_count": TRANSLATED_COUNT,
        "entries": evidence_entries,
        "next_deferred_ranges": [next_placeholder_range],
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v14",
        "batch_id": BATCH_ID,
        "quality_state": "event_label_draft_pending_runtime_review",
        "entry_count": TRANSLATED_COUNT,
        "uncertain_reading_count": len(UNCERTAIN_READING_IDS),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "classification": classify(entry_id),
                "translation_origin": (
                    "reviewed_input_map_obvious_typo_corrected"
                    if entry_id in INPUT_CORRECTION_IDS
                    else "reviewed_input_map_exact"
                ),
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": (
                    ["rare_place_reading"]
                    if entry_id in UNCERTAIN_READING_IDS
                    else []
                )
                + (
                    ["input_map_typo_corrected"]
                    if entry_id in INPUT_CORRECTION_IDS
                    else []
                ),
            }
            for entry_id in ids
        ],
        "next_deferred_ranges": [next_placeholder_range],
        "contains_commercial_source_text": False,
    }

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    for path, value in (
        (overlay_path, overlay),
        (evidence_path, evidence),
        (review_path, review),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(shared.encode_json(value))

    source_free_scan = {
        path.relative_to(out_root).as_posix(): shared.source_free_counts(path.read_bytes())
        for path in (overlay_path, evidence_path, review_path)
    }
    if any(
        counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for counts in source_free_scan.values()
    ):
        raise shared.EvStrDataError(
            "v0.14 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.14 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v14",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "sequential_next_id": SEQUENTIAL_NEXT_ID,
            "next_display_id": NEXT_DISPLAY_ID,
            "translated_ids_sha256": shared.hash_json(ids),
            "next_placeholder_ids_sha256": shared.hash_json(
                list(range(NEXT_PLACEHOLDER_START, NEXT_PLACEHOLDER_END + 1))
            ),
            "total_string_slots": shared.STRING_COUNT,
            "sc_display_translation_target_count": shared.DISPLAY_TARGET_COUNT_SC,
            "functional_class_counts": CLASS_COUNTS,
        },
        "source_alignment": {
            "languages": list(shared.LANGUAGES),
            "english_reference_available": False,
            "traditional_chinese_used_as_third_reference": True,
            "string_count_each": shared.STRING_COUNT,
            "translated_reference_hash_count": TRANSLATED_COUNT * len(shared.LANGUAGES),
            "translated_ids_nonempty_in_all_references": TRANSLATED_COUNT,
            "ordered_sc_source_hashes_sha256": SOURCE_SC_HASHES_SHA256,
            "ordered_all_reference_hashes_sha256": ALL_REFERENCE_HASHES_SHA256,
            "source_files": source_files,
        },
        "translation": {
            "input_map_sha256": INPUT_MAP_SHA256,
            "input_map_entry_count": TRANSLATED_COUNT,
            "exact_sc_hashes_emitted": TRANSLATED_COUNT,
            "obvious_typo_correction_count": len(INPUT_CORRECTION_IDS),
            "corrected_ids_sha256": shared.hash_json(sorted(INPUT_CORRECTION_IDS)),
            "uncertain_reading_review_flag_count": len(UNCERTAIN_READING_IDS),
            "source_text_embedded": False,
        },
        "repeated_source_policy": {
            "same_source_same_translation_required": True,
            "translated_unique_source_hash_count": TRANSLATED_COUNT,
            "translated_repeated_source_group_count": 0,
            "failures": 0,
        },
        "next_placeholder_range": next_placeholder_range,
        "replacement_invariants": {
            "checked": TRANSLATED_COUNT,
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_placeholders_in_order",
            ],
        },
        "raw_format": {
            "lz4_wrapper_decompression": "OK",
            "message_table_parser": "tools/nobu16_msg_table.py",
            "raw_parse_rebuild_byte_exact_languages": list(shared.LANGUAGES),
            "binary_builder_state": "enabled_offline_output_only",
        },
        "offline_binary_build": {
            **binary,
            "installed_target_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": shared.sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "existing_v01_through_v013_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.14 validation is not source-free")
    return {
        "entry_count": TRANSLATED_COUNT,
        "next_display_id": NEXT_DISPLAY_ID,
        "next_placeholder_count": NEXT_PLACEHOLDER_COUNT,
        "files": generated_file_map(out_root),
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [
        game_root / "MSG" / language / "ev_strdata.bin"
        for language in shared.LANGUAGES
    ]
    before = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr14-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr14-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.14 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.14 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.14 build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"translated={result['entry_count']}")
    print(f"next_placeholder_count={result['next_placeholder_count']}")
    print(f"next_display_id={result['next_display_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={shared.sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
