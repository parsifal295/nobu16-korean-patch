#!/usr/bin/env python3
"""Build and strictly verify the v0.95 fixes for GitHub issues #122 and #123."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [
    str(REPO / "tools"),
    str(REPO / "workstreams" / "strdata"),
    str(REPO / "workstreams" / "msggame"),
]

from msggame_format import MsgGameFormatError, iter_literals, parse_packed_msggame  # noqa: E402
from nobu16_lz4 import (  # noqa: E402
    LZ4Error,
    decompress_wrapper,
    recompress_wrapper,
    recompress_wrapper_greedy,
)
from nobu16_msg_table import (  # noqa: E402
    MessageTable,
    MessageTableError,
    parse_message_table,
    rebuild_message_table,
)
from strdata_format import StrdataFormatError, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


SCHEMA = "nobu16.kr.issue122-123-name-reading-validation.v1"
OVERLAY_SCHEMA = "nobu16.kr.issue122-123-name-reading-overlay.v1"
OVERLAY_PATH = HERE / "issue_122_123_name_reading_fixes.overlay.v1.json"
VALIDATION_NAME = "validation.issue122_123_name_reading_fixes.v1.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

MSG_DATA = Path("MSG_PK/JP/msgdata.bin")
MSG_EV = Path("MSG_PK/JP/msgev.bin")
STR_DATA = Path("MSG/JP/strdata.bin")
PK_MSGGAME = Path("MSG_PK/JP/msggame.bin")
RESOURCE_ORDER = (MSG_DATA, MSG_EV)
READ_ONLY_DEPENDENCY_ORDER = (STR_DATA, PK_MSGGAME)

INPUT_SPECS = {
    MSG_DATA: {
        "packed_size": 476_948,
        "packed_sha256": "6B5F6852DB0CB0D6F3791C43E56B54A15CC6439B0D4CC8A8A32985E1D1A0207E",
        "raw_size": 475_060,
        "raw_sha256": "E35523254DA5FE35E743140C450960434509BDA33F84B95EB2EEE94C8DE694F9",
        "string_count": 29_218,
        "compression": "literal_only",
    },
    MSG_EV: {
        "packed_size": 582_303,
        "packed_sha256": "DAA32DFA5DE1C4B2FAEC8C9F2E5984085D37F4459C63AA151E829C99B4199808",
        "raw_size": 1_044_204,
        "raw_sha256": "25AA4DFADBF3B892AC3369F0FD2420CFDB0F58FA178A81D14726EA7B14F2A04E",
        "string_count": 17_916,
        "compression": "greedy",
    },
    STR_DATA: {
        "packed_size": 940_981,
        "packed_sha256": "44A3621C5E4E6833260C2A8C0207D5FD74EB1F4A455E7AF81E7B93C571FB7029",
        "raw_size": 937_280,
        "raw_sha256": "8EB6410396392C5256616909B4787AB35EBF9DAA807170B820A4E97C1AECDCA7",
    },
    PK_MSGGAME: {
        "packed_size": 1_813_943,
        "packed_sha256": "2DACF44094FD3D309BEC415AE4F1DFC5303410435FDD997CC34B95F49AC17C1C",
        "raw_size": 1_806_832,
        "raw_sha256": "BDCE5FFD06F2A11650C0EF0142E98DF138B432AA244E4ED7E0688B1A4F27F073",
    },
}

JP_REFERENCE_SPECS = {
    MSG_DATA: {
        "packed_size": 272_453,
        "packed_sha256": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
        "raw_size": 434_000,
        "raw_sha256": "D09F61E34E4AA498F3DDEF23E7B7FD2CC8E9FE50B24F39D3BA1034BE82E6D0F6",
        "string_count": 29_218,
    },
    MSG_EV: {
        "packed_size": 562_226,
        "packed_sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        "raw_size": 894_800,
        "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
        "string_count": 17_916,
    },
}

FINAL_SPECS = {
    MSG_DATA: {
        "packed_size": 476_948,
        "packed_sha256": "7630EA5C4B6809C91F1F9DE3721C54769FC52EDD16FB89B3D111F7A58CC8238C",
        "raw_size": 475_060,
        "raw_sha256": "0BF79ECF9933053B3F2FCC7BA71A3CE0538B4B6590D4F29D68333426B7D05AC6",
    },
    MSG_EV: {
        "packed_size": 582_303,
        "packed_sha256": "1CE958C8036BA014A4142E0CCB10E12EA0E7FF7A8552CD01CEEE502A98C12E55",
        "raw_size": 1_044_208,
        "raw_sha256": "27FDCB0AB35412783500C66BDDD7E52E030ECCC2C229F57FD5089357F27951D5",
    },
}

EXPECTED_CHANGED_IDS = {
    MSG_DATA: (2_502, 24_765),
    MSG_EV: (1_625, 2_012),
}
EXPECTED_ENTRIES = {
    (MSG_DATA, 2_502): (122, "모토지", "모토우지", "shared_given_name"),
    (MSG_EV, 1_625): (122, "하타야마 모토지", "하타야마 모토우지", "complete_officer_name"),
    (MSG_EV, 2_012): (122, "모리 모토지", "모리 모토우지", "complete_officer_name"),
    (MSG_DATA, 24_765): (123, "야차미농", "야샤미노", "trait_reading"),
}
EXPECTED_ANCHORS = {
    (MSG_EV, 3_085): (122, "깃카와 모토우지"),
    (MSG_DATA, 24_510): (123, "야샤미노"),
}


class BuildError(RuntimeError):
    """Raised when a pinned input, mapping, or surgical output differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def utf16le_sha256(text: str) -> str:
    return sha256(text.encode("utf-16le"))


def resolved_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def packed_raw_spec(packed: bytes) -> tuple[dict[str, int | str], Any, bytes]:
    header, raw = decompress_wrapper(packed)
    return (
        {
            "packed_size": len(packed),
            "packed_sha256": sha256(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
        },
        header,
        raw,
    )


def _spec_core(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        key: spec[key]
        for key in ("packed_size", "packed_sha256", "raw_size", "raw_sha256")
    }


def _read_pinned(path: Path, spec: dict[str, Any], label: str) -> tuple[bytes, Any, bytes]:
    try:
        packed = path.read_bytes()
    except OSError as exc:
        raise BuildError(f"cannot read {label}: {path}") from exc
    actual, header, raw = packed_raw_spec(packed)
    if actual != _spec_core(spec):
        raise BuildError(f"{label} packed/raw pin differs")
    return packed, header, raw


def _read_message(
    path: Path,
    spec: dict[str, Any],
    label: str,
    *,
    verify_compression: bool = False,
) -> tuple[bytes, Any, bytes, MessageTable]:
    packed, header, raw = _read_pinned(path, spec, label)
    table = parse_message_table(raw)
    if table.string_count != spec["string_count"]:
        raise BuildError(f"{label} string count differs")
    if rebuild_message_table(table, table.texts) != raw:
        raise BuildError(f"{label} unchanged rebuild differs")
    if verify_compression:
        if spec["compression"] == "literal_only":
            rebuilt = recompress_wrapper(raw, header)
        elif spec["compression"] == "greedy":
            rebuilt = recompress_wrapper_greedy(raw, header)
        else:
            raise BuildError(f"{label} compression mode is unsupported")
        if rebuilt != packed:
            raise BuildError(f"{label} compression strategy differs")
    return packed, header, raw, table


def load_overlay() -> tuple[dict[Path, dict[int, dict[str, Any]]], dict[tuple[Path, int], dict[str, Any]]]:
    payload = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    if payload.get("schema") != OVERLAY_SCHEMA:
        raise BuildError("overlay schema differs")
    if payload.get("source_profile") != {
        "release_id": "v0.95.0-resources",
        "resource_count": 2,
    }:
        raise BuildError("overlay source profile differs")
    if payload.get("entry_count") != 4 or len(payload.get("entries", ())) != 4:
        raise BuildError("overlay entry count differs")
    if len(payload.get("verified_anchors", ())) != 2:
        raise BuildError("overlay anchor count differs")
    policy = payload.get("distribution_policy", {})
    if any(
        policy.get(key) is not False
        for key in (
            "contains_commercial_source_text",
            "contains_complete_game_resource",
            "contains_switch_binary",
        )
    ):
        raise BuildError("overlay distribution policy differs")

    entries: dict[Path, dict[int, dict[str, Any]]] = {resource: {} for resource in RESOURCE_ORDER}
    for entry in payload["entries"]:
        resource = Path(str(entry.get("resource", "")))
        identifier = int(entry.get("id", -1))
        key = (resource, identifier)
        if key not in EXPECTED_ENTRIES or identifier in entries.get(resource, {}):
            raise BuildError(f"overlay coordinate differs: {resource.as_posix()}:{identifier}")
        issue, before, after, role = EXPECTED_ENTRIES[key]
        if (
            entry.get("issue") != issue
            or entry.get("source_ko") != before
            or entry.get("ko") != after
            or entry.get("role") != role
        ):
            raise BuildError(f"overlay text or role differs: {resource.as_posix()}:{identifier}")
        if entry.get("source_ko_utf16le_sha256") != utf16le_sha256(before):
            raise BuildError(f"overlay source hash differs: {resource.as_posix()}:{identifier}")
        if entry.get("ko_utf16le_sha256") != utf16le_sha256(after):
            raise BuildError(f"overlay target hash differs: {resource.as_posix()}:{identifier}")
        source_jp_hash = entry.get("source_jp_utf16le_sha256")
        if not isinstance(source_jp_hash, str) or len(source_jp_hash) != 64:
            raise BuildError(f"overlay JP source hash differs: {resource.as_posix()}:{identifier}")
        entries[resource][identifier] = entry
    if {(resource, identifier) for resource, rows in entries.items() for identifier in rows} != set(
        EXPECTED_ENTRIES
    ):
        raise BuildError("overlay coordinate set differs")

    anchors: dict[tuple[Path, int], dict[str, Any]] = {}
    for anchor in payload["verified_anchors"]:
        resource = Path(str(anchor.get("resource", "")))
        identifier = int(anchor.get("id", -1))
        key = (resource, identifier)
        if key not in EXPECTED_ANCHORS or key in anchors:
            raise BuildError(f"overlay anchor differs: {resource.as_posix()}:{identifier}")
        issue, expected_ko = EXPECTED_ANCHORS[key]
        if anchor.get("issue") != issue or anchor.get("ko") != expected_ko:
            raise BuildError(f"overlay anchor text differs: {resource.as_posix()}:{identifier}")
        source_jp_hash = anchor.get("source_jp_utf16le_sha256")
        if not isinstance(source_jp_hash, str) or len(source_jp_hash) != 64:
            raise BuildError(f"overlay anchor JP hash differs: {resource.as_posix()}:{identifier}")
        anchors[key] = anchor
    if set(anchors) != set(EXPECTED_ANCHORS):
        raise BuildError("overlay anchor set differs")
    return entries, anchors


def _compress(raw: bytes, header: Any, mode: str) -> bytes:
    if mode == "literal_only":
        return recompress_wrapper(raw, header)
    if mode == "greedy":
        return recompress_wrapper_greedy(raw, header)
    raise BuildError(f"unsupported compression mode: {mode}")


def _verify_read_only_dependencies(input_root: Path) -> list[dict[str, Any]]:
    str_packed, _str_header, str_raw = _read_pinned(
        input_root / STR_DATA, INPUT_SPECS[STR_DATA], "input strdata"
    )
    archive = parse_raw_strdata(str_raw)
    if rebuild_raw_strdata(archive) != str_raw:
        raise BuildError("input strdata unchanged rebuild differs")
    if archive.blocks[0].texts[2_502] != "모토우지":
        raise BuildError("strdata shared name anchor differs")
    if "야샤미노" not in archive.blocks[2].texts[1_650]:
        raise BuildError("strdata trait biography anchor differs")

    msggame_packed, _msggame_header, _msggame_raw = _read_pinned(
        input_root / PK_MSGGAME, INPUT_SPECS[PK_MSGGAME], "input PK msggame"
    )
    parsed = parse_packed_msggame(msggame_packed)
    variants = ("야샤미노", "야사미노", "야차미노", "야차미농")
    hits = [
        literal
        for literal in iter_literals(parsed.archive)
        if any(variant in literal.text for variant in variants)
    ]
    hit_coordinates = [
        (literal.block_id, literal.record_id, literal.literal_id) for literal in hits
    ]
    if hit_coordinates != [(9, 972, 0), (9, 3_892, 1), (9, 3_914, 1)]:
        raise BuildError(f"PK msggame Yashamino coordinate vector differs: {hit_coordinates}")
    if any("야샤미노" not in literal.text for literal in hits):
        raise BuildError("PK msggame contains a stale Yashamino variant")

    return [
        {
            "resource": STR_DATA.as_posix(),
            "role": "read_only_dependency",
            "input": _spec_core(INPUT_SPECS[STR_DATA]),
            "anchors": ["block0:2502", "block2:1650"],
            "output_emitted": False,
            "all_texts_unchanged": True,
        },
        {
            "resource": PK_MSGGAME.as_posix(),
            "role": "read_only_dependency",
            "input": _spec_core(INPUT_SPECS[PK_MSGGAME]),
            "yashamino_literal_coordinates": [list(value) for value in hit_coordinates],
            "output_emitted": False,
            "all_bytes_unchanged": True,
        },
    ]


def build_candidate(input_root: Path, jp_reference_root: Path, output_root: Path) -> dict[str, Any]:
    input_root = input_root.resolve()
    jp_reference_root = jp_reference_root.resolve()
    output_root = output_root.resolve()
    if resolved_under(output_root, input_root) or resolved_under(input_root, output_root):
        raise BuildError("output root must not overlap the input root")
    if resolved_under(output_root, jp_reference_root) or resolved_under(jp_reference_root, output_root):
        raise BuildError("output root must not overlap the JP reference root")
    if resolved_under(output_root, DEFAULT_STEAM_ROOT):
        raise BuildError("output root must not be inside the Steam installation")
    if output_root.exists() and any(output_root.iterdir()):
        raise BuildError(f"output root is not empty: {output_root}")

    entries, anchors = load_overlay()
    input_tables: dict[Path, MessageTable] = {}
    input_headers: dict[Path, Any] = {}
    for resource in RESOURCE_ORDER:
        _packed, header, _raw, table = _read_message(
            input_root / resource,
            INPUT_SPECS[resource],
            f"input {resource.name}",
            verify_compression=True,
        )
        input_headers[resource] = header
        input_tables[resource] = table

    jp_tables: dict[Path, MessageTable] = {}
    for resource in RESOURCE_ORDER:
        _packed, _header, _raw, table = _read_message(
            jp_reference_root / resource,
            JP_REFERENCE_SPECS[resource],
            f"JP reference {resource.name}",
        )
        jp_tables[resource] = table

    for resource, rows in entries.items():
        for identifier, entry in rows.items():
            if input_tables[resource].texts[identifier] != entry["source_ko"]:
                raise BuildError(f"input text differs: {resource.as_posix()}:{identifier}")
            if utf16le_sha256(jp_tables[resource].texts[identifier]) != entry["source_jp_utf16le_sha256"]:
                raise BuildError(f"JP source mapping differs: {resource.as_posix()}:{identifier}")
    for (resource, identifier), anchor in anchors.items():
        if input_tables[resource].texts[identifier] != anchor["ko"]:
            raise BuildError(f"input anchor differs: {resource.as_posix()}:{identifier}")
        if utf16le_sha256(jp_tables[resource].texts[identifier]) != anchor["source_jp_utf16le_sha256"]:
            raise BuildError(f"JP anchor mapping differs: {resource.as_posix()}:{identifier}")

    dependency_reports = _verify_read_only_dependencies(input_root)
    resource_reports: list[dict[str, Any]] = []
    outputs: dict[Path, bytes] = {}
    for resource in RESOURCE_ORDER:
        table = input_tables[resource]
        texts = list(table.texts)
        for identifier, entry in sorted(entries[resource].items()):
            texts[identifier] = str(entry["ko"])
        rebuilt_raw = rebuild_message_table(table, texts)
        candidate = _compress(
            rebuilt_raw,
            input_headers[resource],
            str(INPUT_SPECS[resource]["compression"]),
        )
        actual, output_header, decoded = packed_raw_spec(candidate)
        if actual != FINAL_SPECS[resource]:
            raise BuildError(f"output packed/raw pin differs: {resource.as_posix()}")
        if output_header.prefix != input_headers[resource].prefix or decoded != rebuilt_raw:
            raise BuildError(f"output wrapper round trip differs: {resource.as_posix()}")
        check = parse_message_table(decoded)
        changed = tuple(
            identifier
            for identifier, (before, after) in enumerate(zip(table.texts, check.texts, strict=True))
            if before != after
        )
        if changed != EXPECTED_CHANGED_IDS[resource]:
            raise BuildError(f"changed id vector differs: {resource.as_posix()}:{changed}")
        for identifier, entry in entries[resource].items():
            if check.texts[identifier] != entry["ko"]:
                raise BuildError(f"output text differs: {resource.as_posix()}:{identifier}")
        for (anchor_resource, identifier), anchor in anchors.items():
            if anchor_resource == resource and check.texts[identifier] != anchor["ko"]:
                raise BuildError(f"output anchor differs: {resource.as_posix()}:{identifier}")
        if any("모토지" in text for text in check.texts):
            raise BuildError(f"stale Motouji spelling remains: {resource.as_posix()}")
        if any(
            variant in text
            for text in check.texts
            for variant in ("야사미노", "야차미노", "야차미농")
        ):
            raise BuildError(f"stale Yashamino spelling remains: {resource.as_posix()}")
        outputs[resource] = candidate
        resource_reports.append(
            {
                "resource": resource.as_posix(),
                "changed_ids": list(changed),
                "changed_text_count": len(changed),
                "compression": INPUT_SPECS[resource]["compression"],
                "input": _spec_core(INPUT_SPECS[resource]),
                "target": FINAL_SPECS[resource],
                "all_other_texts_unchanged": True,
            }
        )

    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "issues": {
            "122": {
                "changed_coordinates": [
                    "MSG_PK/JP/msgdata.bin:2502",
                    "MSG_PK/JP/msgev.bin:1625",
                    "MSG_PK/JP/msgev.bin:2012",
                ],
                "replacement": "모토우지",
                "verified_existing_anchors": [
                    "MSG/JP/strdata.bin:block0:2502",
                    "MSG_PK/JP/msgev.bin:3085",
                ],
            },
            "123": {
                "changed_coordinates": ["MSG_PK/JP/msgdata.bin:24765"],
                "verified_name_coordinate": "MSG_PK/JP/msgdata.bin:24510",
                "replacement": "야샤미노",
                "verified_dialogue_literal_count": 3,
            },
        },
        "resources": resource_reports + dependency_reports,
        "changed_resource_count": 2,
        "output_resource_count": 2,
        "changed_text_count": 4,
        "commercial_source_text_embedded": False,
        "steam_written": False,
    }

    output_root.mkdir(parents=True, exist_ok=True)
    for resource, candidate in outputs.items():
        destination = output_root / resource
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidate)
    validation_blob = (
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    (output_root / VALIDATION_NAME).write_bytes(validation_blob)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--jp-reference-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_candidate(args.input_root, args.jp_reference_root, args.output_root)
    except (
        BuildError,
        LZ4Error,
        MessageTableError,
        StrdataFormatError,
        MsgGameFormatError,
        OSError,
        ValueError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
