#!/usr/bin/env python3
"""Build the PK-runtime shared base ``strdata`` UI overlay and PC candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "workstreams" / "switch_msgbre_v11"))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from strdata_container import (  # noqa: E402
    parse_strdata as parse_raw_strdata,
    rebuild_strdata as rebuild_raw_strdata,
)


RESOURCE = "MSG/SC/strdata.bin"
SWITCH_SOURCE = "Switch v1.3 MSG/JP/strdata.bin"
OVERLAY_NAME = "strdata_ko_pk_shared_ui_b01_1.v1.json"
VALIDATION_NAME = "translation_validation.v1.json"
OVERLAY_ID = "strdata-pk-shared-ui-b01-1-v1"
SCHEMA = "nobu16.kr.strdata-block-overlay.v1"
COORDINATE = (1, 22)
REPLACEMENT = "돌아가기"
SOURCE_TEXT_HASH = "21DB128C982FCC6244FB34C5354D8B0D6002CB9C328EBC13DA08D1796D0D326E"
STOCK_SC = {
    "packed_size": 516628,
    "packed_sha256": "93F88D71210B96783749CEB948E0713D7E6552F764F644092B71A5FD0C994B88",
    "raw_size": 760388,
    "raw_sha256": "17EF622F36BA94009F67519DC79ED543C223B467311E51711A009F9DD0816214",
    "block_slot_counts": [25069, 4100, 3000, 122, 20],
}
HAN_OR_KANA_RE = re.compile(r"[\u2e80-\u2fff\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


class SharedUiBuildError(RuntimeError):
    """A pinned source or reconstruction invariant changed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(value))


def source_fingerprint(packed: bytes) -> tuple[Any, bytes, Any]:
    wrapper, raw = decompress_wrapper(packed)
    archive = parse_raw_strdata(raw)
    actual = {
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "block_slot_counts": [block.slot_count for block in archive.blocks],
    }
    if actual != STOCK_SC:
        raise SharedUiBuildError(f"installed stock fingerprint changed: {actual}")
    return wrapper, raw, archive


def load_pinned_stock(game_root: Path) -> bytes:
    """Load the exact stock blob from live state or a verified transaction backup."""
    live = game_root / Path(RESOURCE)
    packed = live.read_bytes()
    if len(packed) == STOCK_SC["packed_size"] and sha256(packed) == STOCK_SC["packed_sha256"]:
        return packed
    backup_root = game_root / "KR_PATCH_BACKUP" / "file_only_transaction"
    matches = []
    for path in sorted(backup_root.glob(f"*/originals/{RESOURCE}")):
        candidate = path.read_bytes()
        if len(candidate) == STOCK_SC["packed_size"] and sha256(candidate) == STOCK_SC["packed_sha256"]:
            matches.append(candidate)
    if matches:
        return matches[0]
    raise SharedUiBuildError("exact stock strdata is neither live nor present in transaction backups")


def make_overlay() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "overlay_id": OVERLAY_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": 1,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "provenance": {
            "kind": "coordinate_level_switch_translation_reuse",
            "source_release": "v1.3",
            "source_resource": "MSG/JP/strdata.bin",
            "same_block_slot_coordinate": True,
            "pc_sc_and_jp_semantic_alignment_verified": True,
        },
        "stock_sc": STOCK_SC,
        "entries": [
            {
                "block_id": COORDINATE[0],
                "slot_id": COORDINATE[1],
                "source_sc_utf16le_sha256": SOURCE_TEXT_HASH,
                "ko": REPLACEMENT,
            }
        ],
    }


def validate_overlay(overlay: dict[str, Any]) -> None:
    required = {
        "schema",
        "overlay_id",
        "resource",
        "base_language",
        "defaults",
        "entry_count",
        "distribution_policy",
        "provenance",
        "stock_sc",
        "entries",
    }
    if set(overlay) != required or overlay["schema"] != SCHEMA:
        raise SharedUiBuildError("overlay shape changed")
    if overlay["overlay_id"] != OVERLAY_ID or overlay["resource"] != RESOURCE:
        raise SharedUiBuildError("overlay identity changed")
    if overlay["stock_sc"] != STOCK_SC or overlay["entry_count"] != 1:
        raise SharedUiBuildError("overlay source pin or count changed")
    if overlay["distribution_policy"] != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise SharedUiBuildError("overlay distribution policy changed")
    entry = overlay["entries"][0]
    if (entry["block_id"], entry["slot_id"]) != COORDINATE:
        raise SharedUiBuildError("overlay coordinate changed")
    if entry["source_sc_utf16le_sha256"] != SOURCE_TEXT_HASH or entry["ko"] != REPLACEMENT:
        raise SharedUiBuildError("overlay hash or Korean value changed")
    if HAN_OR_KANA_RE.search(canonical_json(overlay).decode("utf-8")):
        raise SharedUiBuildError("public overlay contains Han or kana source text")


def build_candidate(packed: bytes, overlay: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    validate_overlay(overlay)
    wrapper, _raw, archive = source_fingerprint(packed)
    block_id, slot_id = COORDINATE
    source = archive.blocks[block_id].texts[slot_id]
    if sha256(source.encode("utf-16le")) != SOURCE_TEXT_HASH:
        raise SharedUiBuildError("source text hash mismatch at shared UI coordinate")

    replacements = {block.block_id: list(block.texts) for block in archive.blocks}
    replacements[block_id][slot_id] = REPLACEMENT
    target_raw = rebuild_raw_strdata(archive, replacements)
    target_packed = recompress_wrapper(target_raw, wrapper)
    _target_wrapper, verified_raw = decompress_wrapper(target_packed)
    verified = parse_raw_strdata(verified_raw)

    changed: list[tuple[int, int]] = []
    for original_block, target_block in zip(archive.blocks, verified.blocks, strict=True):
        if original_block.slot_count != target_block.slot_count:
            raise SharedUiBuildError("block slot count changed")
        for current_slot, (before, after) in enumerate(
            zip(original_block.texts, target_block.texts, strict=True)
        ):
            if before != after:
                changed.append((original_block.block_id, current_slot))
    if changed != [COORDINATE]:
        raise SharedUiBuildError(f"unexpected changed coordinates: {changed}")
    if verified.blocks[block_id].texts[slot_id] != REPLACEMENT:
        raise SharedUiBuildError("rebuilt Korean value did not survive reparse")

    return target_packed, {
        "target_packed_size": len(target_packed),
        "target_packed_sha256": sha256(target_packed),
        "target_raw_size": len(target_raw),
        "target_raw_sha256": sha256(target_raw),
        "changed_coordinate_count": len(changed),
        "unchanged_coordinate_count": sum(STOCK_SC["block_slot_counts"]) - len(changed),
        "block_slot_counts_preserved": True,
        "offline_reparse_verified": True,
    }


def build(game_root: Path, out_root: Path, candidate_out: Path) -> dict[str, Any]:
    packed = load_pinned_stock(game_root)
    overlay = make_overlay()
    first, first_stats = build_candidate(packed, overlay)
    second, second_stats = build_candidate(packed, overlay)
    if first != second or first_stats != second_stats:
        raise SharedUiBuildError("candidate build is not byte deterministic")

    overlay_path = out_root / "public" / OVERLAY_NAME
    write_json(overlay_path, overlay)
    candidate_out.parent.mkdir(parents=True, exist_ok=True)
    candidate_out.write_bytes(first)
    validation = {
        "schema": "nobu16.kr.strdata-pk-shared-ui-validation.v1",
        "overlay_id": OVERLAY_ID,
        "resource": RESOURCE,
        "runtime_scope": "PK execution shared base UI table",
        "switch_reuse": {
            "source": SWITCH_SOURCE,
            "same_coordinate": list(COORDINATE),
            "translation_reused": True,
            "whole_switch_file_copied": False,
        },
        "stock_sc": STOCK_SC,
        "overlay": {
            "path": f"public/{OVERLAY_NAME}",
            "size": overlay_path.stat().st_size,
            "sha256": sha256(overlay_path.read_bytes()),
            "source_free_han_or_kana_count": 0,
        },
        "candidate": first_stats,
        "deterministic_builds_identical": True,
        "installed_game_file_written": False,
    }
    write_json(out_root / VALIDATION_NAME, validation)
    return validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    parser.add_argument(
        "--candidate-out",
        type=Path,
        default=REPO_ROOT / "tmp" / "strdata_pk_shared_ui" / "candidate" / RESOURCE,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build(args.game_root.resolve(), args.out_root.resolve(), args.candidate_out.resolve())
    print(f"overlay_entries=1")
    print(f"target_sha256={result['candidate']['target_packed_sha256']}")
    print(f"candidate={args.candidate_out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
