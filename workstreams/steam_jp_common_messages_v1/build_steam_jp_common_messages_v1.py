#!/usr/bin/env python3
"""Rebase five common-message resources onto the current Steam JP layout.

The tracked overlays produced by ``bootstrap`` contain only project-authored
Korean text, JP UTF-16LE hashes, integer IDs, and structural proof.  Bootstrap
never reads an SC file: it derives the Korean side by diffing a pinned,
previously audited JP-native candidate against its pinned JP stock input, then
aligns the two JP hash sequences with the current Steam JP tables.

``build`` and ``verify`` need only the tracked overlays and pristine Steam JP
files.  Complete candidate binaries are allowed only below ``tmp`` and an
installed game file is never an output.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-common-message-overlay.v1"
EVIDENCE_SCHEMA = "nobu16.kr.steam-jp-common-message-evidence.v1"
REVIEW_SCHEMA = "nobu16.kr.steam-jp-common-message-unmapped-review.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-common-message-validation.v1"
PRIVATE_MANIFEST_SCHEMA = "nobu16.kr.steam-jp-common-message-private-candidate.v1"
MAPPING_ALGORITHM = "jp_utf16le_hash_sequence_equal_blocks_v1"

FILES = ("msgev.bin", "msgdata.bin", "msgbre.bin", "msgire.bin", "msgstf.bin")
RESOURCES = tuple(f"MSG_PK/JP/{name}" for name in FILES)
OVERLAY_PATHS = {
    name: WORKSTREAM_ROOT / "public" / f"{Path(name).stem}_ko_steam_jp_native.v1.json"
    for name in FILES
}
EVIDENCE_PATH = WORKSTREAM_ROOT / "evidence" / "steam_jp_common_message_evidence.v1.json"
REVIEW_PATH = WORKSTREAM_ROOT / "review" / "steam_jp_common_message_unmapped.v1.json"
VALIDATION_PATH = WORKSTREAM_ROOT / "validation.v1.json"

DEFAULT_STEAM_ROOT = Path("F:/SteamLibrary/steamapps/common/NOBU16")
DEFAULT_LEGACY_STOCK_ROOT = Path(
    "I:/Workspaces/NOBU16-Korean/archive/legacy-root/KR_PATCH_BACKUP/file_only_transaction/"
    "jp-runtime-wave05-20260715-v1/originals"
)
DEFAULT_LEGACY_CANDIDATE_A = REPO_ROOT / "tmp" / "jp_pk_message_route_audit_v1_candidate_a_20260715" / "native_exact_subset"
DEFAULT_LEGACY_CANDIDATE_B = REPO_ROOT / "tmp" / "jp_pk_message_route_audit_v1_candidate_b_20260715" / "native_exact_subset"
DEFAULT_PRIVATE_OUTPUT = REPO_ROOT / "tmp" / "steam_jp_common_messages_v1_candidate"

HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")


STEAM_PINS: dict[str, dict[str, Any]] = {
    "msgev.bin": {
        "size": 562_226,
        "packed_sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        "raw_size": 894_800,
        "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
        "string_count": 17_916,
    },
    "msgdata.bin": {
        "size": 272_453,
        "packed_sha256": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
        "raw_size": 434_000,
        "raw_sha256": "D09F61E34E4AA498F3DDEF23E7B7FD2CC8E9FE50B24F39D3BA1034BE82E6D0F6",
        "string_count": 29_218,
    },
    "msgbre.bin": {
        "size": 221_127,
        "packed_sha256": "945A0E9157E2DBD12781FFA5A986D93681325F40B6486348B1AB311D3BEE1D6D",
        "raw_size": 333_516,
        "raw_sha256": "02237F07362E0E3DFF92C0E999A29B887EBE5971B1C3EF8F26EAA5C969FB9668",
        "string_count": 3_000,
    },
    "msgire.bin": {
        "size": 12_376,
        "packed_sha256": "0AFBFE11A380A9C98FB3B368092A05B39ABB6F80C4B0723AD3B6DB55C2559C5D",
        "raw_size": 17_192,
        "raw_sha256": "242CE228115746AA1153CDE617C300754D2F82BCAEC5683C70191A88F0BFE94F",
        "string_count": 122,
    },
    "msgstf.bin": {
        "size": 6_841,
        "packed_sha256": "01EEB0B1B4879B6C70E9D7564F9D2FBD93E7B537CF8C614A58EEA82A83785A29",
        "raw_size": 11_620,
        "raw_sha256": "70182BA6ADC9D002E54A1276C7372DF3C5F88DE3A9E4F949B97E4BE1E41CC5C2",
        "string_count": 20,
    },
}

LEGACY_STOCK_PINS: dict[str, dict[str, Any]] = {
    "msgev.bin": {
        "size": 555_784,
        "packed_sha256": "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002",
        "raw_size": 890_428,
        "raw_sha256": "4A916CA6837C4F8FC2D8B6254ECBEF26339558D2DDFEBF5A1637F8426F5918DE",
        "string_count": 17_910,
    },
    "msgdata.bin": {
        "size": 273_734,
        "packed_sha256": "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38",
        "raw_size": 431_044,
        "raw_sha256": "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0",
        "string_count": 29_210,
    },
    "msgbre.bin": {
        "size": 221_127,
        "packed_sha256": "DA9BE8242CF0A90592D573DF676ECDE26566B11C5707273EEB4AF5BA54132AD5",
        "raw_size": 333_516,
        "raw_sha256": "02237F07362E0E3DFF92C0E999A29B887EBE5971B1C3EF8F26EAA5C969FB9668",
        "string_count": 3_000,
    },
    "msgire.bin": {
        "size": 12_376,
        "packed_sha256": "2856E5DDAF36DD170833B306A4C9C9293AB6E0DC55761086BEDDED90772CB040",
        "raw_size": 17_192,
        "raw_sha256": "242CE228115746AA1153CDE617C300754D2F82BCAEC5683C70191A88F0BFE94F",
        "string_count": 122,
    },
    "msgstf.bin": {
        "size": 6_348,
        "packed_sha256": "2138888A6ECB8E49E1C72E60BDD1A18AE577E32C2A72EDC11A813F48F006D96B",
        "raw_size": 10_488,
        "raw_sha256": "6D06572BB5AFDAC041DF50A789FD0405F3B5C7844FA502329C8E4D27C8BE1620",
        "string_count": 20,
    },
}

LEGACY_CANDIDATE_PINS: dict[str, dict[str, Any]] = {
    "msgev.bin": {"size": 1_035_659, "packed_sha256": "B7BE936BA1C3DBC10EDCA843E33282682D8B0F09B3973CCED2C9B488A7C6C110"},
    "msgdata.bin": {"size": 490_040, "packed_sha256": "9AA46E279DC64448E70508D15599684C9CA887E93E6D4C0B893AE440CDF73353"},
    "msgbre.bin": {"size": 478_527, "packed_sha256": "B51BCDB6D9DF9DEC272D6100B8A141147FB7F7C498D4C12693DB87883328C48E"},
    "msgire.bin": {"size": 23_136, "packed_sha256": "9E2A81F2E9BD2265F73EF3E7DF806A9F1C85DBEF70AC0AB9362734E5736CC09A"},
    "msgstf.bin": {"size": 15_968, "packed_sha256": "721835AA953095C9FDFE2AD752566C98FCE0D6D9ED0812EE4DC0963A5687E86E"},
}


class SteamJpCommonError(ValueError):
    """Raised whenever a pin, mapping, or structure contract differs."""


@dataclass(frozen=True)
class LoadedTable:
    packed: bytes
    raw: bytes
    table: MessageTable


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16le"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return sha256(canonical_bytes(value))


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        if not isinstance(key, str):
            raise SteamJpCommonError("JSON key is not a string")
        normalized = key.casefold()
        if normalized in folded:
            raise SteamJpCommonError(f"duplicate/case-colliding JSON key: {key!r}")
        folded[normalized] = key
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SteamJpCommonError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SteamJpCommonError(f"JSON root is not an object: {path}")
    return value, blob


def require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64_RE.fullmatch(value) is None:
        raise SteamJpCommonError(f"{label} must be an uppercase SHA-256")
    return value


def require_int(value: Any, label: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise SteamJpCommonError(f"{label} must be an integer >= {minimum}")
    return value


def exact_keys(value: Any, keys: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        actual = set(value) if isinstance(value, dict) else set()
        raise SteamJpCommonError(
            f"{label} keys differ: missing={sorted(keys-actual)!r}, extra={sorted(actual-keys)!r}"
        )
    return value


def pin_public(pin: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "size": int(pin["size"]),
        "packed_sha256": str(pin["packed_sha256"]),
        "raw_size": int(pin["raw_size"]),
        "raw_sha256": str(pin["raw_sha256"]),
        "string_count": int(pin["string_count"]),
    }


def load_pinned(path: Path, pin: Mapping[str, Any], label: str) -> LoadedTable:
    packed = path.read_bytes()
    if len(packed) != int(pin["size"]) or sha256(packed) != str(pin["packed_sha256"]):
        raise SteamJpCommonError(f"{label} packed pin differs")
    _header, raw = decompress_wrapper(packed)
    if "raw_size" in pin:
        if len(raw) != int(pin["raw_size"]) or sha256(raw) != str(pin["raw_sha256"]):
            raise SteamJpCommonError(f"{label} raw pin differs")
    table = parse_message_table(raw)
    if "string_count" in pin and table.string_count != int(pin["string_count"]):
        raise SteamJpCommonError(f"{label} string count differs")
    if rebuild_message_table(table, table.texts) != raw:
        raise SteamJpCommonError(f"{label} unchanged parse/rebuild is not byte-exact")
    return LoadedTable(packed, raw, table)


def load_legacy_candidate(path: Path, name: str, label: str) -> LoadedTable:
    pin = LEGACY_CANDIDATE_PINS[name]
    packed = path.read_bytes()
    if len(packed) != pin["size"] or sha256(packed) != pin["packed_sha256"]:
        raise SteamJpCommonError(f"{label} packed pin differs")
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise SteamJpCommonError(f"{label} unchanged parse/rebuild is not byte-exact")
    return LoadedTable(packed, raw, table)


def _artifact(path: Path, blob: bytes) -> dict[str, Any]:
    return {"path": path.relative_to(REPO_ROOT).as_posix(), "size": len(blob), "sha256": sha256(blob)}


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _hash_sequence(texts: Sequence[str]) -> list[str]:
    return [text_hash(text) for text in texts]


def build_overlay_value(
    name: str,
    legacy_stock: LoadedTable,
    legacy_candidate: LoadedTable,
    steam_stock: LoadedTable,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    if legacy_stock.table.string_count != legacy_candidate.table.string_count:
        raise SteamJpCommonError(f"{name}: legacy stock/candidate string counts differ")
    changed = [
        entry_id
        for entry_id, (source, replacement) in enumerate(
            zip(legacy_stock.table.texts, legacy_candidate.table.texts)
        )
        if source != replacement
    ]
    old_hashes = _hash_sequence(legacy_stock.table.texts)
    steam_hashes = _hash_sequence(steam_stock.table.texts)
    matcher = difflib.SequenceMatcher(None, old_hashes, steam_hashes, autojunk=False)
    opcodes = matcher.get_opcodes()

    mapped: dict[int, tuple[int, int]] = {}
    blocks: list[dict[str, Any]] = []
    changed_set = set(changed)
    for tag, old_start, old_end, steam_start, steam_end in opcodes:
        if tag != "equal":
            continue
        relevant = [entry_id for entry_id in range(old_start, old_end) if entry_id in changed_set]
        if not relevant:
            continue
        block_index = len(blocks)
        block_hashes = old_hashes[old_start:old_end]
        blocks.append(
            {
                "legacy_start_id": old_start,
                "steam_start_id": steam_start,
                "length": old_end - old_start,
                "jp_utf16le_hash_sequence_sha256": canonical_hash(block_hashes),
            }
        )
        for old_id in relevant:
            target_id = steam_start + (old_id - old_start)
            if old_hashes[old_id] != steam_hashes[target_id]:
                raise SteamJpCommonError(f"{name}: equal opcode source hash differs")
            mapped[old_id] = (target_id, block_index)

    entries: list[dict[str, Any]] = []
    for old_id, (target_id, block_index) in sorted(mapped.items(), key=lambda item: item[1][0]):
        replacement = legacy_candidate.table.texts[old_id]
        source = steam_stock.table.texts[target_id]
        mismatches = common.invariant_mismatches(source, replacement)
        if mismatches:
            raise SteamJpCommonError(
                f"{name}: mapped id {target_id} invariant mismatch: {'; '.join(mismatches)}"
            )
        entries.append(
            {
                "id": target_id,
                "legacy_jp_id": old_id,
                "mapping": "ordered_equal_hash_block",
                "mapping_block_index": block_index,
                "source_jp_utf16le_sha256": steam_hashes[target_id],
                "ko": replacement,
            }
        )
    ids = [int(entry["id"]) for entry in entries]
    if ids != sorted(set(ids)):
        raise SteamJpCommonError(f"{name}: mapped Steam ids are not sorted unique")

    nonmapped: list[dict[str, Any]] = []
    steam_hash_set = set(steam_hashes)
    mapped_translation_pairs = {
        (str(entry["source_jp_utf16le_sha256"]), text_hash(str(entry["ko"])))
        for entry in entries
    }
    for old_id in sorted(changed_set - set(mapped)):
        source_hash = old_hashes[old_id]
        ko_hash = text_hash(legacy_candidate.table.texts[old_id])
        collapsed_duplicate = (source_hash, ko_hash) in mapped_translation_pairs
        nonmapped.append(
            {
                "legacy_jp_id": old_id,
                "source_jp_utf16le_sha256": source_hash,
                "ko_utf16le_sha256": ko_hash,
                "coverage": (
                    "covered_by_collapsed_duplicate_target"
                    if collapsed_duplicate
                    else "unresolved"
                ),
                "reason": (
                    "same_jp_hash_and_korean_already_applied_to_surviving_target"
                    if collapsed_duplicate
                    else "source_jp_hash_not_in_ordered_equal_block"
                    if source_hash in steam_hash_set
                    else "source_jp_hash_absent_from_steam_stock"
                ),
            }
        )
    collapsed_duplicate_count = sum(
        row["coverage"] == "covered_by_collapsed_duplicate_target"
        for row in nonmapped
    )
    unresolved_count = len(nonmapped) - collapsed_duplicate_count

    overlay = {
        "schema": SCHEMA,
        "overlay_id": f"{Path(name).stem}-steam-jp-native-v1",
        "resource": f"MSG_PK/JP/{name}",
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": pin_public(STEAM_PINS[name]),
        "provenance": {
            "bootstrap_source": "pinned_verified_jp_native_candidate_ab_diff",
            "sc_binary_used": False,
            "sc_coordinate_used": False,
            "legacy_stock_jp": pin_public(LEGACY_STOCK_PINS[name]),
            "legacy_candidate_jp": dict(LEGACY_CANDIDATE_PINS[name]),
            "mapping_algorithm": MAPPING_ALGORITHM,
            "effective_legacy_translation_count": len(changed),
            "mapped_count": len(entries),
            "legacy_nonmapped_coordinate_count": len(nonmapped),
            "collapsed_duplicate_coverage_count": collapsed_duplicate_count,
            "unresolved_count": unresolved_count,
            "mapped_legacy_ids_sha256": canonical_hash(sorted(mapped)),
            "mapped_steam_ids_sha256": canonical_hash(ids),
            "nonmapped_legacy_ids_sha256": canonical_hash(
                [int(row["legacy_jp_id"]) for row in nonmapped]
            ),
        },
        "equal_hash_blocks": blocks,
        "entry_count": len(entries),
        "entries": entries,
    }
    metrics = {
        "resource": f"MSG_PK/JP/{name}",
        "legacy_effective_translation_count": len(changed),
        "applied_count": len(entries),
        "legacy_nonmapped_coordinate_count": len(nonmapped),
        "collapsed_duplicate_coverage_count": collapsed_duplicate_count,
        "unresolved_count": unresolved_count,
        "equal_hash_block_count": len(blocks),
        "full_sequence_equal_count": sum(
            old_end - old_start
            for tag, old_start, old_end, _steam_start, _steam_end in opcodes
            if tag == "equal"
        ),
        "legacy_string_count": legacy_stock.table.string_count,
        "steam_string_count": steam_stock.table.string_count,
    }
    return overlay, nonmapped, metrics


def validate_overlay(value: dict[str, Any], name: str) -> list[dict[str, Any]]:
    exact_keys(
        value,
        {
            "schema", "overlay_id", "resource", "base_language", "distribution_policy",
            "stock_jp", "provenance", "equal_hash_blocks", "entry_count", "entries",
        },
        f"{name}.overlay",
    )
    if value["schema"] != SCHEMA or value["resource"] != f"MSG_PK/JP/{name}":
        raise SteamJpCommonError(f"{name}: overlay identity differs")
    if value["base_language"] != "JP" or "/SC/" in value["resource"]:
        raise SteamJpCommonError(f"{name}: overlay is not JP-native")
    policy = exact_keys(
        value["distribution_policy"],
        {"contains_commercial_source_text", "contains_complete_game_resource"},
        f"{name}.distribution_policy",
    )
    if policy["contains_commercial_source_text"] is not False or policy["contains_complete_game_resource"] is not False:
        raise SteamJpCommonError(f"{name}: overlay distribution policy is unsafe")
    if value["stock_jp"] != pin_public(STEAM_PINS[name]):
        raise SteamJpCommonError(f"{name}: Steam stock pin differs")

    provenance = value["provenance"]
    if not isinstance(provenance, dict):
        raise SteamJpCommonError(f"{name}: provenance is not an object")
    if provenance.get("sc_binary_used") is not False or provenance.get("sc_coordinate_used") is not False:
        raise SteamJpCommonError(f"{name}: SC input is not forbidden")
    if provenance.get("mapping_algorithm") != MAPPING_ALGORITHM:
        raise SteamJpCommonError(f"{name}: mapping algorithm differs")

    blocks = value["equal_hash_blocks"]
    if not isinstance(blocks, list) or not blocks:
        raise SteamJpCommonError(f"{name}: equal_hash_blocks must be non-empty")
    for index, block in enumerate(blocks):
        exact_keys(
            block,
            {"legacy_start_id", "steam_start_id", "length", "jp_utf16le_hash_sequence_sha256"},
            f"{name}.equal_hash_blocks[{index}]",
        )
        require_int(block["legacy_start_id"], "legacy_start_id")
        require_int(block["steam_start_id"], "steam_start_id")
        require_int(block["length"], "length", 1)
        require_hash(block["jp_utf16le_hash_sequence_sha256"], "block hash")

    entries = value["entries"]
    if not isinstance(entries, list) or require_int(value["entry_count"], "entry_count", 1) != len(entries):
        raise SteamJpCommonError(f"{name}: entry count differs")
    normalized: list[dict[str, Any]] = []
    ids: list[int] = []
    for index, entry in enumerate(entries):
        exact_keys(
            entry,
            {"id", "legacy_jp_id", "mapping", "mapping_block_index", "source_jp_utf16le_sha256", "ko"},
            f"{name}.entries[{index}]",
        )
        target_id = require_int(entry["id"], "entry.id")
        old_id = require_int(entry["legacy_jp_id"], "entry.legacy_jp_id")
        block_index = require_int(entry["mapping_block_index"], "entry.mapping_block_index")
        if block_index >= len(blocks) or entry["mapping"] != "ordered_equal_hash_block":
            raise SteamJpCommonError(f"{name}: entry mapping proof differs")
        block = blocks[block_index]
        if old_id - int(block["legacy_start_id"]) != target_id - int(block["steam_start_id"]):
            raise SteamJpCommonError(f"{name}: entry does not belong to its mapping block")
        if not 0 <= target_id - int(block["steam_start_id"]) < int(block["length"]):
            raise SteamJpCommonError(f"{name}: entry lies outside its mapping block")
        source_hash = require_hash(entry["source_jp_utf16le_sha256"], "source JP hash")
        ko = entry["ko"]
        if not isinstance(ko, str) or "\0" in ko:
            raise SteamJpCommonError(f"{name}: Korean replacement is not NUL-free text")
        try:
            ko.encode("utf-16le")
        except UnicodeEncodeError as exc:
            raise SteamJpCommonError(f"{name}: invalid UTF-16 replacement") from exc
        ids.append(target_id)
        normalized.append({"id": target_id, "source_hash": source_hash, "ko": ko})
    if ids != sorted(set(ids)):
        raise SteamJpCommonError(f"{name}: entry ids are not sorted unique")
    if canonical_hash(ids) != provenance.get("mapped_steam_ids_sha256"):
        raise SteamJpCommonError(f"{name}: mapped Steam ID hash differs")
    return normalized


def _opaque_structure_preserved(before: MessageTable, after: MessageTable, rebuilt_raw: bytes) -> bool:
    return all(
        (
            before.block_offset == after.block_offset,
            before.table_offset == after.table_offset,
            before.table_size == after.table_size,
            before.string_count == after.string_count,
            before.blob[:8] == rebuilt_raw[:8],
            before.blob[12:before.table_offset] == rebuilt_raw[12:after.table_offset],
        )
    )


def build_one(name: str, steam_stock: LoadedTable, overlay: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    entries = validate_overlay(overlay, name)
    source_hashes = _hash_sequence(steam_stock.table.texts)
    for index, block in enumerate(overlay["equal_hash_blocks"]):
        start = int(block["steam_start_id"])
        end = start + int(block["length"])
        if end > len(source_hashes):
            raise SteamJpCommonError(f"{name}: mapping block {index} exceeds Steam table")
        if canonical_hash(source_hashes[start:end]) != block["jp_utf16le_hash_sequence_sha256"]:
            raise SteamJpCommonError(f"{name}: mapping block {index} hash proof differs")

    texts = list(steam_stock.table.texts)
    target_ids: set[int] = set()
    for entry in entries:
        entry_id = int(entry["id"])
        if not 0 <= entry_id < steam_stock.table.string_count:
            raise SteamJpCommonError(f"{name}: id {entry_id} is outside the Steam table")
        source = texts[entry_id]
        if text_hash(source) != entry["source_hash"]:
            raise SteamJpCommonError(f"{name}: id {entry_id} JP source hash differs")
        mismatches = common.invariant_mismatches(source, str(entry["ko"]))
        if mismatches:
            raise SteamJpCommonError(
                f"{name}: id {entry_id} invariant mismatch: {'; '.join(mismatches)}"
            )
        texts[entry_id] = str(entry["ko"])
        target_ids.add(entry_id)

    rebuilt_raw = rebuild_message_table(steam_stock.table, texts)
    reparsed = parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise SteamJpCommonError(f"{name}: rebuilt text table differs")
    if not _opaque_structure_preserved(steam_stock.table, reparsed, rebuilt_raw):
        raise SteamJpCommonError(f"{name}: opaque structure or ID domain changed")
    for entry_id, source in enumerate(steam_stock.table.texts):
        if entry_id not in target_ids and reparsed.texts[entry_id] != source:
            raise SteamJpCommonError(f"{name}: non-target id {entry_id} changed")

    candidate = recompress_wrapper(rebuilt_raw, steam_stock.packed)
    if candidate[:8] != steam_stock.packed[:8]:
        raise SteamJpCommonError(f"{name}: wrapper prefix changed")
    _header, check_raw = decompress_wrapper(candidate)
    if check_raw != rebuilt_raw:
        raise SteamJpCommonError(f"{name}: candidate wrapper round-trip differs")
    metrics = {
        "resource": f"MSG_PK/JP/{name}",
        "applied_count": len(target_ids),
        "legacy_nonmapped_coordinate_count": int(
            overlay["provenance"]["legacy_nonmapped_coordinate_count"]
        ),
        "collapsed_duplicate_coverage_count": int(
            overlay["provenance"]["collapsed_duplicate_coverage_count"]
        ),
        "unresolved_count": int(overlay["provenance"]["unresolved_count"]),
        "non_target_id_count": steam_stock.table.string_count - len(target_ids),
        "id_domain_preserved": True,
        "string_count_preserved": True,
        "opaque_non_string_metadata_preserved": True,
        "non_target_texts_preserved": True,
        "wrapper_prefix_preserved": True,
        "stock": pin_public(STEAM_PINS[name]),
        "candidate": {
            "size": len(candidate),
            "packed_sha256": sha256(candidate),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256(rebuilt_raw),
            "string_count": reparsed.string_count,
        },
        "applied_ids_sha256": canonical_hash(sorted(target_ids)),
    }
    return candidate, metrics


def load_public_overlays() -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    values: dict[str, dict[str, Any]] = {}
    blobs: dict[str, bytes] = {}
    for name in FILES:
        value, blob = read_json(OVERLAY_PATHS[name])
        validate_overlay(value, name)
        values[name] = value
        blobs[name] = blob
    return values, blobs


def build_all(steam_root: Path, overlays: Mapping[str, dict[str, Any]]) -> tuple[dict[str, bytes], list[dict[str, Any]]]:
    candidates: dict[str, bytes] = {}
    metrics: list[dict[str, Any]] = []
    for name in FILES:
        stock = load_pinned(steam_root / "MSG_PK" / "JP" / name, STEAM_PINS[name], f"Steam JP {name}")
        first, first_metrics = build_one(name, stock, overlays[name])
        second, second_metrics = build_one(name, stock, overlays[name])
        if first != second or first_metrics != second_metrics:
            raise SteamJpCommonError(f"{name}: deterministic A/B build differs")
        first_metrics["deterministic_ab_equal"] = True
        candidates[name] = first
        metrics.append(first_metrics)
    return candidates, metrics


def bootstrap(args: argparse.Namespace) -> dict[str, Any]:
    overlays: dict[str, dict[str, Any]] = {}
    overlay_blobs: dict[str, bytes] = {}
    unmapped_by_resource: list[dict[str, Any]] = []
    bootstrap_metrics: list[dict[str, Any]] = []
    for name in FILES:
        legacy_stock = load_pinned(
            args.legacy_stock_root / "MSG_PK" / "JP" / name,
            LEGACY_STOCK_PINS[name],
            f"legacy JP stock {name}",
        )
        candidate_a = load_legacy_candidate(
            args.legacy_candidate_a / "MSG_PK" / "JP" / name, name, f"legacy JP candidate A {name}"
        )
        candidate_b = load_legacy_candidate(
            args.legacy_candidate_b / "MSG_PK" / "JP" / name, name, f"legacy JP candidate B {name}"
        )
        if candidate_a.packed != candidate_b.packed or candidate_a.raw != candidate_b.raw:
            raise SteamJpCommonError(f"{name}: legacy JP candidate A/B differs")
        steam_stock = load_pinned(
            args.steam_root / "MSG_PK" / "JP" / name, STEAM_PINS[name], f"Steam JP {name}"
        )
        overlay, unmapped, metrics = build_overlay_value(name, legacy_stock, candidate_a, steam_stock)
        overlay_again, unmapped_again, metrics_again = build_overlay_value(
            name, legacy_stock, candidate_b, steam_stock
        )
        if (
            pretty_bytes(overlay) != pretty_bytes(overlay_again)
            or pretty_bytes(unmapped) != pretty_bytes(unmapped_again)
            or metrics != metrics_again
        ):
            raise SteamJpCommonError(f"{name}: bootstrap A/B differs")
        validate_overlay(overlay, name)
        overlays[name] = overlay
        overlay_blobs[name] = pretty_bytes(overlay)
        unmapped_by_resource.append(
            {
                "resource": f"MSG_PK/JP/{name}",
                "legacy_nonmapped_coordinate_count": len(unmapped),
                "collapsed_duplicate_coverage_count": metrics[
                    "collapsed_duplicate_coverage_count"
                ],
                "unresolved_count": metrics["unresolved_count"],
                "entries": unmapped,
            }
        )
        bootstrap_metrics.append(
            {
                **metrics,
                "legacy_stock_jp": pin_public(LEGACY_STOCK_PINS[name]),
                "legacy_candidate_jp": dict(LEGACY_CANDIDATE_PINS[name]),
                "steam_stock_jp": pin_public(STEAM_PINS[name]),
                "legacy_candidate_ab_equal": True,
                "bootstrap_ab_equal": True,
            }
        )

    candidates, build_metrics = build_all(args.steam_root, overlays)
    aggregate = {
        "legacy_effective_translation_count": sum(
            int(row["legacy_effective_translation_count"]) for row in bootstrap_metrics
        ),
        "applied_count": sum(int(row["applied_count"]) for row in build_metrics),
        "legacy_nonmapped_coordinate_count": sum(
            int(row["legacy_nonmapped_coordinate_count"]) for row in build_metrics
        ),
        "collapsed_duplicate_coverage_count": sum(
            int(row["collapsed_duplicate_coverage_count"]) for row in build_metrics
        ),
        "unresolved_count": sum(int(row["unresolved_count"]) for row in build_metrics),
        "resource_count": len(FILES),
    }
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "target_structure_authority": "current_pristine_steam_jp",
        "mapping_algorithm": MAPPING_ALGORITHM,
        "sc_binary_used": False,
        "sc_coordinate_used": False,
        "resources": bootstrap_metrics,
        "aggregate": aggregate,
    }
    review = {
        "schema": REVIEW_SCHEMA,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resources": unmapped_by_resource,
        "aggregate_legacy_nonmapped_coordinate_count": aggregate[
            "legacy_nonmapped_coordinate_count"
        ],
        "aggregate_collapsed_duplicate_coverage_count": aggregate[
            "collapsed_duplicate_coverage_count"
        ],
        "aggregate_unresolved_count": aggregate["unresolved_count"],
    }
    evidence_blob = pretty_bytes(evidence)
    review_blob = pretty_bytes(review)
    artifacts = [
        *[_artifact(OVERLAY_PATHS[name], overlay_blobs[name]) for name in FILES],
        _artifact(EVIDENCE_PATH, evidence_blob),
        _artifact(REVIEW_PATH, review_blob),
    ]
    validation = {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "base_language": "JP",
        "steam_game_root_default": DEFAULT_STEAM_ROOT.as_posix(),
        "target_resources": list(RESOURCES),
        "steam_stock_hash_pins_exact": True,
        "jp_hash_sequence_mapping_exact": True,
        "all_source_hashes_revalidated_on_steam": True,
        "all_message_invariants_preserved": True,
        "all_id_domains_preserved": True,
        "all_non_target_texts_preserved": True,
        "all_opaque_non_string_metadata_preserved": True,
        "all_wrapper_prefixes_preserved": True,
        "all_candidate_ab_equal": all(row["deterministic_ab_equal"] for row in build_metrics),
        "sc_binary_used": False,
        "sc_coordinate_used": False,
        "installed_game_files_modified": False,
        "candidate_binaries_tracked": False,
        "aggregate": aggregate,
        "resources": build_metrics,
        "artifacts": artifacts,
        "candidate_hashes": {
            name: {"size": len(candidates[name]), "sha256": sha256(candidates[name])}
            for name in FILES
        },
    }
    validation_blob = pretty_bytes(validation)

    for name in FILES:
        atomic_write(OVERLAY_PATHS[name], overlay_blobs[name])
    atomic_write(EVIDENCE_PATH, evidence_blob)
    atomic_write(REVIEW_PATH, review_blob)
    atomic_write(VALIDATION_PATH, validation_blob)
    return validation


def _safe_private_output(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO_ROOT / "tmp").resolve()
    if not resolved.is_relative_to(tmp_root) or resolved == tmp_root:
        raise SteamJpCommonError("candidate output must be a new directory below KR_PATCH_WORK/tmp")
    if resolved.exists():
        raise SteamJpCommonError(f"candidate output already exists: {resolved}")
    return resolved


def write_private_output(output_root: Path, candidates: Mapping[str, bytes], metrics: list[dict[str, Any]]) -> None:
    output_root = _safe_private_output(output_root)
    output_root.mkdir(parents=True)
    for name in FILES:
        atomic_write(output_root / "MSG_PK" / "JP" / name, candidates[name])
    manifest = {
        "schema": PRIVATE_MANIFEST_SCHEMA,
        "contains_complete_game_resources": True,
        "installed_game_files_modified": False,
        "distribution_eligible": False,
        "resources": metrics,
    }
    atomic_write(output_root / "private_candidate_manifest.json", pretty_bytes(manifest))


def verify_public(steam_root: Path) -> dict[str, Any]:
    overlays, overlay_blobs = load_public_overlays()
    candidates_a, metrics_a = build_all(steam_root, overlays)
    candidates_b, metrics_b = build_all(steam_root, overlays)
    if candidates_a != candidates_b or metrics_a != metrics_b:
        raise SteamJpCommonError("full deterministic A/B build differs")
    validation, _blob = read_json(VALIDATION_PATH)
    if validation.get("schema") != VALIDATION_SCHEMA or validation.get("status") != "PASS":
        raise SteamJpCommonError("tracked validation identity differs")
    expected = validation.get("candidate_hashes")
    actual = {
        name: {"size": len(candidates_a[name]), "sha256": sha256(candidates_a[name])}
        for name in FILES
    }
    if expected != actual:
        raise SteamJpCommonError("tracked candidate hash pins differ")
    for artifact in validation.get("artifacts", []):
        path = REPO_ROOT / str(artifact["path"])
        if path == VALIDATION_PATH:
            continue
        blob = path.read_bytes()
        if len(blob) != int(artifact["size"]) or sha256(blob) != artifact["sha256"]:
            raise SteamJpCommonError(f"tracked artifact differs: {path}")
    return {
        "status": "PASS",
        "resource_count": len(FILES),
        "applied_count": sum(int(row["applied_count"]) for row in metrics_a),
        "legacy_nonmapped_coordinate_count": sum(
            int(row["legacy_nonmapped_coordinate_count"]) for row in metrics_a
        ),
        "collapsed_duplicate_coverage_count": sum(
            int(row["collapsed_duplicate_coverage_count"]) for row in metrics_a
        ),
        "unresolved_count": sum(int(row["unresolved_count"]) for row in metrics_a),
        "overlay_sha256": {name: sha256(overlay_blobs[name]) for name in FILES},
        "candidate_hashes": actual,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap_parser = subparsers.add_parser("bootstrap", help="derive tracked JP-native overlays")
    bootstrap_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    bootstrap_parser.add_argument("--legacy-stock-root", type=Path, default=DEFAULT_LEGACY_STOCK_ROOT)
    bootstrap_parser.add_argument("--legacy-candidate-a", type=Path, default=DEFAULT_LEGACY_CANDIDATE_A)
    bootstrap_parser.add_argument("--legacy-candidate-b", type=Path, default=DEFAULT_LEGACY_CANDIDATE_B)

    verify_parser = subparsers.add_parser("verify", help="verify tracked overlays against Steam JP")
    verify_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)

    build_parser = subparsers.add_parser("build", help="build complete candidates below tmp")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=DEFAULT_PRIVATE_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "bootstrap":
        result = bootstrap(args)
        print(f"status={result['status']}")
        print(f"applied={result['aggregate']['applied_count']}")
        print(
            f"legacy_nonmapped={result['aggregate']['legacy_nonmapped_coordinate_count']}"
        )
        print(f"collapsed_duplicate={result['aggregate']['collapsed_duplicate_coverage_count']}")
        print(f"unresolved={result['aggregate']['unresolved_count']}")
        return 0
    if args.command == "verify":
        result = verify_public(args.steam_root)
        print(f"status={result['status']}")
        print(f"applied={result['applied_count']}")
        print(f"legacy_nonmapped={result['legacy_nonmapped_coordinate_count']}")
        print(f"collapsed_duplicate={result['collapsed_duplicate_coverage_count']}")
        print(f"unresolved={result['unresolved_count']}")
        return 0
    if args.command == "build":
        overlays, _blobs = load_public_overlays()
        candidates, metrics = build_all(args.steam_root, overlays)
        write_private_output(args.output_root, candidates, metrics)
        print("status=PASS")
        print(f"output={args.output_root.resolve()}")
        print(f"applied={sum(int(row['applied_count']) for row in metrics)}")
        print(
            "legacy_nonmapped="
            f"{sum(int(row['legacy_nonmapped_coordinate_count']) for row in metrics)}"
        )
        print(
            "collapsed_duplicate="
            f"{sum(int(row['collapsed_duplicate_coverage_count']) for row in metrics)}"
        )
        print(f"unresolved={sum(int(row['unresolved_count']) for row in metrics)}")
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
