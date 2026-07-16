#!/usr/bin/env python3
"""Assemble and build the active Steam JP P0 strdata integration candidate.

Four independently pinned source-free Korean overlays contribute 1,400
replacements.  The final six P0 coordinates are official credits and are
carried as a separately pinned no-change hold.  The candidate always starts
from the active Steam JP v6 baseline; it is written only below this
workstream's temporary output root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPOSITORY = SCRIPT.parents[2]
GAME_ROOT = REPOSITORY.parent
TOOLS = REPOSITORY / "tools"
STRDATA_TOOLS = REPOSITORY / "workstreams" / "strdata"
sys.path[:0] = [str(TOOLS), str(STRDATA_TOOLS)]

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


RESOURCE = "MSG/JP/strdata.bin"
WORKSTREAM_ID = "steam-jp-strdata-p0-integrated-1400-v1"
COMBINED_SCHEMA = "nobu16.kr.strdata-p0-combined-overlay.v1"
BUILD_SCHEMA = "nobu16.kr.strdata-p0-combined-build-manifest.v1"
COMBINED_NAME = "strdata_ko_steam_jp_p0_combined_1400.v1.json"
COMBINED_PATH = WORKSTREAM / "public" / COMBINED_NAME
TMP_ROOT = REPOSITORY / "tmp" / "steam_jp_strdata_p0_integrated_v1"
DEFAULT_ACTIVE = Path(r"F:\SteamLibrary\steamapps\common\NOBU16") / RESOURCE
KANA_OR_CJK = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
REAL_HANGUL = re.compile(r"[\uac00-\ud7a3]")

ACTIVE_PIN = {
    "size": 956_835,
    "packed_sha256": "E77CD1F5CB72789B12B68FE0C1767950C0F54B1A62C9BB671CB14661D7378034",
    "raw_size": 953_072,
    "raw_sha256": "A3410438A13B2DB4C72B56B804BDF4ACABBEE8954203CA13D210AD848134BF66",
    "block_count": 5,
    "slot_count": 32_311,
}

COMPONENTS = (
    {
        "id": "p0-b01",
        "path": REPOSITORY / "workstreams" / "steam_jp_strdata_p0_b01_v1" / "public" / "strdata_ko_steam_jp_p0_b01_350.v1.json",
        "sha256": "A84553BBC2816FF9DA0C48C1D54AF89A6EE2CF7CE7730E5C2C5CF469AB407287",
        "entry_count": 350,
        "coordinate_sha256": "5DA0F1C55931DDC450755E7E6197F1B5B91E7AD9E11805DA4AA7B9287D427B65",
        "kind": "translated",
    },
    {
        "id": "p0-b02",
        "path": REPOSITORY / "workstreams" / "steam_jp_strdata_p0_b02_v1" / "public" / "strdata_ko_steam_jp_p0_b02_350.v1.json",
        "sha256": "D72A50C02963BC6C46C125B25582FA39DA841792736B16052BFE5F2A8038D2C6",
        "entry_count": 350,
        "coordinate_sha256": "8083C00E140022FD59D6BDCF3CE100DE6BA96C6070237CB3BFEA9D641C73EC6B",
        "kind": "translated",
    },
    {
        "id": "p0-b03",
        "path": REPOSITORY / "workstreams" / "steam_jp_strdata_p0_b03_v1" / "public" / "strdata_ko_steam_jp_p0_b03_350.v1.json",
        "sha256": "555E50404BA8FCFBF5C1A1D1BE83825626C7C9DCF976E5CA3AD211B0DD594152",
        "entry_count": 350,
        "coordinate_sha256": "E93B58820385F38A01F4DD54E6D3EA28B2771E19E05E589BBF56DC469FFC7815",
        "kind": "translated",
    },
    {
        "id": "p0-b04",
        "path": REPOSITORY / "workstreams" / "steam_jp_strdata_p0_b04_v1" / "public" / "strdata_ko_steam_jp_p0_b04_350.v1.json",
        "sha256": "EF45441B5DAB00B6F569A3FD5F6BF4538F2FE0E02DE1512FEE60B4C65A8A92F2",
        "entry_count": 350,
        "coordinate_sha256": "E676D17E1541F9F6B94887F8C1EF4502F54B3BCE2A0A4F2254FB1491FBD4C510",
        "kind": "translated",
    },
    {
        "id": "p0-b05-credit-hold",
        "path": REPOSITORY / "workstreams" / "steam_jp_strdata_p0_b05_credit_hold_v1" / "public" / "strdata_ko_steam_jp_p0_b05_credit_hold.v1.json",
        "sha256": "DD28D44C009D8766FEA191732D368A0BFD972A6E170594047D65F77DA010C239",
        "entry_count": 6,
        "coordinate_sha256": "FAE4643A1B9E1AF483CCB16CAB2828357E39796A45256FD1835BEF975CDAFB9F",
        "kind": "credit_hold",
    },
)
B04_NONWORD_COORDINATES = frozenset({(1, 876), (1, 1608)})


class IntegrationError(ValueError):
    pass


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_hash(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write(path: Path, value: bytes) -> None:
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
        return True
    except ValueError:
        return False


def require_tmp(path: Path) -> None:
    if not under(path, TMP_ROOT):
        raise IntegrationError(f"candidate output must remain below {TMP_ROOT}: {path}")


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        return common.load_json_strict(path)
    except Exception as exc:
        raise IntegrationError(f"invalid JSON {path}: {exc}") from exc


def coordinate(entry: dict[str, Any]) -> tuple[int, int]:
    try:
        block_id, slot_id = entry["block_id"], entry["slot_id"]
    except KeyError as exc:
        raise IntegrationError("entry lacks strdata coordinate") from exc
    if type(block_id) is not int or type(slot_id) is not int or block_id < 0 or slot_id < 0:
        raise IntegrationError("entry coordinate is invalid")
    return block_id, slot_id


def validate_component(component: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    document, blob = load_json(component["path"])
    if sha256(blob) != component["sha256"]:
        raise IntegrationError(f"component hash drift: {component['id']}")
    if document.get("resource") != RESOURCE or document.get("base_language") != "JP" or document.get("stock_jp") != ACTIVE_PIN:
        raise IntegrationError(f"component route/base drift: {component['id']}")
    if document.get("entry_count") != component["entry_count"]:
        raise IntegrationError(f"component count drift: {component['id']}")
    contract = document.get("coordinate_contract")
    if not isinstance(contract, dict) or contract.get("coordinate_sha256") != component["coordinate_sha256"]:
        raise IntegrationError(f"component coordinate pin drift: {component['id']}")
    policy = document.get("distribution_policy")
    if policy != {"contains_commercial_source_text": False, "contains_complete_game_resource": False}:
        raise IntegrationError(f"component policy drift: {component['id']}")
    entries = document.get("entries")
    if not isinstance(entries, list) or len(entries) != component["entry_count"]:
        raise IntegrationError(f"component entries drift: {component['id']}")
    translated: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    keys: list[tuple[int, int]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise IntegrationError(f"non-object entry in {component['id']}")
        key = coordinate(entry)
        keys.append(key)
        source_hash = entry.get("source_jp_utf16le_sha256")
        if not isinstance(source_hash, str) or len(source_hash) != 64:
            raise IntegrationError(f"source hash invalid in {component['id']}:{key}")
        if component["kind"] == "translated":
            korean = entry.get("ko")
            if entry.get("status") != "translated" or not isinstance(korean, str) or not common.has_semantic_text(korean):
                raise IntegrationError(f"translated entry invalid in {component['id']}:{key}")
            if KANA_OR_CJK.search(korean):
                raise IntegrationError(f"Japanese/CJK glyph in {component['id']}:{key}")
            if not REAL_HANGUL.search(korean) and key not in B04_NONWORD_COORDINATES:
                raise IntegrationError(f"unapproved non-word Korean value in {component['id']}:{key}")
            if entry.get("ko_utf16le_sha256") != text_hash(korean):
                raise IntegrationError(f"Korean hash invalid in {component['id']}:{key}")
            translated.append({"block_id": key[0], "slot_id": key[1], "source_jp_utf16le_sha256": source_hash, "ko": korean, "ko_utf16le_sha256": text_hash(korean), "status": "translated"})
        else:
            if entry.get("status") != "deferred_credit_attribution_review" or entry.get("reason_code") != "official_credit_attribution_preserved" or "ko" in entry:
                raise IntegrationError(f"credit-hold entry invalid in {component['id']}:{key}")
            deferred.append({"block_id": key[0], "slot_id": key[1], "source_jp_utf16le_sha256": source_hash, "status": entry["status"], "reason_code": entry["reason_code"]})
    if len(set(keys)) != len(keys) or canonical_hash([{"block_id": key[0], "slot_id": key[1]} for key in keys]) != component["coordinate_sha256"]:
        raise IntegrationError(f"component coordinate set/order drift: {component['id']}")
    return translated, deferred, {"id": component["id"], "path": component["path"].relative_to(REPOSITORY).as_posix(), "sha256": component["sha256"], "entry_count": component["entry_count"], "coordinate_sha256": component["coordinate_sha256"], "kind": component["kind"]}


def load_components() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    translated: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for component in COMPONENTS:
        new_translated, new_deferred, info = validate_component(component)
        for entry in new_translated + new_deferred:
            key = coordinate(entry)
            if key in seen:
                raise IntegrationError(f"overlap across P0 components: {key}")
            seen.add(key)
        translated.extend(new_translated)
        deferred.extend(new_deferred)
        metadata.append(info)
    if len(translated) != 1_400 or len(deferred) != 6 or len(seen) != 1_406:
        raise IntegrationError("P0 aggregate count mismatch")
    return translated, deferred, metadata


def assemble(output: Path) -> dict[str, Any]:
    if not under(output, WORKSTREAM):
        raise IntegrationError(f"combined overlay must remain below workstream: {output}")
    translated, deferred, components = load_components()
    all_coordinates = [{"block_id": entry["block_id"], "slot_id": entry["slot_id"]} for entry in translated + deferred]
    overlay = {
        "schema": COMBINED_SCHEMA,
        "overlay_id": WORKSTREAM_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "stock_jp": ACTIVE_PIN,
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "components": components,
        "translated_entry_count": len(translated),
        "deferred_credit_entry_count": len(deferred),
        "all_p0_coordinate_count": len(all_coordinates),
        "all_p0_coordinate_sha256": canonical_hash(all_coordinates),
        "translated_entries": translated,
        "deferred_credit_entries": deferred,
    }
    write(output, json_bytes(overlay))
    checked, blob = load_combined(output)
    if checked != overlay:
        raise IntegrationError("combined overlay did not round-trip exactly")
    return {"action": "assemble", "output": str(output), "output_size": len(blob), "output_sha256": sha256(blob), "translated_entries": len(translated), "deferred_credit_entries": len(deferred), "all_p0_entries": len(all_coordinates), "game_install_modified": False, "release_modified": False, "github_modified": False}


def load_combined(path: Path) -> tuple[dict[str, Any], bytes]:
    document, blob = load_json(path)
    if document.get("schema") != COMBINED_SCHEMA or document.get("overlay_id") != WORKSTREAM_ID or document.get("resource") != RESOURCE or document.get("base_language") != "JP" or document.get("stock_jp") != ACTIVE_PIN:
        raise IntegrationError("combined overlay identity/base mismatch")
    if document.get("distribution_policy") != {"contains_commercial_source_text": False, "contains_complete_game_resource": False}:
        raise IntegrationError("combined overlay policy mismatch")
    translated, deferred, metadata = load_components()
    if document.get("components") != metadata or document.get("translated_entries") != translated or document.get("deferred_credit_entries") != deferred:
        raise IntegrationError("combined overlay component content drift")
    all_coordinates = [{"block_id": entry["block_id"], "slot_id": entry["slot_id"]} for entry in translated + deferred]
    if document.get("translated_entry_count") != 1_400 or document.get("deferred_credit_entry_count") != 6 or document.get("all_p0_coordinate_count") != 1_406 or document.get("all_p0_coordinate_sha256") != canonical_hash(all_coordinates):
        raise IntegrationError("combined overlay aggregate count/hash drift")
    return document, blob


def read_active(path: Path) -> tuple[bytes, bytes, Any]:
    if not path.is_file():
        raise IntegrationError(f"active JP source missing: {path}")
    packed = path.read_bytes()
    if {"size": len(packed), "packed_sha256": sha256(packed)} != {"size": ACTIVE_PIN["size"], "packed_sha256": ACTIVE_PIN["packed_sha256"]}:
        raise IntegrationError("active JP packed baseline mismatch")
    _, raw = decompress_wrapper(packed)
    if {"raw_size": len(raw), "raw_sha256": sha256(raw)} != {"raw_size": ACTIVE_PIN["raw_size"], "raw_sha256": ACTIVE_PIN["raw_sha256"]}:
        raise IntegrationError("active JP raw baseline mismatch")
    archive = parse_raw_strdata(raw)
    if archive.block_count != ACTIVE_PIN["block_count"] or archive.slot_count != ACTIVE_PIN["slot_count"] or rebuild_raw_strdata(archive) != raw:
        raise IntegrationError("active JP strdata structure/identity mismatch")
    return packed, raw, archive


def build_candidate(active_path: Path, overlay_path: Path, output_dir: Path) -> dict[str, Any]:
    require_tmp(output_dir)
    packed, _, archive = read_active(active_path)
    overlay, overlay_blob = load_combined(overlay_path)
    original = coordinate_texts(archive)
    replacements: dict[int, list[str]] = {}
    selected: dict[tuple[int, int], str] = {}
    for entry in overlay["translated_entries"]:
        key = coordinate(entry)
        source = original.get(key)
        if source is None or text_hash(source) != entry["source_jp_utf16le_sha256"]:
            raise IntegrationError(f"translated active source hash mismatch: {key}")
        mismatches = common.invariant_mismatches(source, entry["ko"])
        if mismatches:
            raise IntegrationError(f"translated formatting invariant mismatch at {key}: {mismatches!r}")
        if key[0] not in replacements:
            replacements[key[0]] = list(archive.blocks[key[0]].texts)
        replacements[key[0]][key[1]] = entry["ko"]
        selected[key] = entry["ko"]
    for entry in overlay["deferred_credit_entries"]:
        key = coordinate(entry)
        if text_hash(original[key]) != entry["source_jp_utf16le_sha256"]:
            raise IntegrationError(f"deferred credit source hash mismatch: {key}")
        if key in selected:
            raise IntegrationError(f"deferred credit overlaps translated coordinate: {key}")
    raw = rebuild_raw_strdata(archive, replacements)
    rebuilt = parse_raw_strdata(raw)
    rebuilt_text = coordinate_texts(rebuilt)
    if rebuilt.block_count != archive.block_count or rebuilt.slot_count != archive.slot_count:
        raise IntegrationError("candidate changed block/slot count")
    for before, after in zip(archive.blocks, rebuilt.blocks, strict=True):
        if before.inner_header != after.inner_header or before.slot_count != after.slot_count:
            raise IntegrationError(f"candidate altered protected block structure: {before.block_id}")
    if any(rebuilt_text[key] != value for key, value in selected.items()):
        raise IntegrationError("candidate translated coordinate verification failed")
    nonselected = sum(1 for key, value in original.items() if key not in selected and rebuilt_text.get(key) == value)
    if nonselected != len(original) - len(selected):
        raise IntegrationError("candidate altered a non-selected text coordinate")
    candidate = recompress_wrapper(raw, packed)
    _, roundtrip = decompress_wrapper(candidate)
    if roundtrip != raw or coordinate_texts(parse_raw_strdata(roundtrip)) != rebuilt_text:
        raise IntegrationError("candidate packed round-trip mismatch")
    candidate_path = output_dir / "candidate" / RESOURCE
    manifest_path = output_dir / "build_manifest.v1.json"
    require_tmp(candidate_path)
    write(candidate_path, candidate)
    result = {
        "schema": BUILD_SCHEMA,
        "workstream_id": WORKSTREAM_ID,
        "resource": RESOURCE,
        "base_jp": ACTIVE_PIN,
        "overlay": {"path": str(overlay_path), "size": len(overlay_blob), "sha256": sha256(overlay_blob), "translated_entries": len(selected), "deferred_credit_entries": len(overlay["deferred_credit_entries"]), "component_count": len(overlay["components"])},
        "candidate": {"path": candidate_path.relative_to(output_dir).as_posix(), "packed_size": len(candidate), "packed_sha256": sha256(candidate), "raw_size": len(raw), "raw_sha256": sha256(raw)},
        "validation": {"active_jp_pin_gated": True, "component_coordinates_nonoverlapping": True, "translated_replacements_verified": len(selected), "deferred_credits_hash_verified_and_preserved": len(overlay["deferred_credit_entries"]), "nonselected_text_coordinates_preserved": nonselected, "protected_inner_headers_preserved": True, "packed_roundtrip_byte_exact": True},
        "distribution_policy": {"candidate_is_temporary_only": True, "game_install_modified": False, "release_modified": False, "github_modified": False},
    }
    write(manifest_path, json_bytes(result))
    return result


def determinism(active_path: Path, overlay_path: Path, output_dir: Path) -> dict[str, Any]:
    require_tmp(output_dir)
    first = build_candidate(active_path, overlay_path, output_dir / "a")
    second = build_candidate(active_path, overlay_path, output_dir / "b")
    a = (output_dir / "a" / "candidate" / RESOURCE).read_bytes()
    b = (output_dir / "b" / "candidate" / RESOURCE).read_bytes()
    if a != b:
        raise IntegrationError("two clean integration builds are not byte-identical")
    result = {"action": "determinism", "byte_identical": True, "candidate_sha256": sha256(a), "candidate_size": len(a), "first_raw_sha256": first["candidate"]["raw_sha256"], "second_raw_sha256": second["candidate"]["raw_sha256"], "game_install_modified": False, "release_modified": False, "github_modified": False}
    write(output_dir / "determinism.v1.json", json_bytes(result))
    return result


def verify(active_path: Path, overlay_path: Path, output_dir: Path) -> dict[str, Any]:
    require_tmp(output_dir)
    existing = output_dir / "candidate" / RESOURCE
    if not existing.is_file():
        raise IntegrationError("candidate does not exist for verification")
    rebuilt = build_candidate(active_path, overlay_path, output_dir / "verification_rebuild")
    regenerated = output_dir / "verification_rebuild" / "candidate" / RESOURCE
    if existing.read_bytes() != regenerated.read_bytes():
        raise IntegrationError("integration candidate differs from clean rebuild")
    return {"action": "verify", "candidate_sha256": sha256(existing.read_bytes()), "regenerated_candidate_sha256": rebuilt["candidate"]["packed_sha256"], "deterministic": True, "game_install_modified": False, "release_modified": False, "github_modified": False}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    assemble_command = commands.add_parser("assemble")
    assemble_command.add_argument("--output", type=Path, default=COMBINED_PATH)
    for name in ("build", "determinism", "verify"):
        command = commands.add_parser(name)
        command.add_argument("--active-input", type=Path, default=DEFAULT_ACTIVE)
        command.add_argument("--overlay", type=Path, default=COMBINED_PATH)
        command.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "assemble":
            result = assemble(args.output)
        elif args.command == "build":
            result = build_candidate(args.active_input, args.overlay, args.output_dir)
        elif args.command == "determinism":
            result = determinism(args.active_input, args.overlay, args.output_dir)
        else:
            result = verify(args.active_input, args.overlay, args.output_dir)
    except (OSError, IntegrationError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
