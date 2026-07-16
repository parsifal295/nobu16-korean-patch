#!/usr/bin/env python3
"""Source-free preservation proof for the six official P0-05 credit strings.

P0-05 is not gameplay/UI copy: every coordinate is an official end-credit
attribution block.  Both pinned public Switch Korean references preserve the
same JP strings byte-for-text.  This builder therefore deliberately emits no
Korean replacement and only permits a byte-identical temporary candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
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
sys.path[:0] = [str(TOOLS), str(STRDATA_TOOLS)]

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


RESOURCE = "MSG/JP/strdata.bin"
BUNDLE_ID = "p0-MSG_JP_strdata-05"
OVERLAY_SCHEMA = "nobu16.kr.strdata-credit-attribution-hold.v1"
BUILD_SCHEMA = "nobu16.kr.strdata-credit-hold-build-manifest.v1"
WORKSTREAM_ID = "steam-jp-strdata-p0-b05-credit-hold-v1"
HOLD_NAME = "strdata_ko_steam_jp_p0_b05_credit_hold.v1.json"
CONTRACT = REPOSITORY / "workstreams" / "jp_active_message_residual_audit_v1" / "public" / "active_jp_remaining_coordinates.v1.json"
DEFAULT_ACTIVE = Path(r"F:\SteamLibrary\steamapps\common\NOBU16") / RESOURCE
DEFAULT_OLD = GAME_ROOT / "KR_PATCH_BACKUP" / "file_only_transaction" / "jp-runtime-wave05-20260715-v1" / "originals" / RESOURCE
V13_ZIP = REPOSITORY / "tmp" / "third_party_switch_v13" / "NobunagaShinsei_KoreanPatch_v1.3.zip"
V20_ZIP = REPOSITORY / "tmp" / "third_party_switch_v20" / "NobunagaShinsei_KoreanPatch_v2.0.zip"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/strdata.bin"
DEFAULT_HOLD = WORKSTREAM / "public" / HOLD_NAME
TMP_ROOT = REPOSITORY / "tmp" / "steam_jp_strdata_p0_b05_credit_hold_v1"

ACTIVE_PIN = {
    "size": 956_835,
    "packed_sha256": "E77CD1F5CB72789B12B68FE0C1767950C0F54B1A62C9BB671CB14661D7378034",
    "raw_size": 953_072,
    "raw_sha256": "A3410438A13B2DB4C72B56B804BDF4ACABBEE8954203CA13D210AD848134BF66",
    "block_count": 5,
    "slot_count": 32_311,
}
OLD_PIN = {
    "size": 507_054,
    "packed_sha256": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "raw_size": 763_928,
    "raw_sha256": "EAB14063C2060CE11794232F483F0B2210B3BD58118165CBEEC2F37176C25649",
}
V13_ZIP_PIN = {"size": 72_977_145, "sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4"}
V13_MEMBER_PIN = {"size": 404_189, "sha256": "5F065B9DBDAE4DC75E2D7186A76C0AC988FB504F018F820C204262BF07D5061B"}
V20_ZIP_PIN = {"size": 84_385_377, "sha256": "A7497986FCC53312BC40B470465CD4DD0AE5179B0B9DB92526541E10987079DD"}
V20_MEMBER_PIN = {"size": 403_386, "sha256": "FF38F586F46145A9C0F2BA370E129266EEDEEA02A83C3F2BEE60A0144AED9A21"}
EXPECTED_COUNT = 6
EXPECTED_COORDINATE_SHA256 = "FAE4643A1B9E1AF483CCB16CAB2828357E39796A45256FD1835BEF975CDAFB9F"


class CreditHoldError(ValueError):
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


def require_output(path: Path, root: Path) -> None:
    if not under(path, root):
        raise CreditHoldError(f"unsafe output path: {path}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value, _ = common.load_json_strict(path)
    except Exception as exc:
        raise CreditHoldError(f"invalid JSON {path}: {exc}") from exc
    return value


def read_pinned(path: Path, pin: dict[str, Any], label: str) -> tuple[bytes, bytes, Any]:
    if not path.is_file():
        raise CreditHoldError(f"missing {label}: {path}")
    packed = path.read_bytes()
    if {"size": len(packed), "packed_sha256": sha256(packed)} != {"size": pin["size"], "packed_sha256": pin["packed_sha256"]}:
        raise CreditHoldError(f"{label} packed pin mismatch")
    _, raw = decompress_wrapper(packed)
    if {"raw_size": len(raw), "raw_sha256": sha256(raw)} != {"raw_size": pin["raw_size"], "raw_sha256": pin["raw_sha256"]}:
        raise CreditHoldError(f"{label} raw pin mismatch")
    archive = parse_raw_strdata(raw)
    if archive.block_count != pin.get("block_count", archive.block_count) or archive.slot_count != pin.get("slot_count", archive.slot_count):
        raise CreditHoldError(f"{label} structure pin mismatch")
    if rebuild_raw_strdata(archive) != raw:
        raise CreditHoldError(f"{label} identity rebuild is not byte-identical")
    return packed, raw, archive


def contract_entries() -> tuple[list[dict[str, int]], dict[tuple[int, int], str]]:
    document = load_json(CONTRACT)
    if document.get("basis", {}).get("active_steam_file_sha256", {}).get(RESOURCE) != ACTIVE_PIN["packed_sha256"]:
        raise CreditHoldError("active JP contract baseline drift")
    bundle = next((value for value in document.get("recommended_parallel_bundles", []) if value.get("bundle_id") == BUNDLE_ID), None)
    if not isinstance(bundle, dict) or bundle.get("resource") != RESOURCE or bundle.get("coordinate_count") != EXPECTED_COUNT or bundle.get("coordinate_sha256") != EXPECTED_COORDINATE_SHA256:
        raise CreditHoldError("P0-05 coordinate contract mismatch")
    coordinates = bundle.get("coordinates")
    if not isinstance(coordinates, list) or canonical_hash(coordinates) != EXPECTED_COORDINATE_SHA256:
        raise CreditHoldError("P0-05 coordinate list mismatch")
    lookup = {}
    for item in document["entries_by_resource"][RESOURCE]:
        coordinate = item.get("coordinate", {})
        key = (coordinate.get("block_id"), coordinate.get("slot_id"))
        if key in {(entry["block_id"], entry["slot_id"]) for entry in coordinates}:
            lookup[key] = item.get("active_utf16le_sha256")
    if len(lookup) != EXPECTED_COUNT:
        raise CreditHoldError("P0-05 source hash coverage mismatch")
    return coordinates, lookup


def read_member(zip_path: Path, zip_pin: dict[str, Any], member_pin: dict[str, Any]) -> bytes:
    if {"size": zip_path.stat().st_size, "sha256": sha256(zip_path.read_bytes())} != zip_pin:
        raise CreditHoldError(f"Switch ZIP pin mismatch: {zip_path}")
    with zipfile.ZipFile(zip_path) as archive:
        member = archive.read(SWITCH_MEMBER)
    if {"size": len(member), "sha256": sha256(member)} != member_pin:
        raise CreditHoldError(f"Switch member pin mismatch: {zip_path}")
    return member


def v20_credit_texts(member: bytes) -> tuple[str, ...]:
    """Parse only block 4; v2.0 has an older block-0 count but same credits."""
    _, raw = decompress_wrapper(member)
    if len(raw) != 952_212 or sha256(raw) != "FDAF3D630FC6C9ACD37616EFB4E45CECA0FBA63968FC4F20A1E9A0DAE4CA5D55":
        raise CreditHoldError("Switch v2.0 raw pin mismatch")
    if struct.unpack_from("<II", raw, 0) != (5, 0x2C):
        raise CreditHoldError("Switch v2.0 outer header mismatch")
    offset, size = struct.unpack_from("<II", raw, 12 + 3 * 8)
    inner = raw[offset : offset + size]
    if len(inner) != size or struct.unpack_from("<I", inner, 0x0C)[0] != 0x14:
        raise CreditHoldError("Switch v2.0 credits block header mismatch")
    table = parse_message_table(struct.pack("<III", 1, 12, len(inner)) + inner)
    if table.string_count != 20:
        raise CreditHoldError("Switch v2.0 credits slot count mismatch")
    return tuple(table.texts[:6])


def derive_hold(active_path: Path, old_path: Path, output: Path) -> dict[str, Any]:
    require_output(output, WORKSTREAM)
    _, _, active = read_pinned(active_path, ACTIVE_PIN, "active Steam JP")
    _, _, old = read_pinned(old_path, OLD_PIN, "official JP backup")
    v13_member = read_member(V13_ZIP, V13_ZIP_PIN, V13_MEMBER_PIN)
    v13 = parse_raw_strdata(decompress_wrapper(v13_member)[1])
    v20 = v20_credit_texts(read_member(V20_ZIP, V20_ZIP_PIN, V20_MEMBER_PIN))
    coordinates, hashes = contract_entries()
    active_map, old_map, v13_map = coordinate_texts(active), coordinate_texts(old), coordinate_texts(v13)
    entries = []
    for item in coordinates:
        key = (item["block_id"], item["slot_id"])
        source = active_map[key]
        if source != old_map[key] or source != v13_map[key] or source != v20[key[1]]:
            raise CreditHoldError(f"credits reference text differs at {key}")
        if text_hash(source) != hashes[key]:
            raise CreditHoldError(f"active source hash differs at {key}")
        entries.append({
            "block_id": key[0],
            "slot_id": key[1],
            "source_jp_utf16le_sha256": text_hash(source),
            "status": "deferred_credit_attribution_review",
            "reason_code": "official_credit_attribution_preserved",
        })
    hold = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": WORKSTREAM_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "entry_count": len(entries),
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False},
        "stock_jp": ACTIVE_PIN,
        "coordinate_contract": {"path": CONTRACT.relative_to(REPOSITORY).as_posix(), "bundle_id": BUNDLE_ID, "coordinate_count": EXPECTED_COUNT, "coordinate_sha256": EXPECTED_COORDINATE_SHA256},
        "reference_evidence": {"switch_v13_unchanged": True, "switch_v20_unchanged": True},
        "entries": entries,
    }
    write(output, json_bytes(hold))
    return {"action": "derive-credit-hold", "output": str(output), "output_size": output.stat().st_size, "output_sha256": sha256(output.read_bytes()), "deferred_credit_entries": len(entries), "game_install_modified": False, "release_modified": False, "github_modified": False}


def load_hold(path: Path) -> dict[str, Any]:
    hold = load_json(path)
    if hold.get("schema") != OVERLAY_SCHEMA or hold.get("overlay_id") != WORKSTREAM_ID or hold.get("resource") != RESOURCE or hold.get("entry_count") != EXPECTED_COUNT:
        raise CreditHoldError("credit-hold identity mismatch")
    if hold.get("distribution_policy") != {"contains_commercial_source_text": False, "contains_complete_game_resource": False}:
        raise CreditHoldError("credit-hold policy mismatch")
    coordinates, hashes = contract_entries()
    expected = [(item["block_id"], item["slot_id"]) for item in coordinates]
    actual = []
    for entry in hold.get("entries", []):
        key = (entry.get("block_id"), entry.get("slot_id"))
        if entry.get("source_jp_utf16le_sha256") != hashes.get(key) or entry.get("status") != "deferred_credit_attribution_review" or entry.get("reason_code") != "official_credit_attribution_preserved":
            raise CreditHoldError(f"credit-hold entry mismatch: {key}")
        actual.append(key)
    if actual != expected:
        raise CreditHoldError("credit-hold coordinate order/set mismatch")
    return hold


def build_identity_candidate(active_path: Path, hold_path: Path, output_dir: Path) -> dict[str, Any]:
    require_output(output_dir, TMP_ROOT)
    packed, _, active = read_pinned(active_path, ACTIVE_PIN, "active Steam JP")
    hold = load_hold(hold_path)
    texts = coordinate_texts(active)
    for entry in hold["entries"]:
        key = (entry["block_id"], entry["slot_id"])
        if text_hash(texts[key]) != entry["source_jp_utf16le_sha256"]:
            raise CreditHoldError(f"credit candidate source differs: {key}")
    candidate = output_dir / "candidate" / RESOURCE
    manifest = output_dir / "build_manifest.v1.json"
    require_output(candidate, TMP_ROOT)
    write(candidate, packed)
    result = {
        "schema": BUILD_SCHEMA,
        "workstream_id": WORKSTREAM_ID,
        "resource": RESOURCE,
        "base_jp": ACTIVE_PIN,
        "candidate": {"path": candidate.relative_to(output_dir).as_posix(), "packed_size": len(packed), "packed_sha256": sha256(packed), "byte_identical_to_active_jp": True},
        "validation": {"deferred_credit_entries_source_hash_verified": EXPECTED_COUNT, "official_credit_attributions_preserved": EXPECTED_COUNT, "candidate_byte_identical_to_active_jp": True},
        "distribution_policy": {"candidate_is_temporary_only": True, "game_install_modified": False, "release_modified": False, "github_modified": False},
    }
    write(manifest, json_bytes(result))
    return result


def determinism(active_path: Path, hold_path: Path, output_dir: Path) -> dict[str, Any]:
    first = build_identity_candidate(active_path, hold_path, output_dir / "a")
    second = build_identity_candidate(active_path, hold_path, output_dir / "b")
    a = (output_dir / "a" / "candidate" / RESOURCE).read_bytes()
    b = (output_dir / "b" / "candidate" / RESOURCE).read_bytes()
    if a != b:
        raise CreditHoldError("credit hold candidate is not deterministic")
    result = {"action": "determinism", "byte_identical": True, "candidate_sha256": sha256(a), "candidate_size": len(a), "deferred_credit_entries": EXPECTED_COUNT, "game_install_modified": False, "release_modified": False, "github_modified": False}
    write(output_dir / "determinism.v1.json", json_bytes(result))
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    derive = commands.add_parser("derive-hold")
    derive.add_argument("--active-input", type=Path, default=DEFAULT_ACTIVE)
    derive.add_argument("--old-input", type=Path, default=DEFAULT_OLD)
    derive.add_argument("--output", type=Path, default=DEFAULT_HOLD)
    for name in ("build", "determinism"):
        command = commands.add_parser(name)
        command.add_argument("--active-input", type=Path, default=DEFAULT_ACTIVE)
        command.add_argument("--hold", type=Path, default=DEFAULT_HOLD)
        command.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "derive-hold":
            result = derive_hold(args.active_input, args.old_input, args.output)
        elif args.command == "build":
            result = build_identity_candidate(args.active_input, args.hold, args.output_dir)
        else:
            result = determinism(args.active_input, args.hold, args.output_dir)
    except (OSError, CreditHoldError, ValueError, struct.error, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
