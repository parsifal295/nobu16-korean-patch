#!/usr/bin/env python3
"""Build the deterministic Base/PK msggame correction for issue #109."""

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


SCHEMA = "nobu16.kr.issue109-marriage-support-validation.v1"
VALIDATION_NAME = "validation.issue109_marriage_support.v1.json"
REPLACEMENT_LITERALS = (
    "의 자격으로 ",
    "에게 힘이 되어 줄 준비는\n되어 있겠지",
)
OPAQUE_SPANS = ("023C", "014301000000", "050505")
FINAL_RECORD_SIZE = 79
FINAL_RECORD_SHA256 = "7BC4BDE66733FAC24ECC92C8D94A7D37342BF48742DE471CEB260E3CE533A325"

# The two stock Japanese records are byte-identical.  Cross-language static
# analysis establishes the opaque slots as the role token (023C) followed by
# the supported-person token (014301000000).
JP_SOURCE_EVIDENCE = {
    "stock_record_size": 57,
    "stock_record_sha256": "DD9212984441F9992347E56B7FB0A651601FE60DD035A39F5E3CDEF6C67C2EBF",
    "literal_utf16le_sha256": [
        "B44FEE9A4B423FFDF4B3DF3652A9C1D3B6E0158CF48FB6D90F3C1FEC590D565D",
        "A4CDB80F1ADAFDB249B4F411FD206E2DF667B447364C138391DFBFEE59DEB669",
    ],
    "opaque_spans": list(OPAQUE_SPANS),
}

RESOURCE_SPECS: dict[str, dict[str, Any]] = {
    "MSG/JP/msggame.bin": {
        "coordinate": (6, 3577),
        "input": {
            "packed_size": 1_557_899,
            "packed_sha256": "E490F2B42B749DB0C43940C1AD6CCBFA3E5ED7816BE9C29CA4B1CBC50652FF84",
            "raw_size": 1_551_788,
            "raw_sha256": "4C32C6927FCF75F552AEB2335BF9E98A63378EC2C3A76333B53ED3D4D9BD82B2",
            "record_size": 75,
            "record_sha256": "96681321B3DE29D00D87F8DEC5F6FB537B944C261FE65D419260E20B0C7F6B65",
            "literals": (" 자격으로서 ", " 자신을 보필할 준비는\n되어 있겠지"),
        },
        "final": {
            "packed_size": 1_557_903,
            "packed_sha256": "9742B5EA5EF34B6C7D9FDFC596A3DFE6C76F6C0A5D4790BE7EFB8246CE7A4A73",
            "raw_size": 1_551_792,
            "raw_sha256": "4BD5DA0BA2B135F3849FF5198C1AFFFAD02A90D9174F07659335830019C9B7BB",
        },
    },
    "MSG_PK/JP/msggame.bin": {
        "coordinate": (6, 3584),
        "input": {
            "packed_size": 1_815_553,
            "packed_sha256": "FF16AD8210D68D109EFF9B43BE2A3573AED5F3A67BC1468E574BCE6CE510F3BC",
            "raw_size": 1_808_436,
            "raw_sha256": "3DAA168D9975882113BA570FA2AB1AADD3407ED743E5379B4084B9140C561943",
            "record_size": 53,
            "record_sha256": "4D5E06F314CCC7581F8481D47DF2D87DECF92FB7D71AC34D8B573912241CB68A",
            "literals": (" 신분:", "으로서\n보필할 대상:"),
        },
        "final": {
            "packed_size": 1_815_581,
            "packed_sha256": "5A9993C112DE1E434F977C0134ED3FF1611F73FBDF0C89C41A7A6A7FF97B5069",
            "raw_size": 1_808_464,
            "raw_sha256": "FBCE1F1D6576A72D77778C8D0FA5581A7F6AFF5BFBDB8DF0B394E5B84FFA3BF8",
        },
    },
}


class BuildError(RuntimeError):
    """Raised when an input or generated candidate violates the pinned contract."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def packed_spec(packed: bytes) -> dict[str, int | str]:
    _header, raw = decompress_wrapper(packed)
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
    }


def record_at(archive: msggame.MsgGameArchive, coordinate: tuple[int, int]) -> msggame.MsgGameRecord:
    block_id, record_id = coordinate
    try:
        record = archive.blocks[block_id].records[record_id]
    except IndexError as exc:
        raise BuildError(f"record coordinate is absent: {block_id}:{record_id}") from exc
    if (record.block_id, record.record_id) != coordinate:
        raise BuildError(f"record coordinate mapping changed: {block_id}:{record_id}")
    return record


def opaque_spans(record: msggame.MsgGameRecord) -> tuple[str, ...]:
    spans: list[str] = []
    cursor = 0
    for literal in msggame.parse_record_literals(record):
        spans.append(record.data[cursor : literal.marker_offset].hex().upper())
        cursor = literal.marker_end
    spans.append(record.data[cursor:].hex().upper())
    return tuple(spans)


def literal_texts(record: msggame.MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in msggame.parse_record_literals(record))


def changed_records(
    before: msggame.MsgGameArchive, after: msggame.MsgGameArchive
) -> tuple[tuple[int, int], ...]:
    if len(before.blocks) != len(after.blocks):
        raise BuildError("block count changed")
    changed: list[tuple[int, int]] = []
    for before_block, after_block in zip(before.blocks, after.blocks, strict=True):
        if len(before_block.records) != len(after_block.records):
            raise BuildError(f"record count changed in block {before_block.block_id}")
        for before_record, after_record in zip(
            before_block.records, after_block.records, strict=True
        ):
            if before_record.data != after_record.data:
                changed.append((before_record.block_id, before_record.record_id))
    return tuple(changed)


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
    if output_root.exists() and any(output_root.iterdir()):
        raise BuildError(f"output root is not empty: {output_root}")

    outputs: dict[str, bytes] = {}
    resource_reports: list[dict[str, Any]] = []
    final_records: list[bytes] = []
    for relative_path, contract in RESOURCE_SPECS.items():
        source_path = input_root / Path(relative_path)
        try:
            source = source_path.read_bytes()
        except OSError as exc:
            raise BuildError(f"cannot read pinned input: {source_path}") from exc

        actual_input = packed_spec(source)
        expected_input = {
            key: contract["input"][key]
            for key in ("packed_size", "packed_sha256", "raw_size", "raw_sha256")
        }
        if actual_input != expected_input:
            raise BuildError(f"input pin differs: {relative_path}: {actual_input}")

        parsed_before = msggame.parse_packed_msggame(source)
        coordinate = tuple(contract["coordinate"])
        record_before = record_at(parsed_before.archive, coordinate)
        if len(record_before.data) != contract["input"]["record_size"]:
            raise BuildError(f"input record size differs: {relative_path}")
        if sha256(record_before.data) != contract["input"]["record_sha256"]:
            raise BuildError(f"input record hash differs: {relative_path}")
        if literal_texts(record_before) != tuple(contract["input"]["literals"]):
            raise BuildError(f"input record literals differ: {relative_path}")
        if opaque_spans(record_before) != OPAQUE_SPANS:
            raise BuildError(f"input opaque spans differ: {relative_path}")

        replacements = {
            (coordinate[0], coordinate[1], literal_id): text
            for literal_id, text in enumerate(REPLACEMENT_LITERALS)
        }
        candidate = msggame.rebuild_packed_with_literals(source, replacements)
        parsed_after = msggame.parse_packed_msggame(candidate)
        if parsed_before.header.prefix != parsed_after.header.prefix:
            raise BuildError(f"wrapper prefix changed: {relative_path}")
        if changed_records(parsed_before.archive, parsed_after.archive) != (coordinate,):
            raise BuildError(f"changed-record vector differs: {relative_path}")

        record_after = record_at(parsed_after.archive, coordinate)
        if literal_texts(record_after) != REPLACEMENT_LITERALS:
            raise BuildError(f"output record literals differ: {relative_path}")
        if opaque_spans(record_after) != OPAQUE_SPANS:
            raise BuildError(f"output opaque spans differ: {relative_path}")
        if len(record_after.data) != FINAL_RECORD_SIZE:
            raise BuildError(f"output record size differs: {relative_path}")
        if sha256(record_after.data) != FINAL_RECORD_SHA256:
            raise BuildError(f"output record hash differs: {relative_path}")

        actual_final = packed_spec(candidate)
        if actual_final != contract["final"]:
            raise BuildError(f"final output pin differs: {relative_path}: {actual_final}")
        outputs[relative_path] = candidate
        final_records.append(record_after.data)
        resource_reports.append(
            {
                "resource": relative_path,
                "coordinate": list(coordinate),
                "input": actual_input,
                "final": actual_final,
                "changed_record_count": 1,
                "opaque_spans_preserved": True,
            }
        )

    if len({record for record in final_records}) != 1:
        raise BuildError("Base and PK output records are not byte-identical")

    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "issue": 109,
        "resources": resource_reports,
        "replacement_literals": list(REPLACEMENT_LITERALS),
        "opaque_spans": list(OPAQUE_SPANS),
        "final_record_size": FINAL_RECORD_SIZE,
        "final_record_sha256": FINAL_RECORD_SHA256,
        "base_pk_final_record_byte_identical": True,
        "jp_source_evidence": JP_SOURCE_EVIDENCE,
        "steam_written": False,
    }
    validation = (
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    output_root.mkdir(parents=True, exist_ok=True)
    for relative_path, candidate in outputs.items():
        output_path = output_root / Path(relative_path)
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
