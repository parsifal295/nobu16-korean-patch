#!/usr/bin/env python3
"""Assemble the Steam PK 1.1.7 JP-route v0.7.0 ten-file candidate.

The v0.6.0 candidate workstream remains immutable.  This wrapper reuses its
reviewed ten-file container and ZIP gates while replacing only the three
components that advance in v0.7.0: msgui, msggame, and both JP font routes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
STEAM_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
STOCK_ROOT = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
DEFAULT_FONT_ROOT = (
    REPO
    / "tmp"
    / "font_jp_seoulhangang_wave07_final"
    / "private"
    / "candidate"
)
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_117_candidate_v2"
DEFAULT_ZIP_NAME = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.7.0.zip"
SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-manifest.v2"
VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-verification.v2"
VERIFICATION_PATH = WORKSTREAM / "verification.v2.json"
FONT_EVIDENCE = REPO / "workstreams" / "font_jp_seoulhangang_v1" / "verification.v1.json"
# Replaced with the reviewed final evidence hash after the wave07 font A/B build.
FONT_EVIDENCE_SHA256 = "6478308F1A3198FE0AAD10F05D6C7030C3C4F8093D112CB885738FE78306F68E"
SUPPLEMENT = (
    REPO
    / "workstreams"
    / "steam_jp_msgui_wave07_recovery"
    / "public"
    / "msgui_ko_pk_jp_steam_wave07_recovery_343.v1.json"
)
SUPPLEMENT_SHA256 = "3F89B1EB791686BBA4C1AFA790A157EB88F60DF14D746B81D437365201629B51"
SUPPLEMENT_COORDINATE_SHA256 = "BEF7EAE59645DBADEFFD31CB261BB0C366105715A58420987CDA339487D3219D"
SUPPLEMENT_WITHHELD_AUDIT_SHA256 = "B9E65B6360AAA48F097873D218052A8A1D74CDB6FE462BD79963A17D414A397E"
SUPPLEMENT_WITHHELD_COORDINATE_SHA256 = "040FC071EA485FDA3FBC5443F1253BDE6A351B3BFFC6F4ED5AB69A3823C916E4"
SUPPLEMENT_FOUNDATION_SHA256 = "1581C52901FE536AF45F4FD6225E8D94795FDA883798947B6610D5CF86E09424"
SUPPLEMENT_FOUNDATION_COORDINATE_SHA256 = "E1FFD90081D66D47E695E98AD1CE5BBA2EBADB6A5FE33EF7EA3CE1B5F7D0AF6F"
EXCLUDED_MSGUI_ID = 2_657
EXCLUDED_MSGUI_SOURCE_SHA256 = "869F1DFB999A452F497A4CF7F44DB2D6EE661F74A9E7E05251BC1420E50672D4"
SUPPLEMENT_COUNT = 343
MSGUI_MAPPED = 4_036
MSGUI_EFFECTIVE = 3_955
MSGUI_NOOPS = 81
MSGUI_WITHHELD = 1
MSGGAME_APPLIED = 28_272


class CandidateV2Error(RuntimeError):
    """A v0.7.0 component or pin failed closed."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CandidateV2Error(f"cannot import component: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(
    "nobu16_steam_jp_117_candidate_v2_base",
    REPO
    / "workstreams"
    / "steam_jp_117_candidate_v1"
    / "build_steam_jp_117_candidate_v1.py",
)
INTEGRATION = load_module(
    "nobu16_steam_jp_msggame_wave07_complete",
    REPO
    / "workstreams"
    / "msggame_pk_jp_native_wave07_integration"
    / "build_wave07_integration.py",
)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in pairs:
        normalized = key.casefold()
        if normalized in folded:
            raise CandidateV2Error(f"duplicate or case-colliding JSON key: {key!r}")
        folded.add(normalized)
        result[key] = value
    return result


def read_object(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    value = json.loads(
        blob.decode("utf-8"),
        object_pairs_hook=strict_pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(
            CandidateV2Error(f"invalid JSON constant: {value}")
        ),
    )
    if not isinstance(value, dict):
        raise CandidateV2Error(f"JSON root is not an object: {path}")
    return value, blob


def atomic_write(path: Path, blob: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise CandidateV2Error(f"atomic-write temporary already exists: {temporary}")
    try:
        with temporary.open("xb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def require_positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise CandidateV2Error(f"{label} must be a positive integer")
    return value


def require_upper_hash(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789ABCDEF" for char in value)
    ):
        raise CandidateV2Error(f"{label} must be uppercase SHA-256")
    return value


def load_msgui_supplement() -> list[dict[str, Any]]:
    value, blob = read_object(SUPPLEMENT)
    if sha256(blob) != SUPPLEMENT_SHA256:
        raise CandidateV2Error("msgui recovery supplement hash changed")
    if set(value) != {
        "base_language",
        "coordinate_sha256",
        "distribution_policy",
        "effective_change_count",
        "entries",
        "entry_count",
        "excluded_entry_count",
        "foundation",
        "no_op_count",
        "resource",
        "runtime_version",
        "schema",
        "semantic_review",
        "stock_jp",
        "supplement_id",
        "withheld_input",
    }:
        raise CandidateV2Error("msgui recovery supplement top-level shape changed")
    if (
        value.get("schema") != "nobu16.kr.steam-jp-msgui-supplement.v1"
        or value.get("resource") != BASE.MSGUI.RESOURCE
        or value.get("base_language") != "JP"
        or value.get("runtime_version") != "1.1.7"
        or value.get("entry_count") != SUPPLEMENT_COUNT
        or value.get("effective_change_count") != 341
        or value.get("no_op_count") != 2
        or value.get("excluded_entry_count") != MSGUI_WITHHELD
    ):
        raise CandidateV2Error("msgui recovery supplement contract changed")
    policy = value.get("distribution_policy")
    if policy != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise CandidateV2Error("msgui recovery supplement is not source-free")
    if value.get("stock_jp") != BASE.MSGUI.stock_spec():
        raise CandidateV2Error("msgui recovery stock pin changed")
    if value.get("foundation") != {
        "sha256": SUPPLEMENT_FOUNDATION_SHA256,
        "entry_count": 3_693,
        "coordinate_sha256": SUPPLEMENT_FOUNDATION_COORDINATE_SHA256,
    }:
        raise CandidateV2Error("msgui recovery foundation pin changed")
    if value.get("withheld_input") != {
        "audit_sha256": SUPPLEMENT_WITHHELD_AUDIT_SHA256,
        "entry_count": 344,
        "coordinate_sha256": SUPPLEMENT_WITHHELD_COORDINATE_SHA256,
    }:
        raise CandidateV2Error("msgui recovery withheld partition changed")
    if value.get("coordinate_sha256") != SUPPLEMENT_COORDINATE_SHA256:
        raise CandidateV2Error("msgui recovery coordinate hash changed")
    raw_entries = value.get("entries")
    if not isinstance(raw_entries, list) or len(raw_entries) != SUPPLEMENT_COUNT:
        raise CandidateV2Error("msgui recovery supplement entries changed")
    entries: list[dict[str, Any]] = []
    ids: list[int] = []
    for index, item in enumerate(raw_entries):
        if not isinstance(item, dict) or set(item) != {
            "id",
            "source_jp_utf16le_sha256",
            "ko",
        }:
            raise CandidateV2Error(f"msgui recovery entry {index} has an unsafe shape")
        entry_id = item["id"]
        source_hash = item["source_jp_utf16le_sha256"]
        ko = item["ko"]
        if (
            isinstance(entry_id, bool)
            or not isinstance(entry_id, int)
            or not 0 <= entry_id < BASE.MSGUI.STOCK_STRING_COUNT
            or not isinstance(source_hash, str)
            or len(source_hash) != 64
            or any(char not in "0123456789ABCDEF" for char in source_hash)
            or not isinstance(ko, str)
            or not BASE.MSGUI.has_semantic_text(ko)
            or BASE.MSGUI.has_cjk_or_kana(ko)
            or "\0" in ko
            or "\ufffd" in ko
            or not unicodedata.is_normalized("NFC", ko)
        ):
            raise CandidateV2Error(f"msgui recovery entry {index} is invalid")
        ids.append(entry_id)
        entries.append(dict(item))
    if ids != sorted(set(ids)):
        raise CandidateV2Error("msgui recovery IDs are not sorted and unique")
    audit_path = BASE.MSGUI.DEFAULT_AUDIT
    audit, audit_blob = read_object(audit_path)
    if sha256(audit_blob) != SUPPLEMENT_WITHHELD_AUDIT_SHA256:
        raise CandidateV2Error("msgui v1 withheld audit hash changed")
    result = audit.get("result")
    if not isinstance(result, dict):
        raise CandidateV2Error("msgui v1 withheld audit result is malformed")
    reason_dictionary = result.get("reason_dictionary")
    withheld_rows = result.get("unmapped_entries")
    if (
        not isinstance(reason_dictionary, list)
        or not isinstance(withheld_rows, list)
        or any(not isinstance(row, list) or len(row) != 4 for row in withheld_rows)
    ):
        raise CandidateV2Error("msgui v1 withheld audit rows are malformed")
    withheld_ids = {int(row[0]) for row in withheld_rows}
    excluded_rows = [row for row in withheld_rows if int(row[0]) == EXCLUDED_MSGUI_ID]
    if (
        set(ids) | {EXCLUDED_MSGUI_ID} != withheld_ids
        or set(ids) & {EXCLUDED_MSGUI_ID}
        or BASE.MSGUI.coordinate_hash(withheld_ids) != SUPPLEMENT_WITHHELD_COORDINATE_SHA256
        or len(excluded_rows) != 1
        or excluded_rows[0][2] != EXCLUDED_MSGUI_SOURCE_SHA256
    ):
        raise CandidateV2Error("msgui recovery is not the exact withheld partition minus ID 2657")
    return entries


def build_msgui(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    contract, foundation, _overlay_blob = BASE.MSGUI.load_frozen_inputs(
        BASE.MSGUI.DEFAULT_CONTRACT
    )
    supplement = load_msgui_supplement()
    foundation_ids = {int(entry["id"]) for entry in foundation}
    supplement_ids = {int(entry["id"]) for entry in supplement}
    if foundation_ids & supplement_ids:
        raise CandidateV2Error("msgui foundation and recovery supplement overlap")
    entries = sorted([*foundation, *supplement], key=lambda entry: int(entry["id"]))
    if len(entries) != MSGUI_MAPPED:
        raise CandidateV2Error("msgui combined entry count changed")
    _path, packed, raw, table = BASE.MSGUI.load_stock(stock_root)
    candidate, candidate_raw, changed = BASE.MSGUI.candidate_from_entries(
        packed, raw, table, entries
    )
    observed_noops = len(entries) - len(changed)
    if len(changed) != MSGUI_EFFECTIVE or observed_noops != MSGUI_NOOPS:
        raise CandidateV2Error("msgui effective/no-op accounting changed")
    if contract["overlay"]["unmapped_entry_count"] != 344:
        raise CandidateV2Error("msgui v1 withheld foundation changed")
    return candidate, {
        "builder": "steam_jp_msgui_v1+wave07_recovery",
        "mapped_entries": len(entries),
        "effective_changes": len(changed),
        "unmapped_entries": MSGUI_WITHHELD,
        "foundation_sha256": SUPPLEMENT_FOUNDATION_SHA256,
        "supplement_sha256": SUPPLEMENT_SHA256,
        "supplement_coordinate_sha256": SUPPLEMENT_COORDINATE_SHA256,
        "withheld_audit_sha256": SUPPLEMENT_WITHHELD_AUDIT_SHA256,
        "excluded_id": EXCLUDED_MSGUI_ID,
        "excluded_source_jp_utf16le_sha256": EXCLUDED_MSGUI_SOURCE_SHA256,
        "candidate": {
            "size": len(candidate),
            "sha256": sha256(candidate),
            "raw_size": len(candidate_raw),
            "raw_sha256": sha256(candidate_raw),
        },
    }


def build_msggame(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    stock_path = stock_root / Path(INTEGRATION.RESOURCE)
    candidate, manifest, integration = INTEGRATION.build_complete(stock_path)
    translation = manifest.get("translation")
    if translation != {
        "applied_entry_count": MSGGAME_APPLIED,
        "semantic_target_count": MSGGAME_APPLIED,
        "remaining_jp_semantic_count": 0,
    }:
        raise CandidateV2Error("complete msggame accounting changed")
    return candidate, {
        "builder": "steam_jp_msggame_v1+wave07_integration",
        "applied_entries": MSGGAME_APPLIED,
        "remaining_jp_semantic": 0,
        "wave07_entries": integration["coordinate_count"],
        "wave07_coordinates_sha256": integration["coordinates_sha256"],
        "wave07_unique_source_hash_count": integration["unique_source_hash_count"],
        "wave07_contextual_variant_source_count": integration[
            "contextual_variant_source_count"
        ],
        "wave07_overlays": integration["overlay_rows"],
        "candidate": {"size": len(candidate), "sha256": sha256(candidate)},
    }


def configure_font_candidates(font_root: Path) -> dict[str, Any]:
    evidence, blob = read_object(FONT_EVIDENCE)
    evidence_hash = sha256(blob)
    if evidence_hash != FONT_EVIDENCE_SHA256:
        raise CandidateV2Error(
            f"JP font evidence hash changed: {evidence_hash} != {FONT_EVIDENCE_SHA256}"
        )
    if set(evidence) != {
        "schema",
        "public_source_free",
        "private_binary_payload_included",
        "stock_archives",
        "pk_runtime_route_evidence",
        "demand",
        "official_font_pin",
        "g1n_structure",
        "stock_reuse_evidence",
        "independent_private_builds",
        "preservation_contract",
        "expected_private_outputs",
    }:
        raise CandidateV2Error("JP font evidence top-level shape changed")
    if (
        evidence.get("schema") != "nobu16.kr.font-jp-seoulhangang-v1-verification.v1"
        or evidence.get("public_source_free") is not True
        or evidence.get("private_binary_payload_included") is not False
    ):
        raise CandidateV2Error("JP font evidence policy changed")
    stocks = evidence.get("stock_archives")
    if not isinstance(stocks, dict) or set(stocks) != set(BASE.RUNTIME.FONT_RESOURCES):
        raise CandidateV2Error("JP font stock vector changed")
    for relative, contract in BASE.RUNTIME.FONT_RESOURCES.items():
        stock = stocks[relative]
        if not isinstance(stock, dict) or {
            "size": stock.get("size"),
            "sha256": stock.get("sha256"),
        } != contract["stock"]:
            raise CandidateV2Error(f"JP font stock pin changed: {relative}")
    preservation = evidence.get("preservation_contract")
    required_preservation = {
        "stock_hash_gate_fail_closed": True,
        "non_target_link_entries_exact": True,
        "non_target_g1t_and_nested_payloads_exact": True,
        "existing_maps_exact_outside_append_codepoints": True,
        "existing_records_exact": True,
        "palette_exact": True,
        "complete_stock_atlas_exact_prefix": True,
        "gdi_font_fallback_allowed": False,
        "stock_reuse_pixels_copied_to_new_table2_tail": True,
        "direct_stock_pointer_alias_allowed": False,
        "switch_archive_raw_copy": False,
        "installed_game_files_modified": False,
    }
    if preservation != required_preservation:
        raise CandidateV2Error("JP font preservation contract changed")
    demand = evidence.get("demand")
    if not isinstance(demand, dict):
        raise CandidateV2Error("JP font demand evidence is incomplete")
    require_positive_int(demand.get("source_count"), "font demand source_count")
    require_positive_int(
        demand.get("source_entry_count"), "font demand source_entry_count"
    )
    require_positive_int(demand.get("codepoint_count"), "font demand codepoint_count")
    require_positive_int(
        demand.get("hangul_syllable_count"), "font demand hangul_syllable_count"
    )
    require_upper_hash(demand.get("codepoints_sha256"), "font demand codepoints")
    require_upper_hash(
        demand.get("hangul_syllables_sha256"), "font demand Hangul syllables"
    )
    expected = evidence.get("expected_private_outputs")
    if not isinstance(expected, dict) or not isinstance(expected.get("routes"), list):
        raise CandidateV2Error("JP font verification has no expected routes")
    routes = expected["routes"]
    if len(routes) != len(BASE.RUNTIME.FONT_RESOURCES):
        raise CandidateV2Error("JP font route count changed")
    normalized: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(routes):
        if not isinstance(row, dict):
            raise CandidateV2Error(f"JP font route {index} is not an object")
        relative = row.get("logical_path")
        size = row.get("candidate_archive_size")
        digest = row.get("candidate_archive_sha256")
        if (
            relative in normalized
            or relative not in BASE.RUNTIME.FONT_RESOURCES
            or isinstance(size, bool)
            or not isinstance(size, int)
            or size <= 0
            or not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789ABCDEF" for char in digest)
        ):
            raise CandidateV2Error(f"invalid JP font candidate route {index}")
        normalized[str(relative)] = {"size": size, "sha256": digest}
    if set(normalized) != set(BASE.RUNTIME.FONT_RESOURCES):
        raise CandidateV2Error("JP font verification route vector changed")
    for relative, candidate in normalized.items():
        BASE.RUNTIME.FONT_RESOURCES[relative]["candidate"] = candidate
    BASE.RUNTIME.FONT_CANDIDATE_ROOT = font_root.resolve()
    return {
        "evidence_path": FONT_EVIDENCE.relative_to(REPO).as_posix(),
        "evidence_sha256": evidence_hash,
        "demand": demand,
        "routes": normalized,
    }


def verification_projection(manifest: dict[str, Any]) -> dict[str, Any]:
    msgui = manifest["components"]["msgui"]
    msggame = manifest["components"]["msggame"]
    common = manifest["components"]["common_messages"]
    strdata = manifest["components"]["strdata"]
    fonts = manifest["components"]["fonts"]
    return {
        "schema": VERIFICATION_SCHEMA,
        "runtime": manifest["runtime"],
        "candidate_file_count": manifest["candidate_file_count"],
        "candidate_paths": manifest["candidate_paths"],
        "predecessors": manifest["predecessors"],
        "candidates": manifest["candidates"],
        "translation": {
            "strdata_applied": strdata["applied_entries"],
            "msgui_mapped": msgui["mapped_entries"],
            "msgui_effective_changes": msgui["effective_changes"],
            "msgui_unmapped": msgui["unmapped_entries"],
            "common_messages_applied": common["applied_entries"],
            "common_messages_unresolved": common["unresolved_entries"],
            "msggame_applied": msggame["applied_entries"],
            "msggame_remaining_jp_semantic": msggame["remaining_jp_semantic"],
        },
        "provenance": {
            "msgui": {
                key: msgui[key]
                for key in (
                    "foundation_sha256",
                    "supplement_sha256",
                    "supplement_coordinate_sha256",
                    "withheld_audit_sha256",
                    "excluded_id",
                    "excluded_source_jp_utf16le_sha256",
                )
            },
            "msggame": {
                key: msggame[key]
                for key in (
                    "wave07_entries",
                    "wave07_coordinates_sha256",
                    "wave07_unique_source_hash_count",
                    "wave07_contextual_variant_source_count",
                    "wave07_overlays",
                )
            },
            "fonts": fonts["evidence"],
        },
        "zip": manifest["zip"],
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "component_candidate_pins_exact": True,
            "exact_ten_files": True,
            "zip_payloads_equal_candidates": True,
            "staged_before_promote": True,
            "sc_container_used": False,
            "steam_files_written": False,
        },
    }


def validate_destination(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise CandidateV2Error(f"output must be below repository tmp: {resolved}")
    if resolved.exists():
        raise CandidateV2Error(f"output already exists: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def build_staged(
    stock_root: Path, font_root: Path, staging: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    before = BASE.predecessor_vector(stock_root)
    font_evidence = configure_font_candidates(font_root)
    strdata, strdata_meta = BASE.build_strdata(stock_root)
    msgui, msgui_meta = build_msgui(stock_root)
    common, common_meta = BASE.build_common(stock_root)
    msggame, msggame_meta = build_msggame(stock_root)
    candidate_root = staging / "candidate"
    candidates: dict[str, dict[str, Any]] = {}
    candidates["MSG/JP/strdata.bin"] = BASE.write_candidate_file(
        candidate_root, "MSG/JP/strdata.bin", strdata
    )
    candidates["MSG_PK/JP/msgui.bin"] = BASE.write_candidate_file(
        candidate_root, "MSG_PK/JP/msgui.bin", msgui
    )
    for name, blob in common.items():
        relative = f"MSG_PK/JP/{name}"
        candidates[relative] = BASE.write_candidate_file(candidate_root, relative, blob)
    candidates["MSG_PK/JP/msggame.bin"] = BASE.write_candidate_file(
        candidate_root, "MSG_PK/JP/msggame.bin", msggame
    )
    for relative, route in BASE.RUNTIME.FONT_RESOURCES.items():
        source = BASE.RUNTIME.FONT_CANDIDATE_ROOT / Path(relative)
        observed = BASE.copy_candidate_file(candidate_root, relative, source)
        if observed != route["candidate"]:
            raise CandidateV2Error(f"font candidate pin mismatch: {relative}")
        candidates[relative] = observed
    if BASE.candidate_files(candidate_root) != list(BASE.TARGETS):
        raise CandidateV2Error("candidate root is not the exact ten-file vector")
    if set(candidates) != set(BASE.TARGETS):
        raise CandidateV2Error("candidate manifest does not cover the exact target vector")
    if BASE.predecessor_vector(stock_root) != before:
        raise CandidateV2Error("Steam stock vector changed during offline build")
    zip_path = staging / DEFAULT_ZIP_NAME
    if zip_path.parent != staging or zip_path.exists():
        raise CandidateV2Error("unsafe fixed ZIP destination")
    zip_spec = BASE.make_zip(candidate_root, zip_path)
    manifest = {
        "schema": SCHEMA,
        "runtime": {
            "distribution": "Steam",
            "pk_version": "1.1.7",
            "steam_build_id": 18_823_764,
            "language_route": "JP",
        },
        "candidate_root": "candidate",
        "candidate_file_count": len(candidates),
        "candidate_paths": list(BASE.TARGETS),
        "predecessors": before,
        "candidates": {key: candidates[key] for key in BASE.TARGETS},
        "components": {
            "strdata": strdata_meta,
            "msgui": msgui_meta,
            "common_messages": common_meta,
            "msggame": msggame_meta,
            "fonts": {
                "builder": "font_jp_seoulhangang_v1",
                "evidence": font_evidence,
                "routes": {
                    relative: candidates[relative]
                    for relative in BASE.RUNTIME.FONT_RESOURCES
                },
            },
        },
        "zip": {
            "name": DEFAULT_ZIP_NAME,
            **zip_spec,
            "member_count": len(BASE.TARGETS),
        },
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "jp_route_exact": True,
            "exact_ten_files": True,
            "component_candidate_pins_exact": True,
            "zip_payloads_equal_candidates": True,
            "staged_before_promote": True,
            "sc_container_used": False,
            "memory_patch": False,
            "dll_injection": False,
            "hooking": False,
            "exe_or_registry_modified": False,
            "steam_files_written": False,
        },
    }
    projection = verification_projection(manifest)
    (staging / "candidate_manifest.v2.json").write_bytes(BASE.json_bytes(manifest))
    return manifest, projection


def staged_build(
    stock_root: Path, font_root: Path, destination_parent: Path
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    staging = Path(
        tempfile.mkdtemp(prefix=".steam-jp-117-v2-", dir=destination_parent)
    )
    try:
        manifest, projection = build_staged(stock_root, font_root, staging)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return staging, manifest, projection


def load_tracked_verification() -> dict[str, Any]:
    value, _blob = read_object(VERIFICATION_PATH)
    if value.get("schema") != VERIFICATION_SCHEMA:
        raise CandidateV2Error("tracked v2 verification schema changed")
    return value


def command_bootstrap(args: argparse.Namespace) -> int:
    proposal = validate_destination(args.proposal)
    staging, _manifest, projection = staged_build(
        args.stock_root.resolve(),
        args.font_candidate_root.resolve(),
        proposal.parent,
    )
    try:
        atomic_write(proposal, BASE.json_bytes(projection))
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    print(f"proposal={proposal}")
    print(f"proposal_sha256={BASE.sha256_path(proposal)}")
    print("candidate_outputs_retained=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    output = validate_destination(args.output_root)
    staging, manifest, projection = staged_build(
        args.stock_root.resolve(),
        args.font_candidate_root.resolve(),
        output.parent,
    )
    try:
        if projection != expected:
            raise CandidateV2Error("integrated candidate differs from tracked verification pin")
        os.replace(staging, output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    print("status=PASS")
    print(f"steam_pk_version={manifest['runtime']['pk_version']}")
    print(f"steam_build_id={manifest['runtime']['steam_build_id']}")
    print(f"candidate_files={manifest['candidate_file_count']}")
    print(f"zip_name={manifest['zip']['name']}")
    print(f"zip_sha256={manifest['zip']['sha256']}")
    print("steam_files_written=False")
    return 0


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--stock-root", type=Path, default=STOCK_ROOT)
    parser.add_argument("--font-candidate-root", type=Path, default=DEFAULT_FONT_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    bootstrap = commands.add_parser(
        "bootstrap", help="emit only a source-free proposed verification pin"
    )
    add_common_arguments(bootstrap)
    bootstrap.add_argument(
        "--proposal",
        type=Path,
        default=REPO / "tmp" / "steam_jp_117_candidate_v2.proposed.json",
    )
    bootstrap.set_defaults(handler=command_bootstrap)
    build = commands.add_parser("build", help="stage, verify, and promote the ten files")
    add_common_arguments(build)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.set_defaults(handler=command_build)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (CandidateV2Error, BASE.CandidateError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
