"""Build and verify the private PC B15 static-quality candidate v2.

The only permitted output root is this release worktree's tmp directory.
No Steam file, Git file, or external service is touched by this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


WORKSTREAM_DIR = Path(__file__).resolve().parent
RELEASE_ROOT = WORKSTREAM_DIR.parents[1]
PARSER_DIR = RELEASE_ROOT / "workstreams" / "msggame"
if str(PARSER_DIR) not in sys.path:
    sys.path.insert(0, str(PARSER_DIR))

from msggame_format import (  # noqa: E402
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


Coord = tuple[int, int, int]
RecordCoord = tuple[int, int]

PRIVATE_OUTPUT_ROOT = (
    RELEASE_ROOT / "tmp" / "pc_b15_static_quality_candidate_v2" / "candidate"
)
PRIVATE_ROOT_PARENT = (RELEASE_ROOT / "tmp").resolve()


class CandidateVerificationError(RuntimeError):
    """Raised when a pinned preimage or candidate invariant is violated."""


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    source_path: Path
    output_relative_path: Path
    preimage_packed_sha256: str
    preimage_raw_sha256: str
    candidate_packed_sha256: str
    candidate_raw_sha256: str
    wrapper_prefix_hex: str
    packed_bytes: int
    raw_bytes: int
    compressed_size: int
    raw_diff_bytes: int
    replacements: Mapping[Coord, str]
    expected_preimage_literals: Mapping[Coord, str]
    hold_coordinates: tuple[Coord, ...]


BASE_REPLACEMENTS: dict[Coord, str] = {
    (15, 1875, 1): "\n승마 훈련을 실시해\n병사를 강화하고",
    (15, 1890, 1): "\n승마 훈련을 실시해\n병사를 강화하고",
    (15, 1460, 0): "공성이란 성주의 마음을 치는 것\n",
    (15, 2030, 1): "을 허락해 주십시오",
    (15, 2114, 1): "을 허락해 주십시오",
    (15, 2131, 1): "을 허락하시오",
}

PK_REPLACEMENTS: dict[Coord, str] = {
    (15, 1475, 0): "공성이란 성주의 마음을 치는 것\n",
    (15, 2060, 1): "을 허락해 주십시오",
    (15, 2144, 1): "을 허락해 주십시오",
    (15, 2161, 1): "을 허락하시오",
}


SPECS: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        name="Base",
        source_path=Path(
            r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"
        ),
        output_relative_path=Path("MSG") / "JP" / "msggame.bin",
        preimage_packed_sha256=(
            "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB"
        ),
        preimage_raw_sha256=(
            "27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D"
        ),
        candidate_packed_sha256=(
            "F8D6B86536654D0E0FE8C721F8068964C8F908759CC372E5DDBAB4D8489ACB04"
        ),
        candidate_raw_sha256=(
            "F23B2869E9D2526B5C49D809C7489E6B954FC285DBC2E2EBFE91A2E528F5B440"
        ),
        wrapper_prefix_hex="0101F6A1FB7F0000",
        packed_bytes=1_504_410,
        raw_bytes=1_498_508,
        compressed_size=1_504_386,
        raw_diff_bytes=22,
        replacements=BASE_REPLACEMENTS,
        expected_preimage_literals={
            (15, 1875, 1): "\n마술 훈련을 실시해\n병사를 강화하고",
            (15, 1890, 1): "\n마술 훈련을 실시해\n병사를 강화하고",
            (15, 1460, 0): "공성이란 성장의 마음을 치는 것\n",
            (15, 2030, 1): "을 용서해 주십시오",
            (15, 2114, 1): "을 용서해 주십시오",
            (15, 2131, 1): "을 용서하시오",
        },
        hold_coordinates=(
            (15, 1434, 0),
            (15, 1434, 1),
            (15, 2254, 0),
            (15, 2254, 1),
        ),
    ),
    CandidateSpec(
        name="PK",
        source_path=Path(
            r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
        ),
        output_relative_path=Path("MSG_PK") / "JP" / "msggame.bin",
        preimage_packed_sha256=(
            "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092"
        ),
        preimage_raw_sha256=(
            "737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E"
        ),
        candidate_packed_sha256=(
            "712798DA7ACF7182340BC996359F45F324FF4CE41D41699420819406F1E95EBC"
        ),
        candidate_raw_sha256=(
            "03E505277F9CB4D8AE15715742802A4DC6BA782BE410ED7E404E3464D08C6962"
        ),
        wrapper_prefix_hex="0101442672020000",
        packed_bytes=1_806_538,
        raw_bytes=1_799_456,
        compressed_size=1_806_514,
        raw_diff_bytes=14,
        replacements=PK_REPLACEMENTS,
        expected_preimage_literals={
            (15, 1475, 0): "공성이란 성장의 마음을 치는 것\n",
            (15, 2060, 1): "을 용서해 주십시오",
            (15, 2144, 1): "을 용서해 주십시오",
            (15, 2161, 1): "을 용서하시오",
        },
        hold_coordinates=((15, 2285, 0), (15, 2285, 1)),
    ),
)


def sha256_hex(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateVerificationError(message)


def _private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    try:
        resolved.relative_to(PRIVATE_ROOT_PARENT)
    except ValueError as exc:
        raise ValueError(
            f"private candidate output must stay under {PRIVATE_ROOT_PARENT}: {resolved}"
        ) from exc
    return resolved


def _literal_text(archive, coordinate: Coord) -> str:
    block_id, record_id, literal_id = coordinate
    try:
        record = archive.blocks[block_id].records[record_id]
        return parse_record_literals(record)[literal_id].text
    except (IndexError, KeyError) as exc:
        raise CandidateVerificationError(f"missing literal coordinate {coordinate}") from exc


def _record_skeleton(record) -> bytes:
    """Replace literal spans with a sentinel, retaining all opaque bytes."""

    output: list[bytes] = []
    cursor = 0
    for literal in parse_record_literals(record):
        output.append(record.data[cursor : literal.marker_offset])
        output.append(b"<literal>")
        cursor = literal.marker_end
    output.append(record.data[cursor:])
    return b"".join(output)


def _verify_preimage(spec: CandidateSpec, packed: bytes):
    _require(
        sha256_hex(packed) == spec.preimage_packed_sha256,
        f"{spec.name}: unexpected W45 packed preimage hash",
    )
    header, raw = decompress_wrapper(packed)
    _require(
        sha256_hex(raw) == spec.preimage_raw_sha256,
        f"{spec.name}: unexpected W45 raw preimage hash",
    )
    _require(
        header.prefix.hex().upper() == spec.wrapper_prefix_hex,
        f"{spec.name}: unexpected W45 wrapper prefix",
    )
    _require(
        len(packed) == spec.packed_bytes
        and header.uncompressed_size == spec.raw_bytes
        and header.compressed_size == spec.compressed_size
        and len(raw) == spec.raw_bytes,
        f"{spec.name}: unexpected W45 wrapper size profile",
    )
    parsed = parse_packed_msggame(packed)
    _require(
        rebuild_raw_msggame(parsed.archive) == raw,
        f"{spec.name}: W45 preimage parser rebuild mismatch",
    )
    for coordinate, expected in spec.expected_preimage_literals.items():
        _require(
            _literal_text(parsed.archive, coordinate) == expected,
            f"{spec.name}: W45 preimage literal changed at {coordinate}",
        )
    return parsed, header, raw


def _verify_pair(
    spec: CandidateSpec,
    source_packed: bytes,
    candidate_packed: bytes,
) -> dict[str, object]:
    source, source_header, source_raw = _verify_preimage(spec, source_packed)
    _require(
        sha256_hex(candidate_packed) == spec.candidate_packed_sha256,
        f"{spec.name}: candidate packed hash mismatch",
    )

    candidate_header, candidate_raw = decompress_wrapper(candidate_packed)
    _require(
        sha256_hex(candidate_raw) == spec.candidate_raw_sha256,
        f"{spec.name}: candidate raw hash mismatch",
    )
    _require(
        candidate_header.prefix == source_header.prefix,
        f"{spec.name}: candidate wrapper prefix drift",
    )
    _require(
        len(candidate_packed) == spec.packed_bytes
        and candidate_header.uncompressed_size == spec.raw_bytes
        and candidate_header.compressed_size == spec.compressed_size
        and len(candidate_raw) == spec.raw_bytes,
        f"{spec.name}: candidate wrapper size profile drift",
    )

    candidate = parse_packed_msggame(candidate_packed)
    _require(
        rebuild_raw_msggame(candidate.archive) == candidate_raw,
        f"{spec.name}: candidate parser rebuild mismatch",
    )

    target_records: set[RecordCoord] = {
        (block_id, record_id)
        for block_id, record_id, _literal_id in spec.replacements
    }
    changed_records: list[RecordCoord] = []
    changed_literals: list[Coord] = []
    target_raw_intervals: list[tuple[int, int]] = []

    _require(
        len(source.archive.blocks) == len(candidate.archive.blocks),
        f"{spec.name}: block count changed",
    )
    for source_block, candidate_block in zip(
        source.archive.blocks, candidate.archive.blocks
    ):
        _require(
            (
                source_block.block_id,
                source_block.offset,
                source_block.size,
                source_block.gap_after,
                len(source_block.records),
            )
            == (
                candidate_block.block_id,
                candidate_block.offset,
                candidate_block.size,
                candidate_block.gap_after,
                len(candidate_block.records),
            ),
            f"{spec.name}: block topology drift at {source_block.block_id}",
        )
        for source_record, candidate_record in zip(
            source_block.records, candidate_block.records
        ):
            record_coordinate = (source_record.block_id, source_record.record_id)
            _require(
                (
                    source_record.block_id,
                    source_record.record_id,
                    source_record.relative_offset,
                    len(source_record.data),
                )
                == (
                    candidate_record.block_id,
                    candidate_record.record_id,
                    candidate_record.relative_offset,
                    len(candidate_record.data),
                ),
                f"{spec.name}: record topology drift at {record_coordinate}",
            )
            _require(
                _record_skeleton(source_record) == _record_skeleton(candidate_record),
                f"{spec.name}: opaque control drift at {record_coordinate}",
            )
            if source_record.data != candidate_record.data:
                changed_records.append(record_coordinate)
                start = source_block.offset + source_record.relative_offset
                target_raw_intervals.append((start, start + len(source_record.data)))
            elif record_coordinate in target_records:
                raise CandidateVerificationError(
                    f"{spec.name}: approved target record unchanged at {record_coordinate}"
                )

            source_literals = parse_record_literals(source_record)
            candidate_literals = parse_record_literals(candidate_record)
            _require(
                len(source_literals) == len(candidate_literals),
                f"{spec.name}: literal topology drift at {record_coordinate}",
            )
            for source_literal, candidate_literal in zip(
                source_literals, candidate_literals
            ):
                coordinate = (
                    source_literal.block_id,
                    source_literal.record_id,
                    source_literal.literal_id,
                )
                _require(
                    source_literal.text.count("\n") == candidate_literal.text.count("\n"),
                    f"{spec.name}: LF count drift at {coordinate}",
                )
                if coordinate in spec.replacements:
                    _require(
                        source_literal.text
                        == spec.expected_preimage_literals[coordinate],
                        f"{spec.name}: target preimage text drift at {coordinate}",
                    )
                    _require(
                        candidate_literal.text == spec.replacements[coordinate],
                        f"{spec.name}: target candidate text mismatch at {coordinate}",
                    )
                    changed_literals.append(coordinate)
                else:
                    _require(
                        source_literal.text == candidate_literal.text,
                        f"{spec.name}: unapproved literal changed at {coordinate}",
                    )

    _require(
        set(changed_records) == target_records,
        f"{spec.name}: changed record scope mismatch: {changed_records}",
    )
    _require(
        set(changed_literals) == set(spec.replacements),
        f"{spec.name}: changed literal scope mismatch: {changed_literals}",
    )
    for coordinate in spec.hold_coordinates:
        _require(
            _literal_text(source.archive, coordinate)
            == _literal_text(candidate.archive, coordinate),
            f"{spec.name}: Hold literal changed at {coordinate}",
        )

    diff_positions = [
        index
        for index, (before, after) in enumerate(zip(source_raw, candidate_raw))
        if before != after
    ]
    _require(
        len(diff_positions) == spec.raw_diff_bytes,
        f"{spec.name}: raw diff byte count mismatch: {len(diff_positions)}",
    )
    outside_target = [
        index
        for index in diff_positions
        if not any(start <= index < end for start, end in target_raw_intervals)
    ]
    _require(
        not outside_target,
        f"{spec.name}: raw changed outside approved records: {outside_target[:8]}",
    )

    return {
        "candidate_packed_sha256": sha256_hex(candidate_packed),
        "candidate_raw_sha256": sha256_hex(candidate_raw),
        "changed_records": [list(item) for item in sorted(changed_records)],
        "changed_literals": [list(item) for item in sorted(changed_literals)],
        "hold_literals_unchanged": [list(item) for item in spec.hold_coordinates],
        "raw_diff_bytes": len(diff_positions),
        "outside_target_raw_diff_bytes": len(outside_target),
        "profile_prefix_hex": candidate_header.prefix.hex().upper(),
        "parser_rebuild_exact": True,
    }


def build_private_candidate(
    output_root: Path = PRIVATE_OUTPUT_ROOT,
) -> dict[str, dict[str, object]]:
    """Rebuild the pinned candidate under the private tmp output root."""

    output_root = _private_output_root(output_root)
    for spec in SPECS:
        source_packed = spec.source_path.read_bytes()
        _verify_preimage(spec, source_packed)
        candidate_packed = rebuild_packed_with_literals(
            source_packed, spec.replacements
        )
        destination = output_root / spec.output_relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidate_packed)
    return verify_private_candidate(output_root)


def verify_private_candidate(
    output_root: Path = PRIVATE_OUTPUT_ROOT,
) -> dict[str, dict[str, object]]:
    """Verify hashes, profile, literal scope, LF, controls, and raw diff scope."""

    output_root = _private_output_root(output_root)
    reports: dict[str, dict[str, object]] = {}
    for spec in SPECS:
        candidate_path = output_root / spec.output_relative_path
        _require(candidate_path.is_file(), f"{spec.name}: missing {candidate_path}")
        reports[spec.name] = _verify_pair(
            spec,
            spec.source_path.read_bytes(),
            candidate_path.read_bytes(),
        )
    return reports


def diff_check_private_candidate(
    output_root: Path = PRIVATE_OUTPUT_ROOT,
) -> dict[str, dict[str, object]]:
    """Run the whole-archive KO-to-KO diff scope check and return its evidence."""

    reports = verify_private_candidate(output_root)
    return {
        name: {
            "changed_records": report["changed_records"],
            "changed_literals": report["changed_literals"],
            "raw_diff_bytes": report["raw_diff_bytes"],
            "outside_target_raw_diff_bytes": report[
                "outside_target_raw_diff_bytes"
            ],
            "hold_literals_unchanged": report["hold_literals_unchanged"],
        }
        for name, report in reports.items()
    }


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Build or verify the private PC B15 static-quality candidate v2."
    )
    parser.add_argument(
        "command",
        choices=("build", "verify-private", "diff-check"),
        help="private candidate operation",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PRIVATE_OUTPUT_ROOT,
        help="private output root; must be under this worktree's tmp directory",
    )
    args = parser.parse_args()

    if args.command == "build":
        report = build_private_candidate(args.output_root)
    elif args.command == "verify-private":
        report = verify_private_candidate(args.output_root)
    else:
        report = diff_check_private_candidate(args.output_root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
