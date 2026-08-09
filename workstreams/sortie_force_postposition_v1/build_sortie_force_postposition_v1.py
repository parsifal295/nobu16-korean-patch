#!/usr/bin/env python3
"""Build the deterministic sortie-dialogue postposition correction."""

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


SCHEMA = "nobu16.kr.sortie-force-postposition-validation.v1"
VALIDATION_NAME = "validation.sortie_force_postposition.v1.json"
OLD_PREFIX = "와의 전투"
NEW_PREFIX = "과의 전투"

RESOURCE_SPECS: dict[str, dict[str, Any]] = {
    "MSG/JP/msggame.bin": {
        "input": {
            "packed_size": 1_557_903,
            "packed_sha256": "9742B5EA5EF34B6C7D9FDFC596A3DFE6C76F6C0A5D4790BE7EFB8246CE7A4A73",
            "raw_size": 1_551_792,
            "raw_sha256": "4BD5DA0BA2B135F3849FF5198C1AFFFAD02A90D9174F07659335830019C9B7BB",
        },
        "final": {
            "packed_size": 1_557_903,
            "packed_sha256": "CF25369C9355C48AACAC31B91C369C179F99FDB31E3BC2FC426062B33A1D2888",
            "raw_size": 1_551_792,
            "raw_sha256": "6740A52A94B94914E19EC9253979CDA7F6812CAB459068D83A8E736683A29F2D",
        },
        "records": {
            (7, 2418): {
                "literal_id": 0,
                "before": "와의 전투에는\n충분한 병력",
                "after": "과의 전투에는\n충분한 병력",
                "before_size": 90,
                "before_sha256": "A268464C3F090039DFF743DF9DB9482AFE212A306FF6F962DE013B09FD3CA47D",
                "after_sha256": "8896F5C524137AE726D6765051FE9C2F732D62E2E3E1F830E88BD6F375053848",
            },
            (7, 2419): {
                "literal_id": 0,
                "before": "와의 전투에는\n충분한 병력",
                "after": "과의 전투에는\n충분한 병력",
                "before_size": 46,
                "before_sha256": "AD3E3502B188641B565F9BA4233F9697BC589BFD28869961ADAA31B985DED0DD",
                "after_sha256": "60B16C67A29E32D232E64ED687DA2A1EC7828413583211069A6DF0BB8E10B7FE",
            },
            (7, 2420): {
                "literal_id": 0,
                "before": "와의 전투에는 병력이 부족",
                "after": "과의 전투에는 병력이 부족",
                "before_size": 146,
                "before_sha256": "116D5A742AA5204DD7A043E3DF1B41AE22B3987B2424BB417C47CBC8DA0E54F3",
                "after_sha256": "AAD3E3472B01025C5F1E471FFD23490599985224F1939838629CE278EB2853B6",
            },
            (7, 2421): {
                "literal_id": 0,
                "before": "와의 전투에는 병력이 부족",
                "after": "과의 전투에는 병력이 부족",
                "before_size": 128,
                "before_sha256": "37FB51219C103FCF29F77410FFD73DA44FBCC4D8989E33C1BE52BA3311EDE222",
                "after_sha256": "E4F85302CF8C68C3D9FB8A9151BA495DDAC9CEF217C0D281B2392FB658A9F825",
            },
            (7, 2422): {
                "literal_id": 0,
                "before": "와의 전투에는 병력이 부족",
                "after": "과의 전투에는 병력이 부족",
                "before_size": 84,
                "before_sha256": "55BDA0A96644FCEC97202B1ED0BE9DB3428053C96BD3BEBF4095B2D15E201FDC",
                "after_sha256": "F45326135C0C107A1362D2255BE7A8400D9B7240111C199BD050441F31241B77",
            },
        },
    },
    "MSG_PK/JP/msggame.bin": {
        "input": {
            "packed_size": 1_815_581,
            "packed_sha256": "5A9993C112DE1E434F977C0134ED3FF1611F73FBDF0C89C41A7A6A7FF97B5069",
            "raw_size": 1_808_464,
            "raw_sha256": "FBCE1F1D6576A72D77778C8D0FA5581A7F6AFF5BFBDB8DF0B394E5B84FFA3BF8",
        },
        "final": {
            "packed_size": 1_815_581,
            "packed_sha256": "8146E02714578B9634405C1F8EBFAB5180A13D90A45B28919E33CAEAAFDD1F87",
            "raw_size": 1_808_464,
            "raw_sha256": "A9B63D2DA0615D653C08E83EA83BCC28273BF65DA110F2EBCE88B702038728B2",
        },
        "records": {
            (7, 2463): {
                "literal_id": 0,
                "before": "와의 전투에는\n병력 충분",
                "after": "과의 전투에는\n병력 충분",
                "before_size": 78,
                "before_sha256": "FB636AB0F5BF681D5CD7A5C5440E7758922CF5A8F89CCEF2DE0E38BB2BF4EF71",
                "after_sha256": "7CEB41C6C5AE844520C8416AE357777D547E729134295F3F0BF8E600496EF34D",
            },
            (7, 2464): {
                "literal_id": 0,
                "before": "와의 전투에는\n충분한 병력",
                "after": "과의 전투에는\n충분한 병력",
                "before_size": 46,
                "before_sha256": "3DBF1871CD2DDCD53E163B3421A7794577941F8977A4875DAFBC8EEC10149BE9",
                "after_sha256": "2BA7B1EB3EA576F6F0510727B69E9DAC77504B0D806B674DED6FA546098310DF",
            },
        },
    },
}


class BuildError(RuntimeError):
    """Raised when an input or output violates the pinned contract."""


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


def record_at(
    archive: msggame.MsgGameArchive, coordinate: tuple[int, int]
) -> msggame.MsgGameRecord:
    block_id, record_id = coordinate
    try:
        record = archive.blocks[block_id].records[record_id]
    except IndexError as exc:
        raise BuildError(f"record coordinate is absent: {block_id}:{record_id}") from exc
    if (record.block_id, record.record_id) != coordinate:
        raise BuildError(f"record coordinate mapping changed: {block_id}:{record_id}")
    return record


def literal_texts(record: msggame.MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in msggame.parse_record_literals(record))


def opaque_spans(record: msggame.MsgGameRecord) -> tuple[bytes, ...]:
    spans: list[bytes] = []
    cursor = 0
    for literal in msggame.parse_record_literals(record):
        spans.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    spans.append(record.data[cursor:])
    return tuple(spans)


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
    for relative_path, contract in RESOURCE_SPECS.items():
        source_path = input_root / Path(relative_path)
        try:
            source = source_path.read_bytes()
        except OSError as exc:
            raise BuildError(f"cannot read pinned input: {source_path}") from exc

        actual_input = packed_spec(source)
        if actual_input != contract["input"]:
            raise BuildError(f"input pin differs: {relative_path}: {actual_input}")

        parsed_before = msggame.parse_packed_msggame(source)
        replacements: dict[tuple[int, int, int], str] = {}
        before_opaque: dict[tuple[int, int], tuple[bytes, ...]] = {}
        for coordinate, record_contract in contract["records"].items():
            record = record_at(parsed_before.archive, coordinate)
            literal_id = record_contract["literal_id"]
            literals = literal_texts(record)
            if len(record.data) != record_contract["before_size"]:
                raise BuildError(f"input record size differs: {relative_path} {coordinate}")
            if sha256(record.data) != record_contract["before_sha256"]:
                raise BuildError(f"input record hash differs: {relative_path} {coordinate}")
            if literals[literal_id] != record_contract["before"]:
                raise BuildError(f"input literal differs: {relative_path} {coordinate}")
            replacements[(coordinate[0], coordinate[1], literal_id)] = record_contract[
                "after"
            ]
            before_opaque[coordinate] = opaque_spans(record)

        candidate = msggame.rebuild_packed_with_literals(source, replacements)
        parsed_after = msggame.parse_packed_msggame(candidate)
        if parsed_before.header.prefix != parsed_after.header.prefix:
            raise BuildError(f"wrapper prefix changed: {relative_path}")
        expected_changed = tuple(contract["records"].keys())
        if changed_records(parsed_before.archive, parsed_after.archive) != expected_changed:
            raise BuildError(f"changed-record vector differs: {relative_path}")

        rows: list[dict[str, Any]] = []
        for coordinate, record_contract in contract["records"].items():
            before_record = record_at(parsed_before.archive, coordinate)
            after_record = record_at(parsed_after.archive, coordinate)
            literal_id = record_contract["literal_id"]
            after_literals = literal_texts(after_record)
            if after_literals[literal_id] != record_contract["after"]:
                raise BuildError(f"output literal differs: {relative_path} {coordinate}")
            if len(after_record.data) != record_contract["before_size"]:
                raise BuildError(f"output record size differs: {relative_path} {coordinate}")
            if sha256(after_record.data) != record_contract["after_sha256"]:
                raise BuildError(f"output record hash differs: {relative_path} {coordinate}")
            if opaque_spans(after_record) != before_opaque[coordinate]:
                raise BuildError(f"opaque spans changed: {relative_path} {coordinate}")
            before_literals = literal_texts(before_record)
            for index, (before_text, after_text) in enumerate(
                zip(before_literals, after_literals, strict=True)
            ):
                if index != literal_id and before_text != after_text:
                    raise BuildError(
                        f"non-target literal changed: {relative_path} {coordinate}:{index}"
                    )
            rows.append(
                {
                    "coordinate": [coordinate[0], coordinate[1], literal_id],
                    "before": record_contract["before"],
                    "after": record_contract["after"],
                    "before_record_sha256": record_contract["before_sha256"],
                    "after_record_sha256": record_contract["after_sha256"],
                    "opaque_spans_preserved": True,
                }
            )

        actual_final = packed_spec(candidate)
        if actual_final != contract["final"]:
            raise BuildError(f"final output pin differs: {relative_path}: {actual_final}")
        outputs[relative_path] = candidate
        resource_reports.append(
            {
                "resource": relative_path,
                "input": actual_input,
                "final": actual_final,
                "changed_record_count": len(rows),
                "rows": rows,
            }
        )

    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "scope": "sortie force/family battle assessment",
        "old_prefix": OLD_PREFIX,
        "new_prefix": NEW_PREFIX,
        "changed_record_count": sum(
            len(contract["records"]) for contract in RESOURCE_SPECS.values()
        ),
        "resources": resource_reports,
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
