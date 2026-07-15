#!/usr/bin/env python3
"""Build the next source-free PK msgdata name-component batch (3222-3315)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
PATCH_ROOT = WORKSPACE_ROOT / "KR_PATCH_WORK"
TOOLS_DIR = PATCH_ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "msgdata_name_components_3222_3315.v0.1"
RESOURCE = "MSG_PK/SC/msgdata.bin"
OVERLAY_NAME = "msgdata_ko_name_components_3222_3315.v0.1.json"
EVIDENCE_NAME = "alignment_evidence_name_components_3222_3315.v0.1.json"
REVIEW_NAME = "review_index_name_components_3222_3315.v0.1.json"
VALIDATION_NAME = "validation_name_components_3222_3315.v0.1.json"
STRING_COUNT = 29_210
LANGUAGES = ("SC", "JP", "EN", "TC")
SCOPE_START = 3222
SCOPE_END = 3315
SUCCESSOR_BLOCKED_ID = 3316
TRANSLATED_COUNT = SCOPE_END - SCOPE_START + 1

RESOURCE_PINS: dict[str, dict[str, Any]] = {
    "SC": {
        "logical_path": "MSG_PK/SC/msgdata.bin",
        "packed_size": 516_796,
        "packed_sha256": "DFFC1FA9E8D175085568C14A407B9CB4BE81CF1416DA4485A64CA330D908ADA5",
        "raw_size": 514_752,
        "raw_sha256": "5982D520BF2E66260943DE61D0CB7F1135D1BA81A211E917E3F426C58D9125D6",
    },
    "JP": {
        "logical_path": "MSG_PK/JP/msgdata.bin",
        "packed_size": 273_734,
        "packed_sha256": "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38",
        "raw_size": 431_044,
        "raw_sha256": "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0",
    },
    "EN": {
        "logical_path": "MSG_PK/EN/msgdata.bin",
        "packed_size": 267_550,
        "packed_sha256": "15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1",
        "raw_size": 744_236,
        "raw_sha256": "DA913D870DA3C13F108E8E6727C9A8881B9E13A83F8EB7F02DD3C55D1D444B32",
    },
    "TC": {
        "logical_path": "MSG_PK/TC/msgdata.bin",
        "packed_size": 270_032,
        "packed_sha256": "A3743D318383C5D6E4D16F20B5228337DB0AE9124D144E4FBF3D4AC660FFFC5E",
        "raw_size": 442_224,
        "raw_sha256": "4D0CEB95818CC9C17623299B2B104482FED03ACCD27116604F8E29BB4C9D7684",
    },
}

EXISTING_OVERLAYS = (
    {
        "logical_path": "KR_PATCH_WORK/data/public/msgdata_ko_officer_names_0000_2399.v0.1.json",
        "sha256": "D787EB64BFFC54D1ACA2F23BC9407991FEB4FCF76D102E1EE017EEF416FE4FA3",
        "entry_count": 3831,
    },
    {
        "logical_path": "KR_PATCH_WORK/workstreams/castle_names/public/castle_names_ko_9151_9542.v0.2.json",
        "sha256": "0CEFDE11008F4503198903E1FA25ACDDB120F6B407405EF9ACE2B01B39577E5E",
        "entry_count": 392,
    },
    {
        "logical_path": "KR_PATCH_WORK/workstreams/province_names/public/province_names_ko_13975_14046.v0.2.json",
        "sha256": "2EF65EBDEF21521857477EA180E7FBC7AB92F1626FC69D06BD6262E97BFDBDF5",
        "entry_count": 72,
    },
    {
        "logical_path": "KR_PATCH_WORK/workstreams/msgdata/public/msgdata_ko_faction_labels_3032_3221.v0.1.json",
        "sha256": "A277CC298262A46683CDB81273487BB5EF4AAD25FE361C1977251B52A1BF7244",
        "entry_count": 190,
    },
)

GROUPS = (
    {
        "group_id": "personal_name_components",
        "start_id": 3222,
        "end_id": 3243,
        "selected_count": 22,
    },
    {
        "group_id": "regional_groups_and_religious_labels",
        "start_id": 3244,
        "end_id": 3315,
        "selected_count": 72,
    },
)

# Korean-only translations.  No official SC/JP/EN/TC text is emitted by the
# generated overlay, evidence, review, or validation artifacts.
TRANSLATIONS: dict[int, str] = {
    3222: "나카",
    3223: "혼자와",
    3224: "나오코",
    3225: "미나모토",
    3226: "요시쓰네",
    3227: "코",
    3228: "우",
    3229: "소",
    3230: "칭기스",
    3231: "칸",
    3232: "오키타",
    3233: "소지",
    3234: "덴시쓰",
    3235: "고이쿠",
    3236: "도라치요",
    3237: "야스히데",
    3238: "쇼요켄",
    3239: "요시스케",
    3240: "셋쓰",
    3241: "하루카도",
    3242: "다마",
    3243: "데루토라",
    3244: "조호지중",
    3245: "사가에중",
    3246: "고쿠부중",
    3247: "니혼마쓰중",
    3248: "고미네중",
    3249: "로쿠고중",
    3250: "가토리중",
    3251: "오스가중",
    3252: "조난중",
    3253: "모테기중",
    3254: "도미오카중",
    3255: "미부중",
    3256: "안나카중",
    3257: "하뉴중",
    3258: "기사이중",
    3259: "다미야중",
    3260: "이루마중",
    3261: "다쿠마중",
    3262: "마이다중",
    3263: "도가쿠시중",
    3264: "아오야기중",
    3265: "조노중",
    3266: "즈이센지",
    3267: "마쓰네중",
    3268: "구라타니중",
    3269: "가노중",
    3270: "오키쓰중",
    3271: "마무시즈카중",
    3272: "혼고중",
    3273: "요로중",
    3274: "오하라중",
    3275: "아오치중",
    3276: "엔랴쿠지",
    3277: "구미하마중",
    3278: "맛타중",
    3279: "마쓰라중",
    3280: "미쓰보시중",
    3281: "야마가타중",
    3282: "야기중",
    3283: "도이다중",
    3284: "쿤다니중",
    3285: "마스다중",
    3286: "와카사중",
    3287: "후쿠요리중",
    3288: "진자이중",
    3289: "미스미중",
    3290: "가미중",
    3291: "구사미중",
    3292: "기쿠치중",
    3293: "하타중",
    3294: "다케오중",
    3295: "이노중",
    3296: "게도인중",
    3297: "안도수군",
    3298: "구로카와중",
    3299: "야마노우치중",
    3300: "아와수군",
    3301: "도쿠다중",
    3302: "사카나이중",
    3303: "도이치중",
    3304: "오다카중",
    3305: "쿠게중",
    3306: "고자이중",
    3307: "오히라중",
    3308: "아마쿠사중",
    3309: "혼쇼지",
    3310: "구쓰키중",
    3311: "초칸사이",
    3312: "덴토쿠지",
    3313: "호엔",
    3314: "도쿤",
    3315: "마사하루",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3227: ["single_component_reading_requires_runtime_name_builder_review"],
    3228: ["single_component_reading_requires_runtime_name_builder_review"],
    3229: ["single_component_reading_requires_runtime_name_builder_review"],
    3234: ["personal_name_reading_requires_glossary_review"],
    3235: ["personal_name_reading_requires_glossary_review"],
    3238: ["religious_style_name_reading_requires_glossary_review"],
    3241: ["personal_name_reading_requires_glossary_review"],
    3265: ["regional_group_reading_requires_glossary_review"],
    3278: ["regional_group_reading_requires_glossary_review"],
    3283: ["regional_group_reading_requires_glossary_review"],
    3284: ["regional_group_reading_requires_glossary_review"],
    3286: ["regional_group_reading_requires_glossary_review"],
    3288: ["regional_group_reading_requires_glossary_review"],
    3290: ["regional_group_reading_requires_glossary_review"],
    3296: ["regional_group_reading_requires_glossary_review"],
    3302: ["regional_group_reading_requires_glossary_review"],
    3306: ["regional_group_reading_requires_glossary_review"],
    3311: ["religious_style_name_reading_requires_glossary_review"],
    3313: ["religious_style_name_reading_requires_glossary_review"],
    3314: ["religious_style_name_reading_requires_glossary_review"],
}

CJK_RE = re.compile(r"[\u3400-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF]")
BRACKET_TOKEN_RE = re.compile(r"\[[A-Za-z0-9_]+\]")


class MsgdataBatch2Error(ValueError):
    """Raised when the fixed scope, source pins, or safety invariants differ."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(out_root: Path, path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": path.relative_to(out_root).as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def selected_ids() -> list[int]:
    return list(range(SCOPE_START, SCOPE_END + 1))


def group_for(entry_id: int) -> str:
    for group in GROUPS:
        if int(group["start_id"]) <= entry_id <= int(group["end_id"]):
            return str(group["group_id"])
    raise MsgdataBatch2Error(f"no group for ID {entry_id}")


def public_script_counts(blob: bytes) -> dict[str, int]:
    text = blob.decode("utf-8")
    return {
        "cjk_unified_count": len(CJK_RE.findall(text)),
        "kana_count": len(KANA_RE.findall(text)),
        "embedded_nul_count": text.count("\x00"),
    }


def source_structure(text: str) -> dict[str, Any]:
    invariant = common.message_invariants(text)
    bracket_tokens = BRACKET_TOKEN_RE.findall(text)
    return {
        "utf16le_sha256": common.text_hash(text),
        "printf_tokens_sha256": hash_json(invariant["printf"]),
        "printf_token_count": len(invariant["printf"]),
        "unknown_percent_count": invariant["unknown_percent_count"],
        "leading_whitespace_utf16le_sha256": common.text_hash(invariant["leading_whitespace"]),
        "trailing_whitespace_utf16le_sha256": common.text_hash(invariant["trailing_whitespace"]),
        "escape_tokens_sha256": hash_json(invariant["esc"]),
        "escape_token_count": len(invariant["esc"]),
        "control_codepoints": invariant["controls"],
        "line_breaks_sha256": hash_json(invariant["line_breaks"]),
        "private_use_codepoints": invariant["pua"],
        "bracket_placeholder_count": len(bracket_tokens),
        "bracket_placeholders_sha256": hash_json(bracket_tokens),
    }


def invariant_failures(source: str, replacement: str) -> list[str]:
    failures = common.invariant_mismatches(source, replacement)
    if BRACKET_TOKEN_RE.findall(source) != BRACKET_TOKEN_RE.findall(replacement):
        failures.append("bracket_placeholder_sequence differs")
    return failures


def validate_static_scope() -> None:
    ids = selected_ids()
    if ids != sorted(TRANSLATIONS) or len(ids) != TRANSLATED_COUNT:
        raise MsgdataBatch2Error("translations do not exactly cover the fixed contiguous range")
    if ids[0] != SCOPE_START or ids[-1] != SCOPE_END:
        raise MsgdataBatch2Error("scope boundary changed")
    if sum(int(group["selected_count"]) for group in GROUPS) != TRANSLATED_COUNT:
        raise MsgdataBatch2Error("group total changed")
    if [group_for(entry_id) for entry_id in ids].count("personal_name_components") != 22:
        raise MsgdataBatch2Error("personal-name group boundary changed")
    if [group_for(entry_id) for entry_id in ids].count("regional_groups_and_religious_labels") != 72:
        raise MsgdataBatch2Error("regional group boundary changed")


def source_snapshot(game_root: Path) -> dict[str, str]:
    return {
        pin["logical_path"]: sha256((game_root / pin["logical_path"]).read_bytes())
        for pin in RESOURCE_PINS.values()
    }


def load_resource(game_root: Path, language: str) -> dict[str, Any]:
    pin = RESOURCE_PINS[language]
    path = game_root / pin["logical_path"]
    packed = path.read_bytes()
    if len(packed) != pin["packed_size"] or sha256(packed) != pin["packed_sha256"]:
        raise MsgdataBatch2Error(f"{pin['logical_path']}: packed source pin mismatch")
    _wrapper, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise MsgdataBatch2Error(f"{pin['logical_path']}: raw source pin mismatch")
    table = parse_message_table(raw)
    if table.string_count != STRING_COUNT:
        raise MsgdataBatch2Error(f"{pin['logical_path']}: unexpected string count")
    if rebuild_message_table(table, table.texts) != raw:
        raise MsgdataBatch2Error(f"{pin['logical_path']}: parse/rebuild is not byte-identical")
    return {"packed": packed, "raw": raw, "table": table}


def _load_existing_overlay(workspace_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    path = workspace_root / spec["logical_path"]
    blob = path.read_bytes()
    if sha256(blob) != spec["sha256"]:
        raise MsgdataBatch2Error(f"existing overlay pin changed: {spec['logical_path']}")
    try:
        value = json.loads(blob.decode("utf-8"), object_pairs_hook=common.strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MsgdataBatch2Error(f"invalid existing overlay: {spec['logical_path']}") from exc
    entries = value.get("entries")
    if not isinstance(entries, list) or len(entries) != spec["entry_count"]:
        raise MsgdataBatch2Error(f"existing overlay entry count changed: {spec['logical_path']}")
    ids = [int(entry["id"]) for entry in entries if isinstance(entry, dict) and "id" in entry]
    if len(ids) != len(entries) or len(ids) != len(set(ids)):
        raise MsgdataBatch2Error(f"existing overlay IDs invalid: {spec['logical_path']}")
    return {
        "logical_path": spec["logical_path"],
        "sha256": spec["sha256"],
        "entry_count": len(ids),
        "min_id": min(ids),
        "max_id": max(ids),
        "ids": set(ids),
        "entries": entries,
    }


def existing_overlay_snapshot(workspace_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    loaded = [_load_existing_overlay(workspace_root, spec) for spec in EXISTING_OVERLAYS]
    total_entries = sum(record["entry_count"] for record in loaded)
    union: set[int] = set()
    for record in loaded:
        union.update(record["ids"])
    selected_overlap = sorted(set(selected_ids()) & union)
    if selected_overlap:
        raise MsgdataBatch2Error(f"selected IDs overlap existing overlays: {selected_overlap}")
    if SUCCESSOR_BLOCKED_ID not in union:
        raise MsgdataBatch2Error("expected successor conflict is absent; scope must be re-reviewed")
    return (
        {
            "overlays": [
                {
                    key: record[key]
                    for key in ("logical_path", "sha256", "entry_count", "min_id", "max_id")
                }
                for record in loaded
            ],
            "total_authored_entry_count": total_entries,
            "effective_unique_coordinate_count": len(union),
            "cross_overlay_duplicate_coordinate_count": total_entries - len(union),
            "selected_overlap_ids": [],
            "next_contiguous_id": SUCCESSOR_BLOCKED_ID,
            "next_contiguous_id_conflicts_with_existing_overlay": True,
        },
        loaded,
    )


def translation_memory_review(table: Any, existing_records: list[dict[str, Any]]) -> dict[str, Any]:
    selected_hashes = {
        common.text_hash(table.texts[entry_id]): entry_id for entry_id in selected_ids()
    }
    candidates: dict[int, list[dict[str, Any]]] = {entry_id: [] for entry_id in selected_ids()}
    for record in existing_records:
        for entry in record["entries"]:
            source_hash = entry.get("source_sc_utf16le_sha256")
            if source_hash in selected_hashes:
                candidates[selected_hashes[source_hash]].append(
                    {
                        "logical_path": record["logical_path"],
                        "id": int(entry["id"]),
                        "ko": str(entry["ko"]),
                    }
                )
    matched = []
    exact_agreement_count = 0
    for entry_id, rows in candidates.items():
        if not rows:
            continue
        agrees = any(row["ko"] == TRANSLATIONS[entry_id] for row in rows)
        exact_agreement_count += int(agrees)
        matched.append(
            {
                "id": entry_id,
                "candidate_entry_count": len(rows),
                "candidate_overlay_paths": sorted({row["logical_path"] for row in rows}),
                "independent_coordinate_context_reviewed": True,
                "chosen_translation_exactly_agrees_with_a_candidate": agrees,
            }
        )
    matched.sort(key=lambda entry: int(entry["id"]))
    summary = {
        "policy": {
            "matching_source_hash_is_translation_memory_only": True,
            "automatic_reuse_permitted": False,
            "independent_sc_jp_en_tc_coordinate_context_reviewed": True,
        },
        "summary": {
            "selected_coordinate_count": TRANSLATED_COUNT,
            "matching_source_hash_coordinate_count": len(matched),
            "matching_reference_entry_count": sum(int(entry["candidate_entry_count"]) for entry in matched),
            "exact_agreement_after_independent_review_count": exact_agreement_count,
            "automatic_reuse_count": 0,
        },
        "matched_coordinates": matched,
    }
    if summary["summary"] != {
        "selected_coordinate_count": 94,
        "matching_source_hash_coordinate_count": 3,
        "matching_reference_entry_count": 3,
        "exact_agreement_after_independent_review_count": 3,
        "automatic_reuse_count": 0,
    }:
        raise MsgdataBatch2Error("translation-memory review summary changed")
    return summary


def _overlay_ids(overlay: dict[str, Any]) -> list[int]:
    return [int(entry["id"]) for entry in overlay["entries"]]


def validate_overlay_shape(overlay: dict[str, Any]) -> None:
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE or overlay["overlay_id"] != BATCH_ID:
        raise MsgdataBatch2Error("overlay identity changed")
    if overlay["entry_count"] != TRANSLATED_COUNT or _overlay_ids(overlay) != selected_ids():
        raise MsgdataBatch2Error("overlay scope changed")
    if len(entries) != TRANSLATED_COUNT:
        raise MsgdataBatch2Error("overlay entry count changed")


def apply_overlay_blob(packed: bytes, overlay: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    """Apply this source-free overlay in memory without touching game files."""
    validate_overlay_shape(overlay)
    _wrapper, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    expected_stock = {
        "size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": table.string_count,
    }
    if overlay["stock_sc"] != expected_stock:
        raise MsgdataBatch2Error("overlay stock SC fingerprint mismatch")
    texts = list(table.texts)
    for entry in overlay["entries"]:
        entry_id = int(entry["id"])
        source = texts[entry_id]
        if common.text_hash(source) != entry["source_sc_utf16le_sha256"]:
            raise MsgdataBatch2Error(f"source hash mismatch at ID {entry_id}")
        failures = invariant_failures(source, str(entry["ko"]))
        if failures:
            raise MsgdataBatch2Error(f"replacement invariants failed at ID {entry_id}: {failures}")
        texts[entry_id] = str(entry["ko"])
    rebuilt_raw = rebuild_message_table(table, texts)
    rebuilt = recompress_wrapper(rebuilt_raw, packed)
    _check_wrapper, check_raw = decompress_wrapper(rebuilt)
    check = parse_message_table(check_raw)
    if check.texts != tuple(texts):
        raise MsgdataBatch2Error("rebuilt target table does not match selected replacements")
    return rebuilt, {
        "target_packed_sha256": sha256(rebuilt),
        "target_packed_size": len(rebuilt),
        "target_raw_sha256": sha256(rebuilt_raw),
        "target_raw_size": len(rebuilt_raw),
        "changed_entry_count": sum(
            table.texts[entry_id] != texts[entry_id] for entry_id in selected_ids()
        ),
        "complete_target_included": False,
        "installed_game_file_written": False,
    }


def _assert_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    results: dict[str, dict[str, int]] = {}
    expected = {"cjk_unified_count": 0, "kana_count": 0, "embedded_nul_count": 0}
    for path in paths:
        counts = public_script_counts(path.read_bytes())
        if counts != expected:
            raise MsgdataBatch2Error(f"source script leaked into generated artifact: {path.name}")
        results[path.name] = counts
    return results


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    validate_static_scope()
    sources_before = source_snapshot(game_root)
    loaded = {language: load_resource(game_root, language) for language in LANGUAGES}
    tables = {language: loaded[language]["table"] for language in LANGUAGES}
    for entry_id in selected_ids():
        if any(not tables[language].texts[entry_id].strip() for language in LANGUAGES):
            raise MsgdataBatch2Error(f"selected ID is empty in an alignment language: {entry_id}")
    exclusion, existing_records = existing_overlay_snapshot(game_root)
    memory_review = translation_memory_review(tables["SC"], existing_records)

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    invariant_errors: list[dict[str, Any]] = []
    for entry_id in selected_ids():
        source = tables["SC"].texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        failures = invariant_failures(source, replacement)
        if failures:
            invariant_errors.append({"id": entry_id, "failures": failures})
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "group_id": group_for(entry_id),
                "references": {
                    language: source_structure(tables[language].texts[entry_id])
                    for language in LANGUAGES
                },
                "manual_semantic_crosscheck": True,
            }
        )
    if invariant_errors:
        raise MsgdataBatch2Error(f"translation invariant errors: {invariant_errors}")

    sc = loaded["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc["packed"]),
            "packed_sha256": sha256(sc["packed"]),
            "raw_size": len(sc["raw"]),
            "raw_sha256": sha256(sc["raw"]),
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    validate_overlay_shape(overlay)
    target_a, target_a_info = apply_overlay_blob(sc["packed"], overlay)
    target_b, target_b_info = apply_overlay_blob(sc["packed"], overlay)
    if target_a != target_b or target_a_info != target_b_info:
        raise MsgdataBatch2Error("independent SC target reconstructions differ")
    _target_wrapper, target_raw = decompress_wrapper(target_a)
    target_table = parse_message_table(target_raw)
    replacements = {entry_id: TRANSLATIONS[entry_id] for entry_id in selected_ids()}
    for entry_id, source in enumerate(tables["SC"].texts):
        expected = replacements.get(entry_id, source)
        if target_table.texts[entry_id] != expected:
            raise MsgdataBatch2Error(f"reconstructed target mismatch at ID {entry_id}")
    if target_a_info["changed_entry_count"] != TRANSLATED_COUNT:
        raise MsgdataBatch2Error("not every selected entry changed")

    evidence = {
        "schema": "nobu16.kr.msgdata-name-component-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_entry_count": TRANSLATED_COUNT,
            "next_contiguous_id": SUCCESSOR_BLOCKED_ID,
            "next_contiguous_id_blocked_by_existing_overlay": True,
        },
        "alignment_basis": [
            "same_msgdata_resource_role",
            "same_29210_entry_count",
            "same_numeric_string_coordinates",
            "sc_jp_en_tc_all_nonempty_for_selected_coordinates",
            "manual_semantic_crosscheck_of_selected_coordinates",
        ],
        "source_files": {
            language: {**RESOURCE_PINS[language], "string_count": STRING_COUNT}
            for language in LANGUAGES
        },
        "groups": list(GROUPS),
        "existing_overlay_coordinate_exclusion": exclusion,
        "cross_resource_translation_memory_review": memory_review,
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(tables[language].texts[entry_id])
                    for language in LANGUAGES
                },
            }
            for entry_id in (3221, 3222, 3315)
        ],
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msgdata-name-component-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_pending_human_and_runtime_review",
        "entry_count": TRANSLATED_COUNT,
        "entries": [
            {
                "id": entry_id,
                "group_id": group_for(entry_id),
                "status": "translated",
                "translation_origin": "independent_sc_jp_en_tc_coordinate_review",
                "automatic_cross_resource_reuse": False,
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": UNCERTAINTY_FLAGS.get(entry_id, []),
            }
            for entry_id in selected_ids()
        ],
        "contains_commercial_source_text": False,
    }

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts = {
        "overlay": write_json(out_root, overlay_path, overlay),
        "alignment_evidence": write_json(out_root, evidence_path, evidence),
        "review_index": write_json(out_root, review_path, review),
    }
    source_free_scan = _assert_source_free((overlay_path, evidence_path, review_path))
    sources_after = source_snapshot(game_root)
    if sources_before != sources_after:
        raise MsgdataBatch2Error("installed PK msgdata source changed while building")

    validation = {
        "schema": "nobu16.kr.msgdata-name-component-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_entry_count": TRANSLATED_COUNT,
            "selected_ids_sha256": hash_json(selected_ids()),
            "next_contiguous_id": SUCCESSOR_BLOCKED_ID,
            "next_contiguous_id_blocked_by_existing_overlay": True,
        },
        "existing_overlay_coordinate_exclusion": exclusion,
        "cross_resource_translation_memory_review": memory_review,
        "source_alignment": {
            "languages": list(LANGUAGES),
            "string_count_each": STRING_COUNT,
            "selected_reference_hash_count": TRANSLATED_COUNT * len(LANGUAGES),
            "all_selected_coordinates_nonempty_in_every_language": True,
            "manual_semantic_crosschecks": TRANSLATED_COUNT,
        },
        "replacement_invariants": {
            "checked": TRANSLATED_COUNT,
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
                "bracket_placeholder_sequence",
            ],
        },
        "reconstruction": {
            "source_parse_rebuild_byte_identical": {language: True for language in LANGUAGES},
            "sc_overlay_rebuild_a_b_byte_identical": True,
            "changed_entry_count": target_a_info["changed_entry_count"],
            "unselected_entries_preserved": True,
            "target": target_a_info,
        },
        "source_free_scan": source_free_scan,
        "translation_status": {
            "translated_draft": TRANSLATED_COUNT,
            "human_review_required": TRANSLATED_COUNT,
            "runtime_reviewed": 0,
            "specific_uncertainty_entries": len(UNCERTAINTY_FLAGS),
        },
        "safety": {
            "installed_game_files_modified": False,
            "other_workstream_modified": False,
            "global_progress_modified": False,
            "deployment_artifacts_modified": False,
            "commit_or_push_performed": False,
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
        },
        "installed_msgdata_before": sources_before,
        "installed_msgdata_after": sources_after,
        "artifacts": artifacts,
    }
    validation_path = out_root / VALIDATION_NAME
    artifacts["generation_validation"] = write_json(out_root, validation_path, validation)
    _assert_source_free((validation_path,))
    return {
        "entry_count": TRANSLATED_COUNT,
        "next_contiguous_id": SUCCESSOR_BLOCKED_ID,
        "target_packed_sha256": target_a_info["target_packed_sha256"],
        "artifacts": artifacts,
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    sources_before = source_snapshot(game_root)
    with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b02-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b02-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["target_packed_sha256"] != second["target_packed_sha256"]:
                raise MsgdataBatch2Error("isolated A/B target blobs differ")
            first_hashes = {name: artifact["sha256"] for name, artifact in first["artifacts"].items()}
            second_hashes = {name: artifact["sha256"] for name, artifact in second["artifacts"].items()}
            if first_hashes != second_hashes:
                raise MsgdataBatch2Error("isolated A/B public artifacts differ")
    final = build_once(game_root, out_root)
    if final["target_packed_sha256"] != first["target_packed_sha256"]:
        raise MsgdataBatch2Error("final target differs from isolated build")
    for name, artifact in final["artifacts"].items():
        if artifact["sha256"] != first["artifacts"][name]["sha256"]:
            raise MsgdataBatch2Error(f"final artifact differs from isolated build: {name}")
    if source_snapshot(game_root) != sources_before:
        raise MsgdataBatch2Error("installed PK msgdata source changed across build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=WORKSPACE_ROOT)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"entries={result['entry_count']}")
    print(f"next_contiguous_id={result['next_contiguous_id']}")
    print(f"target_packed_sha256={result['target_packed_sha256']}")
    for name, artifact in sorted(result["artifacts"].items()):
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
