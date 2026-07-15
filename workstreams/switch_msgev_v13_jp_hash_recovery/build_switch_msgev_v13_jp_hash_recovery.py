#!/usr/bin/env python3
"""Recover 245 unclaimed PK msgev entries by exact Japanese-text mapping.

Switch v1.3 contains the same patched event-message member as v1.1.  The
earlier PC port intentionally used numeric-coordinate identity only.  This
builder handles the remaining safe case: an unclaimed, stock-visible PC PK
coordinate whose Japanese value has an exact hash and in-memory match in the
Switch-aligned base table, and whose matching coordinates converge on one
source-script-free Korean value.

Only a source-free overlay and audit metadata are emitted.  The Switch archive
and PC resources are read-only; no complete game resource is written.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
UPSTREAM_ROOT = REPO_ROOT / "workstreams" / "switch_msgev_v11"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(UPSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_switch_msgev_v11 as upstream  # noqa: E402


BATCH_ID = "switch-v13-pk-msgev-exact-jp-hash-recovery-245.v1"
OVERLAY_NAME = "msgev_ko_switch_v13_exact_jp_hash_recovery_245.v1.json"
EVIDENCE_NAME = "switch_v13_exact_jp_hash_recovery_alignment.v1.json"
REVIEW_NAME = "switch_v13_exact_jp_hash_recovery_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
RESOURCE = upstream.RESOURCE

SWITCH_ARCHIVE_RELATIVE = Path(
    "tmp/third_party_switch_v13/NobunagaShinsei_KoreanPatch_v1.3.zip"
)
SWITCH_ENTRY = upstream.SWITCH_ENTRY
SWITCH_RELEASE = {
    "title": "NobunagaShinsei Korean Patch",
    "platform": "Nintendo Switch",
    "release_tag": "v1.3",
    "release_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.3",
    "source_repository": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
    "author_account": "snake7594",
    "attribution": "snake7594_unofficial_fan_translation_v1_3",
    "archive_relative_path": SWITCH_ARCHIVE_RELATIVE.as_posix(),
    "archive_size": 72_977_145,
    "archive_sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
    "entry_path": SWITCH_ENTRY,
    "entry_crc32": "018EAC29",
    "entry_uncompressed_size": 396_257,
    "entry_compressed_size": 314_537,
}

V11_TEXT_MEMBER = {
    "release_tag": "v1.1",
    "packed_sha256": upstream.SOURCE_PINS["switch_ko"]["packed_sha256"],
    "raw_sha256": upstream.SOURCE_PINS["switch_ko"]["raw_sha256"],
    "string_count": upstream.SOURCE_PINS["switch_ko"]["string_count"],
}

OWNER_OVERLAYS = (
    {
        "path": Path(
            "workstreams/switch_msgev_v11/public/"
            "msgev_ko_switch_v11_ported_7025.v1.json"
        ),
        "sha256": "71652CACEB757BFFF47FB119789150BD841DD9FF6B6AC180D5B2AA1B06231703",
        "entry_count": 7_025,
        "ids_sha256": upstream.EXPECTED_SELECTED_IDS_SHA256,
    },
    {
        "path": Path(
            "workstreams/switch_msgev_v11_cjk_cleanup/public/"
            "msgev_ko_switch_v11_cjk_kana_cleanup_20.v1.json"
        ),
        "sha256": "2A2EE0488CCF6BB70DBBDA2B00A005821DB4CD5C5C8300E4A30F9DF52890295C",
        "entry_count": 20,
        "ids_sha256": "F9B2C54B499583605D1D8748747123DE1C4FF2C3C990383FD0E672DF8D7BCFDB",
    },
)

EXPECTED_EFFECTIVE_OWNER_COUNT = 12_514
EXPECTED_EFFECTIVE_OWNER_IDS_SHA256 = (
    "20DCD9904DF9BE289B697FDE9749FFBB4EC954E7C885C3CB3AE4794606BE2479"
)
EXPECTED_SELECTED_COUNT = 245
EXPECTED_SELECTED_IDS_SHA256 = (
    "92CB73170DB575A017400DCEB7FB79CB41FECB0DC6339F401BF594D6C424ACF4"
)
EXPECTED_STOCK_VISIBLE_COUNT = 12_906
EXPECTED_STOCK_VISIBLE_IDS_SHA256 = (
    "00D725442F097A6F369FC3AC662C753976EAA07C714FDF6F436A7EF8B62E7C89"
)
EXPECTED_EFFECTIVE_VISIBLE_OWNER_COUNT = 10_916
EXPECTED_UNCLAIMED_VISIBLE_COUNT = 1_990
EXPECTED_JP_HASH_BUCKET_MATCH_COUNT = 664
EXPECTED_JP_EXACT_MATCH_COUNT = 664
EXPECTED_UNIQUE_MEANINGFUL_KO_COUNT = 506
EXPECTED_SOURCE_SCRIPT_FREE_COUNT = 502
EXPECTED_SC_INVARIANT_MATCH_COUNT = 245
EXPECTED_BRACKET_TOKEN_MATCH_COUNT = 245

EXPECTED_NO_JP_MATCH_COUNT = 1_326
EXPECTED_NO_JP_MATCH_IDS_SHA256 = (
    "E91BFF36168AD21C71A5BE090E1D9D88AC8A19FBD4A5F3C967349EA0C0719813"
)
EXPECTED_NONUNIQUE_KO_COUNT = 158
EXPECTED_NONUNIQUE_KO_IDS_SHA256 = (
    "E6ED102357C08F682CE0B6CE4E02F196BD7EA50E1D80D5504C30037469567AF8"
)
EXPECTED_SOURCE_SCRIPT_EXCLUDED_COUNT = 4
EXPECTED_SOURCE_SCRIPT_EXCLUDED_IDS_SHA256 = (
    "BB969DF289D8AF7256C9EEF5B97211F4C16062D3394483FDFB893AD94BB87619"
)
EXPECTED_INVARIANT_EXCLUDED_COUNT = 257
EXPECTED_INVARIANT_EXCLUDED_IDS_SHA256 = (
    "8685192614BE873A49693441DB47B614582A4EC570745CF99CADE23CA13D6076"
)
EMPTY_LIST_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"

ACTIVATED_JP_ONLY_START = 14_799
ACTIVATED_JP_ONLY_END = 16_396
EXPECTED_ACTIVATED_JP_ONLY_COUNT = 1_598


class RecoveryError(ValueError):
    """Raised when a pinned recovery or safety condition fails."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def hash_json(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def source_free_counts(blob: bytes) -> dict[str, int]:
    return upstream.source_free_counts(blob)


def read_switch_v13_table(archive_path: Path) -> dict[str, Any]:
    archive_blob = archive_path.read_bytes()
    if len(archive_blob) != int(SWITCH_RELEASE["archive_size"]):
        raise RecoveryError("Switch v1.3 archive size does not match pin")
    if sha256(archive_blob) != str(SWITCH_RELEASE["archive_sha256"]):
        raise RecoveryError("Switch v1.3 archive SHA-256 does not match pin")
    with zipfile.ZipFile(archive_path) as archive:
        info = archive.getinfo(SWITCH_ENTRY)
        if f"{info.CRC:08X}" != SWITCH_RELEASE["entry_crc32"]:
            raise RecoveryError("Switch v1.3 event member CRC32 does not match pin")
        if info.file_size != int(SWITCH_RELEASE["entry_uncompressed_size"]):
            raise RecoveryError("Switch v1.3 event member size does not match pin")
        if info.compress_size != int(SWITCH_RELEASE["entry_compressed_size"]):
            raise RecoveryError(
                "Switch v1.3 event member compressed size does not match pin"
            )
        packed = archive.read(info)
    if sha256(packed) != V11_TEXT_MEMBER["packed_sha256"]:
        raise RecoveryError("Switch v1.3 event member is not byte-identical to v1.1")
    return upstream.load_pinned_table(
        "switch_v13_ko", packed, upstream.SOURCE_PINS["switch_ko"]
    )


def load_sources(
    game_root: Path, repo_root: Path, archive_path: Path
) -> dict[str, dict[str, Any]]:
    pins = upstream.SOURCE_PINS
    return {
        "switch_ko": read_switch_v13_table(archive_path),
        "base_jp": upstream.load_pinned_table(
            "base_jp",
            (game_root / pins["base_jp"]["logical_path"]).read_bytes(),
            pins["base_jp"],
        ),
        "pk_jp": upstream.load_pinned_table(
            "pk_jp",
            (game_root / pins["pk_jp"]["logical_path"]).read_bytes(),
            pins["pk_jp"],
        ),
        "pk_sc_stock": upstream.load_pinned_table(
            "pk_sc_stock",
            (repo_root / pins["pk_sc_stock"]["logical_path"]).read_bytes(),
            pins["pk_sc_stock"],
        ),
    }


def input_snapshot(
    game_root: Path, repo_root: Path, archive_path: Path
) -> dict[str, str]:
    pins = upstream.SOURCE_PINS
    paths = {
        "switch_v13_archive": archive_path,
        "base_jp": game_root / pins["base_jp"]["logical_path"],
        "pk_jp": game_root / pins["pk_jp"]["logical_path"],
        "pk_sc_stock": repo_root / pins["pk_sc_stock"]["logical_path"],
    }
    for index, descriptor in enumerate(OWNER_OVERLAYS):
        paths[f"owner_overlay_{index}"] = repo_root / descriptor["path"]
    return {name: sha256(path.read_bytes()) for name, path in paths.items()}


def load_owner_overlay(repo_root: Path, descriptor: dict[str, Any]) -> dict[str, Any]:
    path = repo_root / descriptor["path"]
    overlay, blob = common.load_json_strict(path)
    if sha256(blob) != descriptor["sha256"]:
        raise RecoveryError(f"owner overlay SHA-256 changed: {descriptor['path']}")
    resource, _stock, entries = common.validate_overlay_shape(overlay)
    if resource != RESOURCE:
        raise RecoveryError(f"owner overlay targets another resource: {descriptor['path']}")
    ids = [int(entry["id"]) for entry in entries]
    if len(ids) != int(descriptor["entry_count"]):
        raise RecoveryError(f"owner overlay count changed: {descriptor['path']}")
    if hash_json(ids) != descriptor["ids_sha256"]:
        raise RecoveryError(f"owner overlay IDs changed: {descriptor['path']}")
    return {
        "path": descriptor["path"].as_posix(),
        "sha256": sha256(blob),
        "entry_count": len(ids),
        "ids_sha256": hash_json(ids),
        "ids": ids,
    }


def effective_owner_catalog(repo_root: Path) -> dict[str, Any]:
    base = upstream.existing_msgev_catalog_snapshot(repo_root)
    rows = [load_owner_overlay(repo_root, descriptor) for descriptor in OWNER_OVERLAYS]
    owner_sets = [set(base["ids"])] + [set(row["ids"]) for row in rows]
    for index, left in enumerate(owner_sets):
        for right in owner_sets[index + 1 :]:
            if left & right:
                raise RecoveryError("effective owner catalogs overlap")
    ids = sorted(set().union(*owner_sets))
    if len(ids) != EXPECTED_EFFECTIVE_OWNER_COUNT:
        raise RecoveryError("effective owner count does not match pin")
    if hash_json(ids) != EXPECTED_EFFECTIVE_OWNER_IDS_SHA256:
        raise RecoveryError("effective owner IDs do not match pin")
    return {
        "unique_id_count": len(ids),
        "ids_sha256": hash_json(ids),
        "cross_catalog_overlap_count": 0,
        "prior_public_catalog": {key: value for key, value in base.items() if key != "ids"},
        "switch_owner_overlays": [
            {key: row[key] for key in ("path", "sha256", "entry_count", "ids_sha256")}
            for row in rows
        ],
        "ids": ids,
    }


def exact_jp_buckets(
    sources: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    base_jp = sources["base_jp"]["table"]
    switch_ko = sources["switch_ko"]["table"]
    if base_jp.string_count != switch_ko.string_count:
        raise RecoveryError("base JP and Switch Korean table counts differ")
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for coordinate, (jp_value, ko_value) in enumerate(
        zip(base_jp.texts, switch_ko.texts)
    ):
        buckets[common.text_hash(jp_value)].append(
            {"coordinate": coordinate, "jp": jp_value, "ko": ko_value}
        )
    return dict(buckets)


def resolve_unique_meaningful_ko(
    exact_rows: list[dict[str, Any]], jp_value: str
) -> str | None:
    """Return the sole semantic Korean value, or fail the gate with ``None``."""

    semantic_values = {
        str(row["ko"])
        for row in exact_rows
        if upstream.has_meaningful_hangul(str(row["ko"]))
        and str(row["ko"]) != jp_value
    }
    if len(semantic_values) != 1:
        return None
    return next(iter(semantic_values))


def select_recoverable_entries(
    sources: dict[str, dict[str, Any]],
    owners: dict[str, Any],
    repo_root: Path = REPO_ROOT,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pk_jp = sources["pk_jp"]["table"]
    pk_sc = sources["pk_sc_stock"]["table"]
    if pk_jp.string_count != pk_sc.string_count:
        raise RecoveryError("PK JP and pristine SC table counts differ")

    buckets = exact_jp_buckets(sources)
    owner_ids = set(owners["ids"])
    visible_ids = [
        coordinate
        for coordinate, value in enumerate(pk_sc.texts)
        if common.has_semantic_text(value)
    ]
    if len(visible_ids) != EXPECTED_STOCK_VISIBLE_COUNT:
        raise RecoveryError("pristine SC visible-target count changed")
    if hash_json(visible_ids) != EXPECTED_STOCK_VISIBLE_IDS_SHA256:
        raise RecoveryError("pristine SC visible-target IDs changed")

    activated_ids = list(range(ACTIVATED_JP_ONLY_START, ACTIVATED_JP_ONLY_END + 1))
    if len(activated_ids) != EXPECTED_ACTIVATED_JP_ONLY_COUNT:
        raise RecoveryError("activated JP-only range definition changed")
    strict_overlay_ids = set(
        load_owner_overlay(repo_root, OWNER_OVERLAYS[0])["ids"]
    )
    if not set(activated_ids).issubset(strict_overlay_ids):
        raise RecoveryError("activated JP-only range is not owned by strict predecessor")
    if any(common.has_semantic_text(pk_sc.texts[item]) for item in activated_ids):
        raise RecoveryError("activated JP-only range is no longer pristine-SC blank")
    claimed_blank_ids = sorted(
        coordinate
        for coordinate in owner_ids
        if not common.has_semantic_text(pk_sc.texts[coordinate])
    )
    if claimed_blank_ids != activated_ids:
        raise RecoveryError("effective blank-coordinate ownership changed")

    stages = {
        "pk_slot_count": pk_jp.string_count,
        "stock_visible_target_count": len(visible_ids),
        "effective_owner_count": len(owner_ids),
        "effective_visible_owner_count": sum(item in owner_ids for item in visible_ids),
        "activated_jp_only_claimed_count": len(claimed_blank_ids),
        "unclaimed_stock_visible_count": 0,
        "jp_hash_bucket_match_count": 0,
        "jp_exact_in_memory_match_count": 0,
        "unique_meaningful_switch_ko_count": 0,
        "source_script_free_count": 0,
        "sc_invariant_match_count": 0,
        "custom_bracket_token_match_count": 0,
        "selected_count": 0,
    }
    exclusions: dict[str, list[int]] = {
        "no_jp_match": [],
        "nonunique_meaningful_ko": [],
        "source_script": [],
        "sc_invariant": [],
        "bracket_token": [],
    }
    selected: list[dict[str, Any]] = []

    for coordinate in visible_ids:
        if coordinate in owner_ids:
            continue
        stages["unclaimed_stock_visible_count"] += 1
        jp_value = pk_jp.texts[coordinate]
        jp_hash = common.text_hash(jp_value)
        hash_rows = buckets.get(jp_hash, [])
        if not hash_rows:
            exclusions["no_jp_match"].append(coordinate)
            continue
        stages["jp_hash_bucket_match_count"] += 1
        exact_rows = [row for row in hash_rows if row["jp"] == jp_value]
        if not exact_rows:
            raise RecoveryError("Japanese UTF-16LE hash collision failed exact equality")
        if len(exact_rows) != len(hash_rows):
            raise RecoveryError("Japanese hash bucket contains mixed exact values")
        stages["jp_exact_in_memory_match_count"] += 1

        ko_value = resolve_unique_meaningful_ko(exact_rows, jp_value)
        if ko_value is None:
            exclusions["nonunique_meaningful_ko"].append(coordinate)
            continue
        stages["unique_meaningful_switch_ko_count"] += 1
        if upstream.contains_cjk_or_kana(ko_value):
            exclusions["source_script"].append(coordinate)
            continue
        stages["source_script_free_count"] += 1
        invariant_failures = common.invariant_mismatches(
            pk_sc.texts[coordinate], ko_value
        )
        if invariant_failures:
            exclusions["sc_invariant"].append(coordinate)
            continue
        stages["sc_invariant_match_count"] += 1
        if upstream.BRACKET_TOKEN_RE.findall(
            pk_sc.texts[coordinate]
        ) != upstream.BRACKET_TOKEN_RE.findall(ko_value):
            exclusions["bracket_token"].append(coordinate)
            continue
        stages["custom_bracket_token_match_count"] += 1
        source_coordinates = sorted(int(row["coordinate"]) for row in exact_rows)
        selected.append(
            {
                "id": coordinate,
                "ko": ko_value,
                "source_sc_utf16le_sha256": common.text_hash(pk_sc.texts[coordinate]),
                "jp_utf16le_sha256": jp_hash,
                "switch_ko_utf16le_sha256": common.text_hash(ko_value),
                "base_jp_coordinate_count": len(source_coordinates),
                "base_jp_coordinate_ids_sha256": hash_json(source_coordinates),
                "pk_sc_structure": upstream.source_structure(pk_sc.texts[coordinate]),
                "ported_ko_structure": upstream.source_structure(ko_value),
            }
        )

    stages["selected_count"] = len(selected)
    expected_stages = {
        "effective_visible_owner_count": EXPECTED_EFFECTIVE_VISIBLE_OWNER_COUNT,
        "activated_jp_only_claimed_count": EXPECTED_ACTIVATED_JP_ONLY_COUNT,
        "unclaimed_stock_visible_count": EXPECTED_UNCLAIMED_VISIBLE_COUNT,
        "jp_hash_bucket_match_count": EXPECTED_JP_HASH_BUCKET_MATCH_COUNT,
        "jp_exact_in_memory_match_count": EXPECTED_JP_EXACT_MATCH_COUNT,
        "unique_meaningful_switch_ko_count": EXPECTED_UNIQUE_MEANINGFUL_KO_COUNT,
        "source_script_free_count": EXPECTED_SOURCE_SCRIPT_FREE_COUNT,
        "sc_invariant_match_count": EXPECTED_SC_INVARIANT_MATCH_COUNT,
        "custom_bracket_token_match_count": EXPECTED_BRACKET_TOKEN_MATCH_COUNT,
        "selected_count": EXPECTED_SELECTED_COUNT,
    }
    for key, expected in expected_stages.items():
        if int(stages[key]) != expected:
            raise RecoveryError(f"selection stage {key} changed")

    expected_exclusions = {
        "no_jp_match": (EXPECTED_NO_JP_MATCH_COUNT, EXPECTED_NO_JP_MATCH_IDS_SHA256),
        "nonunique_meaningful_ko": (
            EXPECTED_NONUNIQUE_KO_COUNT,
            EXPECTED_NONUNIQUE_KO_IDS_SHA256,
        ),
        "source_script": (
            EXPECTED_SOURCE_SCRIPT_EXCLUDED_COUNT,
            EXPECTED_SOURCE_SCRIPT_EXCLUDED_IDS_SHA256,
        ),
        "sc_invariant": (
            EXPECTED_INVARIANT_EXCLUDED_COUNT,
            EXPECTED_INVARIANT_EXCLUDED_IDS_SHA256,
        ),
        "bracket_token": (0, EMPTY_LIST_SHA256),
    }
    for label, (expected_count, expected_hash) in expected_exclusions.items():
        ids = exclusions[label]
        if len(ids) != expected_count or hash_json(ids) != expected_hash:
            raise RecoveryError(f"selection exclusion set {label} changed")

    ids = [int(entry["id"]) for entry in selected]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise RecoveryError("selected IDs are not sorted and unique")
    if len(ids) != EXPECTED_SELECTED_COUNT:
        raise RecoveryError("selected recovery count does not match pin")
    if hash_json(ids) != EXPECTED_SELECTED_IDS_SHA256:
        raise RecoveryError("selected recovery IDs do not match pin")
    if set(ids) & owner_ids:
        raise RecoveryError("selected recovery IDs overlap an existing owner")
    if set(ids) & set(activated_ids):
        raise RecoveryError("selected recovery IDs overlap activated JP-only slots")
    if any(not common.has_semantic_text(pk_sc.texts[item]) for item in ids):
        raise RecoveryError("selected recovery includes a non-visible pristine SC slot")

    audit = {
        "stages": stages,
        "exclusions": {
            label: {"count": len(ids), "ids_sha256": hash_json(ids)}
            for label, ids in exclusions.items()
        },
        "stock_visible_ids_sha256": hash_json(visible_ids),
        "selected_ids_sha256": hash_json(ids),
        "selected_within_stock_visible_target": True,
        "selected_activated_jp_only_overlap_count": 0,
        "activated_jp_only_range": {
            "start": ACTIVATED_JP_ONLY_START,
            "end": ACTIVATED_JP_ONLY_END,
            "count": len(activated_ids),
            "ids_sha256": hash_json(activated_ids),
            "pristine_sc_visible_count": 0,
        },
    }
    return selected, audit


def artifact_metadata(relative: str, blob: bytes) -> dict[str, Any]:
    return {"path": relative, "size": len(blob), "sha256": sha256(blob)}


def build_once(
    game_root: Path, repo_root: Path, archive_path: Path, out_root: Path
) -> dict[str, Any]:
    before = input_snapshot(game_root, repo_root, archive_path)
    sources = load_sources(game_root, repo_root, archive_path)
    owners = effective_owner_catalog(repo_root)
    selected, selection = select_recoverable_entries(sources, owners, repo_root)
    ids = [int(entry["id"]) for entry in selected]
    target = upstream.reconstruct_pk_sc_target(sources["pk_sc_stock"], selected)

    source_pin = dict(upstream.SOURCE_PINS["switch_ko"])
    source_pin["logical_path"] = f"ZIP!/{SWITCH_ENTRY}"
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(selected),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            key: upstream.SOURCE_PINS["pk_sc_stock"][key]
            for key in (
                "size",
                "packed_sha256",
                "raw_size",
                "raw_sha256",
                "string_count",
            )
        },
        "defaults": {"status": "translated"},
        "entries": [
            {
                "id": int(entry["id"]),
                "source_sc_utf16le_sha256": entry["source_sc_utf16le_sha256"],
                "ko": entry["ko"],
            }
            for entry in selected
        ],
    }
    common.validate_overlay_shape(overlay)

    evidence = {
        "schema": "nobu16.kr.switch-msgev-v13-exact-jp-hash-recovery-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "source_release": SWITCH_RELEASE,
        "switch_text_identity": {
            "v13_member_packed_sha256": source_pin["packed_sha256"],
            "v13_member_raw_sha256": source_pin["raw_sha256"],
            "v11_member_packed_sha256": V11_TEXT_MEMBER["packed_sha256"],
            "v11_member_raw_sha256": V11_TEXT_MEMBER["raw_sha256"],
            "v13_is_byte_identical_to_v11": True,
        },
        "source_files": {
            "switch_v13_ko": source_pin,
            "base_jp": dict(upstream.SOURCE_PINS["base_jp"]),
            "pk_jp": dict(upstream.SOURCE_PINS["pk_jp"]),
            "pk_sc_stock": dict(upstream.SOURCE_PINS["pk_sc_stock"]),
        },
        "selection_method": [
            "pk_coordinate_is_pristine_sc_visible_target",
            "pk_coordinate_is_not_claimed_by_any_existing_public_msgev_owner",
            "pk_jp_utf16le_hash_matches_a_base_jp_hash_bucket",
            "pk_jp_value_equals_every_matched_base_jp_value_in_memory",
            "matched_base_jp_coordinates_converge_on_one_meaningful_switch_korean_value",
            "switch_korean_value_contains_no_cjk_unified_ideograph_or_kana",
            "switch_korean_value_preserves_every_pk_sc_structural_invariant",
            "switch_korean_value_preserves_custom_bracket_tokens",
            "selected_coordinates_are_disjoint_from_activated_jp_only_blank_range",
        ],
        "selection": selection,
        "effective_public_catalog_exclusion": {
            key: value for key, value in owners.items() if key != "ids"
        },
        "entry_count": len(selected),
        "selected_ids_sha256": hash_json(ids),
        "selected_within_stock_visible_target": True,
        "selected_activated_jp_only_overlap_count": 0,
        "entries": [
            {
                "id": int(entry["id"]),
                "pk_jp_utf16le_sha256": entry["jp_utf16le_sha256"],
                "base_jp_utf16le_sha256": entry["jp_utf16le_sha256"],
                "pk_sc_utf16le_sha256": entry["source_sc_utf16le_sha256"],
                "switch_ko_utf16le_sha256": entry["switch_ko_utf16le_sha256"],
                "base_jp_coordinate_count": entry["base_jp_coordinate_count"],
                "base_jp_coordinate_ids_sha256": entry[
                    "base_jp_coordinate_ids_sha256"
                ],
                "jp_hash_matches": True,
                "jp_exact_in_memory_equality": True,
                "unique_meaningful_switch_ko": True,
                "switch_ko_contains_cjk_or_kana": False,
                "pk_sc_invariants_match": True,
                "custom_bracket_tokens_match": True,
                "stock_visible_target": True,
                "activated_jp_only_slot": False,
                "pk_sc_structure": entry["pk_sc_structure"],
                "ported_ko_structure": entry["ported_ko_structure"],
            }
            for entry in selected
        ],
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.switch-msgev-v13-exact-jp-hash-recovery-review.v1",
        "batch_id": BATCH_ID,
        "quality_state": "strict_transfer_pending_pc_runtime_review",
        "entry_count": len(selected),
        "entries": [
            {
                "id": int(entry["id"]),
                "status": "translated",
                "translation_origin": "switch_v13_exact_jp_hash_recovery",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": [
                    "cross_coordinate_context_review",
                    "pc_pk_runtime_layout_review",
                ],
            }
            for entry in selected
        ],
        "contains_commercial_source_text": False,
    }

    values = {
        f"public/{OVERLAY_NAME}": overlay,
        f"evidence/{EVIDENCE_NAME}": evidence,
        f"review/{REVIEW_NAME}": review,
    }
    files = {relative: encode_json(value) for relative, value in values.items()}
    source_free_scan = {
        relative: source_free_counts(blob) for relative, blob in files.items()
    }
    expected_scan = {"han_or_kana_count": 0, "embedded_nul_count": 0}
    if any(scan != expected_scan for scan in source_free_scan.values()):
        raise RecoveryError("generated public artifact contains source script")
    artifacts = {
        relative: artifact_metadata(relative, blob) for relative, blob in files.items()
    }

    validation = {
        "schema": "nobu16.kr.switch-msgev-v13-exact-jp-hash-recovery-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "entry_count": len(selected),
        "selected_ids_sha256": hash_json(ids),
        "selection": selection,
        "selected_within_stock_visible_target": True,
        "selected_activated_jp_only_overlap_count": 0,
        "source_release": SWITCH_RELEASE,
        "switch_text_identity": evidence["switch_text_identity"],
        "source_alignment": {
            "source_string_counts": {
                "switch_v13_ko": source_pin["string_count"],
                "base_jp": upstream.SOURCE_PINS["base_jp"]["string_count"],
                "pk_jp": upstream.SOURCE_PINS["pk_jp"]["string_count"],
                "pk_sc_stock": upstream.SOURCE_PINS["pk_sc_stock"]["string_count"],
            },
            "selected_entry_reference_hash_count": len(selected) * 5,
            "jp_hash_then_exact_equality_required": True,
            "unique_meaningful_switch_ko_required": True,
            "pk_sc_parse_rebuild_byte_exact": True,
            "switch_patch_parse_rebuild_byte_exact": True,
            "official_source_text_embedded": False,
        },
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "custom_bracket_tokens",
            ],
        },
        "effective_public_catalog_exclusion": {
            "existing_unique_id_count": owners["unique_id_count"],
            "existing_ids_sha256": owners["ids_sha256"],
            "selected_overlap_count": 0,
        },
        "reconstruction": {
            "complete_target_included": False,
            "changed_entry_count": target["changed_entry_count"],
            "target": target,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "switch_archive_extracted": False,
            "complete_game_resource_emitted": False,
            "installed_game_files_modified": False,
            "base_msg_sc_modified": False,
            "font_files_modified": False,
            "root_readme_or_progress_modified": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
        },
    }
    validation_blob = encode_json(validation)
    if source_free_counts(validation_blob) != expected_scan:
        raise RecoveryError("generated validation contains source script")
    files[VALIDATION_NAME] = validation_blob

    out_root = out_root.resolve()
    for relative, blob in files.items():
        path = out_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)

    after = input_snapshot(game_root, repo_root, archive_path)
    if before != after:
        raise RecoveryError("an input changed while building")
    return {
        "entry_count": len(selected),
        "selected_ids_sha256": hash_json(ids),
        "selection": selection,
        "target": target,
        "files": files,
    }


def build_reproducibly(
    game_root: Path, repo_root: Path, archive_path: Path, out_root: Path
) -> dict[str, Any]:
    game_root = game_root.resolve()
    repo_root = repo_root.resolve()
    archive_path = archive_path.resolve()
    out_root = out_root.resolve()
    before = input_snapshot(game_root, repo_root, archive_path)
    with tempfile.TemporaryDirectory(prefix="nobu16-msgev-v13-hash-a-") as first_dir:
        with tempfile.TemporaryDirectory(prefix="nobu16-msgev-v13-hash-b-") as second_dir:
            first = build_once(game_root, repo_root, archive_path, Path(first_dir))
            second = build_once(game_root, repo_root, archive_path, Path(second_dir))
            if first["files"] != second["files"]:
                raise RecoveryError("isolated builds are not byte-identical")
    final = build_once(game_root, repo_root, archive_path, out_root)
    if first["files"] != final["files"]:
        raise RecoveryError("final build differs from isolated build")
    after = input_snapshot(game_root, repo_root, archive_path)
    if before != after:
        raise RecoveryError("an input changed across reproducible build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--archive", type=Path, default=REPO_ROOT / SWITCH_ARCHIVE_RELATIVE)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(
            args.game_root, args.repo_root, args.archive, args.out_root
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"recovered_entries={result['entry_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"target_wrapper_sha256={result['target']['wrapper_sha256']}")
    print("selected_within_stock_visible_target=True")
    print("selected_activated_jp_only_overlap_count=0")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
