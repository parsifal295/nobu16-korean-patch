"""Build and verify the isolated PC B15 highrisk grammar candidate v1.

Only the two approved B15 grammar literals are rebuilt. Output is confined to
this release worktree's tmp directory; no Steam, Git, or network action occurs.
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
    RELEASE_ROOT / "tmp" / "pc_b15_highrisk_static_candidate_v1" / "candidate"
)
PRIVATE_ROOT_PARENT = (RELEASE_ROOT / "tmp").resolve()
TARGET_BLOCK_ID = 15


class CandidateVerificationError(RuntimeError):
    """Raised when a pinned preimage or candidate invariant is violated."""


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    source_path: Path
    output_relative_path: Path
    coordinate: Coord
    preimage_text: str
    candidate_text: str
    hold_records: tuple[RecordCoord, ...]
    preimage_packed_sha256: str
    preimage_raw_sha256: str
    candidate_packed_sha256: str
    candidate_raw_sha256: str
    wrapper_prefix_hex: str
    preimage_packed_bytes: int
    preimage_raw_bytes: int
    preimage_compressed_size: int
    candidate_packed_bytes: int
    candidate_raw_bytes: int
    candidate_compressed_size: int

    @property
    def target_record(self) -> RecordCoord:
        return self.coordinate[:2]

    @property
    def literal_byte_delta(self) -> int:
        return len(self.candidate_text.encode("utf-16-le")) - len(
            self.preimage_text.encode("utf-16-le")
        )


BASE_SPEC = CandidateSpec(
    name="Base",
    source_path=Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"),
    output_relative_path=Path("MSG") / "JP" / "msggame.bin",
    coordinate=(15, 2348, 0),
    preimage_text="우선 가신들이 건의를 제안할 수 있도록\n공략할 세력을 정하고",
    candidate_text="우선 가신들이 건의할 수 있도록\n공략할 세력을 정하고",
    hold_records=((15, 2257), (15, 2258), (15, 2279)),
    preimage_packed_sha256=(
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB"
    ),
    preimage_raw_sha256=(
        "27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D"
    ),
    candidate_packed_sha256=(
        "B69C95ADC52B7261E409B49E7CE907A10049439C629473E6D6DEF31E59DB0952"
    ),
    candidate_raw_sha256=(
        "35C566AF0E9F24A04E91D0CDBBD5C8057924BE5D40D1A958ACC5E49D0675F818"
    ),
    wrapper_prefix_hex="0101F6A1FB7F0000",
    preimage_packed_bytes=1_504_410,
    preimage_raw_bytes=1_498_508,
    preimage_compressed_size=1_504_386,
    candidate_packed_bytes=1_504_402,
    candidate_raw_bytes=1_498_500,
    candidate_compressed_size=1_504_378,
)

PK_SPEC = CandidateSpec(
    name="PK",
    source_path=Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
    ),
    output_relative_path=Path("MSG_PK") / "JP" / "msggame.bin",
    coordinate=(15, 2379, 0),
    preimage_text="우선 가신들이 건의를 제안할 수 있도록\n공략할 세력을 정하고",
    candidate_text="우선 가신들이 건의할 수 있도록\n공략할 세력을 정하고",
    hold_records=((15, 2257), (15, 2258), (15, 2279)),
    preimage_packed_sha256=(
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092"
    ),
    preimage_raw_sha256=(
        "737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E"
    ),
    candidate_packed_sha256=(
        "D1FFFD772CD35B14113ED18076F572284D2B372234396AC3B9F74ED31FE814F7"
    ),
    candidate_raw_sha256=(
        "5D89EFA87DC51E29F91357B1B95C4D74B1CF7E1406024AC893917DA98EC30CD5"
    ),
    wrapper_prefix_hex="0101442672020000",
    preimage_packed_bytes=1_806_538,
    preimage_raw_bytes=1_799_456,
    preimage_compressed_size=1_806_514,
    candidate_packed_bytes=1_806_530,
    candidate_raw_bytes=1_799_448,
    candidate_compressed_size=1_806_506,
)

SPECS = (BASE_SPEC, PK_SPEC)


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


def _record(archive, coordinate: RecordCoord):
    block_id, record_id = coordinate
    try:
        return archive.blocks[block_id].records[record_id]
    except IndexError as exc:
        raise CandidateVerificationError(f"missing record {coordinate}") from exc


def _literal_text(archive, coordinate: Coord) -> str:
    block_id, record_id, literal_id = coordinate
    try:
        return parse_record_literals(_record(archive, (block_id, record_id)))[
            literal_id
        ].text
    except IndexError as exc:
        raise CandidateVerificationError(f"missing literal {coordinate}") from exc


def _record_literal_texts(archive, coordinate: RecordCoord) -> tuple[str, ...]:
    return tuple(item.text for item in parse_record_literals(_record(archive, coordinate)))


def _record_skeleton(record) -> bytes:
    """Remove literal bodies while retaining all literal markers and opaque bytes."""

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
        len(packed) == spec.preimage_packed_bytes
        and len(raw) == spec.preimage_raw_bytes
        and header.uncompressed_size == spec.preimage_raw_bytes
        and header.compressed_size == spec.preimage_compressed_size,
        f"{spec.name}: unexpected W45 profile",
    )
    parsed = parse_packed_msggame(packed)
    _require(
        rebuild_raw_msggame(parsed.archive) == raw,
        f"{spec.name}: preimage parser rebuild mismatch",
    )
    _require(
        _literal_text(parsed.archive, spec.coordinate) == spec.preimage_text,
        f"{spec.name}: target preimage text drift",
    )
    return parsed, header, raw


def _verify_expected_block_layout(spec: CandidateSpec, source, candidate) -> None:
    """Allow only the expected -8-byte B15 block contraction and downstream shift."""

    _require(
        len(source.archive.blocks) == len(candidate.archive.blocks),
        f"{spec.name}: block count changed",
    )
    delta = spec.literal_byte_delta
    _require(delta == -8, f"{spec.name}: unexpected literal byte delta {delta}")
    for source_block, candidate_block in zip(
        source.archive.blocks, candidate.archive.blocks
    ):
        _require(
            (
                source_block.block_id,
                source_block.gap_after,
                len(source_block.records),
            )
            == (
                candidate_block.block_id,
                candidate_block.gap_after,
                len(candidate_block.records),
            ),
            f"{spec.name}: block identity or record count drift at {source_block.block_id}",
        )
        if source_block.block_id < TARGET_BLOCK_ID:
            expected_offset_delta, expected_size_delta = 0, 0
        elif source_block.block_id == TARGET_BLOCK_ID:
            expected_offset_delta, expected_size_delta = 0, delta
        else:
            expected_offset_delta, expected_size_delta = delta, 0
        _require(
            candidate_block.offset - source_block.offset == expected_offset_delta
            and candidate_block.size - source_block.size == expected_size_delta,
            f"{spec.name}: unexpected block layout drift at {source_block.block_id}",
        )


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
        f"{spec.name}: wrapper prefix drift",
    )
    _require(
        len(candidate_packed) == spec.candidate_packed_bytes
        and len(candidate_raw) == spec.candidate_raw_bytes
        and candidate_header.uncompressed_size == spec.candidate_raw_bytes
        and candidate_header.compressed_size == spec.candidate_compressed_size,
        f"{spec.name}: candidate output profile drift",
    )
    _require(
        len(candidate_packed) - len(source_packed) == spec.literal_byte_delta,
        f"{spec.name}: packed size delta mismatch",
    )
    _require(
        len(candidate_raw) - len(source_raw) == spec.literal_byte_delta,
        f"{spec.name}: raw size delta mismatch",
    )

    candidate = parse_packed_msggame(candidate_packed)
    _require(
        rebuild_raw_msggame(candidate.archive) == candidate_raw,
        f"{spec.name}: candidate parser rebuild mismatch",
    )
    _verify_expected_block_layout(spec, source, candidate)

    changed_records: list[RecordCoord] = []
    changed_literals: list[Coord] = []
    for source_block, candidate_block in zip(
        source.archive.blocks, candidate.archive.blocks
    ):
        for source_record, candidate_record in zip(
            source_block.records, candidate_block.records
        ):
            record_coordinate = (source_record.block_id, source_record.record_id)
            expected_relative_delta = 0
            if (
                source_record.block_id == TARGET_BLOCK_ID
                and source_record.record_id > spec.target_record[1]
            ):
                expected_relative_delta = spec.literal_byte_delta
            _require(
                candidate_record.relative_offset - source_record.relative_offset
                == expected_relative_delta,
                f"{spec.name}: unexpected relative offset drift at {record_coordinate}",
            )

            if source_record.data != candidate_record.data:
                changed_records.append(record_coordinate)
            _require(
                _record_skeleton(source_record) == _record_skeleton(candidate_record),
                f"{spec.name}: opaque control drift at {record_coordinate}",
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
                if coordinate == spec.coordinate:
                    _require(
                        source_literal.text == spec.preimage_text,
                        f"{spec.name}: target preimage text mismatch",
                    )
                    _require(
                        candidate_literal.text == spec.candidate_text,
                        f"{spec.name}: target candidate text mismatch",
                    )
                    changed_literals.append(coordinate)
                else:
                    _require(
                        source_literal.text == candidate_literal.text,
                        f"{spec.name}: unapproved literal changed at {coordinate}",
                    )

    _require(
        changed_records == [spec.target_record],
        f"{spec.name}: changed record scope mismatch: {changed_records}",
    )
    _require(
        changed_literals == [spec.coordinate],
        f"{spec.name}: changed literal scope mismatch: {changed_literals}",
    )
    for hold_record in spec.hold_records:
        _require(
            _record_literal_texts(source.archive, hold_record)
            == _record_literal_texts(candidate.archive, hold_record),
            f"{spec.name}: Hold record changed at {hold_record}",
        )

    return {
        "candidate_packed_sha256": sha256_hex(candidate_packed),
        "candidate_raw_sha256": sha256_hex(candidate_raw),
        "changed_records": [list(item) for item in changed_records],
        "changed_literals": [list(item) for item in changed_literals],
        "hold_records_unchanged": [list(item) for item in spec.hold_records],
        "literal_byte_delta": spec.literal_byte_delta,
        "packed_size_delta": len(candidate_packed) - len(source_packed),
        "raw_size_delta": len(candidate_raw) - len(source_raw),
        "profile_prefix_hex": candidate_header.prefix.hex().upper(),
        "target_opaque_skeleton_preserved": True,
        "parser_rebuild_exact": True,
    }


def build_private_candidate(
    output_root: Path = PRIVATE_OUTPUT_ROOT,
) -> dict[str, dict[str, object]]:
    """Build the two-file private candidate from pinned W45 PC KO inputs."""

    output_root = _private_output_root(output_root)
    for spec in SPECS:
        source_packed = spec.source_path.read_bytes()
        _verify_preimage(spec, source_packed)
        candidate_packed = rebuild_packed_with_literals(
            source_packed, {spec.coordinate: spec.candidate_text}
        )
        destination = output_root / spec.output_relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidate_packed)
    return verify_private_candidate(output_root)


def verify_private_candidate(
    output_root: Path = PRIVATE_OUTPUT_ROOT,
) -> dict[str, dict[str, object]]:
    """Verify the W45 pins, profile, target-only record scope, and Holds."""

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
    """Return target-only opaque record diff evidence for the private candidate."""

    reports = verify_private_candidate(output_root)
    return {
        name: {
            "changed_records": report["changed_records"],
            "changed_literals": report["changed_literals"],
            "hold_records_unchanged": report["hold_records_unchanged"],
            "literal_byte_delta": report["literal_byte_delta"],
            "packed_size_delta": report["packed_size_delta"],
            "raw_size_delta": report["raw_size_delta"],
            "target_opaque_skeleton_preserved": report[
                "target_opaque_skeleton_preserved"
            ],
        }
        for name, report in reports.items()
    }


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Build or verify the private PC B15 highrisk grammar candidate v1."
    )
    parser.add_argument(
        "command",
        choices=("build", "verify-private", "diff-check"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PRIVATE_OUTPUT_ROOT,
        help="private output root; it must remain under this worktree's tmp directory",
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
