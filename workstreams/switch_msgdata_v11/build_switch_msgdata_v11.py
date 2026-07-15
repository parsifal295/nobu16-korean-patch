#!/usr/bin/env python3
"""Strictly transfer convergent Switch v1.1 Korean strings into PK msgdata."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
PATCH_ROOT = SCRIPT_PATH.parents[2]
TOOLS_DIR = PATCH_ROOT / "tools"
STRDATA_WORKSTREAM_DIR = PATCH_ROOT / "workstreams" / "strdata"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(STRDATA_WORKSTREAM_DIR))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_format import (  # noqa: E402
    EXPECTED_SLOT_COUNTS,
    coordinate_texts,
    parse_raw_strdata,
    rebuild_raw_strdata,
)


BATCH_ID = "switch_v11_msgdata_strict_transfer.v0.1"
OVERLAY_NAME = "msgdata_ko_switch_v11_strict_transfer.v0.1.json"
SELF_OVERLAY_LOGICAL_PATH = f"workstreams/switch_msgdata_v11/public/{OVERLAY_NAME}"
EVIDENCE_NAME = "switch_v11_msgdata_alignment_evidence.v0.1.json"
REVIEW_NAME = "switch_v11_msgdata_review_index.v0.1.json"
VALIDATION_NAME = "switch_v11_msgdata_validation.v0.1.json"
RESOURCE = "MSG_PK/SC/msgdata.bin"
STRING_COUNT = 29_210
EXPECTED_SELECTED_COUNT = 16_176
EXPECTED_SELECTED_IDS_SHA256 = "B8AC5996A1D9A6231E8A22AC130C077E0F11830F181FF66FA5FB6929C6FB34BB"
EXPECTED_CONVERGENT_PK_JP_CANDIDATE_COUNT = 20_807
EXPECTED_SOURCE_SCRIPT_EXCLUSION_COUNT = 8
SWITCH_ARCHIVE_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/strdata.bin"
SWITCH_README_MEMBER = "NobunagaShinsei_KR/README.md"

SOURCE_RELEASE = {
    "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
    "release_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1",
    "tag": "v1.1",
    "published_at": "2026-07-14T14:13:23Z",
    "author_attribution": "GitHub user snake7594",
    "archive_member": SWITCH_ARCHIVE_MEMBER,
    "archive_readme_member": SWITCH_README_MEMBER,
    "archive_contains_complete_game_resource": False,
}

ARCHIVE_PIN = {
    "size": 73_040_529,
    "sha256": "931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6",
}
SWITCH_MEMBER_PIN = {
    "size": 404_189,
    "sha256": "5F065B9DBDAE4DC75E2D7186A76C0AC988FB504F018F820C204262BF07D5061B",
    "raw_size": 953_512,
    "raw_sha256": "245538466576E3880B3C53C0CB4929685096DF394C27CCB93B2C893615A46ADE",
}
SWITCH_README_PIN = {
    "size": 2_080,
    "sha256": "F46BB5414BFD2BBA3A739DB9900B696A008CE85718A38B3802B89DB9758064F4",
}
BASE_JP_STRDATA_PIN = {
    "logical_path": "MSG/JP/strdata.bin",
    "size": 507_054,
    "sha256": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "raw_size": 763_928,
    "raw_sha256": "EAB14063C2060CE11794232F483F0B2210B3BD58118165CBEEC2F37176C25649",
}
PK_JP_MSGDATA_PIN = {
    "logical_path": "MSG_PK/JP/msgdata.bin",
    "size": 273_734,
    "sha256": "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38",
    "raw_size": 431_044,
    "raw_sha256": "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0",
}
PK_SC_MSGDATA_PIN = {
    "logical_path": RESOURCE,
    "size": 516_796,
    "sha256": "DFFC1FA9E8D175085568C14A407B9CB4BE81CF1416DA4485A64CA330D908ADA5",
    "raw_size": 514_752,
    "raw_sha256": "5982D520BF2E66260943DE61D0CB7F1135D1BA81A211E917E3F426C58D9125D6",
}

CJK_UNIFIED_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def ids_sha256(ids: list[int]) -> str:
    return sha256(json.dumps(ids, separators=(",", ":")).encode("utf-8"))


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any, relative_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": relative_path, "size": len(blob), "sha256": sha256(blob)}


def script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": len(CJK_UNIFIED_RE.findall(text)),
        "kana_count": len(KANA_RE.findall(text)),
    }


def has_meaningful_hangul(text: str) -> bool:
    return bool(HANGUL_RE.search(text)) and common.has_semantic_text(text)


def source_script_free(text: str) -> bool:
    return script_counts(text) == {"cjk_unified_count": 0, "kana_count": 0}


def _validate_blob(blob: bytes, pin: dict[str, Any], label: str) -> None:
    if len(blob) != int(pin["size"]):
        raise ValueError(f"{label} size={len(blob)}, expected={pin['size']}")
    actual_hash = sha256(blob)
    if actual_hash != pin["sha256"]:
        raise ValueError(f"{label} SHA-256={actual_hash}, expected={pin['sha256']}")


def _load_pinned_wrapper(path: Path, pin: dict[str, Any], label: str) -> tuple[bytes, bytes]:
    packed = path.read_bytes()
    _validate_blob(packed, pin, label)
    _, raw = decompress_wrapper(packed)
    if len(raw) != int(pin["raw_size"]):
        raise ValueError(f"{label} raw size={len(raw)}, expected={pin['raw_size']}")
    raw_hash = sha256(raw)
    if raw_hash != pin["raw_sha256"]:
        raise ValueError(f"{label} raw SHA-256={raw_hash}, expected={pin['raw_sha256']}")
    return packed, raw


def _strdata_layout(archive: Any) -> list[dict[str, Any]]:
    return [
        {
            "block_id": block.block_id,
            "slot_count": block.slot_count,
            "inner_header_sha256": sha256(block.inner_header),
        }
        for block in archive.blocks
    ]


def _load_switch_archive(archive_path: Path) -> tuple[bytes, bytes, Any, dict[str, Any]]:
    archive_blob = archive_path.read_bytes()
    _validate_blob(archive_blob, ARCHIVE_PIN, "Switch v1.1 archive")
    with zipfile.ZipFile(archive_path) as archive:
        member_info = archive.getinfo(SWITCH_ARCHIVE_MEMBER)
        readme_info = archive.getinfo(SWITCH_README_MEMBER)
        if member_info.flag_bits & 0x1 or readme_info.flag_bits & 0x1:
            raise ValueError("Switch archive members must not be encrypted")
        packed = archive.read(SWITCH_ARCHIVE_MEMBER)
        readme_blob = archive.read(SWITCH_README_MEMBER)
    _validate_blob(packed, SWITCH_MEMBER_PIN, "Switch strdata member")
    if len(readme_blob) != SWITCH_README_PIN["size"] or sha256(readme_blob) != SWITCH_README_PIN["sha256"]:
        raise ValueError("Switch archive README member does not match its pin")
    _, raw = decompress_wrapper(packed)
    if len(raw) != SWITCH_MEMBER_PIN["raw_size"] or sha256(raw) != SWITCH_MEMBER_PIN["raw_sha256"]:
        raise ValueError("Switch strdata raw payload does not match its pin")
    parsed = parse_raw_strdata(raw)
    if tuple(block.slot_count for block in parsed.blocks) != EXPECTED_SLOT_COUNTS:
        raise ValueError("Switch strdata block slot layout differs")
    if rebuild_raw_strdata(parsed) != raw:
        raise ValueError("Switch strdata parse/rebuild is not byte-identical")
    provenance = {
        **SOURCE_RELEASE,
        "archive_size": len(archive_blob),
        "archive_sha256": sha256(archive_blob),
        "member_size": len(packed),
        "member_sha256": sha256(packed),
        "member_raw_size": len(raw),
        "member_raw_sha256": sha256(raw),
        "readme_size": len(readme_blob),
        "readme_sha256": sha256(readme_blob),
        "block_layout": _strdata_layout(parsed),
    }
    return packed, raw, parsed, provenance


def _load_base_jp_strdata(path: Path) -> tuple[bytes, bytes, Any]:
    packed, raw = _load_pinned_wrapper(path, BASE_JP_STRDATA_PIN, "PC base JP strdata")
    parsed = parse_raw_strdata(raw)
    if tuple(block.slot_count for block in parsed.blocks) != EXPECTED_SLOT_COUNTS:
        raise ValueError("PC base JP strdata block slot layout differs")
    if rebuild_raw_strdata(parsed) != raw:
        raise ValueError("PC base JP strdata parse/rebuild is not byte-identical")
    return packed, raw, parsed


def _load_pk_msgdata(path: Path, pin: dict[str, Any], label: str) -> tuple[bytes, bytes, Any]:
    packed, raw = _load_pinned_wrapper(path, pin, label)
    table = parse_message_table(raw)
    if table.string_count != STRING_COUNT:
        raise ValueError(f"{label} strings={table.string_count}, expected={STRING_COUNT}")
    if rebuild_message_table(table, table.texts) != raw:
        raise ValueError(f"{label} parse/rebuild is not byte-identical")
    return packed, raw, table


def load_existing_overlay_coordinates(progress_path: Path) -> tuple[set[int], dict[str, Any]]:
    progress, progress_blob = common.load_json_strict(progress_path)
    resources = progress.get("resources")
    if not isinstance(resources, list):
        raise ValueError("translation progress has no resources array")
    matches = [resource for resource in resources if resource.get("path") == RESOURCE]
    if len(matches) != 1:
        raise ValueError("translation progress must contain exactly one PK msgdata resource")
    overlay_globs = matches[0].get("overlay_globs")
    if not isinstance(overlay_globs, list) or not all(isinstance(pattern, str) for pattern in overlay_globs):
        raise ValueError("PK msgdata overlay_globs are invalid")
    if overlay_globs.count(SELF_OVERLAY_LOGICAL_PATH) != 1:
        raise ValueError(
            "translation progress must register this Switch msgdata overlay exactly once"
        )

    claimed: set[int] = set()
    authored_ids: list[int] = []
    overlays: list[dict[str, Any]] = []
    prior_overlay_globs: list[str] = []
    self_registration: dict[str, Any] | None = None
    for pattern in overlay_globs:
        paths = sorted(PATCH_ROOT.glob(pattern))
        if len(paths) != 1:
            raise ValueError(f"overlay glob {pattern!r} resolved to {len(paths)} files")
        path = paths[0]
        overlay, blob = common.load_json_strict(path)
        target = overlay.get("target")
        resource = overlay.get("resource")
        if resource is None and isinstance(target, dict):
            resource = target.get("resource")
        if resource != RESOURCE:
            raise ValueError(f"existing overlay {path.name} targets {resource}, not {RESOURCE}")
        entries = overlay.get("entries")
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"existing overlay {path.name} has no nonempty entries array")
        if any(not isinstance(entry, dict) or type(entry.get("id")) is not int for entry in entries):
            raise ValueError(f"existing overlay {path.name} has an invalid entry id")
        ids = [int(entry["id"]) for entry in entries]
        declared_count = overlay.get("entry_count")
        if declared_count is None and isinstance(target, dict):
            declared_count = target.get("entry_count")
        if declared_count is not None and (type(declared_count) is not int or declared_count != len(ids)):
            raise ValueError(f"existing overlay {path.name} entry count differs")
        logical_path = path.relative_to(PATCH_ROOT).as_posix()
        is_self = logical_path == SELF_OVERLAY_LOGICAL_PATH
        if is_self and pattern != SELF_OVERLAY_LOGICAL_PATH:
            raise ValueError(
                "this Switch msgdata overlay must be registered by its exact logical path"
            )
        if is_self:
            if overlay.get("overlay_id") != BATCH_ID:
                raise ValueError("self overlay registration has an unexpected overlay_id")
            if len(ids) != EXPECTED_SELECTED_COUNT:
                raise ValueError("self overlay registration entry count differs from the v1.1 pin")
            if ids_sha256(sorted(ids)) != EXPECTED_SELECTED_IDS_SHA256:
                raise ValueError("self overlay registration ID set differs from the v1.1 pin")
            if self_registration is not None:
                raise ValueError("translation progress resolved this Switch msgdata overlay more than once")
            self_registration = {
                "logical_path": logical_path,
                "sha256": sha256(blob),
                "entry_count": len(ids),
                "ids_sha256": ids_sha256(sorted(ids)),
                "configured_exactly_once": True,
                "excluded_from_prior_claims": True,
            }
            continue
        claimed.update(ids)
        authored_ids.extend(ids)
        prior_overlay_globs.append(pattern)
        overlays.append(
            {
                "logical_path": logical_path,
                "sha256": sha256(blob),
                "entry_count": len(ids),
                "min_id": min(ids),
                "max_id": max(ids),
            }
        )
    if self_registration is None:
        raise ValueError("translation progress did not resolve this Switch msgdata overlay")
    snapshot = {
        "progress_logical_path": progress_path.relative_to(PATCH_ROOT).as_posix(),
        "progress_sha256": sha256(progress_blob),
        "overlay_globs": overlay_globs,
        "prior_overlay_globs": prior_overlay_globs,
        "self_overlay_registration": self_registration,
        "overlays": overlays,
        "total_authored_entry_count": len(authored_ids),
        "effective_unique_coordinate_count": len(claimed),
        "cross_overlay_duplicate_coordinate_count": len(authored_ids) - len(claimed),
        "effective_coordinate_ids_sha256": ids_sha256(sorted(claimed)),
    }
    return claimed, snapshot


def build_jp_hash_reverse_index(base_archive: Any, switch_archive: Any) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    if len(base_archive.blocks) != len(switch_archive.blocks):
        raise ValueError("base and Switch strdata block counts differ")
    index: dict[str, dict[str, Any]] = {}
    for base_block, switch_block in zip(base_archive.blocks, switch_archive.blocks, strict=True):
        if base_block.block_id != switch_block.block_id or base_block.slot_count != switch_block.slot_count:
            raise ValueError("base and Switch strdata coordinate structures differ")
        for slot_id, (jp, ko) in enumerate(zip(base_block.texts, switch_block.texts, strict=True)):
            jp_hash = common.text_hash(jp)
            record = index.setdefault(
                jp_hash,
                {"jp": jp, "coordinates": [], "switch_ko": []},
            )
            if record["jp"] != jp:
                raise ValueError("SHA-256 collision in base JP reverse index")
            record["coordinates"].append((base_block.block_id, slot_id))
            record["switch_ko"].append(ko)

    convergent = 0
    ambiguous = 0
    no_meaningful_korean = 0
    for record in index.values():
        jp = str(record["jp"])
        switch_values = list(record["switch_ko"])
        valid_values = {
            ko
            for ko in switch_values
            if ko != jp and has_meaningful_hangul(ko)
        }
        all_valid = len(valid_values) > 0 and all(
            ko != jp and has_meaningful_hangul(ko) for ko in switch_values
        )
        record["candidate_ko"] = next(iter(valid_values)) if all_valid and len(valid_values) == 1 else None
        record["coordinate_count"] = len(record["coordinates"])
        record["coordinate_ids_sha256"] = sha256(
            json.dumps(record["coordinates"], separators=(",", ":")).encode("utf-8")
        )
        if record["candidate_ko"] is not None:
            convergent += 1
        elif valid_values:
            ambiguous += 1
        else:
            no_meaningful_korean += 1
    return index, {
        "base_total_coordinate_count": sum(block.slot_count for block in base_archive.blocks),
        "base_unique_jp_hash_count": len(index),
        "convergent_korean_hash_count": convergent,
        "ambiguous_korean_hash_count": ambiguous,
        "no_meaningful_korean_hash_count": no_meaningful_korean,
        "reverse_index_key": "base_jp_utf16le_sha256",
        "complete_match_policy": "hash_lookup_then_in_memory_exact_jp_string_equality",
        "convergence_policy": "all_base_coordinates_for_hash_have_meaningful_hangul_ko_distinct_from_jp_and_exactly_one_ko_value",
    }


def derive_strict_entries(
    pk_jp: Any,
    pk_sc: Any,
    reverse_index: dict[str, dict[str, Any]],
    claimed_ids: set[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    selected_ids: list[int] = []
    source_script_ids: list[int] = []
    invariant_ids: list[int] = []
    collision_ids: list[int] = []
    unchanged_sc_ids: list[int] = []
    invariant_histogram: dict[str, int] = {}
    target_jp_hash_match_count = 0
    convergent_candidate_count = 0

    for entry_id, (jp, sc) in enumerate(zip(pk_jp.texts, pk_sc.texts, strict=True)):
        jp_hash = common.text_hash(jp)
        record = reverse_index.get(jp_hash)
        if record is None or record["jp"] != jp:
            continue
        target_jp_hash_match_count += 1
        ko = record["candidate_ko"]
        if ko is None:
            continue
        convergent_candidate_count += 1
        if entry_id in claimed_ids:
            collision_ids.append(entry_id)
            continue
        imported_counts = script_counts(ko)
        if imported_counts != {"cjk_unified_count": 0, "kana_count": 0}:
            source_script_ids.append(entry_id)
            continue
        problems = common.invariant_mismatches(sc, ko)
        if problems:
            invariant_ids.append(entry_id)
            for problem in problems:
                key = problem.split(":", 1)[0]
                invariant_histogram[key] = invariant_histogram.get(key, 0) + 1
            continue
        if ko == sc:
            unchanged_sc_ids.append(entry_id)
            continue
        selected_ids.append(entry_id)
        sc_hash = common.text_hash(sc)
        ko_hash = common.text_hash(ko)
        entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": sc_hash,
                "ko": ko,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "pk_jp_utf16le_sha256": jp_hash,
                "pk_sc_utf16le_sha256": sc_hash,
                "switch_ko_utf16le_sha256": ko_hash,
                "base_jp_coordinate_count": record["coordinate_count"],
                "base_jp_coordinate_ids_sha256": record["coordinate_ids_sha256"],
                "jp_complete_match": True,
                "korean_hash_converged": True,
                "source_script_free": True,
                "pk_sc_invariants_preserved": True,
            }
        )

    stats = {
        "pk_total_slot_count": pk_jp.string_count,
        "pk_jp_complete_hash_match_count": target_jp_hash_match_count,
        "convergent_pk_jp_candidate_count": convergent_candidate_count,
        "existing_overlay_collision_count": len(collision_ids),
        "existing_overlay_collision_ids_sha256": ids_sha256(collision_ids),
        "source_script_exclusion": {
            "count": len(source_script_ids),
            "ids": source_script_ids,
            "ids_sha256": ids_sha256(source_script_ids),
            "reason": "switch_korean_contains_cjk_unified_or_kana",
            "policy": "pc_korean_font_compatibility_and_source_free_output",
        },
        "pk_sc_invariant_exclusion_count": len(invariant_ids),
        "pk_sc_invariant_exclusion_ids_sha256": ids_sha256(invariant_ids),
        "pk_sc_invariant_mismatch_histogram": dict(sorted(invariant_histogram.items())),
        "unchanged_sc_exclusion_count": len(unchanged_sc_ids),
        "selected_entry_count": len(entries),
        "selected_ids_sha256": ids_sha256(selected_ids),
    }
    if [entry["id"] for entry in entries] != selected_ids:
        raise ValueError("strict transfer entry ordering differs")
    return entries, evidence_entries, stats


def reconstruct_sc_target(sc_packed: bytes, sc_table: Any, entries: list[dict[str, Any]]) -> dict[str, Any]:
    texts = list(sc_table.texts)
    for entry in entries:
        entry_id = int(entry["id"])
        if common.text_hash(texts[entry_id]) != entry["source_sc_utf16le_sha256"]:
            raise ValueError(f"SC source hash changed before reconstruction at id {entry_id}")
        texts[entry_id] = str(entry["ko"])
    rebuilt_raw = rebuild_message_table(sc_table, texts)
    rebuilt_table = parse_message_table(rebuilt_raw)
    if rebuilt_table.texts != tuple(texts):
        raise ValueError("translated PK SC msgdata parse/rebuild differs")
    rebuilt_packed = recompress_wrapper(rebuilt_raw, sc_packed)
    _, round_trip_raw = decompress_wrapper(rebuilt_packed)
    if round_trip_raw != rebuilt_raw:
        raise ValueError("translated PK SC msgdata wrapper round-trip differs")
    return {
        "resource": RESOURCE,
        "entry_count": len(entries),
        "complete_target_included": False,
        "packed_size": len(rebuilt_packed),
        "packed_sha256": sha256(rebuilt_packed),
        "raw_size": len(rebuilt_raw),
        "raw_sha256": sha256(rebuilt_raw),
        "parse_rebuild_round_trip": True,
        "wrapper_round_trip": True,
    }


def input_snapshot(args: argparse.Namespace) -> dict[str, str]:
    return {
        "switch_archive": sha256(args.switch_zip.read_bytes()),
        "base_jp_strdata": sha256(args.base_jp_strdata.read_bytes()),
        "pk_jp_msgdata": sha256(args.stock_pk_jp.read_bytes()),
        "pk_sc_msgdata": sha256(args.stock_pk_sc.read_bytes()),
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    claimed_ids, prior_before = load_existing_overlay_coordinates(args.progress)
    input_before = input_snapshot(args)
    _, _, switch_archive, provenance = _load_switch_archive(args.switch_zip)
    _, _, base_jp_archive = _load_base_jp_strdata(args.base_jp_strdata)
    pk_jp_packed, _, pk_jp_table = _load_pk_msgdata(
        args.stock_pk_jp, PK_JP_MSGDATA_PIN, "PK JP msgdata"
    )
    pk_sc_packed, pk_sc_raw, pk_sc_table = _load_pk_msgdata(
        args.stock_pk_sc, PK_SC_MSGDATA_PIN, "PK SC msgdata"
    )
    if pk_jp_packed == pk_sc_packed:
        raise ValueError("PK JP and SC msgdata cannot be identical source wrappers")
    reverse_index, reverse_summary = build_jp_hash_reverse_index(base_jp_archive, switch_archive)
    entries, evidence_entries, selection = derive_strict_entries(
        pk_jp_table, pk_sc_table, reverse_index, claimed_ids
    )
    if selection["convergent_pk_jp_candidate_count"] != EXPECTED_CONVERGENT_PK_JP_CANDIDATE_COUNT:
        raise ValueError("strict convergent candidate count differs from the v1.1 pin")
    if selection["source_script_exclusion"]["count"] != EXPECTED_SOURCE_SCRIPT_EXCLUSION_COUNT:
        raise ValueError("source-script exclusion count differs from the v1.1 pin")
    if len(entries) != EXPECTED_SELECTED_COUNT:
        raise ValueError(f"strict selected count={len(entries)}, expected={EXPECTED_SELECTED_COUNT}")
    if selection["selected_ids_sha256"] != EXPECTED_SELECTED_IDS_SHA256:
        raise ValueError("strict selected ID set differs from the v1.1 pin")
    if set(entry["id"] for entry in entries).intersection(claimed_ids):
        raise ValueError("strict transfer overlaps a translation_progress msgdata overlay")
    if any(not source_script_free(str(entry["ko"])) for entry in entries):
        raise ValueError("strict transfer retained CJK unified or kana in Korean output")

    target_a = reconstruct_sc_target(pk_sc_packed, pk_sc_table, entries)
    target_b = reconstruct_sc_target(pk_sc_packed, pk_sc_table, entries)
    if target_a != target_b:
        raise ValueError("PK SC target reconstruction is not deterministic")

    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(pk_sc_packed),
            "packed_sha256": sha256(pk_sc_packed),
            "raw_size": len(pk_sc_raw),
            "raw_sha256": sha256(pk_sc_raw),
            "string_count": pk_sc_table.string_count,
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    common.validate_overlay_shape(overlay)

    evidence = {
        "schema": "nobu16.kr.switch-msgdata-v11-strict-transfer-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": "msgdata",
        "scope": {
            "selected_entry_count": len(entries),
            "selected_ids_sha256": selection["selected_ids_sha256"],
            "pk_string_count": STRING_COUNT,
        },
        "source_release": provenance,
        "base_jp_strdata": {
            **BASE_JP_STRDATA_PIN,
            "block_layout": _strdata_layout(base_jp_archive),
            "coordinate_count": sum(block.slot_count for block in base_jp_archive.blocks),
        },
        "structure_verification": {
            "expected_slot_counts": list(EXPECTED_SLOT_COUNTS),
            "switch_block_count": len(switch_archive.blocks),
            "base_jp_block_count": len(base_jp_archive.blocks),
            "switch_and_base_slot_counts_equal": [
                block.slot_count for block in switch_archive.blocks
            ]
            == [block.slot_count for block in base_jp_archive.blocks],
            "switch_parse_rebuild_byte_identical": True,
            "base_jp_parse_rebuild_byte_identical": True,
        },
        "pk_source_files": {
            "JP": {**PK_JP_MSGDATA_PIN, "string_count": pk_jp_table.string_count},
            "SC": {**PK_SC_MSGDATA_PIN, "string_count": pk_sc_table.string_count},
        },
        "matching_policy": {
            **reverse_summary,
            "switch_ko_eligibility": "contains_meaningful_hangul_and_is_distinct_from_base_jp",
            "target_eligibility": [
                "pk_jp_exactly_matches_a_base_jp_hash_and_text",
                "same_base_jp_hash_has_exactly_one_convergent_switch_korean_result",
                "id_is_not_claimed_by_prior_translation_progress_msgdata_overlay_globs",
                "this_switch_overlay_is_registered_exactly_once_but_excluded_from_prior_claims",
                "switch_korean_contains_no_cjk_unified_or_kana",
                "pk_sc_printf_esc_controls_linebreak_pua_and_edge_whitespace_invariants_match",
            ],
        },
        "selection": selection,
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    review = {
        "schema": "nobu16.kr.switch-msgdata-v11-strict-transfer-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "strict_external_transfer_not_human_or_runtime_reviewed",
        "entry_count": len(entries),
        "entries": [
            {
                "id": entry["id"],
                "status": "translated",
                "translation_origin": "switch_v1.1_hash_convergent_transfer",
                "strict_transfer": True,
                "source_script_free": True,
                "pk_sc_invariants_preserved": True,
                "human_review_required": True,
                "runtime_reviewed": False,
            }
            for entry in entries
        ],
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["overlay"] = write_json(out_root / "public" / OVERLAY_NAME, overlay, f"public/{OVERLAY_NAME}")
    artifacts["alignment_evidence"] = write_json(
        out_root / "evidence" / EVIDENCE_NAME, evidence, f"evidence/{EVIDENCE_NAME}"
    )
    artifacts["review_index"] = write_json(
        out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}"
    )
    public_paths = {
        "overlay": out_root / "public" / OVERLAY_NAME,
        "alignment_evidence": out_root / "evidence" / EVIDENCE_NAME,
        "review_index": out_root / "review" / REVIEW_NAME,
    }
    source_free_scan = {
        name: script_counts(path.read_text(encoding="utf-8")) for name, path in public_paths.items()
    }
    if any(counts != {"cjk_unified_count": 0, "kana_count": 0} for counts in source_free_scan.values()):
        raise ValueError("source-free artifact contains CJK unified or kana")

    prior_after = load_existing_overlay_coordinates(args.progress)[1]
    input_after = input_snapshot(args)
    if prior_before != prior_after:
        raise ValueError("translation_progress-referenced existing msgdata overlays changed during build")
    if input_before != input_after:
        raise ValueError("pinned Switch or game input changed during build")

    validation = {
        "schema": "nobu16.kr.switch-msgdata-v11-strict-transfer-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "source_release": provenance,
        "scope": {
            "selected_entry_count": len(entries),
            "expected_selected_entry_count": EXPECTED_SELECTED_COUNT,
            "selected_ids_sha256": selection["selected_ids_sha256"],
            "expected_selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        },
        "strict_selection": selection,
        "structure_verification": {
            "expected_slot_counts": list(EXPECTED_SLOT_COUNTS),
            "switch_and_base_slot_counts_equal": [
                block.slot_count for block in switch_archive.blocks
            ]
            == [block.slot_count for block in base_jp_archive.blocks],
            "switch_parse_rebuild_byte_identical": True,
            "base_jp_parse_rebuild_byte_identical": True,
        },
        "existing_overlay_exclusion": prior_before,
        "target_reconstruction": target_a,
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "target_a_b_equal": True,
        },
        "source_free_scan": source_free_scan,
        "safety": {
            "zip_included": False,
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "installed_game_files_modified": False,
            "global_progress_modified": False,
            "global_readme_modified": False,
            "commit_or_push_performed": False,
            "deployment_performed": False,
        },
        "input_snapshot_before": input_before,
        "input_snapshot_after": input_after,
        "artifacts": artifacts,
    }
    validation["source_free_scan"]["generation_validation"] = script_counts(
        encode_json(validation).decode("utf-8")
    )
    if validation["source_free_scan"]["generation_validation"] != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise ValueError("generation validation contains CJK unified or kana")
    artifacts["generation_validation"] = write_json(
        out_root / VALIDATION_NAME, validation, VALIDATION_NAME
    )
    return {"out_root": out_root, "entry_count": len(entries), "artifacts": artifacts}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--switch-zip",
        type=Path,
        default=PATCH_ROOT / "tmp" / "third_party_switch_v11" / "NobunagaShinsei_KoreanPatch_v1.1.zip",
    )
    parser.add_argument(
        "--base-jp-strdata", type=Path, default=WORKSPACE_ROOT / "MSG" / "JP" / "strdata.bin"
    )
    parser.add_argument(
        "--stock-pk-jp", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgdata.bin"
    )
    parser.add_argument(
        "--stock-pk-sc", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "SC" / "msgdata.bin"
    )
    parser.add_argument(
        "--progress", type=Path, default=PATCH_ROOT / "data" / "public" / "translation_progress.v0.1.json"
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
    print(f"entries={result['entry_count']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
