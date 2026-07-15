#!/usr/bin/env python3
"""Strictly import Switch v1.1 biography strings into PK ``msgbre``.

The Switch release does not ship a separate ``msgbre.bin``.  Its base-game
``strdata.bin`` block 2 is a 3,000-slot biography table, and this importer
accepts a row only when the base JP text, Switch Korean text, PK JP text, and
PK SC structural invariants prove a deterministic correspondence.

It reads the Switch ZIP and installed game resources only.  Outputs are
source-free overlays and audit JSON; a complete game resource is rebuilt only
in memory to validate the recipe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path[:0] = [str(TOOLS_ROOT), str(WORKSTREAM_ROOT)]

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_container import EXPECTED_SLOT_COUNTS, parse_strdata, rebuild_strdata  # noqa: E402


BATCH_ID = "switch_v11_msgbre_strict_transfer.v0.1"
OVERLAY_NAME = "msgbre_ko_switch_v11_strict_transfer.v0.1.json"
EVIDENCE_NAME = "switch_v11_msgbre_alignment_evidence.v0.1.json"
REVIEW_NAME = "switch_v11_msgbre_review_index.v0.1.json"
VALIDATION_NAME = "switch_v11_msgbre_validation.v0.1.json"
RESOURCE = "MSG_PK/SC/msgbre.bin"
BIOGRAPHY_BLOCK_ID = 2
STRING_COUNT = 3_000
SELF_OVERLAY_PATH = f"workstreams/switch_msgbre_v11/public/{OVERLAY_NAME}"
EXPECTED_SELF_OVERLAY_SHA256 = "BFEFB590F10B073E9510F598BDFDCC840DDEDC165B637F9F0FEA0CB6B2675FC1"
HISTORICAL_PROGRESS_SHA256 = "FE89A4EEF52E29B083B6B0D25D49F01091D82FE051749F750DBF9FAAF01305FC"
HISTORICAL_PROGRESS_LOGICAL_PATH = "data/public/translation_progress.v0.1.json"
PRIOR_MANUAL_OVERLAY_PATHS = tuple(
    f"workstreams/msgbre/public/msgbre_ko_biographies_{suffix}"
    for suffix in (
        "0000_0128.v0.1.json",
        "0129_0250.v0.2.json",
        "0251_0350.v0.3.json",
        "0351_0457.v0.4.json",
        "0458_0565.v0.5.json",
        "0566_0610.v0.6.json",
        "0611_0655.v0.7.json",
        "0656_0700.v0.8.json",
        "0701_0745.v0.9.json",
        "0746_0790.v0.10.json",
        "0791_0835.v0.11.json",
    )
)
SUCCESSOR_OVERLAYS = (
    {
        "path": "workstreams/switch_msgbre_v13_cjk_cleanup/public/msgbre_ko_switch_v13_cjk_cleanup_3.v0.1.json",
        "sha256": "170A49AE210ED546888B33A4A4BD626AA44E66966B64217E4398847B989A4E43",
        "entry_count": 3,
        "ids_sha256": "C19CF4F02CB33DF4FC72C25443BA4E0FD7D5978B142DA7C2A62536881670BFC3",
    },
    {
        "path": "workstreams/msgbre_pk_native_completion/public/msgbre_ko_pk_native_completion_11.v0.1.json",
        "sha256": "961DB30C18524544DC58ED67E256CAA2EA2BC8CB337465778585EF54404CB8D2",
        "entry_count": 11,
        "ids_sha256": "31F6AEC16C201CCDE31984F70A477A9673F651ACFE878D956C8CBAAE024BEC47",
    },
)

SWITCH_ARCHIVE_RELATIVE = Path("tmp/third_party_switch_v11/NobunagaShinsei_KoreanPatch_v1.1.zip")
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/strdata.bin"
SWITCH_README_MEMBER = "NobunagaShinsei_KR/README.md"
LOCAL_STOCK_SC_BACKUP = (
    GAME_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "pk-full-messages-seoulhangang-v1"
    / "originals"
    / "MSG_PK"
    / "SC"
    / "msgbre.bin"
)

ARCHIVE_PIN = {
    "size": 73_040_529,
    "sha256": "931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6",
}
SWITCH_MEMBER_PIN = {
    "size": 404_189,
    "compressed_size": 294_162,
    "crc32": "B17A2EBB",
    "sha256": "5F065B9DBDAE4DC75E2D7186A76C0AC988FB504F018F820C204262BF07D5061B",
    "raw_size": 953_512,
    "raw_sha256": "245538466576E3880B3C53C0CB4929685096DF394C27CCB93B2C893615A46ADE",
}
BASE_JP_STRDATA_PIN = {
    "logical_path": "MSG/JP/strdata.bin",
    "size": 507_054,
    "packed_sha256": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "raw_size": 763_928,
    "raw_sha256": "EAB14063C2060CE11794232F483F0B2210B3BD58118165CBEEC2F37176C25649",
}
PK_JP_MSGBRE_PIN = {
    "logical_path": "MSG_PK/JP/msgbre.bin",
    "size": 221_127,
    "packed_sha256": "DA9BE8242CF0A90592D573DF676ECDE26566B11C5707273EEB4AF5BA54132AD5",
    "raw_size": 333_516,
    "raw_sha256": "02237F07362E0E3DFF92C0E999A29B887EBE5971B1C3EF8F26EAA5C969FB9668",
}
PK_SC_MSGBRE_PIN = {
    "logical_path": RESOURCE,
    "size": 226_918,
    "packed_sha256": "AD1FEC313228AADB00581C25AE59D8C6AFF54DD771A4D0F7BC35CD1B44D77B8D",
    "raw_size": 291_256,
    "raw_sha256": "E0343DCDB1BE7C62E515DE52B9045DC54A4D8FE77BF9B6F0836A3478CBD77779",
}

EXPECTED_BASE_BLOCK_UNIQUE_JP_HASHES = 2_208
EXPECTED_CONVERGENT_KOREAN_HASHES = 2_206
EXPECTED_PK_JP_MATCHES = 2_206
EXPECTED_EXISTING_CLAIMED_COUNT = 836
EXPECTED_EXISTING_CLAIMED_IDS_SHA256 = "337661DAE0007262685A6FCC38D623AD252FE5B49270127375693297E5CD7C81"
EXPECTED_EXISTING_COLLISION_COUNT = 836
EXPECTED_SOURCE_SCRIPT_EXCLUSION_COUNT = 3
EXPECTED_SELECTED_COUNT = 1_367
EXPECTED_SELECTED_IDS_SHA256 = "60CF3C3DF6FDA0A19038927806050092CFC95CE6D449057D25C1A84EA0E49BED"

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")


class SwitchMsgbreImportError(ValueError):
    """Raised when the pinned Switch-to-PK eligibility gate fails."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def ids_sha256(ids: list[int]) -> str:
    return sha256(json.dumps(ids, separators=(",", ":")).encode("utf-8"))


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any, logical_path: str) -> dict[str, Any]:
    blob = json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": logical_path, "size": len(blob), "sha256": sha256(blob)}


def script_counts(text: str) -> dict[str, int]:
    return {"cjk_unified_count": len(CJK_RE.findall(text)), "kana_count": len(KANA_RE.findall(text))}


def source_script_free(text: str) -> bool:
    return script_counts(text) == {"cjk_unified_count": 0, "kana_count": 0}


def meaningful_korean(text: str) -> bool:
    return bool(HANGUL_RE.search(text)) and common.has_semantic_text(text)


def validate_msgbre_overlay_shape(overlay: dict[str, Any]) -> None:
    """Validate the common overlay schema without widening a shared allowlist.

    ``build_common_message_overlay`` currently advertises only its two older
    resources.  The structure itself is resource-agnostic, but changing that
    shared deploy allowlist belongs to the integration step, not this read-only
    Switch extraction workstream.
    """
    expected_root = {
        "schema", "overlay_id", "resource", "base_language", "entry_count",
        "distribution_policy", "stock_sc", "defaults", "entries",
    }
    if set(overlay) != expected_root or overlay["schema"] != common.OVERLAY_SCHEMA:
        raise SwitchMsgbreImportError("msgbre overlay root schema is invalid")
    if overlay["resource"] != RESOURCE or overlay["base_language"] != "SC":
        raise SwitchMsgbreImportError("msgbre overlay target is invalid")
    if overlay["entry_count"] != len(overlay["entries"]) or not overlay["entries"]:
        raise SwitchMsgbreImportError("msgbre overlay entry count is invalid")
    policy = overlay["distribution_policy"]
    if policy != {"contains_commercial_source_text": False, "contains_complete_game_resource": False}:
        raise SwitchMsgbreImportError("msgbre overlay distribution policy is invalid")
    stock = overlay["stock_sc"]
    if set(stock) != {"size", "packed_sha256", "raw_size", "raw_sha256", "string_count"} or stock["string_count"] != STRING_COUNT:
        raise SwitchMsgbreImportError("msgbre overlay stock specification is invalid")
    ids: list[int] = []
    for entry in overlay["entries"]:
        if set(entry) != {"id", "source_sc_utf16le_sha256", "ko"} or type(entry["id"]) is not int:
            raise SwitchMsgbreImportError("msgbre overlay entry shape is invalid")
        if not re.fullmatch(r"[0-9A-F]{64}", str(entry["source_sc_utf16le_sha256"])):
            raise SwitchMsgbreImportError("msgbre overlay source hash is invalid")
        if not isinstance(entry["ko"], str) or "\0" in entry["ko"] or not common.has_semantic_text(entry["ko"]):
            raise SwitchMsgbreImportError("msgbre overlay Korean text is invalid")
        entry["ko"].encode("utf-16le")
        ids.append(entry["id"])
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise SwitchMsgbreImportError("msgbre overlay IDs are not sorted and unique")


def _validate_blob(blob: bytes, pin: dict[str, Any], label: str, hash_key: str = "packed_sha256") -> None:
    if len(blob) != int(pin["size"]):
        raise SwitchMsgbreImportError(f"{label} size does not match pin")
    if sha256(blob) != str(pin[hash_key]):
        raise SwitchMsgbreImportError(f"{label} SHA-256 does not match pin")


def _load_pinned_message_table(path: Path, pin: dict[str, Any], label: str) -> tuple[bytes, bytes, Any]:
    packed = path.read_bytes()
    _validate_blob(packed, pin, label)
    _, raw = decompress_wrapper(packed)
    if len(raw) != int(pin["raw_size"]) or sha256(raw) != str(pin["raw_sha256"]):
        raise SwitchMsgbreImportError(f"{label} raw payload does not match pin")
    table = parse_message_table(raw)
    if table.string_count != STRING_COUNT or rebuild_message_table(table, table.texts) != raw:
        raise SwitchMsgbreImportError(f"{label} message table does not round-trip")
    return packed, raw, table


def _load_pinned_strdata(path: Path, pin: dict[str, Any], label: str) -> tuple[bytes, bytes, Any]:
    packed = path.read_bytes()
    _validate_blob(packed, pin, label)
    _, raw = decompress_wrapper(packed)
    if len(raw) != int(pin["raw_size"]) or sha256(raw) != str(pin["raw_sha256"]):
        raise SwitchMsgbreImportError(f"{label} raw payload does not match pin")
    archive = parse_strdata(raw)
    if tuple(block.slot_count for block in archive.blocks) != EXPECTED_SLOT_COUNTS:
        raise SwitchMsgbreImportError(f"{label} block-slot layout does not match pin")
    if rebuild_strdata(archive) != raw:
        raise SwitchMsgbreImportError(f"{label} container does not round-trip")
    return packed, raw, archive


def load_switch_strdata(archive_path: Path) -> tuple[bytes, bytes, Any, dict[str, Any]]:
    archive_blob = archive_path.read_bytes()
    if len(archive_blob) != ARCHIVE_PIN["size"] or sha256(archive_blob) != ARCHIVE_PIN["sha256"]:
        raise SwitchMsgbreImportError("Switch v1.1 archive does not match release pin")
    with zipfile.ZipFile(archive_path) as archive:
        info = archive.getinfo(SWITCH_MEMBER)
        if info.flag_bits & 1:
            raise SwitchMsgbreImportError("Switch strdata member must not be encrypted")
        if (
            info.file_size != SWITCH_MEMBER_PIN["size"]
            or info.compress_size != SWITCH_MEMBER_PIN["compressed_size"]
            or f"{info.CRC:08X}" != SWITCH_MEMBER_PIN["crc32"]
        ):
            raise SwitchMsgbreImportError("Switch strdata ZIP metadata does not match pin")
        packed = archive.read(info)
        readme = archive.read(SWITCH_README_MEMBER)
    if len(packed) != SWITCH_MEMBER_PIN["size"] or sha256(packed) != SWITCH_MEMBER_PIN["sha256"]:
        raise SwitchMsgbreImportError("Switch strdata member does not match pin")
    _, raw = decompress_wrapper(packed)
    if len(raw) != SWITCH_MEMBER_PIN["raw_size"] or sha256(raw) != SWITCH_MEMBER_PIN["raw_sha256"]:
        raise SwitchMsgbreImportError("Switch strdata raw payload does not match pin")
    parsed = parse_strdata(raw)
    if tuple(block.slot_count for block in parsed.blocks) != EXPECTED_SLOT_COUNTS or rebuild_strdata(parsed) != raw:
        raise SwitchMsgbreImportError("Switch strdata does not strictly parse/rebuild")
    provenance = {
        "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
        "release_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1",
        "tag": "v1.1",
        "author_attribution": "GitHub user snake7594",
        "archive_member": SWITCH_MEMBER,
        "archive_size": len(archive_blob),
        "archive_sha256": sha256(archive_blob),
        "member_size": len(packed),
        "member_sha256": sha256(packed),
        "member_raw_size": len(raw),
        "member_raw_sha256": sha256(raw),
        "member_readme_size": len(readme),
        "block_slot_counts": [block.slot_count for block in parsed.blocks],
    }
    return packed, raw, parsed, provenance


def _relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def load_existing_msgbre_claims(progress_path: Path) -> tuple[set[int], dict[str, Any]]:
    """Load pinned manual owners and validate but exclude later owners."""
    progress_blob = progress_path.read_bytes()
    progress = json.loads(progress_blob.decode("utf-8"))
    resources = progress.get("resources")
    matches = [resource for resource in resources if resource.get("path") == RESOURCE] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise SwitchMsgbreImportError("translation progress has no unique PK msgbre resource")
    globs = matches[0].get("overlay_globs")
    if not isinstance(globs, list) or not all(isinstance(pattern, str) for pattern in globs):
        raise SwitchMsgbreImportError("PK msgbre overlay configuration is invalid")
    claims: set[int] = set()
    authored = 0
    overlays: list[dict[str, Any]] = []
    self_registered = 0
    manual_paths_seen: list[str] = []
    successor_descriptors = {str(item["path"]): item for item in SUCCESSOR_OVERLAYS}
    successor_ids: set[int] = set()
    successor_overlays: list[dict[str, Any]] = []
    checked_self_blob = (REPO_ROOT / SELF_OVERLAY_PATH).read_bytes()
    checked_self = json.loads(checked_self_blob.decode("utf-8"))
    checked_self_entries = checked_self.get("entries")
    if not isinstance(checked_self_entries, list):
        raise SwitchMsgbreImportError("checked candidate overlay entries are invalid")
    checked_self_ids = [entry.get("id") for entry in checked_self_entries]
    if (
        checked_self.get("resource") != RESOURCE
        or checked_self.get("overlay_id") != BATCH_ID
        or sha256(checked_self_blob) != EXPECTED_SELF_OVERLAY_SHA256
        or any(type(entry_id) is not int for entry_id in checked_self_ids)
        or checked_self_ids != sorted(checked_self_ids)
        or len(checked_self_ids) != EXPECTED_SELECTED_COUNT
        or ids_sha256(checked_self_ids) != EXPECTED_SELECTED_IDS_SHA256
    ):
        raise SwitchMsgbreImportError("checked candidate overlay contract changed")
    self_ids = set(checked_self_ids)
    for pattern in globs:
        paths = sorted(REPO_ROOT.glob(pattern))
        if len(paths) != 1:
            raise SwitchMsgbreImportError(f"overlay pattern {pattern!r} resolved to {len(paths)} files")
        path = paths[0]
        logical_path = _relative(path)
        overlay_blob = path.read_bytes()
        overlay = json.loads(overlay_blob.decode("utf-8"))
        if overlay.get("resource") != RESOURCE:
            raise SwitchMsgbreImportError(f"overlay {logical_path} targets a different resource")
        entries = overlay.get("entries")
        if not isinstance(entries, list) or any(not isinstance(entry, dict) or type(entry.get("id")) is not int for entry in entries):
            raise SwitchMsgbreImportError(f"overlay {logical_path} entries are invalid")
        ids = [entry["id"] for entry in entries]
        if ids != sorted(ids) or len(ids) != len(set(ids)):
            raise SwitchMsgbreImportError(f"overlay {logical_path} IDs are not sorted and unique")
        if logical_path == SELF_OVERLAY_PATH:
            if pattern != SELF_OVERLAY_PATH:
                raise SwitchMsgbreImportError("candidate overlay must use its exact logical path")
            self_registered += 1
            if self_registered > 1:
                raise SwitchMsgbreImportError("candidate overlay is registered more than once")
            if (
                overlay.get("overlay_id") != BATCH_ID
                or sha256(overlay_blob) != EXPECTED_SELF_OVERLAY_SHA256
                or len(ids) != EXPECTED_SELECTED_COUNT
                or ids_sha256(ids) != EXPECTED_SELECTED_IDS_SHA256
            ):
                raise SwitchMsgbreImportError("candidate overlay contract changed")
            continue

        successor = successor_descriptors.get(logical_path)
        if successor is not None:
            if pattern != logical_path:
                raise SwitchMsgbreImportError("successor overlays must use exact logical paths")
            policy = overlay.get("distribution_policy")
            if (
                sha256(overlay_blob) != successor["sha256"]
                or len(ids) != successor["entry_count"]
                or ids_sha256(ids) != successor["ids_sha256"]
                or not isinstance(policy, dict)
                or policy.get("contains_commercial_source_text") is not False
                or policy.get("contains_complete_game_resource") is not False
            ):
                raise SwitchMsgbreImportError(f"successor overlay contract changed: {logical_path}")
            overlap = claims.intersection(ids)
            if overlap:
                raise SwitchMsgbreImportError(
                    f"successor overlaps a prior manual owner at {min(overlap)}: {logical_path}"
                )
            overlap = self_ids.intersection(ids)
            if overlap:
                raise SwitchMsgbreImportError(
                    f"successor overlaps this batch at {min(overlap)}: {logical_path}"
                )
            overlap = successor_ids.intersection(ids)
            if overlap:
                raise SwitchMsgbreImportError(
                    f"successor overlays overlap at {min(overlap)}: {logical_path}"
                )
            successor_ids.update(ids)
            successor_overlays.append(
                {
                    "logical_path": logical_path,
                    "sha256": sha256(overlay_blob),
                    "entry_count": len(ids),
                    "ids_sha256": ids_sha256(ids),
                    "source_free": True,
                    "excluded_from_prior_claims": True,
                }
            )
            continue

        if logical_path not in PRIOR_MANUAL_OVERLAY_PATHS:
            raise SwitchMsgbreImportError(f"unrecognized PK msgbre owner overlay: {logical_path}")
        if pattern != logical_path:
            raise SwitchMsgbreImportError("prior manual overlays must use exact logical paths")
        if claims.intersection(ids):
            raise SwitchMsgbreImportError(f"prior PK msgbre overlays overlap at {logical_path}")
        claims.update(ids)
        authored += len(ids)
        manual_paths_seen.append(logical_path)
        overlays.append({"logical_path": logical_path, "sha256": sha256(overlay_blob), "entry_count": len(ids), "min_id": min(ids), "max_id": max(ids)})
    if manual_paths_seen != list(PRIOR_MANUAL_OVERLAY_PATHS):
        raise SwitchMsgbreImportError("prior manual PK biography owner paths changed")
    overlap = claims.intersection(successor_ids)
    if overlap:
        raise SwitchMsgbreImportError(
            f"successor overlays overlap a pinned manual owner at {min(overlap)}"
        )
    snapshot = {
        "progress_logical_path": _relative(progress_path),
        "progress_sha256": sha256(progress_blob),
        "prior_overlay_globs": list(PRIOR_MANUAL_OVERLAY_PATHS),
        "candidate_overlay_registered": bool(self_registered),
        "candidate_overlay_excluded_from_prior_claims": True,
        "prior_overlays": overlays,
        "authored_entry_count": authored,
        "unique_claimed_count": len(claims),
        "claimed_ids_sha256": ids_sha256(sorted(claims)),
        "successor_overlays": successor_overlays,
        "successor_overlay_count": len(successor_overlays),
        "successor_effective_id_count": len(successor_ids),
        "successors_excluded_from_prior_claims": True,
    }
    return claims, snapshot


def historical_existing_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return the immutable owner snapshot embedded in the v1.1 validation."""

    return {
        "progress_logical_path": HISTORICAL_PROGRESS_LOGICAL_PATH,
        "progress_sha256": HISTORICAL_PROGRESS_SHA256,
        "prior_overlay_globs": list(PRIOR_MANUAL_OVERLAY_PATHS),
        "candidate_overlay_registered": True,
        "candidate_overlay_excluded_from_prior_claims": True,
        "prior_overlays": snapshot["prior_overlays"],
        "authored_entry_count": snapshot["authored_entry_count"],
        "unique_claimed_count": snapshot["unique_claimed_count"],
        "claimed_ids_sha256": snapshot["claimed_ids_sha256"],
    }


def build_biography_reverse_index(base_archive: Any, switch_archive: Any) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    if len(base_archive.blocks) != len(switch_archive.blocks):
        raise SwitchMsgbreImportError("base and Switch strdata block counts differ")
    base_block = base_archive.blocks[BIOGRAPHY_BLOCK_ID]
    switch_block = switch_archive.blocks[BIOGRAPHY_BLOCK_ID]
    if base_block.block_id != BIOGRAPHY_BLOCK_ID or switch_block.block_id != BIOGRAPHY_BLOCK_ID or base_block.slot_count != STRING_COUNT or switch_block.slot_count != STRING_COUNT:
        raise SwitchMsgbreImportError("Switch/base biography block layout differs")
    index: dict[str, dict[str, Any]] = {}
    for slot_id, (jp, ko) in enumerate(zip(base_block.texts, switch_block.texts, strict=True)):
        jp_hash = common.text_hash(jp)
        record = index.setdefault(jp_hash, {"jp": jp, "switch_ko": [], "slot_ids": []})
        if record["jp"] != jp:
            raise SwitchMsgbreImportError("unexpected SHA-256 text collision")
        record["switch_ko"].append(ko)
        record["slot_ids"].append(slot_id)
    convergent = ambiguous = no_korean = 0
    for record in index.values():
        jp = str(record["jp"])
        values = list(record["switch_ko"])
        valid = {ko for ko in values if ko != jp and meaningful_korean(ko)}
        all_valid = bool(valid) and all(ko != jp and meaningful_korean(ko) for ko in values)
        record["candidate_ko"] = next(iter(valid)) if all_valid and len(valid) == 1 else None
        record["slot_ids_sha256"] = ids_sha256(list(record["slot_ids"]))
        record["slot_count"] = len(record["slot_ids"])
        if record["candidate_ko"] is not None:
            convergent += 1
        elif valid:
            ambiguous += 1
        else:
            no_korean += 1
    summary = {
        "source_block_id": BIOGRAPHY_BLOCK_ID,
        "source_block_slot_count": base_block.slot_count,
        "base_unique_jp_hash_count": len(index),
        "convergent_korean_hash_count": convergent,
        "ambiguous_korean_hash_count": ambiguous,
        "no_meaningful_korean_hash_count": no_korean,
        "match_policy": "base_jp_utf16le_sha256_then_exact_in_memory_jp_equality",
        "convergence_policy": "all_duplicate_base_slots_have_one_distinct_meaningful_hangul_result",
    }
    return index, summary


def derive_entries(pk_jp: Any, pk_sc: Any, reverse_index: dict[str, dict[str, Any]], claimed_ids: set[int]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    all_match_ids: list[int] = []
    collision_ids: list[int] = []
    script_ids: list[int] = []
    invariant_ids: list[int] = []
    same_sc_ids: list[int] = []
    invariant_histogram: dict[str, int] = {}
    for entry_id, (jp, sc) in enumerate(zip(pk_jp.texts, pk_sc.texts, strict=True)):
        record = reverse_index.get(common.text_hash(jp))
        if record is None or record["jp"] != jp or record["candidate_ko"] is None:
            continue
        all_match_ids.append(entry_id)
        if entry_id in claimed_ids:
            collision_ids.append(entry_id)
            continue
        ko = str(record["candidate_ko"])
        if not source_script_free(ko):
            script_ids.append(entry_id)
            continue
        problems = common.invariant_mismatches(sc, ko)
        if problems:
            invariant_ids.append(entry_id)
            for problem in problems:
                key = problem.split(":", 1)[0]
                invariant_histogram[key] = invariant_histogram.get(key, 0) + 1
            continue
        if ko == sc:
            same_sc_ids.append(entry_id)
            continue
        sc_hash = common.text_hash(sc)
        entries.append({"id": entry_id, "source_sc_utf16le_sha256": sc_hash, "ko": ko})
        evidence_entries.append({
            "id": entry_id,
            "pk_jp_utf16le_sha256": common.text_hash(jp),
            "pk_sc_utf16le_sha256": sc_hash,
            "switch_ko_utf16le_sha256": common.text_hash(ko),
            "base_biography_slot_count": record["slot_count"],
            "base_biography_slot_ids_sha256": record["slot_ids_sha256"],
            "jp_complete_match": True,
            "korean_hash_converged": True,
            "source_script_free": True,
            "pk_sc_invariants_preserved": True,
        })
    selected_ids = [entry["id"] for entry in entries]
    if selected_ids != sorted(selected_ids):
        raise SwitchMsgbreImportError("strict entry order is not ascending")
    return entries, evidence_entries, {
        "pk_total_slot_count": pk_jp.string_count,
        "pk_jp_complete_hash_match_count": len(all_match_ids),
        "pk_jp_complete_hash_match_ids_sha256": ids_sha256(all_match_ids),
        "existing_overlay_collision_count": len(collision_ids),
        "existing_overlay_collision_ids_sha256": ids_sha256(collision_ids),
        "source_script_exclusion": {
            "count": len(script_ids),
            "ids_sha256": ids_sha256(script_ids),
            "reason": "switch_korean_contains_cjk_unified_or_kana",
        },
        "pk_sc_invariant_exclusion_count": len(invariant_ids),
        "pk_sc_invariant_exclusion_ids_sha256": ids_sha256(invariant_ids),
        "pk_sc_invariant_mismatch_histogram": dict(sorted(invariant_histogram.items())),
        "unchanged_sc_exclusion_count": len(same_sc_ids),
        "selected_entry_count": len(entries),
        "selected_ids_sha256": ids_sha256(selected_ids),
    }


def reconstruct_target(sc_packed: bytes, sc_table: Any, entries: list[dict[str, Any]]) -> dict[str, Any]:
    texts = list(sc_table.texts)
    for entry in entries:
        entry_id = int(entry["id"])
        if common.text_hash(texts[entry_id]) != entry["source_sc_utf16le_sha256"]:
            raise SwitchMsgbreImportError(f"PK SC changed before reconstruction at ID {entry_id}")
        texts[entry_id] = str(entry["ko"])
    raw = rebuild_message_table(sc_table, texts)
    if parse_message_table(raw).texts != tuple(texts):
        raise SwitchMsgbreImportError("translated PK SC msgbre parse/rebuild differs")
    packed = recompress_wrapper(raw, sc_packed)
    if decompress_wrapper(packed)[1] != raw:
        raise SwitchMsgbreImportError("translated PK SC msgbre wrapper round-trip differs")
    return {
        "resource": RESOURCE,
        "entry_count": len(entries),
        "complete_target_included": False,
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "parse_rebuild_round_trip": True,
        "wrapper_round_trip": True,
    }


def _safe_out_root(out_root: Path) -> Path:
    resolved = out_root.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise SwitchMsgbreImportError("output must stay inside KR_PATCH_WORK; game files are never an output") from exc
    return resolved


def input_snapshot(args: argparse.Namespace) -> dict[str, str]:
    return {
        "switch_archive": sha256(args.switch_zip.read_bytes()),
        "base_jp_strdata": sha256(args.base_jp_strdata.read_bytes()),
        "pk_jp_msgbre": sha256(args.stock_pk_jp.read_bytes()),
        "pk_sc_msgbre": sha256(args.stock_pk_sc.read_bytes()),
        "translation_progress": sha256(args.progress.read_bytes()),
    }


def build_once(args: argparse.Namespace, out_root: Path) -> dict[str, Any]:
    out_root = _safe_out_root(out_root)
    before = input_snapshot(args)
    claimed_ids, current_existing_before = load_existing_msgbre_claims(args.progress)
    existing_before = historical_existing_snapshot(current_existing_before)
    if len(claimed_ids) != EXPECTED_EXISTING_CLAIMED_COUNT or ids_sha256(sorted(claimed_ids)) != EXPECTED_EXISTING_CLAIMED_IDS_SHA256:
        raise SwitchMsgbreImportError("prior manual PK biography coverage differs from the v1.1 pin")
    _, _, switch_archive, provenance = load_switch_strdata(args.switch_zip)
    _, _, base_archive = _load_pinned_strdata(args.base_jp_strdata, BASE_JP_STRDATA_PIN, "PC base JP strdata")
    pk_jp_packed, _, pk_jp = _load_pinned_message_table(args.stock_pk_jp, PK_JP_MSGBRE_PIN, "PK JP msgbre")
    pk_sc_packed, pk_sc_raw, pk_sc = _load_pinned_message_table(args.stock_pk_sc, PK_SC_MSGBRE_PIN, "PK SC msgbre")
    if pk_jp_packed == pk_sc_packed:
        raise SwitchMsgbreImportError("PK JP and SC msgbre wrappers cannot be identical")
    reverse_index, reverse_summary = build_biography_reverse_index(base_archive, switch_archive)
    entries, evidence_entries, selection = derive_entries(pk_jp, pk_sc, reverse_index, claimed_ids)
    if reverse_summary["base_unique_jp_hash_count"] != EXPECTED_BASE_BLOCK_UNIQUE_JP_HASHES or reverse_summary["convergent_korean_hash_count"] != EXPECTED_CONVERGENT_KOREAN_HASHES:
        raise SwitchMsgbreImportError("Switch biography convergence count differs from v1.1 pin")
    if selection["pk_jp_complete_hash_match_count"] != EXPECTED_PK_JP_MATCHES:
        raise SwitchMsgbreImportError("PK biography JP correspondence count differs from v1.1 pin")
    if selection["existing_overlay_collision_count"] != EXPECTED_EXISTING_COLLISION_COUNT:
        raise SwitchMsgbreImportError("prior biography collision count differs from v1.1 pin")
    if selection["source_script_exclusion"]["count"] != EXPECTED_SOURCE_SCRIPT_EXCLUSION_COUNT:
        raise SwitchMsgbreImportError("source-script exclusion count differs from v1.1 pin")
    if len(entries) != EXPECTED_SELECTED_COUNT or selection["selected_ids_sha256"] != EXPECTED_SELECTED_IDS_SHA256:
        raise SwitchMsgbreImportError("strict selected biography set differs from v1.1 pin")
    if set(entry["id"] for entry in entries).intersection(claimed_ids) or any(not source_script_free(str(entry["ko"])) for entry in entries):
        raise SwitchMsgbreImportError("strict biography selection is not disjoint/source-free")
    target_a = reconstruct_target(pk_sc_packed, pk_sc, entries)
    if target_a != reconstruct_target(pk_sc_packed, pk_sc, entries):
        raise SwitchMsgbreImportError("in-memory PK target reconstruction is not deterministic")

    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(entries),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "stock_sc": {"size": len(pk_sc_packed), "packed_sha256": sha256(pk_sc_packed), "raw_size": len(pk_sc_raw), "raw_sha256": sha256(pk_sc_raw), "string_count": pk_sc.string_count},
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    validate_msgbre_overlay_shape(overlay)
    evidence = {
        "schema": "nobu16.kr.switch-msgbre-v11-strict-transfer-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": "msgbre",
        "scope": {"selected_entry_count": len(entries), "selected_ids_sha256": selection["selected_ids_sha256"], "pk_string_count": STRING_COUNT, "switch_source_block_id": BIOGRAPHY_BLOCK_ID},
        "source_release": provenance,
        "base_jp_strdata": {**BASE_JP_STRDATA_PIN, "block_slot_counts": list(EXPECTED_SLOT_COUNTS), "parse_rebuild_byte_identical": True},
        "pk_source_files": {"JP": {**PK_JP_MSGBRE_PIN, "string_count": pk_jp.string_count}, "SC": {**PK_SC_MSGBRE_PIN, "string_count": pk_sc.string_count}},
        "matching_policy": {**reverse_summary, "target_eligibility": ["PK JP hash and exact string match base biography block", "one convergent Switch Korean value for all duplicate source slots", "not claimed by prior PK msgbre overlay", "no CJK Unified Ideographs or Kana", "PK SC printf/ESC/control/linebreak/PUA/edge-whitespace invariants match"]},
        "selection": selection,
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    review = {
        "schema": "nobu16.kr.switch-msgbre-v11-strict-transfer-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "strict_external_transfer_not_human_or_runtime_reviewed",
        "entry_count": len(entries),
        "entries": [{"id": entry["id"], "status": "translated", "translation_origin": "switch_v1.1_biography_block_hash_convergent_transfer", "strict_transfer": True, "source_script_free": True, "pk_sc_invariants_preserved": True, "human_review_required": True, "runtime_reviewed": False} for entry in entries],
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    artifacts = {
        "overlay": write_json(out_root / "public" / OVERLAY_NAME, overlay, f"public/{OVERLAY_NAME}"),
        "alignment_evidence": write_json(out_root / "evidence" / EVIDENCE_NAME, evidence, f"evidence/{EVIDENCE_NAME}"),
        "review_index": write_json(out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}"),
    }
    artifact_paths = {"overlay": out_root / "public" / OVERLAY_NAME, "alignment_evidence": out_root / "evidence" / EVIDENCE_NAME, "review_index": out_root / "review" / REVIEW_NAME}
    source_free_scan = {name: script_counts(path.read_text(encoding="utf-8")) for name, path in artifact_paths.items()}
    if any(counts != {"cjk_unified_count": 0, "kana_count": 0} for counts in source_free_scan.values()):
        raise SwitchMsgbreImportError("generated public artifact contains CJK or Kana")
    current_existing_after = load_existing_msgbre_claims(args.progress)[1]
    after = input_snapshot(args)
    if current_existing_before != current_existing_after or before != after:
        raise SwitchMsgbreImportError("an input source or prior overlay changed during the build")
    artifact_before = {**before, "translation_progress": HISTORICAL_PROGRESS_SHA256}
    artifact_after = {**after, "translation_progress": HISTORICAL_PROGRESS_SHA256}
    validation = {
        "schema": "nobu16.kr.switch-msgbre-v11-strict-transfer-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "source_release": provenance,
        "scope": {"selected_entry_count": len(entries), "expected_selected_entry_count": EXPECTED_SELECTED_COUNT, "selected_ids_sha256": selection["selected_ids_sha256"], "expected_selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256},
        "strict_selection": selection,
        "existing_overlay_exclusion": existing_before,
        "target_reconstruction": target_a,
        "reproducibility": {"required_runs": ["isolated_a", "isolated_b", "final"], "byte_identical_artifacts_required": True, "target_a_b_equal": True},
        "source_free_scan": source_free_scan,
        "safety": {"zip_included": False, "commercial_source_text_included": False, "complete_game_resource_included": False, "installed_game_files_modified": False, "deployment_performed": False, "commit_or_push_performed": False},
        "input_snapshot_before": artifact_before,
        "input_snapshot_after": artifact_after,
        "artifacts": artifacts,
    }
    validation["source_free_scan"]["generation_validation"] = script_counts(json_bytes(validation).decode("utf-8"))
    if validation["source_free_scan"]["generation_validation"] != {"cjk_unified_count": 0, "kana_count": 0}:
        raise SwitchMsgbreImportError("generation validation contains source script")
    artifacts["generation_validation"] = write_json(out_root / VALIDATION_NAME, validation, VALIDATION_NAME)
    files = {name: path.read_bytes() for name, path in {**artifact_paths, "generation_validation": out_root / VALIDATION_NAME}.items()}
    return {"entry_count": len(entries), "selected_ids_sha256": selection["selected_ids_sha256"], "target": target_a, "artifacts": artifacts, "files": files}


def build_reproducibly(args: argparse.Namespace) -> dict[str, Any]:
    out_root = _safe_out_root(args.out_root)
    before = input_snapshot(args)
    with tempfile.TemporaryDirectory(prefix="nobu16-switch-msgbre-a-", dir=REPO_ROOT / "tmp") as first_dir, tempfile.TemporaryDirectory(prefix="nobu16-switch-msgbre-b-", dir=REPO_ROOT / "tmp") as second_dir:
        first = build_once(args, Path(first_dir))
        second = build_once(args, Path(second_dir))
        if first["files"] != second["files"]:
            raise SwitchMsgbreImportError("isolated Switch biography builds are not byte-identical")
    final = build_once(args, out_root)
    if final["files"] != first["files"]:
        raise SwitchMsgbreImportError("final Switch biography build differs from isolated build")
    if input_snapshot(args) != before:
        raise SwitchMsgbreImportError("input resource changed across reproducible build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--switch-zip", type=Path, default=REPO_ROOT / SWITCH_ARCHIVE_RELATIVE)
    parser.add_argument("--base-jp-strdata", type=Path, default=GAME_ROOT / "MSG" / "JP" / "strdata.bin")
    parser.add_argument("--stock-pk-jp", type=Path, default=GAME_ROOT / "MSG_PK" / "JP" / "msgbre.bin")
    # The live game can already contain earlier file-only overlays.  This
    # transaction snapshot is the pinned pristine SC input; callers on a
    # different machine must pass an equally pristine original explicitly.
    parser.add_argument("--stock-pk-sc", type=Path, default=LOCAL_STOCK_SC_BACKUP)
    parser.add_argument("--progress", type=Path, default=REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json")
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    try:
        result = build_reproducibly(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"entries={result['entry_count']}")
    print(f"selected_ids_sha256={result['selected_ids_sha256']}")
    print(f"target_wrapper_sha256={result['target']['packed_sha256']}")
    for name, artifact in sorted(result["artifacts"].items()):
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
