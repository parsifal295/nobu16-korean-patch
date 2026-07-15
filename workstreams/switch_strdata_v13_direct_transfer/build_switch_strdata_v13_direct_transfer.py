#!/usr/bin/env python3
"""Build the source-free Switch v1.3 -> PC SC strdata direct-transfer overlay.

The Switch archive is used only as translation input.  The candidate always
starts from the pinned pristine PC ``MSG/SC/strdata.bin`` and changes verified
``(block_id, slot_id)`` coordinates.  The complete Switch binary is never
copied into the PC tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
STRDATA_ROOT = REPO_ROOT / "workstreams" / "switch_msgbre_v11"
sys.path[:0] = [str(TOOLS_ROOT), str(STRDATA_ROOT)]

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from strdata_container import (  # noqa: E402
    parse_strdata as parse_raw_strdata,
    rebuild_strdata as rebuild_raw_strdata,
)


def coordinate_texts(archive: Any) -> dict[tuple[int, int], str]:
    return {
        (block.block_id, slot_id): value
        for block in archive.blocks
        for slot_id, value in enumerate(block.texts)
    }


RESOURCE = "MSG/SC/strdata.bin"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/strdata.bin"
DEFAULT_SWITCH_ZIP = (
    REPO_ROOT
    / "tmp"
    / "third_party_switch_v13"
    / "NobunagaShinsei_KoreanPatch_v1.3.zip"
)
PC_JP_RELATIVE = Path("MSG/JP/strdata.bin")
PC_SC_RELATIVE = Path(RESOURCE)
EXISTING_B00 = (
    REPO_ROOT
    / "workstreams"
    / "strdata"
    / "public"
    / "strdata_ko_name_labels_b00s0000_0099.v0.1.json"
)
EXISTING_SHARED_UI = (
    REPO_ROOT
    / "workstreams"
    / "strdata_pk_shared_ui"
    / "public"
    / "strdata_ko_pk_shared_ui_b01_1.v1.json"
)
EXISTING_OVERLAY_PINS = {
    "b00": {
        "path": "workstreams/strdata/public/strdata_ko_name_labels_b00s0000_0099.v0.1.json",
        "entry_count": 100,
        "size": 18_874,
        "sha256": "9B1C3F1B2C3C1BFC44974C6C2E1573DA6C48433B9E945EEF6EC5BE2C54B85F24",
    },
    "shared_ui": {
        "path": "workstreams/strdata_pk_shared_ui/public/strdata_ko_pk_shared_ui_b01_1.v1.json",
        "entry_count": 1,
        "size": 1_142,
        "sha256": "DF58FD55FF17F5AA39F73DF4445360BA9BE18AC9C87E3B7E245F07C359EC5A4D",
    },
}
# The audit proved that 93 of B00's values equal the safe Switch value.  Only
# these seven B00 coordinates intentionally keep earlier project wording.
# Encoding the small conflict set makes this workstream reproducible even when
# the user-owned predecessor workstream is not part of a checkout.
B00_CONFLICT_OVERRIDES = {
    (0, 21): "이이오",
    (0, 28): "이시마키",
    (0, 32): "이치쿠리",
    (0, 34): "이치마다",
    (0, 54): "우츠노미야",
    (0, 58): "에네이",
    (0, 93): "가상",
}

BATCH_ID = "switch-strdata-v13-direct-transfer-24424-v1"
OVERLAY_ID = BATCH_ID
OVERLAY_NAME = "strdata_ko_switch_v13_direct_transfer_24424.v1.json"
EVIDENCE_NAME = "switch_strdata_v13_direct_transfer_evidence.v1.json"
REVIEW_NAME = "switch_strdata_v13_direct_transfer_review.v1.json"
VALIDATION_NAME = "switch_strdata_v13_direct_transfer_validation.v1.json"
OVERLAY_SCHEMA = "nobu16.kr.strdata-block-overlay.v1"

ZIP_PIN = {
    "size": 72_977_145,
    "sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
}
SWITCH_PIN = {
    "packed_size": 404_189,
    "packed_sha256": "5F065B9DBDAE4DC75E2D7186A76C0AC988FB504F018F820C204262BF07D5061B",
    "raw_size": 953_512,
    "raw_sha256": "245538466576E3880B3C53C0CB4929685096DF394C27CCB93B2C893615A46ADE",
}
PC_JP_PIN = {
    "packed_size": 507_054,
    "packed_sha256": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "raw_size": 763_928,
    "raw_sha256": "EAB14063C2060CE11794232F483F0B2210B3BD58118165CBEEC2F37176C25649",
}
PC_SC_PIN = {
    "packed_size": 516_628,
    "packed_sha256": "93F88D71210B96783749CEB948E0713D7E6552F764F644092B71A5FD0C994B88",
    "raw_size": 760_388,
    "raw_sha256": "17EF622F36BA94009F67519DC79ED543C223B467311E51711A009F9DD0816214",
}
BLOCK_SLOT_COUNTS = [25_069, 4_100, 3_000, 122, 20]
EXPECTED = {
    "total_coordinates": 32_311,
    "direct": 24_525,
    "semantic_aligned": 0,
    "manual": 1_431,
    "unusable": 6_355,
    "existing_b00": 100,
    "existing_shared_ui": 1,
    "net_new": 24_424,
    "net_new_per_block": {"0": 19_020, "1": 3_081, "2": 2_203, "3": 120, "4": 0},
    "direct_coordinates_sha256": "15047708DCC3EEA6254CE0ECB8121D25CBCDC3AEF6CE8DE232BBE40D65DE0A58",
    "net_new_coordinates_sha256": "837B2E38AD16C6F712C2372F214C3DE13209110B62B2A5A4A588473F5F31B15D",
    "integrated_coordinates_sha256": "15047708DCC3EEA6254CE0ECB8121D25CBCDC3AEF6CE8DE232BBE40D65DE0A58",
    "candidate_packed_size": 950_221,
    "candidate_packed_sha256": "7C566A0EB00BFBD9649B5BBC9202B5244AED2EB8DC014CE8417151CAE6B6DAD6",
    "candidate_raw_size": 946_484,
    "candidate_raw_sha256": "24F41BB71CED3EF2A00B6E9A20B50F3DBBEB6BDB0431DFECEF898BD23FCFA54F",
}

BRACKET_TOKEN_RE = re.compile(r"\[[A-Za-z0-9_]+\]")
HAN_OR_KANA_RE = re.compile(
    r"[\u2e80-\u2fff\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)


class DirectTransferError(ValueError):
    """Raised when a pinned input, classification, or rebuild proof differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16le"))


def canonical_hash(value: Any) -> str:
    blob = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256(blob)


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": path.relative_to(WORKSTREAM_ROOT).as_posix()
        if path.is_relative_to(WORKSTREAM_ROOT)
        else str(path),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=common.strict_object)
    if not isinstance(value, dict):
        raise DirectTransferError(f"JSON root is not an object: {path}")
    return value


def has_semantic_text(text: str) -> bool:
    return any(character.isprintable() and not character.isspace() for character in text)


def has_hangul_syllable(text: str) -> bool:
    return any(0xAC00 <= ord(character) <= 0xD7A3 for character in text)


def script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": sum(
            (0x3400 <= ord(character) <= 0x4DBF)
            or (0x4E00 <= ord(character) <= 0x9FFF)
            or (0xF900 <= ord(character) <= 0xFAFF)
            for character in text
        ),
        "kana_count": sum(
            (0x3040 <= ord(character) <= 0x30FF)
            or (0x31F0 <= ord(character) <= 0x31FF)
            for character in text
        ),
    }


def direct_contract(source_sc: str, replacement: str) -> tuple[bool, dict[str, Any]]:
    mismatches = common.invariant_mismatches(source_sc, replacement)
    bracket_equal = BRACKET_TOKEN_RE.findall(source_sc) == BRACKET_TOKEN_RE.findall(replacement)
    scripts = script_counts(replacement)
    good = (
        not mismatches
        and bracket_equal
        and scripts == {"cjk_unified_count": 0, "kana_count": 0}
        and has_hangul_syllable(replacement)
    )
    return good, {
        "invariant_mismatch_count": len(mismatches),
        "bracket_placeholder_sequence_equal": bracket_equal,
        "cjk_unified_count": scripts["cjk_unified_count"],
        "kana_count": scripts["kana_count"],
        "has_hangul_syllable": has_hangul_syllable(replacement),
    }


def verify_pin(blob: bytes, pin: dict[str, Any], label: str, *, prefix: str = "packed") -> None:
    actual = {f"{prefix}_size": len(blob), f"{prefix}_sha256": sha256(blob)}
    expected = {
        f"{prefix}_size": pin[f"{prefix}_size"],
        f"{prefix}_sha256": pin[f"{prefix}_sha256"],
    }
    if actual != expected:
        raise DirectTransferError(f"{label} pin mismatch: {actual}")


def load_pinned_pc_sc(game_root: Path) -> bytes:
    candidates = [game_root / PC_SC_RELATIVE]
    backup_root = game_root / "KR_PATCH_BACKUP" / "file_only_transaction"
    candidates.extend(sorted(backup_root.glob(f"*/originals/{RESOURCE}")))
    matches: list[Path] = []
    for path in candidates:
        if not path.is_file():
            continue
        blob = path.read_bytes()
        if len(blob) == PC_SC_PIN["packed_size"] and sha256(blob) == PC_SC_PIN["packed_sha256"]:
            matches.append(path)
    if not matches:
        raise DirectTransferError("pinned pristine PC SC strdata was not found live or in backups")
    return matches[0].read_bytes()


def parse_pinned(blob: bytes, pin: dict[str, Any], label: str) -> tuple[Any, bytes, Any]:
    verify_pin(blob, pin, label)
    wrapper, raw = decompress_wrapper(blob)
    verify_pin(raw, pin, label, prefix="raw")
    archive = parse_raw_strdata(raw)
    if [block.slot_count for block in archive.blocks] != BLOCK_SLOT_COUNTS:
        raise DirectTransferError(f"{label} block slot counts changed")
    if rebuild_raw_strdata(archive) != raw:
        raise DirectTransferError(f"{label} identity rebuild is not byte-exact")
    return wrapper, raw, archive


def load_inputs(game_root: Path, switch_zip: Path) -> dict[str, Any]:
    zip_blob = switch_zip.read_bytes()
    if {"size": len(zip_blob), "sha256": sha256(zip_blob)} != ZIP_PIN:
        raise DirectTransferError("Switch v1.3 ZIP pin mismatch")
    with zipfile.ZipFile(switch_zip) as archive:
        matches = [item for item in archive.infolist() if item.filename == SWITCH_MEMBER]
        if len(matches) != 1:
            raise DirectTransferError("Switch strdata member is not unique")
        switch_blob = archive.read(matches[0])

    pc_jp_blob = (game_root / PC_JP_RELATIVE).read_bytes()
    pc_sc_blob = load_pinned_pc_sc(game_root)
    result: dict[str, Any] = {
        "zip_blob": zip_blob,
        "pc_jp_blob": pc_jp_blob,
        "pc_sc_blob": pc_sc_blob,
        "switch_blob": switch_blob,
    }
    for name, blob, pin in (
        ("pc_jp", pc_jp_blob, PC_JP_PIN),
        ("pc_sc", pc_sc_blob, PC_SC_PIN),
        ("switch", switch_blob, SWITCH_PIN),
    ):
        wrapper, raw, archive = parse_pinned(blob, pin, name)
        result[f"{name}_wrapper"] = wrapper
        result[f"{name}_raw"] = raw
        result[f"{name}_archive"] = archive
    coordinate_sets = [
        set(coordinate_texts(result[f"{name}_archive"]))
        for name in ("pc_jp", "pc_sc", "switch")
    ]
    if not (coordinate_sets[0] == coordinate_sets[1] == coordinate_sets[2]):
        raise DirectTransferError("PC JP, PC SC, and Switch coordinate sets differ")
    if len(coordinate_sets[0]) != EXPECTED["total_coordinates"]:
        raise DirectTransferError("strdata total coordinate count changed")
    return result


def classify_direct(inputs: dict[str, Any]) -> dict[str, Any]:
    pc_jp = coordinate_texts(inputs["pc_jp_archive"])
    pc_sc = coordinate_texts(inputs["pc_sc_archive"])
    switch = coordinate_texts(inputs["switch_archive"])

    by_jp_hash: dict[str, dict[str, Any]] = {}
    for coordinate in sorted(pc_jp):
        source_jp = pc_jp[coordinate]
        row = by_jp_hash.setdefault(
            text_hash(source_jp), {"source_jp": source_jp, "coordinates": [], "switch_values": []}
        )
        if row["source_jp"] != source_jp:
            raise DirectTransferError("PC JP UTF-16LE SHA-256 collision")
        row["coordinates"].append(coordinate)
        row["switch_values"].append(switch[coordinate])

    safe_values: dict[tuple[int, int], str] = {}
    details: dict[tuple[int, int], dict[str, Any]] = {}
    classes: Counter[str] = Counter()
    per_block: dict[int, Counter[str]] = defaultdict(Counter)
    for coordinate in sorted(pc_sc):
        source_sc = pc_sc[coordinate]
        source_jp = pc_jp[coordinate]
        same_value = switch[coordinate]
        row = by_jp_hash[text_hash(source_jp)]
        all_korean_values = sorted(
            {
                value
                for value in row["switch_values"]
                if value != source_jp and has_semantic_text(value) and has_hangul_syllable(value)
            }
        )
        same_has_korean = (
            same_value != source_jp
            and has_semantic_text(same_value)
            and has_hangul_syllable(same_value)
        )
        same_safe, contract = direct_contract(source_sc, same_value) if same_has_korean else (False, {})
        source_visible = has_semantic_text(source_jp) and has_semantic_text(source_sc)

        classification: str
        usable: str | None = None
        if same_has_korean and same_safe and source_visible:
            classification = "direct"
            usable = same_value
        else:
            safe_hash_values = [
                value
                for value in all_korean_values
                if source_visible and direct_contract(source_sc, value)[0]
            ]
            if len(safe_hash_values) == 1 and safe_hash_values[0] != same_value:
                classification = "semantic-aligned"
                usable = safe_hash_values[0]
                contract = direct_contract(source_sc, usable)[1]
            elif all_korean_values:
                classification = "manual"
            else:
                classification = "unusable"

        classes[classification] += 1
        per_block[coordinate[0]][classification] += 1
        if usable is not None and usable != source_sc:
            safe_values[coordinate] = usable
        details[coordinate] = {
            "classification": classification,
            "source_sc_utf16le_sha256": text_hash(source_sc),
            "pc_jp_utf16le_sha256": text_hash(source_jp),
            "switch_ko_utf16le_sha256": text_hash(usable) if usable is not None else None,
            "pc_jp_source_occurrence_count": len(row["coordinates"]),
            "contract": contract,
        }

    expected_classes = {
        "direct": EXPECTED["direct"],
        "semantic-aligned": EXPECTED["semantic_aligned"],
        "manual": EXPECTED["manual"],
        "unusable": EXPECTED["unusable"],
    }
    if {key: classes[key] for key in expected_classes} != expected_classes:
        raise DirectTransferError(f"classification counts changed: {dict(classes)}")
    safe_coordinates = sorted(safe_values)
    if len(safe_coordinates) != EXPECTED["direct"]:
        raise DirectTransferError("safe direct coordinate count changed")
    if canonical_hash([list(value) for value in safe_coordinates]) != EXPECTED["direct_coordinates_sha256"]:
        raise DirectTransferError("safe direct coordinate set changed")
    return {
        "pc_jp": pc_jp,
        "pc_sc": pc_sc,
        "switch": switch,
        "safe_values": safe_values,
        "details": details,
        "classification_counts": expected_classes,
        "per_block": {
            str(block): {name: counts[name] for name in expected_classes}
            for block, counts in sorted(per_block.items())
        },
    }


def load_existing_overlays(
    pc_sc: dict[tuple[int, int], str],
    safe_values: dict[tuple[int, int], str],
) -> tuple[dict[tuple[int, int], str], dict[str, Any]]:
    b00_coordinates = [(0, slot_id) for slot_id in range(EXPECTED["existing_b00"])]
    shared_coordinates = [(1, 22)]
    if any(coordinate not in safe_values for coordinate in b00_coordinates + shared_coordinates):
        raise DirectTransferError("an existing overlay coordinate left the safe direct set")

    b00_values = {coordinate: safe_values[coordinate] for coordinate in b00_coordinates}
    b00_values.update(B00_CONFLICT_OVERRIDES)
    shared_values = {coordinate: safe_values[coordinate] for coordinate in shared_coordinates}
    values = {**b00_values, **shared_values}
    if len(values) != EXPECTED["existing_b00"] + EXPECTED["existing_shared_ui"]:
        raise DirectTransferError("derived existing-overlay precedence set changed")
    for coordinate, replacement in values.items():
        if coordinate not in pc_sc or not direct_contract(pc_sc[coordinate], replacement)[0]:
            raise DirectTransferError(f"derived existing overlay invariant mismatch: {coordinate}")

    # When the user-owned predecessor workstreams are present, prove that the
    # compact seven-conflict derivation exactly reproduces all 101 values.  The
    # fixed pins remain recorded even when those optional paths are absent.
    for label, path, expected_values in (
        ("b00", EXISTING_B00, b00_values),
        ("shared_ui", EXISTING_SHARED_UI, shared_values),
    ):
        if not path.is_file():
            continue
        blob = path.read_bytes()
        pin = EXISTING_OVERLAY_PINS[label]
        if len(blob) != pin["size"] or sha256(blob) != pin["sha256"]:
            raise DirectTransferError(f"existing {label} overlay pin changed")
        overlay = read_json(path)
        entries = overlay.get("entries")
        if not isinstance(entries, list) or len(entries) != pin["entry_count"]:
            raise DirectTransferError(f"existing {label} overlay count changed")
        actual_values: dict[tuple[int, int], str] = {}
        for entry in entries:
            coordinate = (entry["block_id"], entry["slot_id"])
            if coordinate in actual_values:
                raise DirectTransferError(f"existing {label} overlay duplicate: {coordinate}")
            if entry["source_sc_utf16le_sha256"] != text_hash(pc_sc[coordinate]):
                raise DirectTransferError(f"existing {label} source hash mismatch: {coordinate}")
            actual_values[coordinate] = entry["ko"]
        if actual_values != expected_values:
            raise DirectTransferError(f"derived {label} precedence values differ from pinned overlay")
    return values, EXISTING_OVERLAY_PINS


def build_artifact_models(inputs: dict[str, Any], classified: dict[str, Any]) -> dict[str, Any]:
    safe_values = classified["safe_values"]
    pc_sc = classified["pc_sc"]
    existing_values, existing_metadata = load_existing_overlays(pc_sc, safe_values)
    if not set(existing_values).issubset(safe_values):
        raise DirectTransferError("existing overlays are no longer a subset of safe direct coordinates")
    net_new = {
        coordinate: value
        for coordinate, value in safe_values.items()
        if coordinate not in existing_values
    }
    coordinates = sorted(net_new)
    if len(coordinates) != EXPECTED["net_new"]:
        raise DirectTransferError("net-new direct coordinate count changed")
    if canonical_hash([list(value) for value in coordinates]) != EXPECTED["net_new_coordinates_sha256"]:
        raise DirectTransferError("net-new direct coordinate set changed")
    per_block = Counter(str(block_id) for block_id, _slot_id in coordinates)
    actual_per_block = {str(block): per_block[str(block)] for block in range(5)}
    if actual_per_block != EXPECTED["net_new_per_block"]:
        raise DirectTransferError(f"net-new per-block counts changed: {actual_per_block}")

    entries = [
        {
            "block_id": coordinate[0],
            "slot_id": coordinate[1],
            "source_sc_utf16le_sha256": text_hash(pc_sc[coordinate]),
            "ko": net_new[coordinate],
        }
        for coordinate in coordinates
    ]
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": OVERLAY_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "provenance": {
            "kind": "switch_v1.3_same_coordinate_direct_transfer",
            "source_release": "v1.3",
            "source_member": SWITCH_MEMBER,
            "whole_switch_file_copied": False,
            "pc_pristine_sc_rebuild": True,
            "existing_overlay_values_take_precedence": True,
        },
        "entries": entries,
    }
    evidence_entries = []
    review_entries = []
    for coordinate in coordinates:
        detail = classified["details"][coordinate]
        evidence_entries.append(
            {
                "block_id": coordinate[0],
                "slot_id": coordinate[1],
                "classification": detail["classification"],
                "same_block_slot_coordinate": True,
                "pc_sc_utf16le_sha256": detail["source_sc_utf16le_sha256"],
                "pc_jp_utf16le_sha256": detail["pc_jp_utf16le_sha256"],
                "switch_ko_utf16le_sha256": detail["switch_ko_utf16le_sha256"],
                "pc_jp_source_occurrence_count": detail["pc_jp_source_occurrence_count"],
                "invariant_mismatch_count": detail["contract"]["invariant_mismatch_count"],
                "bracket_placeholder_sequence_equal": detail["contract"]["bracket_placeholder_sequence_equal"],
                "source_script_free": detail["contract"]["cjk_unified_count"] == 0
                and detail["contract"]["kana_count"] == 0,
            }
        )
        review_entries.append(
            {
                "block_id": coordinate[0],
                "slot_id": coordinate[1],
                "status": "translated",
                "translation_origin": "switch_v1.3_same_coordinate_direct_transfer",
                "automatic_contract_review_passed": True,
                "human_review_required": True,
                "runtime_reviewed": False,
                "source_script_free": True,
            }
        )

    common_header = {
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "entry_count": len(coordinates),
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }
    evidence = {
        "schema": "nobu16.kr.strdata-switch-direct-evidence.v1",
        **common_header,
        "classification_policy": {
            "same_coordinate_required": True,
            "pc_jp_and_pc_sc_visible_required": True,
            "pc_sc_format_invariants_required": True,
            "source_script_free_required": True,
            "meaningful_hangul_required": True,
            "manual_and_unusable_excluded": True,
        },
        "input_pins": {
            "switch_v13_zip": ZIP_PIN,
            "switch_member": {"member": SWITCH_MEMBER, **SWITCH_PIN},
            "pc_jp": {"path": PC_JP_RELATIVE.as_posix(), **PC_JP_PIN},
            "pc_sc": {"path": PC_SC_RELATIVE.as_posix(), **PC_SC_PIN},
        },
        "deduplication": {
            "safe_direct_before_dedupe": EXPECTED["direct"],
            "existing_overlays": existing_metadata,
            "existing_coordinate_count": len(existing_values),
            "net_new_coordinate_count": len(coordinates),
            "net_new_coordinates_sha256": EXPECTED["net_new_coordinates_sha256"],
            "existing_values_take_precedence": True,
        },
        "entries": evidence_entries,
    }
    review = {
        "schema": "nobu16.kr.strdata-switch-direct-review.v1",
        **common_header,
        "review_policy": {
            "automatic_binary_and_format_review_complete": True,
            "human_language_review_pending": True,
            "runtime_screen_review_pending": True,
            "whole_switch_file_copy_forbidden": True,
        },
        "entries": review_entries,
    }
    return {
        "overlay": overlay,
        "evidence": evidence,
        "review": review,
        "net_new": net_new,
        "existing_values": existing_values,
        "existing_metadata": existing_metadata,
    }


def validate_source_free(value: Any, label: str) -> dict[str, int]:
    blob = encode_json(value)
    text = blob.decode("utf-8")
    counts = {
        "han_or_kana_count": len(HAN_OR_KANA_RE.findall(text)),
        "embedded_nul_count": text.count("\x00"),
    }
    if counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}:
        raise DirectTransferError(f"{label} is not source-free: {counts}")
    return counts


def validate_overlay(overlay: dict[str, Any], classified: dict[str, Any]) -> dict[str, Any]:
    entries = overlay["entries"]
    coordinates = [(entry["block_id"], entry["slot_id"]) for entry in entries]
    duplicate_count = len(coordinates) - len(set(coordinates))
    membership_failures = [coordinate for coordinate in coordinates if coordinate not in classified["safe_values"]]
    source_hash_failures = [
        coordinate
        for coordinate, entry in zip(coordinates, entries, strict=True)
        if entry["source_sc_utf16le_sha256"] != text_hash(classified["pc_sc"][coordinate])
    ]
    value_failures = [
        coordinate
        for coordinate, entry in zip(coordinates, entries, strict=True)
        if entry["ko"] != classified["safe_values"][coordinate]
        or not direct_contract(classified["pc_sc"][coordinate], entry["ko"])[0]
    ]
    if duplicate_count or membership_failures or source_hash_failures or value_failures:
        raise DirectTransferError("overlay duplicate, membership, hash, or invariant validation failed")
    if coordinates != sorted(coordinates):
        raise DirectTransferError("overlay coordinates are not sorted")
    return {
        "duplicate_coordinate_count": duplicate_count,
        "target_membership_failure_count": len(membership_failures),
        "source_hash_failure_count": len(source_hash_failures),
        "replacement_contract_failure_count": len(value_failures),
        "coordinates_sorted": True,
        "source_free": validate_source_free(overlay, "overlay"),
    }


def build_candidate(inputs: dict[str, Any], models: dict[str, Any]) -> tuple[bytes, bytes, dict[str, Any]]:
    source_archive = inputs["pc_sc_archive"]
    original = coordinate_texts(source_archive)
    integrated = dict(models["existing_values"])
    integrated.update(models["net_new"])
    if len(integrated) != EXPECTED["direct"]:
        raise DirectTransferError("integrated coordinate count changed")
    replacements = {block.block_id: list(block.texts) for block in source_archive.blocks}
    for (block_id, slot_id), replacement in integrated.items():
        replacements[block_id][slot_id] = replacement
    target_raw = rebuild_raw_strdata(source_archive, replacements)
    target_packed = recompress_wrapper(target_raw, inputs["pc_sc_wrapper"])
    _wrapper, checked_raw = decompress_wrapper(target_packed)
    checked_archive = parse_raw_strdata(checked_raw)
    checked = coordinate_texts(checked_archive)
    changed = sorted(coordinate for coordinate in original if original[coordinate] != checked[coordinate])
    expected_changed = sorted(integrated)
    if checked_raw != target_raw:
        raise DirectTransferError("candidate wrapper round-trip changed raw bytes")
    if changed != expected_changed:
        raise DirectTransferError("candidate changed a coordinate outside the integrated set")
    if any(checked[coordinate] != replacement for coordinate, replacement in integrated.items()):
        raise DirectTransferError("candidate did not preserve an integrated replacement")
    if any(checked[coordinate] != original[coordinate] for coordinate in original if coordinate not in integrated):
        raise DirectTransferError("candidate changed an untargeted coordinate")
    if canonical_hash([list(value) for value in changed]) != EXPECTED["integrated_coordinates_sha256"]:
        raise DirectTransferError("integrated candidate coordinate hash changed")
    actual = {
        "packed_size": len(target_packed),
        "packed_sha256": sha256(target_packed),
        "raw_size": len(target_raw),
        "raw_sha256": sha256(target_raw),
    }
    expected = {
        "packed_size": EXPECTED["candidate_packed_size"],
        "packed_sha256": EXPECTED["candidate_packed_sha256"],
        "raw_size": EXPECTED["candidate_raw_size"],
        "raw_sha256": EXPECTED["candidate_raw_sha256"],
    }
    if actual != expected:
        raise DirectTransferError(f"candidate pin changed: {actual}")
    return target_packed, target_raw, {
        **actual,
        "changed_coordinate_count": len(changed),
        "unchanged_coordinate_count": EXPECTED["total_coordinates"] - len(changed),
        "changed_coordinates_sha256": canonical_hash([list(value) for value in changed]),
        "all_other_coordinates_preserved": True,
        "existing_overlay_values_preserved": True,
        "block_slot_counts_preserved": True,
        "wrapper_roundtrip_valid": True,
        "whole_switch_file_copied": False,
    }


def build(game_root: Path, switch_zip: Path, out_root: Path, candidate_out: Path) -> dict[str, Any]:
    inputs = load_inputs(game_root, switch_zip)
    classified = classify_direct(inputs)
    models = build_artifact_models(inputs, classified)
    overlay_validation = validate_overlay(models["overlay"], classified)
    evidence_source_free = validate_source_free(models["evidence"], "evidence")
    review_source_free = validate_source_free(models["review"], "review")

    candidate_a, raw_a, candidate_stats_a = build_candidate(inputs, models)
    candidate_b, raw_b, candidate_stats_b = build_candidate(inputs, models)
    if candidate_a != candidate_b or raw_a != raw_b or candidate_stats_a != candidate_stats_b:
        raise DirectTransferError("A/B candidate builds are not byte-deterministic")

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    overlay_artifact = write_json(overlay_path, models["overlay"])
    evidence_artifact = write_json(evidence_path, models["evidence"])
    review_artifact = write_json(review_path, models["review"])
    overlay_artifact["path"] = f"public/{OVERLAY_NAME}"
    evidence_artifact["path"] = f"evidence/{EVIDENCE_NAME}"
    review_artifact["path"] = f"review/{REVIEW_NAME}"
    candidate_out.parent.mkdir(parents=True, exist_ok=True)
    candidate_out.write_bytes(candidate_a)

    validation = {
        "schema": "nobu16.kr.strdata-switch-direct-validation.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "passed": True,
        "scope": {
            "total_pc_coordinates": EXPECTED["total_coordinates"],
            "safe_direct_before_dedupe": EXPECTED["direct"],
            "existing_overlay_coordinates_preserved": len(models["existing_values"]),
            "net_new_overlay_coordinates": len(models["net_new"]),
            "integrated_changed_coordinates": candidate_stats_a["changed_coordinate_count"],
            "net_new_per_block": EXPECTED["net_new_per_block"],
        },
        "classification": {
            "counts": classified["classification_counts"],
            "per_block": classified["per_block"],
            "direct_coordinates_sha256": EXPECTED["direct_coordinates_sha256"],
            "semantic_aligned_auto_import_count": EXPECTED["semantic_aligned"],
            "manual_and_unusable_auto_import_count": 0,
        },
        "deduplication": {
            "existing_overlays": models["existing_metadata"],
            "duplicate_coordinate_count": overlay_validation["duplicate_coordinate_count"],
            "net_new_coordinates_sha256": EXPECTED["net_new_coordinates_sha256"],
            "existing_values_take_precedence": True,
        },
        "overlay_validation": overlay_validation,
        "source_free_scans": {
            "evidence": evidence_source_free,
            "review": review_source_free,
        },
        "inputs": {
            "switch_v13_zip": ZIP_PIN,
            "switch_member": SWITCH_PIN,
            "pc_jp": PC_JP_PIN,
            "pc_sc_pristine_original": PC_SC_PIN,
            "block_slot_counts": BLOCK_SLOT_COUNTS,
        },
        "candidate": candidate_stats_a,
        "deterministic_builds_identical": True,
        "artifacts": {
            "overlay": overlay_artifact,
            "evidence": evidence_artifact,
            "review": review_artifact,
        },
        "safety": {
            "live_game_file_written": False,
            "progress_file_modified": False,
            "readme_root_modified": False,
            "whole_switch_file_copied": False,
            "memory_patch_used": False,
            "dll_injection_used": False,
            "hooking_used": False,
            "exe_or_registry_modified": False,
        },
    }
    validation_artifact = write_json(out_root / VALIDATION_NAME, validation)
    validation["validation_artifact"] = validation_artifact
    return validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    parser.add_argument(
        "--candidate-out",
        type=Path,
        default=(
            REPO_ROOT
            / "tmp"
            / "switch_strdata_v13_direct_transfer"
            / "candidate"
            / RESOURCE
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build(
        args.game_root.resolve(),
        args.switch_zip.resolve(),
        args.out_root.resolve(),
        args.candidate_out.resolve(),
    )
    print(f"overlay_entries={result['scope']['net_new_overlay_coordinates']}")
    print(f"integrated_changed={result['scope']['integrated_changed_coordinates']}")
    print(f"candidate_sha256={result['candidate']['packed_sha256']}")
    print(f"candidate={args.candidate_out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
