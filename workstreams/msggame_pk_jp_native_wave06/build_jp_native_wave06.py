#!/usr/bin/env python3
"""Build the JP-native PK msggame foundation and five translation batches."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
TOOLS_ROOT = REPO_ROOT / "tools"
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
sys.path[:0] = [str(TOOLS_ROOT), str(MSGGAME_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import msggame_format as msggame  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402


RESOURCE = "MSG_PK/JP/msggame.bin"
CATALOG_SCHEMA = "nobu16.kr.msggame-jp-native-catalog.v1"
PARTITION_SCHEMA = "nobu16.kr.msggame-jp-native-partition.v1"
OVERLAY_SCHEMA = "nobu16.kr.msggame-jp-literal-overlay.v1"
PRIVATE_SCHEMA = "nobu16.kr.msggame-jp-private-context.v1"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/msggame.bin"

DEFAULT_PK_JP = GAME_ROOT / "MSG_PK" / "JP" / "msggame.bin"
DEFAULT_BASE_JP = GAME_ROOT / "MSG" / "JP" / "msggame.bin"
DEFAULT_PK_EN = GAME_ROOT / "MSG_PK" / "EN" / "msggame.bin"
DEFAULT_PK_TC = GAME_ROOT / "MSG_PK" / "TC" / "msggame.bin"
DEFAULT_SWITCH_ZIP = (
    REPO_ROOT
    / "tmp"
    / "third_party_switch_v13"
    / "NobunagaShinsei_KoreanPatch_v1.3.zip"
)
DEFAULT_PRIOR_RECIPE = (
    REPO_ROOT
    / "workstreams"
    / "msggame_pk_jp_transfer_v1"
    / "public"
    / "msggame_ko_pk_jp_native_transfer_v1_8310.v1.json"
)

PK_JP_PIN = {
    "packed_size": 721_304,
    "packed_sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "raw_size": 1_599_324,
    "raw_sha256": "F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8",
    "record_count": 21_751,
    "literal_count": 29_524,
}
BASE_JP_PIN = {
    "packed_size": 610_163,
    "packed_sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "raw_size": 1_337_548,
    "raw_sha256": "353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38",
    "record_count": 19_152,
    "literal_count": 24_262,
}
SWITCH_ZIP_PIN = {
    "size": 72_977_145,
    "sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
}
SWITCH_TEXT_PIN = {
    "packed_size": 487_964,
    "packed_sha256": "89CC6412B8548CA5CCADB6A2AB406D0EC4ED3ABCEBB8B703C4E324C0EAAB2F67",
    "raw_size": 1_498_434,
    "raw_sha256": "759C32FD7EFAABF70C6B82C45E21AB090D6B80CF88827247370AED9F163D6501",
    "record_count": 19_152,
    "literal_count": 24_262,
}
EXPECTED = {
    "semantic_target": 28_272,
    "prior": 9_386,
    "prior_semantic": 9_386,
    "switch_exact": 14_825,
    "foundation_union": 24_211,
    "foundation_semantic": 24_211,
    "remaining": 4_061,
}
EXPECTED_REMAINING_HASH = "8B039DF39C0A69F5A6119E52331D10B3F183C388A302FBAF32A3E55131889085"

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")


class BuildError(ValueError):
    pass


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_hash(value: Any) -> str:
    return sha256(
        json.dumps(
            value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise BuildError(f"JSON root must be an object: {path}")
    return value


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": path.name, "size": len(blob), "sha256": sha256(blob)}


def has_source_script(text: str) -> bool:
    return CJK_RE.search(text) is not None or KANA_RE.search(text) is not None


def literal_map(archive: Any) -> dict[tuple[int, int, int], Any]:
    return {
        (item.block_id, item.record_id, item.literal_id): item
        for item in msggame.iter_literals(archive)
    }


def record_map(archive: Any) -> dict[tuple[int, int], Any]:
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def load_packed(path: Path, pin: dict[str, Any], label: str) -> dict[str, Any]:
    packed = path.read_bytes()
    if len(packed) != pin["packed_size"] or sha256(packed) != pin["packed_sha256"]:
        raise BuildError(f"{label} packed pin changed")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise BuildError(f"{label} raw pin changed")
    parsed = msggame.parse_packed_msggame(packed)
    literals = literal_map(parsed.archive)
    if parsed.archive.record_count != pin["record_count"] or len(literals) != pin["literal_count"]:
        raise BuildError(f"{label} archive shape changed")
    return {
        "packed": packed,
        "raw": raw,
        "archive": parsed.archive,
        "literals": literals,
        "records": record_map(parsed.archive),
    }


def load_switch(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    if len(blob) != SWITCH_ZIP_PIN["size"] or sha256(blob) != SWITCH_ZIP_PIN["sha256"]:
        raise BuildError("Switch v1.3 ZIP pin changed")
    with zipfile.ZipFile(path) as archive:
        packed = archive.read(SWITCH_MEMBER)
    if len(packed) != SWITCH_TEXT_PIN["packed_size"] or sha256(packed) != SWITCH_TEXT_PIN["packed_sha256"]:
        raise BuildError("Switch msggame packed pin changed")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != SWITCH_TEXT_PIN["raw_size"] or sha256(raw) != SWITCH_TEXT_PIN["raw_sha256"]:
        raise BuildError("Switch msggame raw pin changed")
    padded = raw + b"\0" * ((-len(raw)) % 4)
    archive = msggame.parse_raw_msggame(padded)
    literals = literal_map(archive)
    if archive.record_count != SWITCH_TEXT_PIN["record_count"] or len(literals) != SWITCH_TEXT_PIN["literal_count"]:
        raise BuildError("Switch msggame archive shape changed")
    return {"packed": packed, "raw": raw, "archive": archive, "literals": literals}


def overlay(
    overlay_id: str,
    entries: Iterable[dict[str, Any]],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    ordered = sorted(
        entries,
        key=lambda item: (item["block_id"], item["record_id"], item["literal_id"]),
    )
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": overlay_id,
        "resource": RESOURCE,
        "base_language": "JP",
        "entry_count": len(ordered),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": {
            "packed_size": PK_JP_PIN["packed_size"],
            "packed_sha256": PK_JP_PIN["packed_sha256"],
            "raw_size": PK_JP_PIN["raw_size"],
            "raw_sha256": PK_JP_PIN["raw_sha256"],
            "record_count": PK_JP_PIN["record_count"],
            "literal_count": PK_JP_PIN["literal_count"],
        },
        "defaults": {"status": "translated"},
        "translation_provenance": provenance,
        "entries": ordered,
    }


def validate_entries(
    value: dict[str, Any], jp_literals: dict[tuple[int, int, int], Any]
) -> set[tuple[int, int, int]]:
    if value.get("resource") != RESOURCE or value.get("base_language") != "JP":
        raise BuildError("overlay does not target JP msggame")
    entries = value.get("entries")
    if not isinstance(entries, list) or value.get("entry_count") != len(entries):
        raise BuildError("overlay entries are invalid")
    coordinates: set[tuple[int, int, int]] = set()
    for entry in entries:
        coordinate = (entry["block_id"], entry["record_id"], entry["literal_id"])
        if coordinate in coordinates or coordinate not in jp_literals:
            raise BuildError(f"overlay coordinate is duplicate or absent: {coordinate}")
        source = jp_literals[coordinate].text
        if entry["source_jp_utf16le_sha256"] != text_hash(source):
            raise BuildError(f"JP source hash mismatch at {coordinate}")
        ko = entry["ko"]
        if not isinstance(ko, str) or has_source_script(ko):
            raise BuildError(f"source script leaked at {coordinate}")
        if common.invariant_mismatches(source, ko):
            raise BuildError(f"JP invariant mismatch at {coordinate}")
        coordinates.add(coordinate)
    return coordinates


def build_foundation(args: argparse.Namespace) -> dict[str, Any]:
    pk = load_packed(args.pk_jp.resolve(), PK_JP_PIN, "PK JP")
    base = load_packed(args.base_jp.resolve(), BASE_JP_PIN, "base JP")
    switch = load_switch(args.switch_zip.resolve())
    if set(base["literals"]) != set(switch["literals"]):
        raise BuildError("PC base JP and Switch v1.3 coordinate sets differ")

    prior_recipe = read_json(args.prior_recipe.resolve())
    semantic_targets = {
        coordinate
        for coordinate, literal in pk["literals"].items()
        if has_source_script(literal.text)
    }
    prior_by_hash: dict[str, set[str]] = {}
    for entry in prior_recipe.get("entries", []):
        prior_by_hash.setdefault(entry["source_jp_utf16le_sha256"], set()).add(
            entry["ko"]
        )
    prior_unique = {
        source_hash: next(iter(values))
        for source_hash, values in prior_by_hash.items()
        if len(values) == 1
    }
    prior_assignments: dict[tuple[int, int, int], str] = {}
    for entry in prior_recipe.get("entries", []):
        coordinate = (entry["block_id"], entry["record_id"], entry["literal_id"])
        if coordinate not in semantic_targets:
            continue
        source = pk["literals"][coordinate].text
        if (
            entry["source_jp_utf16le_sha256"] == text_hash(source)
            and not common.invariant_mismatches(source, entry["ko"])
        ):
            prior_assignments[coordinate] = entry["ko"]
    for coordinate in sorted(semantic_targets - set(prior_assignments)):
        source = pk["literals"][coordinate].text
        korean = prior_unique.get(text_hash(source))
        if korean is not None and not common.invariant_mismatches(source, korean):
            prior_assignments[coordinate] = korean
    prior_entries = [
        {
            "block_id": coordinate[0],
            "record_id": coordinate[1],
            "literal_id": coordinate[2],
            "source_jp_utf16le_sha256": text_hash(pk["literals"][coordinate].text),
            "ko": korean,
        }
        for coordinate, korean in sorted(prior_assignments.items())
    ]
    prior_overlay = overlay(
        "msggame_pk_jp_native_steam_prior_rebased_9386.v1",
        prior_entries,
        {
            "kind": "prior_korean_entries_rebased_by_stock_steam_jp_hash",
            "context_languages": ["JP"],
            "runtime_reviewed": False,
            "source_text_embedded": False,
        },
    )
    prior_coordinates = validate_entries(prior_overlay, pk["literals"])
    if len(prior_coordinates) != EXPECTED["prior"]:
        raise BuildError("prior JP entry count changed")

    hash_to_korean: dict[str, set[str]] = {}
    for coordinate, source_literal in base["literals"].items():
        source = source_literal.text
        korean = switch["literals"][coordinate].text
        if has_source_script(korean) or common.invariant_mismatches(source, korean):
            continue
        hash_to_korean.setdefault(text_hash(source), set()).add(korean)
    unique_korean = {
        source_hash: next(iter(values))
        for source_hash, values in hash_to_korean.items()
        if len(values) == 1
    }

    switch_entries: list[dict[str, Any]] = []
    for coordinate in sorted(semantic_targets - prior_coordinates):
        source = pk["literals"][coordinate].text
        korean = unique_korean.get(text_hash(source))
        if korean is None or common.invariant_mismatches(source, korean):
            continue
        switch_entries.append(
            {
                "block_id": coordinate[0],
                "record_id": coordinate[1],
                "literal_id": coordinate[2],
                "source_jp_utf16le_sha256": text_hash(source),
                "ko": korean,
            }
        )
    switch_overlay = overlay(
        "msggame_pk_jp_native_steam_switch_v13_exact_14825.v1",
        switch_entries,
        {
            "kind": "switch_v13_exact_pc_jp_source_hash_transfer",
            "context_languages": ["JP"],
            "runtime_reviewed": False,
            "source_text_embedded": False,
            "switch_context": {
                "author": "snake7594",
                "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
                "release_tag": "v1.3",
                "asset_sha256": SWITCH_ZIP_PIN["sha256"],
            },
        },
    )
    switch_coordinates = validate_entries(switch_overlay, pk["literals"])
    if len(switch_coordinates) != EXPECTED["switch_exact"]:
        raise BuildError("Switch exact JP transfer count changed")
    if prior_coordinates & switch_coordinates:
        raise BuildError("JP foundation overlays overlap")

    foundation = prior_coordinates | switch_coordinates
    remaining = semantic_targets - foundation
    if (
        len(semantic_targets) != EXPECTED["semantic_target"]
        or len(foundation) != EXPECTED["foundation_union"]
        or len(remaining) != EXPECTED["remaining"]
        or canonical_hash([list(value) for value in sorted(remaining)])
        != EXPECTED_REMAINING_HASH
    ):
        raise BuildError("JP-native target/remaining contract changed")

    block17 = sorted(value for value in remaining if value[0] == 17)
    block6 = sorted(value for value in remaining if value[0] == 6)
    other = sorted(value for value in remaining if value[0] not in {6, 17})
    batches = [
        ("j01", "block17_a", block17[:970]),
        ("j02", "block17_b", block17[970:]),
        ("j03", "block6", block6),
        ("j04", "other_a", other[:680]),
        ("j05", "other_b", other[680:]),
    ]
    union: set[tuple[int, int, int]] = set()
    batch_payloads: list[dict[str, Any]] = []
    for order, (batch_id, label, coordinates) in enumerate(batches, 1):
        coordinate_set = set(coordinates)
        if union & coordinate_set:
            raise BuildError("JP-native batch overlap")
        union |= coordinate_set
        batch_payloads.append(
            {
                "batch_id": batch_id,
                "label": label,
                "order": order,
                "coordinate_count": len(coordinates),
                "coordinates_sha256": canonical_hash(
                    [list(value) for value in coordinates]
                ),
                "coordinates": [list(value) for value in coordinates],
            }
        )
    if union != remaining:
        raise BuildError("JP-native batch union differs from remaining target")

    catalog = {
        "schema": CATALOG_SCHEMA,
        "resource": RESOURCE,
        "base_language": "JP",
        "source_free": True,
        "stock_jp": prior_overlay["stock_jp"],
        "semantic_target": {
            "coordinate_count": len(semantic_targets),
            "coordinates_sha256": canonical_hash(
                [list(value) for value in sorted(semantic_targets)]
            ),
        },
        "foundation": {
            "prior_entry_count": len(prior_coordinates),
            "prior_semantic_count": len(prior_coordinates & semantic_targets),
            "switch_exact_entry_count": len(switch_coordinates),
            "coordinate_union_count": len(foundation),
            "semantic_coverage_count": len(foundation & semantic_targets),
            "semantic_coverage_percent": round(
                len(foundation & semantic_targets) * 100 / len(semantic_targets), 4
            ),
            "coordinates_sha256": canonical_hash(
                [list(value) for value in sorted(foundation)]
            ),
        },
        "remaining": {
            "coordinate_count": len(remaining),
            "coordinates_sha256": EXPECTED_REMAINING_HASH,
            "by_block": {
                str(key): value
                for key, value in sorted(Counter(item[0] for item in remaining).items())
            },
        },
        "proofs": {
            "runtime_container_language": "JP",
            "jp_source_hash_guarded": True,
            "jp_record_structure_preserved": True,
            "sc_container_used": False,
            "sc_coordinates_used": False,
            "sc_source_text_used": False,
            "memory_or_executable_patch_used": False,
        },
    }
    partition = {
        "schema": PARTITION_SCHEMA,
        "resource": RESOURCE,
        "base_language": "JP",
        "source_free": True,
        "remaining_coordinate_count": len(remaining),
        "remaining_coordinates_sha256": EXPECTED_REMAINING_HASH,
        "batch_count": len(batch_payloads),
        "batches": batch_payloads,
        "proofs": {
            "pairwise_disjoint": True,
            "union_equals_remaining": True,
            "jp_coordinates_only": True,
        },
    }

    out_root = args.out_root.resolve()
    results = {
        "catalog": write_json(out_root / "catalog.v1.json", catalog),
        "partition": write_json(out_root / "partition.v1.json", partition),
        "prior_overlay": write_json(
            out_root / "public" / "msggame_ko_pk_jp_native_steam_prior_rebased_9386.v1.json",
            prior_overlay,
        ),
        "switch_overlay": write_json(
            out_root
            / "public"
            / "msggame_ko_pk_jp_native_steam_switch_v13_exact_14825.v1.json",
            switch_overlay,
        ),
    }
    for path in (
        out_root / "catalog.v1.json",
        out_root / "partition.v1.json",
        out_root / "public" / "msggame_ko_pk_jp_native_steam_prior_rebased_9386.v1.json",
        out_root
        / "public"
        / "msggame_ko_pk_jp_native_steam_switch_v13_exact_14825.v1.json",
    ):
        if has_source_script(path.read_text(encoding="utf-8")):
            raise BuildError(f"source script leaked into public artifact: {path}")
    return {
        "semantic_target": len(semantic_targets),
        "foundation_semantic": len(foundation & semantic_targets),
        "remaining": len(remaining),
        "batches": {
            item["batch_id"]: item["coordinate_count"] for item in batch_payloads
        },
        "artifacts": results,
    }


def record_literals(source: dict[str, Any], coordinate: tuple[int, int, int]) -> list[str]:
    record = source["records"][coordinate[:2]]
    return [item.text for item in msggame.parse_record_literals(record)]


def export_private(args: argparse.Namespace) -> dict[str, Any]:
    build_foundation(args)
    pk = load_packed(args.pk_jp.resolve(), PK_JP_PIN, "PK JP")
    en = msggame.parse_packed_msggame(args.pk_en.resolve().read_bytes())
    tc = msggame.parse_packed_msggame(args.pk_tc.resolve().read_bytes())
    en_source = {"archive": en.archive, "records": record_map(en.archive)}
    tc_source = {"archive": tc.archive, "records": record_map(tc.archive)}
    partition = read_json(args.out_root.resolve() / "partition.v1.json")
    output_root = args.private_output_root.resolve()
    results: dict[str, Any] = {}
    for batch in partition["batches"]:
        entries: list[dict[str, Any]] = []
        for raw_coordinate in batch["coordinates"]:
            coordinate = tuple(raw_coordinate)
            jp_record = record_literals(pk, coordinate)
            block_id, record_id, literal_id = coordinate
            previous = (
                record_literals(pk, (block_id, record_id - 1, 0))
                if record_id > 0
                else None
            )
            block = pk["archive"].blocks[block_id]
            following = (
                record_literals(pk, (block_id, record_id + 1, 0))
                if record_id + 1 < len(block.records)
                else None
            )
            entries.append(
                {
                    "coordinate": list(coordinate),
                    "jp": pk["literals"][coordinate].text,
                    "jp_record": jp_record,
                    "jp_previous_record": previous,
                    "jp_next_record": following,
                    "en_record": record_literals(en_source, coordinate),
                    "tc_record": record_literals(tc_source, coordinate),
                    "jp_invariants": common.message_invariants(
                        pk["literals"][coordinate].text
                    ),
                }
            )
        payload = {
            "schema": PRIVATE_SCHEMA,
            "must_not_be_committed": True,
            "private_commercial_source_context": True,
            "resource": RESOURCE,
            "base_language": "JP",
            "batch_id": batch["batch_id"],
            "coordinate_count": batch["coordinate_count"],
            "coordinates_sha256": batch["coordinates_sha256"],
            "entries": entries,
        }
        path = output_root / f"{batch['batch_id']}.private.json"
        results[batch["batch_id"]] = write_json(path, payload)
    return results


def verify(args: argparse.Namespace) -> dict[str, Any]:
    expected_root = args.out_root.resolve()
    names = (
        "catalog.v1.json",
        "partition.v1.json",
        "public/msggame_ko_pk_jp_native_steam_prior_rebased_9386.v1.json",
        "public/msggame_ko_pk_jp_native_steam_switch_v13_exact_14825.v1.json",
    )
    expected = {name: sha256((expected_root / name).read_bytes()) for name in names}
    with tempfile.TemporaryDirectory(prefix="nobu16-jp-native-wave06-") as temp:
        delegated = argparse.Namespace(**vars(args))
        delegated.out_root = Path(temp)
        build_foundation(delegated)
        actual = {name: sha256((Path(temp) / name).read_bytes()) for name in names}
    if actual != expected:
        raise BuildError("JP-native foundation is not deterministic")
    return {"ok": True, "artifacts": expected}


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    sub = value.add_subparsers(dest="command", required=True)
    for name in ("build", "verify", "export-private"):
        item = sub.add_parser(name)
        item.add_argument("--pk-jp", type=Path, default=DEFAULT_PK_JP)
        item.add_argument("--base-jp", type=Path, default=DEFAULT_BASE_JP)
        item.add_argument("--pk-en", type=Path, default=DEFAULT_PK_EN)
        item.add_argument("--pk-tc", type=Path, default=DEFAULT_PK_TC)
        item.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
        item.add_argument("--prior-recipe", type=Path, default=DEFAULT_PRIOR_RECIPE)
        item.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
        if name == "export-private":
            item.add_argument(
                "--private-output-root",
                type=Path,
                default=REPO_ROOT / "tmp" / "msggame_pk_jp_native_wave06_private",
            )
    return value


def main() -> int:
    args = parser().parse_args()
    if args.command == "build":
        result = build_foundation(args)
    elif args.command == "verify":
        result = verify(args)
    else:
        result = export_private(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
