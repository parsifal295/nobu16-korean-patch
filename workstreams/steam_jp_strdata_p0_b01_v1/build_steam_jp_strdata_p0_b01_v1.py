#!/usr/bin/env python3
"""Build a gated, source-text-free Korean overlay for Steam JP ``strdata``.

Scope is deliberately narrow: only the first 350 coordinates in the active
Steam JP residual-audit P0 bundle are eligible.  The initial Korean values are
derived from the public Switch v1.3 patch *only after* the active Steam JP
source equals the pinned pre-patch official JP source at every coordinate.

The builder always starts from the pinned Steam JP file.  It never writes a
game installation, executable, registry value, release artifact, or GitHub
state.  Candidate resources are allowed only below this workstream's ``tmp``
directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPOSITORY = SCRIPT.parents[2]
GAME_ROOT = REPOSITORY.parent
TOOLS = REPOSITORY / "tools"
STRDATA_TOOLS = REPOSITORY / "workstreams" / "strdata"
for directory in (TOOLS, STRDATA_TOOLS):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


WORKSTREAM_ID = "steam-jp-strdata-p0-b01-350-v1"
RESOURCE = "MSG/JP/strdata.bin"
BUNDLE_ID = "p0-MSG_JP_strdata-01"
OVERLAY_SCHEMA = "nobu16.kr.strdata-block-overlay.v1"
BUILD_SCHEMA = "nobu16.kr.strdata-block-build-manifest.v1"
OVERLAY_NAME = "strdata_ko_steam_jp_p0_b01_350.v1.json"
COORDINATE_CONTRACT = (
    REPOSITORY
    / "workstreams"
    / "jp_active_message_residual_audit_v1"
    / "public"
    / "active_jp_remaining_coordinates.v1.json"
)
DEFAULT_ACTIVE_INPUT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16") / RESOURCE
DEFAULT_OLD_JP_INPUT = (
    GAME_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "jp-runtime-wave05-20260715-v1"
    / "originals"
    / RESOURCE
)
DEFAULT_SWITCH_ZIP = (
    REPOSITORY
    / "tmp"
    / "third_party_switch_v13"
    / "NobunagaShinsei_KoreanPatch_v1.3.zip"
)
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/strdata.bin"
DEFAULT_OVERLAY = WORKSTREAM / "public" / OVERLAY_NAME
SAFE_TMP_ROOT = REPOSITORY / "tmp" / "steam_jp_strdata_p0_b01_v1"

ACTIVE_PIN = {
    "size": 956_835,
    "packed_sha256": "E77CD1F5CB72789B12B68FE0C1767950C0F54B1A62C9BB671CB14661D7378034",
    "raw_size": 953_072,
    "raw_sha256": "A3410438A13B2DB4C72B56B804BDF4ACABBEE8954203CA13D210AD848134BF66",
    "block_count": 5,
    "slot_count": 32_311,
}
OLD_JP_PIN = {
    "size": 507_054,
    "packed_sha256": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "raw_size": 763_928,
    "raw_sha256": "EAB14063C2060CE11794232F483F0B2210B3BD58118165CBEEC2F37176C25649",
}
SWITCH_ZIP_PIN = {
    "size": 72_977_145,
    "sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
}
SWITCH_MEMBER_PIN = {
    "size": 404_189,
    "packed_sha256": "5F065B9DBDAE4DC75E2D7186A76C0AC988FB504F018F820C204262BF07D5061B",
    "raw_size": 953_512,
    "raw_sha256": "245538466576E3880B3C53C0CB4929685096DF394C27CCB93B2C893615A46ADE",
}
EXPECTED_COORDINATE_COUNT = 350
EXPECTED_COORDINATE_SHA256 = "5DA0F1C55931DDC450755E7E6197F1B5B91E7AD9E11805DA4AA7B9287D427B65"
HEX64 = re.compile(r"[0-9A-F]{64}\Z")
KANA_OR_CJK = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL = re.compile(r"[\uac00-\ud7a3]")


class StrdataP0Error(ValueError):
    """Raised when a pinned input or the source-free overlay is unsafe."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_hash(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def require_workstream_output(path: Path) -> None:
    if not under(path, WORKSTREAM):
        raise StrdataP0Error(f"output must remain below workstream: {path}")


def require_tmp_output(path: Path) -> None:
    if not under(path, SAFE_TMP_ROOT):
        raise StrdataP0Error(f"candidate output must remain below {SAFE_TMP_ROOT}: {path}")


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        value, blob = common.load_json_strict(path)
    except Exception as exc:  # shared strict JSON parser has its own error type
        raise StrdataP0Error(f"invalid JSON {path}: {exc}") from exc
    return value, blob


def require_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise StrdataP0Error(f"{label} keys differ: expected={sorted(expected)!r}, actual={actual!r}")
    return value


def require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise StrdataP0Error(f"{label} must be an uppercase SHA-256")
    return value


def verify_packed_pin(packed: bytes, pin: dict[str, Any], label: str) -> bytes:
    actual = {"size": len(packed), "packed_sha256": sha256(packed)}
    expected = {"size": pin["size"], "packed_sha256": pin["packed_sha256"]}
    if actual != expected:
        raise StrdataP0Error(f"{label} packed pin mismatch: {actual}")
    try:
        _, raw = decompress_wrapper(packed)
    except Exception as exc:
        raise StrdataP0Error(f"{label} wrapper cannot be decompressed: {exc}") from exc
    raw_actual = {"raw_size": len(raw), "raw_sha256": sha256(raw)}
    raw_expected = {"raw_size": pin["raw_size"], "raw_sha256": pin["raw_sha256"]}
    if raw_actual != raw_expected:
        raise StrdataP0Error(f"{label} raw pin mismatch: {raw_actual}")
    return raw


def parse_pinned_archive(path: Path, pin: dict[str, Any], label: str) -> tuple[bytes, bytes, Any]:
    if not path.is_file():
        raise StrdataP0Error(f"{label} does not exist: {path}")
    packed = path.read_bytes()
    raw = verify_packed_pin(packed, pin, label)
    try:
        archive = parse_raw_strdata(raw)
    except Exception as exc:
        raise StrdataP0Error(f"{label} strdata structure invalid: {exc}") from exc
    if "block_count" in pin and archive.block_count != pin["block_count"]:
        raise StrdataP0Error(f"{label} block count mismatch")
    if "slot_count" in pin and archive.slot_count != pin["slot_count"]:
        raise StrdataP0Error(f"{label} slot count mismatch")
    if rebuild_raw_strdata(archive) != raw:
        raise StrdataP0Error(f"{label} identity rebuild is not byte-identical")
    return packed, raw, archive


def load_coordinate_contract() -> tuple[list[dict[str, int]], dict[tuple[int, int], str], dict[str, Any]]:
    document, _ = read_json(COORDINATE_CONTRACT)
    if document.get("schema") != "nobu16.kr.jp-active-message-residual-coordinate-contract.v1":
        raise StrdataP0Error("unexpected residual coordinate-contract schema")
    basis = document.get("basis")
    if not isinstance(basis, dict):
        raise StrdataP0Error("coordinate contract has no basis")
    active_hashes = basis.get("active_steam_file_sha256")
    if not isinstance(active_hashes, dict) or active_hashes.get(RESOURCE) != ACTIVE_PIN["packed_sha256"]:
        raise StrdataP0Error("coordinate contract active JP baseline does not match this workstream")
    bundles = document.get("recommended_parallel_bundles")
    if not isinstance(bundles, list):
        raise StrdataP0Error("coordinate contract lacks recommended bundles")
    bundle = next((item for item in bundles if isinstance(item, dict) and item.get("bundle_id") == BUNDLE_ID), None)
    if bundle is None:
        raise StrdataP0Error(f"missing coordinate bundle {BUNDLE_ID}")
    if bundle.get("resource") != RESOURCE:
        raise StrdataP0Error("coordinate bundle resource mismatch")
    if bundle.get("coordinate_count") != EXPECTED_COORDINATE_COUNT:
        raise StrdataP0Error("coordinate bundle count mismatch")
    if bundle.get("coordinate_sha256") != EXPECTED_COORDINATE_SHA256:
        raise StrdataP0Error("coordinate bundle hash mismatch")
    coordinates = bundle.get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) != EXPECTED_COORDINATE_COUNT:
        raise StrdataP0Error("coordinate bundle list invalid")
    normalized: list[dict[str, int]] = []
    seen: set[tuple[int, int]] = set()
    for item in coordinates:
        if not isinstance(item, dict) or set(item) != {"block_id", "slot_id"}:
            raise StrdataP0Error("coordinate has unexpected fields")
        block_id, slot_id = item["block_id"], item["slot_id"]
        if type(block_id) is not int or type(slot_id) is not int or block_id < 0 or slot_id < 0:
            raise StrdataP0Error("coordinate must contain non-negative integer ids")
        key = (block_id, slot_id)
        if key in seen:
            raise StrdataP0Error(f"duplicate coordinate: {key}")
        seen.add(key)
        normalized.append({"block_id": block_id, "slot_id": slot_id})
    if canonical_hash(normalized) != EXPECTED_COORDINATE_SHA256:
        raise StrdataP0Error("coordinate canonical hash mismatch")
    entries_by_resource = document.get("entries_by_resource")
    if not isinstance(entries_by_resource, dict) or not isinstance(entries_by_resource.get(RESOURCE), list):
        raise StrdataP0Error("coordinate contract lacks strdata entry hashes")
    source_hashes: dict[tuple[int, int], str] = {}
    for entry in entries_by_resource[RESOURCE]:
        if not isinstance(entry, dict):
            continue
        coordinate = entry.get("coordinate")
        if not isinstance(coordinate, dict):
            continue
        key = (coordinate.get("block_id"), coordinate.get("slot_id"))
        if key not in seen:
            continue
        source_hash = entry.get("active_utf16le_sha256")
        source_hashes[key] = require_hash(source_hash, f"contract source hash {key}")
    if set(source_hashes) != seen:
        raise StrdataP0Error("coordinate contract source-hash coverage differs from P0 coordinate set")
    return normalized, source_hashes, bundle


def load_overlay(path: Path) -> tuple[dict[str, Any], bytes]:
    document, blob = read_json(path)
    root = require_keys(
        document,
        {
            "base_language",
            "coordinate_contract",
            "defaults",
            "distribution_policy",
            "entries",
            "entry_count",
            "overlay_id",
            "resource",
            "schema",
            "stock_jp",
        },
        "overlay root",
    )
    if root["schema"] != OVERLAY_SCHEMA or root["overlay_id"] != WORKSTREAM_ID:
        raise StrdataP0Error("overlay identity mismatch")
    if root["resource"] != RESOURCE or root["base_language"] != "JP":
        raise StrdataP0Error("overlay route mismatch")
    if root["entry_count"] != EXPECTED_COORDINATE_COUNT or not isinstance(root["entries"], list):
        raise StrdataP0Error("overlay entry count invalid")
    policy = require_keys(
        root["distribution_policy"],
        {"contains_commercial_source_text", "contains_complete_game_resource"},
        "overlay distribution policy",
    )
    if policy != {"contains_commercial_source_text": False, "contains_complete_game_resource": False}:
        raise StrdataP0Error("overlay distribution policy must declare source/resource free")
    stock = require_keys(root["stock_jp"], set(ACTIVE_PIN), "overlay stock_jp")
    if stock != ACTIVE_PIN:
        raise StrdataP0Error("overlay stock JP pin mismatch")
    contract = require_keys(
        root["coordinate_contract"],
        {"bundle_id", "coordinate_count", "coordinate_sha256", "path"},
        "overlay coordinate contract",
    )
    expected_contract = {
        "path": COORDINATE_CONTRACT.relative_to(REPOSITORY).as_posix(),
        "bundle_id": BUNDLE_ID,
        "coordinate_count": EXPECTED_COORDINATE_COUNT,
        "coordinate_sha256": EXPECTED_COORDINATE_SHA256,
    }
    if contract != expected_contract:
        raise StrdataP0Error("overlay coordinate-contract pin mismatch")
    defaults = require_keys(root["defaults"], {"status"}, "overlay defaults")
    if defaults != {"status": "translated"}:
        raise StrdataP0Error("overlay defaults mismatch")
    coordinates, source_hashes, _ = load_coordinate_contract()
    expected_keys = [(item["block_id"], item["slot_id"]) for item in coordinates]
    actual: dict[tuple[int, int], dict[str, Any]] = {}
    for entry in root["entries"]:
        value = require_keys(
            entry,
            {"block_id", "ko", "ko_utf16le_sha256", "slot_id", "source_jp_utf16le_sha256", "status"},
            "overlay entry",
        )
        block_id, slot_id = value["block_id"], value["slot_id"]
        if type(block_id) is not int or type(slot_id) is not int:
            raise StrdataP0Error("overlay coordinate type invalid")
        key = (block_id, slot_id)
        if key in actual:
            raise StrdataP0Error(f"duplicate overlay coordinate: {key}")
        if value["status"] != "translated":
            raise StrdataP0Error(f"unbuildable overlay status at {key}")
        if value["source_jp_utf16le_sha256"] != source_hashes.get(key):
            raise StrdataP0Error(f"source JP hash mismatch in overlay at {key}")
        require_hash(value["source_jp_utf16le_sha256"], f"source hash {key}")
        ko = value["ko"]
        if not isinstance(ko, str) or not common.has_semantic_text(ko):
            raise StrdataP0Error(f"non-semantic Korean replacement at {key}")
        if KANA_OR_CJK.search(ko) or not HANGUL.search(ko):
            raise StrdataP0Error(f"replacement is not Hangul-only Korean at {key}")
        if value["ko_utf16le_sha256"] != text_hash(ko):
            raise StrdataP0Error(f"Korean hash mismatch at {key}")
        actual[key] = value
    if list(actual) != expected_keys:
        raise StrdataP0Error("overlay coordinate order/set differs from exact P0 contract")
    return document, blob


def switch_member_bytes(path: Path) -> bytes:
    if not path.is_file():
        raise StrdataP0Error(f"Switch reference archive does not exist: {path}")
    actual_zip = {"size": path.stat().st_size, "sha256": sha256_file(path)}
    if actual_zip != SWITCH_ZIP_PIN:
        raise StrdataP0Error(f"Switch reference ZIP pin mismatch: {actual_zip}")
    try:
        with zipfile.ZipFile(path) as archive:
            member = archive.read(SWITCH_MEMBER)
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise StrdataP0Error(f"cannot read pinned Switch strdata member: {exc}") from exc
    return member


def derive_overlay(active_input: Path, old_jp_input: Path, switch_zip: Path, output: Path) -> dict[str, Any]:
    require_workstream_output(output)
    active_packed, _, active = parse_pinned_archive(active_input, ACTIVE_PIN, "active Steam JP")
    _, _, old = parse_pinned_archive(old_jp_input, OLD_JP_PIN, "official JP reference backup")
    switch_packed = switch_member_bytes(switch_zip)
    switch_raw = verify_packed_pin(switch_packed, SWITCH_MEMBER_PIN, "Switch v1.3 JP member")
    switch = parse_raw_strdata(switch_raw)
    coordinates, source_hashes, _ = load_coordinate_contract()
    active_text = coordinate_texts(active)
    old_text = coordinate_texts(old)
    switch_text = coordinate_texts(switch)
    entries: list[dict[str, Any]] = []
    reference_equivalent = 0
    for coordinate in coordinates:
        key = (coordinate["block_id"], coordinate["slot_id"])
        try:
            source = active_text[key]
            previous = old_text[key]
            korean = switch_text[key]
        except KeyError as exc:
            raise StrdataP0Error(f"coordinate outside strdata structure: {key}") from exc
        if source != previous:
            raise StrdataP0Error(f"active JP source differs from official JP reference at {key}")
        if text_hash(source) != source_hashes[key]:
            raise StrdataP0Error(f"active JP source hash differs from P0 contract at {key}")
        mismatches = common.invariant_mismatches(source, korean)
        if mismatches:
            raise StrdataP0Error(f"Switch Korean invariant mismatch at {key}: {mismatches!r}")
        if not common.has_semantic_text(korean) or KANA_OR_CJK.search(korean) or not HANGUL.search(korean):
            raise StrdataP0Error(f"Switch Korean value is not safe Hangul text at {key}")
        reference_equivalent += 1
        entries.append(
            {
                "block_id": key[0],
                "slot_id": key[1],
                "source_jp_utf16le_sha256": text_hash(source),
                "ko": korean,
                "ko_utf16le_sha256": text_hash(korean),
                "status": "translated",
            }
        )
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": WORKSTREAM_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": ACTIVE_PIN,
        "coordinate_contract": {
            "path": COORDINATE_CONTRACT.relative_to(REPOSITORY).as_posix(),
            "bundle_id": BUNDLE_ID,
            "coordinate_count": EXPECTED_COORDINATE_COUNT,
            "coordinate_sha256": EXPECTED_COORDINATE_SHA256,
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    atomic_write(output, json_bytes(overlay))
    checked, blob = load_overlay(output)
    if checked != overlay:
        raise StrdataP0Error("serialized overlay did not round-trip exactly")
    return {
        "action": "derive-overlay",
        "output": str(output),
        "output_size": len(blob),
        "output_sha256": sha256(blob),
        "translated_entries": len(entries),
        "exact_active_to_official_jp_source_matches": reference_equivalent,
        "game_install_modified": False,
        "release_modified": False,
        "github_modified": False,
    }


def build_candidate(active_input: Path, overlay_path: Path, output_dir: Path) -> dict[str, Any]:
    require_tmp_output(output_dir)
    packed, raw, archive = parse_pinned_archive(active_input, ACTIVE_PIN, "active Steam JP")
    overlay, overlay_blob = load_overlay(overlay_path)
    original_text = coordinate_texts(archive)
    replacements: dict[int, list[str]] = {}
    selected: dict[tuple[int, int], str] = {}
    for entry in overlay["entries"]:
        key = (entry["block_id"], entry["slot_id"])
        source = original_text.get(key)
        if source is None:
            raise StrdataP0Error(f"overlay coordinate absent from active source: {key}")
        if text_hash(source) != entry["source_jp_utf16le_sha256"]:
            raise StrdataP0Error(f"active JP source hash mismatch at {key}")
        mismatches = common.invariant_mismatches(source, entry["ko"])
        if mismatches:
            raise StrdataP0Error(f"replacement invariant mismatch at {key}: {mismatches!r}")
        block_id, slot_id = key
        if block_id not in replacements:
            replacements[block_id] = list(archive.blocks[block_id].texts)
        replacements[block_id][slot_id] = entry["ko"]
        selected[key] = entry["ko"]
    rebuilt_raw = rebuild_raw_strdata(archive, replacements)
    rebuilt_archive = parse_raw_strdata(rebuilt_raw)
    rebuilt_text = coordinate_texts(rebuilt_archive)
    if rebuilt_archive.block_count != archive.block_count or rebuilt_archive.slot_count != archive.slot_count:
        raise StrdataP0Error("candidate changed strdata block or slot count")
    for before, after in zip(archive.blocks, rebuilt_archive.blocks, strict=True):
        if before.inner_header != after.inner_header or before.slot_count != after.slot_count:
            raise StrdataP0Error(f"candidate changed protected structure in block {before.block_id}")
    for key, korean in selected.items():
        if rebuilt_text[key] != korean:
            raise StrdataP0Error(f"candidate replacement verification failed at {key}")
    unchanged = [key for key, text in original_text.items() if key not in selected and rebuilt_text.get(key) == text]
    if len(unchanged) != len(original_text) - len(selected):
        raise StrdataP0Error("candidate changed at least one non-selected text coordinate")
    candidate_packed = recompress_wrapper(rebuilt_raw, packed)
    try:
        _, roundtrip_raw = decompress_wrapper(candidate_packed)
    except Exception as exc:
        raise StrdataP0Error(f"candidate wrapper verification failed: {exc}") from exc
    if roundtrip_raw != rebuilt_raw:
        raise StrdataP0Error("candidate packed/raw round-trip differs")
    roundtrip_archive = parse_raw_strdata(roundtrip_raw)
    if coordinate_texts(roundtrip_archive) != rebuilt_text:
        raise StrdataP0Error("candidate packed parse differs from raw parse")
    candidate_path = output_dir / "candidate" / RESOURCE
    manifest_path = output_dir / "build_manifest.v1.json"
    require_tmp_output(candidate_path)
    require_tmp_output(manifest_path)
    atomic_write(candidate_path, candidate_packed)
    manifest = {
        "schema": BUILD_SCHEMA,
        "workstream_id": WORKSTREAM_ID,
        "resource": RESOURCE,
        "base_jp": ACTIVE_PIN,
        "overlay": {
            "path": str(overlay_path),
            "size": len(overlay_blob),
            "sha256": sha256(overlay_blob),
            "entry_count": len(selected),
            "coordinate_sha256": EXPECTED_COORDINATE_SHA256,
        },
        "candidate": {
            "path": candidate_path.relative_to(output_dir).as_posix(),
            "packed_size": len(candidate_packed),
            "packed_sha256": sha256(candidate_packed),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256(rebuilt_raw),
        },
        "validation": {
            "identity_raw_rebuild_byte_exact": True,
            "active_jp_pin_gated": True,
            "selected_replacements_verified": len(selected),
            "nonselected_text_coordinates_preserved": len(unchanged),
            "protected_inner_headers_preserved": True,
            "packed_roundtrip_byte_exact": True,
        },
        "distribution_policy": {
            "candidate_is_temporary_only": True,
            "game_install_modified": False,
            "release_modified": False,
            "github_modified": False,
        },
    }
    atomic_write(manifest_path, json_bytes(manifest))
    return manifest


def verify_candidate(active_input: Path, overlay_path: Path, output_dir: Path) -> dict[str, Any]:
    require_tmp_output(output_dir)
    manifest_path = output_dir / "build_manifest.v1.json"
    candidate_path = output_dir / "candidate" / RESOURCE
    manifest, _ = read_json(manifest_path)
    if manifest.get("schema") != BUILD_SCHEMA or manifest.get("resource") != RESOURCE:
        raise StrdataP0Error("candidate manifest identity mismatch")
    rebuilt = build_candidate(active_input, overlay_path, output_dir / "verification_rebuild")
    original_candidate = candidate_path.read_bytes()
    regenerated_candidate = (output_dir / "verification_rebuild" / "candidate" / RESOURCE).read_bytes()
    if original_candidate != regenerated_candidate:
        raise StrdataP0Error("candidate is not deterministic against a clean rebuild")
    if manifest.get("candidate", {}).get("packed_sha256") != sha256(original_candidate):
        raise StrdataP0Error("candidate manifest packed hash mismatch")
    return {
        "action": "verify-candidate",
        "candidate_path": str(candidate_path),
        "candidate_sha256": sha256(original_candidate),
        "regenerated_candidate_sha256": rebuilt["candidate"]["packed_sha256"],
        "deterministic": True,
        "game_install_modified": False,
        "release_modified": False,
        "github_modified": False,
    }


def deterministic_build(active_input: Path, overlay_path: Path, output_dir: Path) -> dict[str, Any]:
    require_tmp_output(output_dir)
    first = build_candidate(active_input, overlay_path, output_dir / "a")
    second = build_candidate(active_input, overlay_path, output_dir / "b")
    first_path = output_dir / "a" / "candidate" / RESOURCE
    second_path = output_dir / "b" / "candidate" / RESOURCE
    first_bytes, second_bytes = first_path.read_bytes(), second_path.read_bytes()
    if first_bytes != second_bytes:
        raise StrdataP0Error("two clean candidate builds are not byte-identical")
    result = {
        "action": "determinism",
        "candidate_sha256": sha256(first_bytes),
        "candidate_size": len(first_bytes),
        "first_raw_sha256": first["candidate"]["raw_sha256"],
        "second_raw_sha256": second["candidate"]["raw_sha256"],
        "byte_identical": True,
        "game_install_modified": False,
        "release_modified": False,
        "github_modified": False,
    }
    atomic_write(output_dir / "determinism.v1.json", json_bytes(result))
    return result


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)
    derive = subparsers.add_parser("derive-overlay", help="derive source-free overlay from pinned references")
    derive.add_argument("--active-input", type=Path, default=DEFAULT_ACTIVE_INPUT)
    derive.add_argument("--old-jp-input", type=Path, default=DEFAULT_OLD_JP_INPUT)
    derive.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
    derive.add_argument("--output", type=Path, default=DEFAULT_OVERLAY)
    for name, help_text in (("build", "build a temporary candidate"), ("verify", "rebuild and compare a temporary candidate"), ("determinism", "make two clean temporary candidates and compare bytes")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("--active-input", type=Path, default=DEFAULT_ACTIVE_INPUT)
        command.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
        command.add_argument("--output-dir", type=Path, required=True)
    return result


def main(argv: Iterable[str] | None = None) -> int:
    arguments = parser().parse_args(list(argv) if argv is not None else None)
    try:
        if arguments.command == "derive-overlay":
            result = derive_overlay(arguments.active_input, arguments.old_jp_input, arguments.switch_zip, arguments.output)
        elif arguments.command == "build":
            result = build_candidate(arguments.active_input, arguments.overlay, arguments.output_dir)
        elif arguments.command == "verify":
            result = verify_candidate(arguments.active_input, arguments.overlay, arguments.output_dir)
        elif arguments.command == "determinism":
            result = deterministic_build(arguments.active_input, arguments.overlay, arguments.output_dir)
        else:  # argparse makes this unreachable; preserve a defensive exit.
            raise StrdataP0Error(f"unsupported command: {arguments.command}")
    except (OSError, StrdataP0Error, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
