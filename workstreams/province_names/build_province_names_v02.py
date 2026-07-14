#!/usr/bin/env python3
"""Build the reviewed, source-free province-name overlay v0.2.

The official SC/EN/JP ``msgdata.bin`` files are accepted only as SHA-pinned
local verification inputs.  No source string is copied into either public
artifact.  The v0.1 overlay remains the merge base, so the reviewed v0.2 file
can be reproduced deterministically without embedding commercial text.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
PATCH_ROOT = SCRIPT_DIR.parents[1]
TOOLS_DIR = PATCH_ROOT / "tools"
FIRST_ID = 13975
LAST_ID = 14046
ENTRY_COUNT = LAST_ID - FIRST_ID + 1
EXPECTED_STRING_COUNT = 29210
OVERLAY_V01_NAME = "province_names_ko_13975_14046.v0.1.json"
OVERLAY_V02_NAME = "province_names_ko_13975_14046.v0.2.json"
VALIDATION_NAME = "validation.v0.2.json"
KO_RE = re.compile(r"^[가-힣 ]+$")


RESOURCE_PINS: dict[str, dict[str, Any]] = {
    "SC": {
        "logical_path": "MSG_PK/SC/msgdata.bin",
        "wrapper_size": 267385,
        "wrapper_sha256": "0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E",
        "raw_size": 499760,
        "raw_sha256": "1290BCDF6B00C6E4516061888C618BC66A246375E271C9D1330A9D168037FBCF",
        "province_block_sha256": "9F83E0D9641420A4EE6193FDDDFA7469C378984F7E634A4F7039A424C0A1F399",
    },
    "EN": {
        "logical_path": "MSG_PK/EN/msgdata.bin",
        "wrapper_size": 267550,
        "wrapper_sha256": "15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1",
        "raw_size": 744236,
        "raw_sha256": "DA913D870DA3C13F108E8E6727C9A8881B9E13A83F8EB7F02DD3C55D1D444B32",
        "province_block_sha256": "6C4D46DDC4209318E0E5CAAD2B24BD788385B52B8CA6EDD53A300C0D6859698E",
    },
    "JP": {
        "logical_path": "MSG_PK/JP/msgdata.bin",
        "wrapper_size": 273734,
        "wrapper_sha256": "9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38",
        "raw_size": 431044,
        "raw_sha256": "119F10F28DAEEFFA7B231764BB5747A8837DEB487E4595504ADE2A77023148A0",
        "province_block_sha256": "39F8682D2FE875EFEEC8789F0EBE407AAF59683555686A4B86B6CF3C4893EB1E",
    },
}

# Full manual review found no incorrect v0.1 readings.  This explicit merge
# map is intentionally empty; later corrections must be added here by ID.
REVIEWED_OVERRIDES: dict[int, str] = {}


class ProvinceNameError(ValueError):
    """Raised when a pinned input or reviewed overlay contract is violated."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ProvinceNameError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LZ4 = load_module("nobu16_province_lz4", TOOLS_DIR / "nobu16_lz4.py")
MSGTABLE = load_module("nobu16_province_msgtable", TOOLS_DIR / "nobu16_msg_table.py")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def block_hash(texts: Sequence[str]) -> str:
    payload = bytearray()
    for entry_id in range(FIRST_ID, LAST_ID + 1):
        encoded = texts[entry_id].encode("utf-8")
        payload.extend(struct.pack("<II", entry_id, len(encoded)))
        payload.extend(encoded)
    return sha256_bytes(bytes(payload))


def load_stock(language: str, path: Path) -> dict[str, Any]:
    pin = RESOURCE_PINS[language]
    wrapper = path.read_bytes()
    if len(wrapper) != pin["wrapper_size"] or sha256_bytes(wrapper) != pin["wrapper_sha256"]:
        raise ProvinceNameError(
            f"{language} msgdata wrapper does not match the pinned game revision"
        )
    _header, raw = LZ4.decompress_wrapper(wrapper)
    if len(raw) != pin["raw_size"] or sha256_bytes(raw) != pin["raw_sha256"]:
        raise ProvinceNameError(f"{language} decompressed msgdata does not match its pin")
    table = MSGTABLE.parse_message_table(raw)
    if table.string_count != EXPECTED_STRING_COUNT:
        raise ProvinceNameError(
            f"{language} msgdata string count is {table.string_count}, expected {EXPECTED_STRING_COUNT}"
        )
    if MSGTABLE.rebuild_message_table(table, table.texts) != raw:
        raise ProvinceNameError(f"{language} msgdata parse/rebuild is not byte-exact")
    province_values = table.texts[FIRST_ID : LAST_ID + 1]
    if len(province_values) != ENTRY_COUNT or any(not value for value in province_values):
        raise ProvinceNameError(f"{language} province block shape changed")
    if len(set(province_values)) != ENTRY_COUNT:
        raise ProvinceNameError(f"{language} province block is no longer unique by source label")
    actual_block_hash = block_hash(table.texts)
    if actual_block_hash != pin["province_block_sha256"]:
        raise ProvinceNameError(f"{language} province block hash changed")
    return {
        "language": language,
        "logical_path": pin["logical_path"],
        "wrapper_size": len(wrapper),
        "wrapper_sha256": sha256_bytes(wrapper),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "string_count": table.string_count,
        "province_block": {
            "first_id": FIRST_ID,
            "last_id": LAST_ID,
            "entry_count": ENTRY_COUNT,
            "nonempty_count": ENTRY_COUNT,
            "unique_source_label_count": ENTRY_COUNT,
            "sha256": actual_block_hash,
        },
        "unchanged_parse_rebuild_byte_exact": True,
    }


def load_v01(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "nobu16.kr.province-names.v0.1":
        raise ProvinceNameError("unexpected v0.1 schema")
    scope = payload.get("scope")
    if scope != {"first_id": FIRST_ID, "last_id": LAST_ID, "entry_count": ENTRY_COUNT}:
        raise ProvinceNameError("v0.1 scope is not the exact province block")
    entries = payload.get("entries")
    if not isinstance(entries, list) or len(entries) != ENTRY_COUNT:
        raise ProvinceNameError("v0.1 must contain exactly 72 entries")
    expected_ids = list(range(FIRST_ID, LAST_ID + 1))
    actual_ids: list[int] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"id", "ko"}:
            raise ProvinceNameError("every v0.1 entry must contain only id and ko")
        if not isinstance(entry["id"], int) or not isinstance(entry["ko"], str):
            raise ProvinceNameError("v0.1 id/ko types are invalid")
        if not KO_RE.fullmatch(entry["ko"]):
            raise ProvinceNameError(f"v0.1 id {entry['id']} is not a Korean label")
        actual_ids.append(entry["id"])
    if actual_ids != expected_ids:
        raise ProvinceNameError("v0.1 ids are not the exact contiguous province range")
    return payload


def build_reviewed_overlay(v01: Mapping[str, Any]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    changed = 0
    for entry in v01["entries"]:
        entry_id = int(entry["id"])
        previous = str(entry["ko"])
        reviewed = REVIEWED_OVERRIDES.get(entry_id, previous)
        if reviewed != previous:
            changed += 1
        entries.append({"id": entry_id, "ko": reviewed, "status": "reviewed"})
    if set(REVIEWED_OVERRIDES) - set(range(FIRST_ID, LAST_ID + 1)):
        raise ProvinceNameError("review override contains an out-of-range id")
    return {
        "schema": "nobu16.kr.province-names.v0.2",
        "base_language": "SC",
        "resource": "MSG_PK/SC/msgdata.bin",
        "scope": {
            "first_id": FIRST_ID,
            "last_id": LAST_ID,
            "entry_count": ENTRY_COUNT,
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "translation_policy": {
            "geographic_tsu": "쓰",
            "japanese_long_vowels": "not_duplicated",
            "preferred_usage": "korean_historical_common_usage",
            "status": "reviewed",
        },
        "review": {
            "source_overlay": OVERLAY_V01_NAME,
            "compared_languages": ["SC", "EN", "JP"],
            "reviewed_entry_count": ENTRY_COUNT,
            "changed_from_v0.1": changed,
        },
        "entries": entries,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    v01_path = args.v01.resolve()
    output_root = args.output_root.resolve()
    overlay_path = output_root / "public" / OVERLAY_V02_NAME
    validation_path = output_root / VALIDATION_NAME
    if overlay_path == v01_path or validation_path == v01_path:
        raise ProvinceNameError("refusing to overwrite the v0.1 merge base")

    v01 = load_v01(v01_path)
    resources = [
        load_stock("SC", args.sc.resolve()),
        load_stock("EN", args.en.resolve()),
        load_stock("JP", args.jp.resolve()),
    ]
    overlay = build_reviewed_overlay(v01)
    overlay_blob = json_bytes(overlay)
    atomic_write(overlay_path, overlay_blob)

    validation = {
        "schema": "nobu16.kr.province-names.validation.v0.2",
        "source_text_free": True,
        "scope": {
            "first_id": FIRST_ID,
            "last_id": LAST_ID,
            "entry_count": ENTRY_COUNT,
        },
        "inputs": {
            "v0.1_overlay": {
                "path": f"public/{OVERLAY_V01_NAME}",
                "sha256": sha256_file(v01_path),
                "entry_count": ENTRY_COUNT,
            },
            "stock_resources": resources,
        },
        "result": {
            "same_ids_compared_in_sc_en_jp": True,
            "all_source_labels_nonempty": True,
            "all_source_labels_unique_within_each_language": True,
            "reviewed_entry_count": ENTRY_COUNT,
            "changed_from_v0.1": overlay["review"]["changed_from_v0.1"],
            "all_entry_statuses_reviewed": True,
            "geographic_tsu_policy": "쓰",
            "japanese_long_vowels": "not_duplicated",
        },
        "artifact": {
            "path": f"public/{OVERLAY_V02_NAME}",
            "sha256": sha256_bytes(overlay_blob),
        },
    }
    atomic_write(validation_path, json_bytes(validation))
    return validation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--v01",
        type=Path,
        default=SCRIPT_DIR / "public" / OVERLAY_V01_NAME,
        help="preserved source-free v0.1 merge base",
    )
    parser.add_argument("--sc", type=Path, required=True, help="pinned stock SC msgdata wrapper")
    parser.add_argument("--en", type=Path, required=True, help="pinned stock EN msgdata wrapper")
    parser.add_argument("--jp", type=Path, required=True, help="pinned stock JP msgdata wrapper")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=SCRIPT_DIR,
        help="writes public v0.2 and validation.v0.2.json beneath this directory",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        validation = build(args)
    except (OSError, json.JSONDecodeError, ProvinceNameError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"reviewed_entries={validation['result']['reviewed_entry_count']}")
    print(f"changed_from_v0.1={validation['result']['changed_from_v0.1']}")
    print(f"overlay_sha256={validation['artifact']['sha256']}")
    print("source_text_free=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
