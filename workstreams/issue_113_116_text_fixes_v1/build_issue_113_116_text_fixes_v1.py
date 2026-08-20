#!/usr/bin/env python3
"""Build and strictly verify the v0.94 resource fixes for issues #113 and #116."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO / "tools"), str(REPO / "workstreams" / "strdata")]

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import (  # noqa: E402
    MessageTableError,
    parse_message_table,
    rebuild_message_table,
)
from strdata_format import (  # noqa: E402
    StrdataFormatError,
    coordinate_texts,
    parse_raw_strdata,
    rebuild_raw_strdata,
)


SCHEMA = "nobu16.kr.issue113-116-text-fixes-validation.v1"
OVERLAY_SCHEMA = "nobu16.kr.issue113-116-text-fixes-overlay.v1"
OVERLAY_PATH = HERE / "issue_113_116_text_fixes.overlay.v1.json"
VALIDATION_NAME = "validation.issue113_116_text_fixes.v1.json"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

MSG_UI = Path("MSG_PK/JP/msgui.bin")
MSG_DATA = Path("MSG_PK/JP/msgdata.bin")
STR_DATA = Path("MSG/JP/strdata.bin")
ISSUE118_PASSTHROUGH = Path("MSG_PK/JP/msggame.bin")
BASE_MSGGAME_PASSTHROUGH = Path("MSG/JP/msggame.bin")
GM2355_PASSTHROUGH = Path("DLC_PK/JP/gm_2355.n16")
RESOURCE_ORDER = (MSG_UI, MSG_DATA, STR_DATA)
PASSTHROUGH_ORDER = (
    ISSUE118_PASSTHROUGH,
    BASE_MSGGAME_PASSTHROUGH,
    GM2355_PASSTHROUGH,
)

MESSAGE_COORDINATES = {
    MSG_UI: 2690,
    MSG_DATA: 10220,
}
STRDATA_COORDINATE = (0, 10136)
STRDATA_SLOT_COUNTS = (25_069, 4_100, 3_000, 122, 20)
PAIRED_MSGDATA_RANGE = (9_935, 11_310)
PAIRED_STRDATA_RANGE = (9_851, 11_226)
PAIRED_OFFSET = 84

INPUT_SPECS = {
    MSG_UI: {
        "packed_size": 122_729,
        "packed_sha256": "E6399C403ADA69322C9F27161549A52A534DBBFF086126FC01ED87FCB07837FA",
        "raw_size": 122_224,
        "raw_sha256": "DCC82E99104B742B061730E254F03CD62711424572671292C1D50A1972484DCB",
        "string_count": 5_100,
    },
    MSG_DATA: {
        "packed_size": 476_860,
        "packed_sha256": "6D7DEA6149FE9B40951B507E7E210A614169D8CB19AEDE3EB85BC8B15EDF2410",
        "raw_size": 474_972,
        "raw_sha256": "3C71C6F6B464C69DE6103316F59A18C0CD41C977985DC7BC8AEECFF78CFC6157",
        "string_count": 29_218,
    },
    STR_DATA: {
        "packed_size": 940_981,
        "packed_sha256": "70FCB097EE999BA8E50723E262C232F782D7DE564DDAB84C9D28180A7AA7FF55",
        "raw_size": 937_280,
        "raw_sha256": "21DAFE66284D6B919B2A0B0E47C45A2058F0BE55A2EC9751F2816B9AC18E8947",
    },
}

FINAL_SPECS = {
    MSG_UI: {
        "packed_size": 122_733,
        "packed_sha256": "C737796FE317FCEB5F0D315548DE6F2BAA683FE17B85CCAE1818FC5BD43BBC50",
        "raw_size": 122_228,
        "raw_sha256": "2CF4626FD9C12C25118B1D38BCA8C053CDB59425AE3C8E0E721AB16CCDBD5DBF",
    },
    MSG_DATA: {
        "packed_size": 476_860,
        "packed_sha256": "2528F53F6F4666DEFD36EA8D5BD577DD60C78630D8E3F63CA0E5A1FE75B60B62",
        "raw_size": 474_972,
        "raw_sha256": "8E70FB63AD145795421BBD6B129073C06D7DA3ECAE5EB430572E10B538111B28",
    },
    STR_DATA: {
        "packed_size": 940_981,
        "packed_sha256": "66AE04C595F05B0FFA478BD4182822365161DF699B418B506EC3A4B828F3BE95",
        "raw_size": 937_280,
        "raw_sha256": "EF25A55FB6725038277E5AFBEA3CA7CAB60FBA55EC8C09E57519920B43B244D7",
    },
}

PASSTHROUGH_SPECS = {
    ISSUE118_PASSTHROUGH: {
        "size": 1_813_943,
        "sha256": "F09D9CCE819E26E3B14E368DD4AA7A7254D7CB81CBB5EB3860D0D1A099C4CFC1",
        "reason": "preserve_issue_118_pk_dialogue_fix",
    },
    BASE_MSGGAME_PASSTHROUGH: {
        "size": 1_556_016,
        "sha256": "3FAE2B624ED1D0C164CCDACF757360C9EAE1DC56EC54D61A6CEBAD06B231BFC7",
        "reason": "preserve_the_already_corrected_base_message_resource",
    },
    GM2355_PASSTHROUGH: {
        "size": 286,
        "sha256": "5A21A487AEA7A5AB3F9005248FB7369D4FF4E2DE10730466C9BBD825B6D9740A",
        "reason": "preserve_the_accumulated_optional_dlc_translation",
    },
}
ISSUE118_SPEC = {
    "packed_size": PASSTHROUGH_SPECS[ISSUE118_PASSTHROUGH]["size"],
    "packed_sha256": PASSTHROUGH_SPECS[ISSUE118_PASSTHROUGH]["sha256"],
}


class BuildError(RuntimeError):
    """Raised when an input, overlay, or surgical-output contract differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def utf16le_sha256(text: str) -> str:
    return sha256(text.encode("utf-16le"))


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


def resolved_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _entry_coordinate(entry: dict[str, Any]) -> tuple[int, ...]:
    if entry.get("resource") == STR_DATA.as_posix():
        return int(entry.get("block_id", -1)), int(entry.get("slot_id", -1))
    return (int(entry.get("id", -1)),)


def load_overlay() -> dict[Path, dict[str, Any]]:
    payload = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    if payload.get("schema") != OVERLAY_SCHEMA:
        raise BuildError("overlay schema differs")
    if payload.get("entry_count") != 3 or len(payload.get("entries", ())) != 3:
        raise BuildError("overlay must contain exactly three entries")
    if payload.get("source_profile") != {
        "release_id": "v0.94.0-resources-issue118",
        "resource_count": 3,
    }:
        raise BuildError("overlay source profile differs")
    expected = {
        MSG_UI: (113, (2690,), "%s%s", "%s %s"),
        MSG_DATA: (116, (10220,), "고려", "고마"),
        STR_DATA: (116, STRDATA_COORDINATE, "고려", "고마"),
    }
    entries: dict[Path, dict[str, Any]] = {}
    for entry in payload["entries"]:
        resource = Path(str(entry.get("resource", "")))
        if resource not in expected or resource in entries:
            raise BuildError(f"overlay resource vector differs: {resource.as_posix()}")
        issue, coordinate, before, after = expected[resource]
        if entry.get("issue") != issue or _entry_coordinate(entry) != coordinate:
            raise BuildError(f"overlay coordinate differs: {resource.as_posix()}")
        if entry.get("source_ko") != before or entry.get("ko") != after:
            raise BuildError(f"overlay text differs: {resource.as_posix()}")
        if entry.get("source_ko_utf16le_sha256") != utf16le_sha256(before):
            raise BuildError(f"overlay source text hash differs: {resource.as_posix()}")
        if entry.get("ko_utf16le_sha256") != utf16le_sha256(after):
            raise BuildError(f"overlay replacement hash differs: {resource.as_posix()}")
        entries[resource] = entry
    if set(entries) != set(expected):
        raise BuildError("overlay resource set differs")
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
    return entries


def _require_input(packed: bytes, resource: Path) -> tuple[Any, bytes]:
    actual, header, raw = packed_raw_spec(packed)
    expected = {key: INPUT_SPECS[resource][key] for key in actual}
    if actual != expected:
        raise BuildError(f"input packed/raw pin differs: {resource.as_posix()}")
    if recompress_wrapper(raw, header) != packed:
        raise BuildError(f"input wrapper is not deterministic literal-only: {resource.as_posix()}")
    return header, raw


def _require_output(candidate: bytes, resource: Path) -> tuple[Any, bytes]:
    actual, header, raw = packed_raw_spec(candidate)
    if actual != FINAL_SPECS[resource]:
        raise BuildError(f"output packed/raw pin differs: {resource.as_posix()}")
    return header, raw


def build_message_candidate(
    packed: bytes,
    resource: Path,
    entry: dict[str, Any],
) -> tuple[bytes, tuple[str, ...], tuple[str, ...], dict[str, Any]]:
    header, raw = _require_input(packed, resource)
    table = parse_message_table(raw)
    if table.string_count != INPUT_SPECS[resource]["string_count"]:
        raise BuildError(f"input string count differs: {resource.as_posix()}")
    if rebuild_message_table(table, table.texts) != raw:
        raise BuildError(f"input unchanged rebuild differs: {resource.as_posix()}")
    identifier = MESSAGE_COORDINATES[resource]
    if table.texts[identifier] != entry["source_ko"]:
        raise BuildError(f"input target text differs: {resource.as_posix()}:{identifier}")

    texts = list(table.texts)
    texts[identifier] = str(entry["ko"])
    rebuilt_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(rebuilt_raw, header)
    output_header, decoded = _require_output(candidate, resource)
    if output_header.prefix != header.prefix or decoded != rebuilt_raw:
        raise BuildError(f"output wrapper round-trip differs: {resource.as_posix()}")
    check = parse_message_table(decoded)
    changed = tuple(
        index
        for index, (before, after) in enumerate(zip(table.texts, check.texts, strict=True))
        if before != after
    )
    if changed != (identifier,):
        raise BuildError(f"changed id vector differs: {resource.as_posix()}:{changed}")
    if check.texts[identifier] != entry["ko"]:
        raise BuildError(f"output target text differs: {resource.as_posix()}:{identifier}")
    return candidate, table.texts, check.texts, {
        "resource": resource.as_posix(),
        "coordinate": [identifier],
        "changed_text_count": 1,
        "all_other_texts_unchanged": True,
        "input": {key: INPUT_SPECS[resource][key] for key in ("packed_size", "packed_sha256", "raw_size", "raw_sha256")},
        "target": FINAL_SPECS[resource],
    }


def build_strdata_candidate(
    packed: bytes,
    entry: dict[str, Any],
) -> tuple[bytes, dict[tuple[int, int], str], dict[tuple[int, int], str], dict[str, Any]]:
    header, raw = _require_input(packed, STR_DATA)
    archive = parse_raw_strdata(raw)
    if tuple(block.slot_count for block in archive.blocks) != STRDATA_SLOT_COUNTS:
        raise BuildError("strdata slot-count vector differs")
    if rebuild_raw_strdata(archive) != raw:
        raise BuildError("strdata input unchanged rebuild differs")
    before = coordinate_texts(archive)
    if before[STRDATA_COORDINATE] != entry["source_ko"]:
        raise BuildError("strdata input target text differs")

    replacements = {0: list(archive.blocks[0].texts)}
    replacements[0][STRDATA_COORDINATE[1]] = str(entry["ko"])
    rebuilt_raw = rebuild_raw_strdata(archive, replacements)
    candidate = recompress_wrapper(rebuilt_raw, header)
    output_header, decoded = _require_output(candidate, STR_DATA)
    if output_header.prefix != header.prefix or decoded != rebuilt_raw:
        raise BuildError("strdata output wrapper round-trip differs")
    check = parse_raw_strdata(decoded)
    after = coordinate_texts(check)
    changed = tuple(coordinate for coordinate in before if before[coordinate] != after[coordinate])
    if changed != (STRDATA_COORDINATE,):
        raise BuildError(f"strdata changed coordinate vector differs: {changed}")
    for old_block, new_block in zip(archive.blocks, check.blocks, strict=True):
        if old_block.inner_header != new_block.inner_header:
            raise BuildError(f"strdata opaque inner header changed: {old_block.block_id}")
    return candidate, before, after, {
        "resource": STR_DATA.as_posix(),
        "coordinate": list(STRDATA_COORDINATE),
        "changed_text_count": 1,
        "all_other_texts_unchanged": True,
        "opaque_inner_headers_preserved": True,
        "input": INPUT_SPECS[STR_DATA],
        "target": FINAL_SPECS[STR_DATA],
    }


def _require_paired_place_name_coordinate(
    msgdata: Sequence[str],
    strdata: dict[tuple[int, int], str],
    expected: str,
) -> None:
    msg_start, msg_end = PAIRED_MSGDATA_RANGE
    str_start, str_end = PAIRED_STRDATA_RANGE
    if msg_end - msg_start != 1_375 or str_end - str_start != 1_375:
        raise BuildError("paired stock place-name range differs")
    if 10220 - PAIRED_OFFSET != STRDATA_COORDINATE[1]:
        raise BuildError("paired place-name coordinate offset differs")
    if msgdata[10220] != expected or strdata[STRDATA_COORDINATE] != expected:
        raise BuildError("paired place-name target differs")


def build_candidate(input_root: Path, output_root: Path) -> dict[str, Any]:
    input_root = input_root.resolve()
    output_root = output_root.resolve()
    if resolved_under(output_root, input_root):
        raise BuildError("output root must not be inside the input root")
    if resolved_under(output_root, DEFAULT_STEAM_ROOT):
        raise BuildError("output root must not be inside the Steam installation")
    if output_root.exists() and any(output_root.iterdir()):
        raise BuildError(f"output root is not empty: {output_root}")

    entries = load_overlay()
    sources: dict[Path, bytes] = {}
    for resource in (*RESOURCE_ORDER, *PASSTHROUGH_ORDER):
        path = input_root / resource
        try:
            sources[resource] = path.read_bytes()
        except OSError as exc:
            raise BuildError(f"cannot read pinned input: {path}") from exc
    for resource, expected in PASSTHROUGH_SPECS.items():
        passthrough = sources[resource]
        if len(passthrough) != expected["size"] or sha256(passthrough) != expected["sha256"]:
            raise BuildError(f"pass-through dependency differs: {resource.as_posix()}")

    msgui, msgui_before, msgui_after, msgui_report = build_message_candidate(
        sources[MSG_UI], MSG_UI, entries[MSG_UI]
    )
    msgdata, msgdata_before, msgdata_after, msgdata_report = build_message_candidate(
        sources[MSG_DATA], MSG_DATA, entries[MSG_DATA]
    )
    strdata, strdata_before, strdata_after, strdata_report = build_strdata_candidate(
        sources[STR_DATA], entries[STR_DATA]
    )

    _require_paired_place_name_coordinate(msgdata_before, strdata_before, "고려")
    _require_paired_place_name_coordinate(msgdata_after, strdata_after, "고마")

    issue113_surfaces = (
        msgui_after[2690] % (msgui_after[2312], msgui_after[2693]),
        msgui_after[2690] % (msgui_after[2310], msgui_after[2713]),
    )
    if issue113_surfaces != ("적 부대의 병력 감소", "자기 부대의 방어 상승"):
        raise BuildError(f"issue 113 composed surfaces differ: {issue113_surfaces}")

    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "issues": {
            "113": {
                **msgui_report,
                "root_cause": "runtime composition template omitted the separator between two %s fragments",
                "composed_surfaces": list(issue113_surfaces),
            },
            "116": {
                "resources": [msgdata_report, strdata_report],
                "changed_text_count": 2,
                "stock_pairing_evidence_run_count": 1_375,
                "paired_offset": PAIRED_OFFSET,
                "all_non_target_occurrences_preserved": True,
            },
        },
        "issue_118_passthrough": {
            "resource": ISSUE118_PASSTHROUGH.as_posix(),
            **ISSUE118_SPEC,
            "byte_exact": True,
        },
        "preserved_passthroughs": [
            {
                "resource": resource.as_posix(),
                **expected,
                "byte_exact": True,
            }
            for resource, expected in PASSTHROUGH_SPECS.items()
        ],
        "output_resource_count": 6,
        "changed_resource_count": 3,
        "changed_text_count": 3,
        "steam_written": False,
    }

    outputs = {
        MSG_UI: msgui,
        MSG_DATA: msgdata,
        STR_DATA: strdata,
        **{resource: sources[resource] for resource in PASSTHROUGH_ORDER},
    }
    output_root.mkdir(parents=True, exist_ok=True)
    for resource, blob in outputs.items():
        destination = output_root / resource
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(blob)
    validation = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (output_root / VALIDATION_NAME).write_bytes(validation)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_candidate(args.input_root, args.output_root)
    except (BuildError, MessageTableError, StrdataFormatError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
