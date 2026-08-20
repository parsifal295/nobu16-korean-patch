#!/usr/bin/env python3
"""Build the deterministic PK msggame correction for GitHub issue #118."""

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
sys.path[:0] = [str(REPO / "workstreams" / "msggame"), str(REPO / "tools")]

import msggame_format as msggame  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402


SCHEMA = "nobu16.kr.issue118-diplomacy-good-plan-validation.v1"
OVERLAY_SCHEMA = "nobu16.kr.issue118-diplomacy-good-plan-overlay.v1"
OVERLAY_PATH = HERE / "issue_118_diplomacy_good_plan.overlay.v1.json"
VALIDATION_NAME = "validation.issue118_diplomacy_good_plan.v1.json"
RESOURCE = Path("MSG_PK/JP/msggame.bin")
COORDINATE = (6, 3778, 1)
RECORD_COORDINATE = COORDINATE[:2]
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

INPUT_SPEC = {
    "packed_size": 1_813_935,
    "packed_sha256": "F974B5B3E33EB91A8849823A3BF7B5B48699062E7199F6D8F981FB11AFA4EA08",
    "raw_size": 1_806_824,
    "raw_sha256": "3A20C652750470D919377E47813B531DF14CA4498856F35C1E396D9D199A09FE",
    "record_size": 59,
    "record_sha256": "85B077B868780D3F6F785C12A55DE6EB08E356CE13DE958C279F08C473525B2D",
    "literal_utf16le_sha256": (
        "D8F318B68F5152031B126672BFB2CD7E10D9DEB38F2322AA10654780D630DA6F",
        "99ED549153C807F40832AC76895E9D17BFB659EFB80E88A959CDCC7BA5270DF4",
    ),
}
FINAL_SPEC = {
    "packed_size": 1_813_943,
    "packed_sha256": "F09D9CCE819E26E3B14E368DD4AA7A7254D7CB81CBB5EB3860D0D1A099C4CFC1",
    "raw_size": 1_806_832,
    "raw_sha256": "503EA406E3A6724C9A5A7FFC003D3263579DB60C4FB2B9DD852246042025179B",
    "record_size": 67,
    "record_sha256": "B797D14D184004097DA2F9A988AB22C0A40EE07D2AE9D3514F7E671C36AA7B65",
    "literal_utf16le_sha256": (
        "D8F318B68F5152031B126672BFB2CD7E10D9DEB38F2322AA10654780D630DA6F",
        "CB007814FE2EF035149088B3EDD27D536E0CCAAB54DF676F5D592FD77027CCDD",
    ),
}
OPAQUE_SPANS = (
    "023C",
    "0143EE000000",
    "014326020000050505",
)


class BuildError(RuntimeError):
    """Raised when the pinned source or surgical-output contract differs."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def utf16le_sha256(text: str) -> str:
    return sha256(text.encode("utf-16le"))


def packed_spec(packed: bytes) -> dict[str, int | str]:
    _header, raw = decompress_wrapper(packed)
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
    }


def load_overlay() -> dict[str, Any]:
    payload = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    if payload.get("schema") != OVERLAY_SCHEMA:
        raise BuildError("overlay schema differs")
    if payload.get("resource") != RESOURCE.as_posix():
        raise BuildError("overlay resource differs")
    if payload.get("entry_count") != 1 or len(payload.get("entries", ())) != 1:
        raise BuildError("overlay must contain exactly one entry")
    source_profile = payload.get("source_profile", {})
    if source_profile != {
        "release_id": "v0.93.0-resources",
        "packed_size": INPUT_SPEC["packed_size"],
        "packed_sha256": INPUT_SPEC["packed_sha256"],
    }:
        raise BuildError("overlay source profile differs")
    entry = payload["entries"][0]
    coordinate = (
        entry.get("block_id"),
        entry.get("record_id"),
        entry.get("literal_id"),
    )
    if coordinate != COORDINATE:
        raise BuildError("overlay coordinate differs")
    if entry.get("source_ko_utf16le_sha256") != INPUT_SPEC["literal_utf16le_sha256"][1]:
        raise BuildError("overlay source literal pin differs")
    replacement = entry.get("ko")
    if replacement != "\n좋은 방안":
        raise BuildError("overlay replacement differs")
    if entry.get("ko_utf16le_sha256") != utf16le_sha256(replacement):
        raise BuildError("overlay replacement hash differs")
    policy = payload.get("distribution_policy", {})
    if any(policy.get(key) is not False for key in (
        "contains_commercial_source_text",
        "contains_complete_game_resource",
        "contains_switch_binary",
    )):
        raise BuildError("overlay distribution policy differs")
    return entry


def record_at(
    archive: msggame.MsgGameArchive,
    coordinate: tuple[int, int] = RECORD_COORDINATE,
) -> msggame.MsgGameRecord:
    block_id, record_id = coordinate
    try:
        record = archive.blocks[block_id].records[record_id]
    except IndexError as exc:
        raise BuildError(f"record coordinate is absent: {block_id}:{record_id}") from exc
    if (record.block_id, record.record_id) != coordinate:
        raise BuildError(f"record coordinate mapping differs: {block_id}:{record_id}")
    return record


def literal_texts(record: msggame.MsgGameRecord) -> tuple[str, ...]:
    return tuple(value.text for value in msggame.parse_record_literals(record))


def literal_hashes(record: msggame.MsgGameRecord) -> tuple[str, ...]:
    return tuple(utf16le_sha256(value) for value in literal_texts(record))


def opaque_spans(record: msggame.MsgGameRecord) -> tuple[str, ...]:
    spans: list[str] = []
    cursor = 0
    for literal in msggame.parse_record_literals(record):
        spans.append(record.data[cursor:literal.marker_offset].hex().upper())
        cursor = literal.marker_end
    spans.append(record.data[cursor:].hex().upper())
    return tuple(spans)


def records_by_coordinate(
    archive: msggame.MsgGameArchive,
) -> dict[tuple[int, int], msggame.MsgGameRecord]:
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def changed_records(
    before: msggame.MsgGameArchive,
    after: msggame.MsgGameArchive,
) -> tuple[tuple[int, int], ...]:
    left = records_by_coordinate(before)
    right = records_by_coordinate(after)
    if left.keys() != right.keys():
        raise BuildError("record coordinate domain changed")
    return tuple(coordinate for coordinate in left if left[coordinate].data != right[coordinate].data)


def changed_literals(
    before: msggame.MsgGameArchive,
    after: msggame.MsgGameArchive,
) -> tuple[tuple[int, int, int], ...]:
    left = records_by_coordinate(before)
    right = records_by_coordinate(after)
    result: list[tuple[int, int, int]] = []
    for coordinate in left:
        old = literal_texts(left[coordinate])
        new = literal_texts(right[coordinate])
        if len(old) != len(new):
            raise BuildError(f"literal topology changed: {coordinate}")
        for literal_id, (old_text, new_text) in enumerate(zip(old, new, strict=True)):
            if old_text != new_text:
                result.append((*coordinate, literal_id))
    return tuple(result)


def resolved_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def build_candidate(input_root: Path, output_root: Path) -> dict[str, Any]:
    input_root = input_root.resolve()
    output_root = output_root.resolve()
    if resolved_under(output_root, input_root):
        raise BuildError("output root must not be inside the input root")
    if resolved_under(output_root, DEFAULT_STEAM_ROOT):
        raise BuildError("output root must not be inside the Steam installation")
    if output_root.exists() and any(output_root.iterdir()):
        raise BuildError(f"output root is not empty: {output_root}")

    entry = load_overlay()
    source_path = input_root / RESOURCE
    try:
        source = source_path.read_bytes()
    except OSError as exc:
        raise BuildError(f"cannot read pinned input: {source_path}") from exc
    if packed_spec(source) != {
        key: INPUT_SPEC[key]
        for key in ("packed_size", "packed_sha256", "raw_size", "raw_sha256")
    }:
        raise BuildError("input packed/raw pin differs")

    before = msggame.parse_packed_msggame(source)
    record_before = record_at(before.archive)
    if len(record_before.data) != INPUT_SPEC["record_size"]:
        raise BuildError("input record size differs")
    if sha256(record_before.data) != INPUT_SPEC["record_sha256"]:
        raise BuildError("input record hash differs")
    if literal_hashes(record_before) != INPUT_SPEC["literal_utf16le_sha256"]:
        raise BuildError("input literal vector differs")
    if opaque_spans(record_before) != OPAQUE_SPANS:
        raise BuildError("input VM/control spans differ")

    candidate = msggame.rebuild_packed_with_literals(
        source,
        {COORDINATE: str(entry["ko"])},
    )
    after = msggame.parse_packed_msggame(candidate)
    if before.header.prefix != after.header.prefix:
        raise BuildError("wrapper prefix changed")
    if changed_records(before.archive, after.archive) != (RECORD_COORDINATE,):
        raise BuildError("changed-record vector differs")
    if changed_literals(before.archive, after.archive) != (COORDINATE,):
        raise BuildError("changed-literal vector differs")

    record_after = record_at(after.archive)
    if len(record_after.data) != FINAL_SPEC["record_size"]:
        raise BuildError("output record size differs")
    if sha256(record_after.data) != FINAL_SPEC["record_sha256"]:
        raise BuildError("output record hash differs")
    if literal_hashes(record_after) != FINAL_SPEC["literal_utf16le_sha256"]:
        raise BuildError("output literal vector differs")
    if literal_texts(record_after)[1] != entry["ko"]:
        raise BuildError("output wording differs")
    if opaque_spans(record_after) != OPAQUE_SPANS:
        raise BuildError("output VM/control spans differ")
    if packed_spec(candidate) != {
        key: FINAL_SPEC[key]
        for key in ("packed_size", "packed_sha256", "raw_size", "raw_sha256")
    }:
        raise BuildError("output packed/raw pin differs")

    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "issue": 118,
        "resource": RESOURCE.as_posix(),
        "coordinate": list(COORDINATE),
        "input": INPUT_SPEC,
        "final": FINAL_SPEC,
        "changed_record_count": 1,
        "changed_literal_count": 1,
        "opaque_spans": list(OPAQUE_SPANS),
        "vm_and_control_bytes_preserved": True,
        "expected_reported_style_surface": "좋은 방안이옵니다",
        "steam_written": False,
    }
    validation = (
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    output_path = output_root / RESOURCE
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(candidate)
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
    except (BuildError, msggame.MsgGameFormatError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
