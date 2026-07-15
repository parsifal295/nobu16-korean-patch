#!/usr/bin/env python3
"""Audit the Steam JP runtime and emit a source-free ten-file contract.

The builder reads only the pinned Steam Japanese resources plus existing
source-free Korean overlays.  It never reads an SC container and never writes
an installed game file or a candidate binary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parent
REPO = SCRIPT.parents[2]
TOOLS = REPO / "tools"
STRDATA_TOOLS = REPO / "workstreams" / "switch_msgbre_v11"
sys.path[:0] = [str(TOOLS), str(STRDATA_TOOLS)]

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import (  # noqa: E402
    decompress_wrapper,
    parse_link,
    parse_wrapper_header,
    recompress_wrapper,
)
from strdata_container import parse_strdata, rebuild_strdata  # noqa: E402


STEAM_ROOT = Path("F:/SteamLibrary/steamapps/common/NOBU16")
FONT_CANDIDATE_ROOT = (
    REPO / "tmp" / "jp_font_verified_stock_reuse_v1" / "private" / "candidate"
)
STRDATA_RESOURCE = "MSG/JP/strdata.bin"
FONT_RESOURCES = {
    "RES_JP/res_lang.bin": {
        "stock": {"size": 153_198_542, "sha256": "D32898C186CBDC7534692269C062E888ACE3B7A58F5DB4FEC8B0C745DADAAE53"},
        "candidate": {"size": 175_097_407, "sha256": "4395B84C5F678E37D8F39BCEEFF1986F62B07A54FF7936FC1402412AF07536F2"},
        "target_entries": [6, 7],
        "entry_count": 42,
    },
    "RES_JP_PK/res_lang_pk.bin": {
        "stock": {"size": 140_729_547, "sha256": "67CC064ED9D138B85255F8AA6AC5B5E47D7239E06E15A4E5AD68922274300EF5"},
        "candidate": {"size": 162_625_225, "sha256": "697F5034140A35A676CC0D0006CCECE4753D823109C5792500C46DE6499C9C12"},
        "target_entries": [16, 17],
        "entry_count": 27,
    },
}

TARGETS = {
    "MSG/JP/strdata.bin": {"size": 507_054, "sha256": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0"},
    "MSG_PK/JP/msgbre.bin": {"size": 221_127, "sha256": "945A0E9157E2DBD12781FFA5A986D93681325F40B6486348B1AB311D3BEE1D6D"},
    "MSG_PK/JP/msgdata.bin": {"size": 272_453, "sha256": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E"},
    "MSG_PK/JP/msgev.bin": {"size": 562_226, "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84"},
    "MSG_PK/JP/msggame.bin": {"size": 721_304, "sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"},
    "MSG_PK/JP/msgire.bin": {"size": 12_376, "sha256": "0AFBFE11A380A9C98FB3B368092A05B39ABB6F80C4B0723AD3B6DB55C2559C5D"},
    "MSG_PK/JP/msgstf.bin": {"size": 6_841, "sha256": "01EEB0B1B4879B6C70E9D7564F9D2FBD93E7B537CF8C614A58EEA82A83785A29"},
    "MSG_PK/JP/msgui.bin": {"size": 64_976, "sha256": "9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A"},
    "RES_JP/res_lang.bin": FONT_RESOURCES["RES_JP/res_lang.bin"]["stock"],
    "RES_JP_PK/res_lang_pk.bin": FONT_RESOURCES["RES_JP_PK/res_lang_pk.bin"]["stock"],
}

OVERLAYS = [
    {
        "path": REPO / "workstreams/strdata/public/strdata_ko_name_labels_b00s0000_0099.v0.1.json",
        "size": 18_874,
        "sha256": "9B1C3F1B2C3C1BFC44974C6C2E1573DA6C48433B9E945EEF6EC5BE2C54B85F24",
        "priority": 0,
    },
    {
        "path": REPO / "workstreams/strdata_pk_shared_ui/public/strdata_ko_pk_shared_ui_b01_1.v1.json",
        "size": 1_142,
        "sha256": "DF58FD55FF17F5AA39F73DF4445360BA9BE18AC9C87E3B7E245F07C359EC5A4D",
        "priority": 1,
    },
    {
        "path": REPO / "workstreams/switch_strdata_v13_direct_transfer/public/strdata_ko_switch_v13_direct_transfer_24424.v1.json",
        "size": 5_169_221,
        "sha256": "2C4B1F7C52D5B04EE915693C20D4662011E18A3B6535212905609B3ABBA9FE98",
        "priority": 2,
    },
]

STRDATA_RAW = {"size": 763_928, "sha256": "EAB14063C2060CE11794232F483F0B2210B3BD58118165CBEEC2F37176C25649"}
SLOT_COUNTS = [25_069, 4_100, 3_000, 122, 20]
BRACKET = re.compile(r"\[[A-Za-z0-9_]+\]")
HAN_KANA = re.compile(r"[\u2e80-\u2fff\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


class AuditError(RuntimeError):
    pass


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha(blob)}


def text_hash(text: str) -> str:
    return sha(text.encode("utf-16le"))


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any, verify: bool) -> dict[str, Any]:
    blob = json_bytes(value)
    if verify:
        if not path.is_file() or path.read_bytes() != blob:
            raise AuditError(f"verification differs: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    return {"path": path.relative_to(ROOT).as_posix(), **spec(blob)}


def require_pin(path: Path, expected: dict[str, Any], label: str) -> bytes:
    if not path.is_file():
        raise AuditError(f"missing {label}: {path}")
    blob = path.read_bytes()
    if spec(blob) != expected:
        raise AuditError(f"{label} pin differs: {spec(blob)}")
    return blob


def coordinate_map(archive: Any) -> dict[tuple[int, int], str]:
    return {
        (block.block_id, slot): value
        for block in archive.blocks
        for slot, value in enumerate(block.texts)
    }


def load_korean_catalog() -> tuple[dict[tuple[int, int], str], list[dict[str, Any]]]:
    merged: dict[tuple[int, int], str] = {}
    metadata: list[dict[str, Any]] = []
    # Later overlays fill only previously unclaimed coordinates.  The first
    # two project overlays intentionally retain their wording over v1.3.
    for item in sorted(OVERLAYS, key=lambda row: row["priority"]):
        blob = require_pin(item["path"], {"size": item["size"], "sha256": item["sha256"]}, "Korean overlay")
        value = json.loads(blob.decode("utf-8"))
        entries = value.get("entries")
        if not isinstance(entries, list):
            raise AuditError("overlay entries are absent")
        added = 0
        conflicts = 0
        for entry in entries:
            coordinate = (entry["block_id"], entry["slot_id"])
            replacement = entry["ko"]
            if coordinate in merged:
                conflicts += 1
                continue
            merged[coordinate] = replacement
            added += 1
        metadata.append({
            "path": item["path"].relative_to(REPO).as_posix(),
            "size": len(blob),
            "sha256": sha(blob),
            "declared_entries": len(entries),
            "accepted_entries": added,
            "precedence_conflicts": conflicts,
            "commercial_source_text_read": False,
        })
    return merged, metadata


def replacement_failures(source: str, replacement: str) -> list[str]:
    failures = [item.split(":", 1)[0] for item in common.invariant_mismatches(source, replacement)]
    if BRACKET.findall(source) != BRACKET.findall(replacement):
        failures.append("bracket_tokens")
    if HAN_KANA.search(replacement):
        failures.append("han_or_kana_in_ko")
    if not any(0xAC00 <= ord(ch) <= 0xD7A3 for ch in replacement):
        failures.append("no_hangul_syllable")
    return sorted(set(failures))


def build_strdata(steam_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    packed = require_pin(steam_root / STRDATA_RESOURCE, TARGETS[STRDATA_RESOURCE], "Steam JP strdata")
    wrapper, raw = decompress_wrapper(packed)
    if spec(raw) != STRDATA_RAW:
        raise AuditError("Steam JP strdata raw pin differs")
    archive = parse_strdata(raw)
    if [block.slot_count for block in archive.blocks] != SLOT_COUNTS:
        raise AuditError("Steam JP strdata slot vector differs")
    if rebuild_strdata(archive) != raw:
        raise AuditError("Steam JP strdata identity rebuild differs")
    source = coordinate_map(archive)
    korean, overlay_metadata = load_korean_catalog()
    if len(korean) != 24_525:
        raise AuditError(f"merged Korean coordinate count differs: {len(korean)}")

    direct: dict[tuple[int, int], str] = {}
    blocked: list[dict[str, Any]] = []
    for coordinate, replacement in sorted(korean.items()):
        if coordinate not in source:
            blocked.append({"coordinate": list(coordinate), "reason": ["coordinate_absent"]})
            continue
        failures = replacement_failures(source[coordinate], replacement)
        if failures:
            blocked.append({
                "coordinate": list(coordinate),
                "source_jp_utf16le_sha256": text_hash(source[coordinate]),
                "ko_utf16le_sha256": text_hash(replacement),
                "reason": failures,
            })
        else:
            direct[coordinate] = replacement

    entries = [
        {
            "block_id": block_id,
            "slot_id": slot_id,
            "source_jp_utf16le_sha256": text_hash(source[(block_id, slot_id)]),
            "ko": replacement,
        }
        for (block_id, slot_id), replacement in sorted(direct.items())
    ]
    overlay = {
        "schema": "nobu16.kr.strdata-jp-block-overlay.v1",
        "overlay_id": "steam-jp-strdata-rebased-v1",
        "resource": STRDATA_RESOURCE,
        "base_language": "JP",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": {**TARGETS[STRDATA_RESOURCE], "raw_size": len(raw), "raw_sha256": sha(raw), "block_slot_counts": SLOT_COUNTS},
        "entries": entries,
    }

    replacements = {block.block_id: list(block.texts) for block in archive.blocks}
    for (block_id, slot_id), replacement in direct.items():
        replacements[block_id][slot_id] = replacement
    candidate_raw = rebuild_strdata(archive, replacements)
    candidate = recompress_wrapper(candidate_raw, wrapper)
    _, check_raw = decompress_wrapper(candidate)
    checked = coordinate_map(parse_strdata(check_raw))
    changed = sorted(key for key in source if source[key] != checked[key])
    if changed != sorted(direct):
        raise AuditError("JP strdata candidate changed an unexpected coordinate")
    if any(checked[key] != value for key, value in direct.items()):
        raise AuditError("JP strdata candidate replacement differs")
    if any(checked[key] != source[key] for key in source if key not in direct):
        raise AuditError("JP strdata candidate failed non-target preservation")

    audit = {
        "source_resource": STRDATA_RESOURCE,
        "source_language": "JP",
        "sc_container_read": False,
        "source": {**TARGETS[STRDATA_RESOURCE], "raw_size": len(raw), "raw_sha256": sha(raw), "coordinate_count": len(source), "block_slot_counts": SLOT_COUNTS},
        "korean_catalog": {"coordinate_count": len(korean), "inputs": overlay_metadata},
        "direct_rebase_count": len(direct),
        "blocked_count": len(blocked),
        "blocked_reason_counts": reason_counts(blocked),
        "candidate": {"packed_size": len(candidate), "packed_sha256": sha(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha(candidate_raw), "changed_coordinate_count": len(changed)},
        "proofs": {"jp_source_hash_guarded": True, "block_slot_counts_preserved": True, "untargeted_coordinates_exact": True, "wrapper_roundtrip_exact": check_raw == candidate_raw, "candidate_binary_written": False},
        "blocked": blocked,
    }
    return overlay, audit, audit["candidate"]


def reason_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for reason in row["reason"]:
            counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items()))


def font_audit(steam_root: Path, candidate_root: Path) -> dict[str, Any]:
    routes: list[dict[str, Any]] = []
    for relative, contract in FONT_RESOURCES.items():
        stock_blob = require_pin(steam_root / relative, contract["stock"], f"Steam {relative}")
        candidate_blob = require_pin(candidate_root / relative, contract["candidate"], f"font candidate {relative}")
        stock = parse_link(stock_blob)
        candidate = parse_link(candidate_blob)
        targets = set(contract["target_entries"])
        if len(stock.entries) != contract["entry_count"] or len(candidate.entries) != contract["entry_count"]:
            raise AuditError(f"{relative} LINK count differs")
        non_target_failures: list[int] = []
        target_prefix_failures: list[int] = []
        target_gap_failures: list[int] = []
        changed: list[int] = []
        for left, right in zip(stock.entries, candidate.entries, strict=True):
            if left.data != right.data:
                changed.append(left.index)
            if left.index not in targets and (left.data != right.data or left.gap_after != right.gap_after):
                non_target_failures.append(left.index)
            if left.index in targets:
                if parse_wrapper_header(left.data).prefix != parse_wrapper_header(right.data).prefix:
                    target_prefix_failures.append(left.index)
                if left.gap_after != right.gap_after:
                    target_gap_failures.append(left.index)
        if changed != sorted(targets) or non_target_failures or target_prefix_failures or target_gap_failures:
            raise AuditError(f"{relative} preservation contract failed")
        routes.append({
            "resource": relative,
            "stock": contract["stock"],
            "candidate": contract["candidate"],
            "link_entry_count": len(stock.entries),
            "changed_entries": changed,
            "proofs": {
                "exact_predecessor": True,
                "non_target_entry_data_and_gaps_exact": True,
                "target_wrapper_prefixes_exact": True,
                "target_gaps_exact": True,
            },
        })
    return {"route_count": len(routes), "routes": routes, "all_passed": True}


def predecessor_audit(steam_root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for relative, expected in sorted(TARGETS.items()):
        blob = require_pin(steam_root / relative, expected, f"Steam predecessor {relative}")
        rows.append({"path": relative, "actual": spec(blob), "matches_contract": True})
    return {
        "file_count": len(rows),
        "all_ten_exact": len(rows) == 10 and all(row["matches_contract"] for row in rows),
        "files": rows,
    }


def build_contract(strdata_candidate: dict[str, Any], fonts: dict[str, Any]) -> dict[str, Any]:
    candidate_specs = {
        STRDATA_RESOURCE: {"size": strdata_candidate["packed_size"], "sha256": strdata_candidate["packed_sha256"], "status": "reproducible_in_memory_not_staged"},
    }
    for route in fonts["routes"]:
        candidate_specs[route["resource"]] = {**route["candidate"], "status": "verified_existing_candidate"}
    entries = []
    for relative in sorted(TARGETS):
        candidate = candidate_specs.get(relative)
        entries.append({
            "path": relative,
            "predecessor": TARGETS[relative],
            "candidate": candidate,
            "ready_for_candidate_root": candidate is not None,
        })
    blocked = [entry["path"] for entry in entries if not entry["ready_for_candidate_root"]]
    return {
        "schema": "nobu16.kr.steam-jp-runtime-candidate-root-contract.v1",
        "runtime_language": "JP",
        "steam_pk_version": "1.1.7",
        "steam_build_id": "18823764",
        "candidate_root_paths": sorted(TARGETS),
        "candidate_root_file_count": 10,
        "entries": entries,
        "readiness": {"known_candidate_count": len(entries) - len(blocked), "blocked_candidate_count": len(blocked), "blocked_paths": blocked, "complete_candidate_root_ready": not blocked},
        "transaction": {
            "tool": "tools/pk_file_only_transaction.py",
            "target_scope": ["MSG/JP/strdata.bin", "MSG_PK/JP", "RES_JP", "RES_JP_PK"],
            "dry_run_prerequisites": [
                "all NOBU16 processes closed",
                "all ten installed predecessor hashes exact",
                "all ten candidate files staged under exact relative paths",
                "candidate-root contains no extra files",
                "hash-only transaction manifest generated from the same predecessor vector",
                "verified backup root under game-root/KR_PATCH_BACKUP",
            ],
            "dry_run_allowed_now": False,
            "write_to_steam_performed": False,
        },
        "prohibitions": {"sc_container_input": True, "memory_patch": True, "dll_injection": True, "hooking": True, "exe_or_registry_modification": True},
    }


def source_free(value: Any, label: str) -> dict[str, int]:
    text = json_bytes(value).decode("utf-8")
    counts = {"han_or_kana_count": len(HAN_KANA.findall(text)), "embedded_nul_count": text.count("\0")}
    if counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}:
        raise AuditError(f"{label} contains forbidden source script: {counts}")
    return counts


def run(args: argparse.Namespace) -> dict[str, Any]:
    predecessors = predecessor_audit(args.steam_root)
    overlay, strdata, strdata_candidate = build_strdata(args.steam_root)
    fonts = font_audit(args.steam_root, args.font_candidate_root)
    contract = build_contract(strdata_candidate, fonts)
    overlay_name = f"strdata_ko_jp_source_rebased_{overlay['entry_count']}.v1.json"
    overlay_meta = write_json(ROOT / "public" / overlay_name, overlay, args.verify)
    contract_meta = write_json(ROOT / "contract.v1.json", contract, args.verify)
    validation = {
        "schema": "nobu16.kr.steam-jp-runtime-skeleton-validation.v1",
        "passed": True,
        "steam_root_written": False,
        "sc_container_read": False,
        "predecessor_vector": predecessors,
        "strdata": strdata,
        "fonts": fonts,
        "candidate_root": contract["readiness"],
        "artifacts": {"overlay": overlay_meta, "contract": contract_meta},
        "source_free": {"overlay": source_free(overlay, "overlay"), "contract": source_free(contract, "contract")},
    }
    validation_meta = write_json(ROOT / "validation.v1.json", validation, args.verify)
    return {**validation, "validation_artifact": validation_meta}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=STEAM_ROOT)
    parser.add_argument("--font-candidate-root", type=Path, default=FONT_CANDIDATE_ROOT)
    parser.add_argument("--verify", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    result = run(parse_args())
    print(json.dumps({
        "passed": result["passed"],
        "strdata_direct": result["strdata"]["direct_rebase_count"],
        "strdata_blocked": result["strdata"]["blocked_count"],
        "font_routes": result["fonts"]["route_count"],
        "candidate_known": result["candidate_root"]["known_candidate_count"],
        "candidate_blocked": result["candidate_root"]["blocked_candidate_count"],
    }, indent=2))
