#!/usr/bin/env python3
"""Build and verify the private PC B07–B10 six-literal quality candidate.

This workstream deliberately reads only the two fixed W45 PC ``msggame`` inputs
and writes only beneath its private ``tmp`` candidate directory.  It never
applies a file to Steam and does not perform Git, network, commit, tag, or
release operations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
PRIVATE_ROOT = REPO_ROOT / "tmp" / "pc_b07_b10_static_quality_candidate_v1"
CANDIDATE_ROOT = PRIVATE_ROOT / "candidate"
README_PATH = WORKSTREAM_ROOT / "README_KO.md"
TEST_PATH = WORKSTREAM_ROOT / "test_pc_b07_b10_static_quality_candidate_v1.py"

sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(MSGGAME_ROOT))

from nobu16_lz4 import WrapperHeader, decompress_wrapper, recompress_wrapper  # noqa: E402
from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameArchive,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_raw_msggame,
    rebuild_raw_with_literals,
    sha256,
)


class CandidateError(ValueError):
    """Raised when the fixed candidate contract is not satisfied."""


@dataclass(frozen=True)
class ByteProfile:
    size: int
    sha256: str


@dataclass(frozen=True)
class LiteralChange:
    block_id: int
    record_id: int
    literal_id: int
    before: str
    before_utf16le_sha256: str
    after: str
    after_utf16le_sha256: str
    rationale: str

    @property
    def coordinate(self) -> tuple[int, int, int]:
        return (self.block_id, self.record_id, self.literal_id)

    @property
    def record_coordinate(self) -> tuple[int, int]:
        return (self.block_id, self.record_id)


@dataclass(frozen=True)
class ResourceSpec:
    key: str
    source_path: Path
    output_relative_path: Path
    source_packed: ByteProfile
    source_raw: ByteProfile
    candidate_packed: ByteProfile
    candidate_raw: ByteProfile
    changes: tuple[LiteralChange, ...]


@dataclass(frozen=True)
class PreparedResource:
    spec: ResourceSpec
    source_packed: bytes
    source_raw: bytes
    source_header: WrapperHeader
    source_archive: MsgGameArchive
    candidate_packed: bytes
    candidate_raw: bytes
    candidate_archive: MsgGameArchive


BASE_CHANGES = (
    LiteralChange(
        9,
        3640,
        0,
        "이것으로 당분간 싸움은 하지 못하리라...",
        "08DCD2DDAA191111089EA952157082D025EBEC0438F87D6469DE71865C114D92",
        "이것으로 당분간 싸움은 하지 못하리라…",
        "80A10359A740BC09B5D0A4E3033C4B57D56B66AB41DB5E5B5DF850B04AD3EB74",
        "말줄임표를 한 글자 표기로 정리",
    ),
    LiteralChange(
        9,
        3776,
        0,
        "강화 사자가 통했군요\n방침을 두고 반목한 것이겠지요",
        "502CEA9756290AC6004B9FF9A9FCD0CAD0DA42BEF6DE7DF3F02ECE6B7F0981EB",
        "강화 사절이 통했군요\n방침을 두고 반목한 것이겠지요",
        "49C6930141FD96950CD1F229F171A5C8FEE3E3FA3D945F2D975C376ABC92C837",
        "사자(使者) 오역을 사절로 정정",
    ),
    LiteralChange(
        9,
        3796,
        0,
        "설마 간파당하다니···",
        "DA2923D02C5C31BAB02BFBB698D5124A7286DE3FB3E4B4D7AAAF6F12FDFF6909",
        "설마 간파당하다니…",
        "12BDA0582865642E1D4E5962D5DF80CFEB2AC0F9444F5B731E6226B9D6AA3CAB",
        "말줄임표를 한 글자 표기로 정리",
    ),
)

PK_CHANGES = (
    LiteralChange(
        9,
        4094,
        0,
        "강화 사자가 통했군요\n방침을 두고 반목한 것이겠지요",
        "502CEA9756290AC6004B9FF9A9FCD0CAD0DA42BEF6DE7DF3F02ECE6B7F0981EB",
        "강화 사절이 통했군요\n방침을 두고 반목한 것이겠지요",
        "49C6930141FD96950CD1F229F171A5C8FEE3E3FA3D945F2D975C376ABC92C837",
        "사자(使者) 오역을 사절로 정정",
    ),
    LiteralChange(
        9,
        4113,
        0,
        "복병이 있었다!혼란한 틈에 쳐부수자!",
        "81C83E910F854320CA5DE5698575DFD560F29FA913F57F31D4D5D5C192947098",
        "복병이 있었다! 혼란한 틈에 쳐부수자!",
        "6EED72FA56D5AA310FD6EC11F7AB3397192EF6A487E27ED5786ACF20995657D7",
        "문장 경계 뒤 공백을 복원",
    ),
    LiteralChange(
        9,
        4114,
        0,
        "설마 간파당하다니···",
        "DA2923D02C5C31BAB02BFBB698D5124A7286DE3FB3E4B4D7AAAF6F12FDFF6909",
        "설마 간파당하다니…",
        "12BDA0582865642E1D4E5962D5DF80CFEB2AC0F9444F5B731E6226B9D6AA3CAB",
        "말줄임표를 한 글자 표기로 정리",
    ),
)

RESOURCES = (
    ResourceSpec(
        key="base",
        source_path=Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"),
        output_relative_path=Path("MSG") / "JP" / "msggame.bin",
        source_packed=ByteProfile(
            1_504_410,
            "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        ),
        source_raw=ByteProfile(
            1_498_508,
            "27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D",
        ),
        candidate_packed=ByteProfile(
            1_504_402,
            "C13090B0D004D54E44872480DE13FA9CF0C0288EAF195B76E7C668F7B198AC74",
        ),
        candidate_raw=ByteProfile(
            1_498_500,
            "F843DA9D2A37F8C857CC5209A4311806019A07B9538B7C3A3283356A6071F292",
        ),
        changes=BASE_CHANGES,
    ),
    ResourceSpec(
        key="pk",
        source_path=Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"),
        output_relative_path=Path("MSG_PK") / "JP" / "msggame.bin",
        source_packed=ByteProfile(
            1_806_538,
            "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        ),
        source_raw=ByteProfile(
            1_799_456,
            "737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E",
        ),
        candidate_packed=ByteProfile(
            1_806_534,
            "618086A21438F61EB31397F94271DBF62EEEEE3D3ADCC0F31D884E17C4E64E8B",
        ),
        candidate_raw=ByteProfile(
            1_799_452,
            "7518C7D55D7382B3B8336F0DC6990576458D348A5C192AB92D9538B090647966",
        ),
        changes=PK_CHANGES,
    ),
)

RUNTIME_TOKEN_PATTERN = re.compile(r"\[[^\]\r\n]*\]|\{[^}\r\n]*\}|<[^>\r\n]*>")


def profile_of(blob: bytes) -> ByteProfile:
    return ByteProfile(len(blob), sha256(blob))


def utf16le_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def profile_dict(profile: ByteProfile) -> dict[str, object]:
    return {"size": profile.size, "sha256": profile.sha256}


def assert_profile(blob: bytes, expected: ByteProfile, label: str) -> None:
    actual = profile_of(blob)
    if actual != expected:
        raise CandidateError(
            f"{label} profile mismatch: expected {expected.size}/{expected.sha256}, "
            f"got {actual.size}/{actual.sha256}"
        )


def require_direct_source(spec: ResourceSpec, path: Path | None = None) -> Path:
    candidate = (path or spec.source_path).resolve()
    if candidate != spec.source_path.resolve():
        raise CandidateError(f"{spec.key}: only its fixed W45 PC input path is permitted")
    return candidate


def require_private_path(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(PRIVATE_ROOT.resolve())
    except ValueError as exc:
        raise CandidateError(f"refusing non-private output path: {resolved}") from exc
    return resolved


def require_candidate_path(path: Path) -> Path:
    resolved = require_private_path(path)
    try:
        resolved.relative_to(CANDIDATE_ROOT.resolve())
    except ValueError as exc:
        raise CandidateError(f"path is not inside the candidate root: {resolved}") from exc
    return resolved


def record_map(archive: MsgGameArchive) -> dict[tuple[int, int], MsgGameRecord]:
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def literal_text_map(archive: MsgGameArchive) -> dict[tuple[int, int, int], str]:
    return {
        (literal.block_id, literal.record_id, literal.literal_id): literal.text
        for block in archive.blocks
        for record in block.records
        for literal in parse_record_literals(record)
    }


def record_opaque_skeleton(record: MsgGameRecord) -> tuple[bytes, ...]:
    """Return every non-text segment, keeping segment boundaries significant."""
    parts: list[bytes] = []
    cursor = 0
    for literal in parse_record_literals(record):
        text_start = literal.marker_offset + len(LITERAL_START)
        text_end = literal.marker_end - len(LITERAL_END)
        parts.append(record.data[cursor:text_start])
        parts.append(record.data[text_end:literal.marker_end])
        cursor = literal.marker_end
    parts.append(record.data[cursor:])
    return tuple(parts)


def line_ending_signature(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\r\n|\r|\n", text))


def control_signature(text: str) -> tuple[int, ...]:
    return tuple(ord(character) for character in text if ord(character) < 0x20)


def runtime_token_signature(text: str) -> tuple[str, ...]:
    return tuple(RUNTIME_TOKEN_PATTERN.findall(text))


def assert_text_invariants(change: LiteralChange) -> None:
    if utf16le_sha256(change.before) != change.before_utf16le_sha256:
        raise CandidateError(f"{change.coordinate}: pinned preimage text hash is invalid")
    if utf16le_sha256(change.after) != change.after_utf16le_sha256:
        raise CandidateError(f"{change.coordinate}: pinned target text hash is invalid")
    if line_ending_signature(change.before) != line_ending_signature(change.after):
        raise CandidateError(f"{change.coordinate}: line-ending sequence would change")
    if control_signature(change.before) != control_signature(change.after):
        raise CandidateError(f"{change.coordinate}: control-code signature would change")
    if runtime_token_signature(change.before) != runtime_token_signature(change.after):
        raise CandidateError(f"{change.coordinate}: runtime-token signature would change")
    if "\r" in change.after:
        raise CandidateError(f"{change.coordinate}: target contains CR; LF-only policy required")


def get_literal(record: MsgGameRecord, literal_id: int):
    literals = parse_record_literals(record)
    if literal_id < 0 or literal_id >= len(literals):
        raise CandidateError(
            f"block {record.block_id}, record {record.record_id}: missing literal {literal_id}"
        )
    return literals[literal_id]


def validate_source_literals(spec: ResourceSpec, archive: MsgGameArchive) -> None:
    coordinates = [change.coordinate for change in spec.changes]
    if len(coordinates) != len(set(coordinates)):
        raise CandidateError(f"{spec.key}: duplicate literal coordinates in recipe")

    records = record_map(archive)
    for change in spec.changes:
        assert_text_invariants(change)
        record = records.get(change.record_coordinate)
        if record is None:
            raise CandidateError(f"{spec.key}: missing record {change.record_coordinate}")
        literal = get_literal(record, change.literal_id)
        if literal.text != change.before:
            raise CandidateError(
                f"{spec.key} {change.coordinate}: source text does not match the pinned preimage"
            )
        if utf16le_sha256(literal.text) != change.before_utf16le_sha256:
            raise CandidateError(f"{spec.key} {change.coordinate}: source UTF-16LE hash mismatch")


def validate_candidate_scope(prepared: PreparedResource) -> None:
    source_records = record_map(prepared.source_archive)
    candidate_records = record_map(prepared.candidate_archive)
    if set(source_records) != set(candidate_records):
        raise CandidateError(f"{prepared.spec.key}: record coordinate set changed")

    expected_record_changes = {change.record_coordinate for change in prepared.spec.changes}
    actual_record_changes = {
        coordinate
        for coordinate, source_record in source_records.items()
        if source_record.data != candidate_records[coordinate].data
    }
    if actual_record_changes != expected_record_changes:
        raise CandidateError(
            f"{prepared.spec.key}: changed records {sorted(actual_record_changes)} do not equal "
            f"the six-literal recipe scope {sorted(expected_record_changes)}"
        )

    source_literals = literal_text_map(prepared.source_archive)
    candidate_literals = literal_text_map(prepared.candidate_archive)
    if set(source_literals) != set(candidate_literals):
        raise CandidateError(f"{prepared.spec.key}: literal coordinate set changed")

    expected_literal_changes = {change.coordinate for change in prepared.spec.changes}
    actual_literal_changes = {
        coordinate
        for coordinate, source_text in source_literals.items()
        if source_text != candidate_literals[coordinate]
    }
    if actual_literal_changes != expected_literal_changes:
        raise CandidateError(
            f"{prepared.spec.key}: changed literals {sorted(actual_literal_changes)} do not equal "
            f"the recipe scope {sorted(expected_literal_changes)}"
        )

    for change in prepared.spec.changes:
        source_record = source_records[change.record_coordinate]
        candidate_record = candidate_records[change.record_coordinate]
        if record_opaque_skeleton(source_record) != record_opaque_skeleton(candidate_record):
            raise CandidateError(f"{prepared.spec.key} {change.coordinate}: opaque record bytes changed")
        source_literal = get_literal(source_record, change.literal_id)
        candidate_literal = get_literal(candidate_record, change.literal_id)
        if source_literal.text != change.before or candidate_literal.text != change.after:
            raise CandidateError(f"{prepared.spec.key} {change.coordinate}: literal text scope mismatch")
        if utf16le_sha256(candidate_literal.text) != change.after_utf16le_sha256:
            raise CandidateError(f"{prepared.spec.key} {change.coordinate}: target UTF-16LE hash mismatch")
        if line_ending_signature(source_literal.text) != line_ending_signature(candidate_literal.text):
            raise CandidateError(f"{prepared.spec.key} {change.coordinate}: LF sequence changed")
        if control_signature(source_literal.text) != control_signature(candidate_literal.text):
            raise CandidateError(f"{prepared.spec.key} {change.coordinate}: control code changed")
        if runtime_token_signature(source_literal.text) != runtime_token_signature(candidate_literal.text):
            raise CandidateError(f"{prepared.spec.key} {change.coordinate}: runtime token changed")


def prepare_resource(spec: ResourceSpec) -> PreparedResource:
    source_path = require_direct_source(spec)
    source_packed = source_path.read_bytes()
    assert_profile(source_packed, spec.source_packed, f"{spec.key} source packed")

    source_header, source_raw = decompress_wrapper(source_packed)
    assert_profile(source_raw, spec.source_raw, f"{spec.key} source raw")
    source_parsed = parse_packed_msggame(source_packed)
    if rebuild_raw_msggame(source_parsed.archive) != source_raw:
        raise CandidateError(f"{spec.key}: source raw parse/rebuild is not byte-exact")
    if recompress_wrapper(source_raw, source_header) != source_packed:
        raise CandidateError(f"{spec.key}: source wrapper recompression is not byte-exact")
    validate_source_literals(spec, source_parsed.archive)

    replacements = {change.coordinate: change.after for change in spec.changes}
    candidate_raw = rebuild_raw_with_literals(source_parsed.archive, replacements)
    assert_profile(candidate_raw, spec.candidate_raw, f"{spec.key} candidate raw")
    candidate_packed = recompress_wrapper(candidate_raw, source_header)
    assert_profile(candidate_packed, spec.candidate_packed, f"{spec.key} candidate packed")

    candidate_header, decoded_candidate_raw = decompress_wrapper(candidate_packed)
    if decoded_candidate_raw != candidate_raw:
        raise CandidateError(f"{spec.key}: candidate wrapper round-trip mismatch")
    if candidate_header.prefix != source_header.prefix:
        raise CandidateError(f"{spec.key}: candidate wrapper prefix changed")
    candidate_parsed = parse_packed_msggame(candidate_packed)
    if rebuild_raw_msggame(candidate_parsed.archive) != candidate_raw:
        raise CandidateError(f"{spec.key}: candidate raw parse/rebuild is not byte-exact")
    if recompress_wrapper(candidate_raw, candidate_header) != candidate_packed:
        raise CandidateError(f"{spec.key}: candidate wrapper recompression is not byte-exact")

    prepared = PreparedResource(
        spec=spec,
        source_packed=source_packed,
        source_raw=source_raw,
        source_header=source_header,
        source_archive=source_parsed.archive,
        candidate_packed=candidate_packed,
        candidate_raw=candidate_raw,
        candidate_archive=candidate_parsed.archive,
    )
    validate_candidate_scope(prepared)
    return prepared


def prepare_all() -> tuple[PreparedResource, ...]:
    return tuple(prepare_resource(spec) for spec in RESOURCES)


def change_dict(change: LiteralChange) -> dict[str, object]:
    return {
        "after": change.after,
        "after_utf16le_sha256": change.after_utf16le_sha256,
        "before": change.before,
        "before_utf16le_sha256": change.before_utf16le_sha256,
        "coordinate": [change.block_id, change.record_id, change.literal_id],
        "line_ending_sequence_preserved": True,
        "opaque_record_skeleton_preserved": True,
        "rationale": change.rationale,
        "runtime_and_control_signature_preserved": True,
    }


def resource_dict(prepared: PreparedResource) -> dict[str, object]:
    spec = prepared.spec
    return {
        "candidate": {
            "packed": profile_dict(spec.candidate_packed),
            "raw": profile_dict(spec.candidate_raw),
            "relative_path": spec.output_relative_path.as_posix(),
        },
        "changed_literal_coordinates": [list(change.coordinate) for change in spec.changes],
        "changed_record_coordinates": [
            list(coordinate) for coordinate in sorted({change.record_coordinate for change in spec.changes})
        ],
        "input": {
            "packed": profile_dict(spec.source_packed),
            "path": str(spec.source_path),
            "raw": profile_dict(spec.source_raw),
        },
        "key": spec.key,
        "literal_changes": [change_dict(change) for change in spec.changes],
    }


def audit_payload(prepared_resources: Sequence[PreparedResource]) -> dict[str, object]:
    return {
        "candidate_only": True,
        "contract": {
            "input_policy": "Fixed W45 PC Base/PK inputs only",
            "output_policy": "Private tmp candidate only",
            "prohibited_operations": [
                "Steam apply",
                "Git operation",
                "network operation",
                "commit",
                "tag",
                "release",
            ],
        },
        "resources": [resource_dict(prepared) for prepared in prepared_resources],
        "schema": "pc-b07-b10-static-quality-audit.v1",
        "scope": {
            "literal_change_count": sum(len(prepared.spec.changes) for prepared in prepared_resources),
            "record_change_count": sum(
                len({change.record_coordinate for change in prepared.spec.changes})
                for prepared in prepared_resources
            ),
            "statement": "This six-literal candidate does not certify a full literary-quality audit.",
        },
        "verification": {
            "candidate_raw_parse_rebuild_byte_exact": True,
            "candidate_wrapper_recompression_byte_exact": True,
            "literal_scope_exact": True,
            "source_raw_parse_rebuild_byte_exact": True,
            "source_wrapper_recompression_byte_exact": True,
        },
    }


def manifest_payload(prepared_resources: Sequence[PreparedResource]) -> dict[str, object]:
    return {
        "candidate_only": True,
        "files": [
            {
                "packed_profile": profile_dict(prepared.spec.candidate_packed),
                "path": prepared.spec.output_relative_path.as_posix(),
                "resource": prepared.spec.key,
            }
            for prepared in prepared_resources
        ],
        "schema": "pc-b07-b10-static-quality-candidate-manifest.v1",
    }


def canonical_json_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def expected_output_files(prepared_resources: Sequence[PreparedResource]) -> set[str]:
    return {
        *(prepared.spec.output_relative_path.as_posix() for prepared in prepared_resources),
        "audit.v1.json",
        "candidate_manifest.v1.json",
    }


def verify_output_tree(root: Path, prepared_resources: Sequence[PreparedResource]) -> None:
    root = require_private_path(root)
    if not root.is_dir():
        raise CandidateError(f"private candidate directory is missing: {root}")
    actual_files = {
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    }
    expected_files = expected_output_files(prepared_resources)
    if actual_files != expected_files:
        raise CandidateError(
            f"private candidate file set mismatch: expected {sorted(expected_files)}, "
            f"got {sorted(actual_files)}"
        )

    for prepared in prepared_resources:
        output_path = root / prepared.spec.output_relative_path
        require_private_path(output_path)
        candidate_packed = output_path.read_bytes()
        if candidate_packed != prepared.candidate_packed:
            raise CandidateError(f"{prepared.spec.key}: private candidate bytes differ from verified build")
        assert_profile(candidate_packed, prepared.spec.candidate_packed, prepared.spec.key)
        candidate_header, candidate_raw = decompress_wrapper(candidate_packed)
        if candidate_raw != prepared.candidate_raw:
            raise CandidateError(f"{prepared.spec.key}: private candidate raw mismatch")
        if recompress_wrapper(candidate_raw, candidate_header) != candidate_packed:
            raise CandidateError(f"{prepared.spec.key}: private candidate wrapper mismatch")
        parsed = parse_packed_msggame(candidate_packed)
        if rebuild_raw_msggame(parsed.archive) != candidate_raw:
            raise CandidateError(f"{prepared.spec.key}: private candidate parse/rebuild mismatch")

    expected_audit = canonical_json_bytes(audit_payload(prepared_resources))
    expected_manifest = canonical_json_bytes(manifest_payload(prepared_resources))
    if (root / "audit.v1.json").read_bytes() != expected_audit:
        raise CandidateError("private audit report differs from the verified payload")
    if (root / "candidate_manifest.v1.json").read_bytes() != expected_manifest:
        raise CandidateError("private candidate manifest differs from the verified payload")


def build_private_candidate() -> Path:
    prepared_resources = prepare_all()
    require_private_path(CANDIDATE_ROOT)
    if CANDIDATE_ROOT.exists():
        raise CandidateError(
            f"private candidate already exists: {CANDIDATE_ROOT}; verify it instead of overwriting it"
        )
    PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
    stage_root = Path(tempfile.mkdtemp(prefix="candidate-staging-", dir=PRIVATE_ROOT))
    require_private_path(stage_root)

    for prepared in prepared_resources:
        output_path = stage_root / prepared.spec.output_relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(prepared.candidate_packed)
    (stage_root / "audit.v1.json").write_bytes(canonical_json_bytes(audit_payload(prepared_resources)))
    (stage_root / "candidate_manifest.v1.json").write_bytes(
        canonical_json_bytes(manifest_payload(prepared_resources))
    )
    verify_output_tree(stage_root, prepared_resources)
    os.replace(stage_root, CANDIDATE_ROOT)
    verify_output_tree(CANDIDATE_ROOT, prepared_resources)
    return CANDIDATE_ROOT


def verify_private_candidate() -> tuple[PreparedResource, ...]:
    prepared_resources = prepare_all()
    require_candidate_path(CANDIDATE_ROOT)
    verify_output_tree(CANDIDATE_ROOT, prepared_resources)
    return prepared_resources


def authoring_whitespace_check() -> None:
    for path in (SCRIPT_PATH, README_PATH, TEST_PATH):
        data = path.read_bytes()
        if b"\r" in data:
            raise CandidateError(f"authoring file has CR byte: {path}")
        for line_number, line in enumerate(data.split(b"\n"), start=1):
            if line.rstrip(b" \t") != line:
                raise CandidateError(f"authoring file has trailing whitespace: {path}:{line_number}")


def profile_payload(prepared_resources: Sequence[PreparedResource]) -> dict[str, object]:
    return {
        "candidate_only": True,
        "resources": [resource_dict(prepared) for prepared in prepared_resources],
        "scope": "six literal changes; not a full literary-quality audit",
    }


def command_profile() -> int:
    print(canonical_json_bytes(profile_payload(prepare_all())).decode("utf-8"), end="")
    return 0


def command_build() -> int:
    output = build_private_candidate()
    print(f"private_candidate={output}")
    print("literal_changes=6")
    print("steam_apply=NOT_PERFORMED")
    return 0


def command_verify_private() -> int:
    prepared_resources = verify_private_candidate()
    print(f"private_candidate={CANDIDATE_ROOT}")
    print(f"literal_changes={sum(len(prepared.spec.changes) for prepared in prepared_resources)}")
    print("verify_private=OK")
    return 0


def command_diff_check() -> int:
    prepared_resources = verify_private_candidate()
    authoring_whitespace_check()
    print(f"private_candidate={CANDIDATE_ROOT}")
    print(f"literal_changes={sum(len(prepared.spec.changes) for prepared in prepared_resources)}")
    print("candidate_file_scope=OK")
    print("authoring_whitespace=OK")
    print("diff_check=OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("profile", help="Verify fixed inputs and print pinned candidate metadata")
    subparsers.add_parser("build", help="Build the private candidate without touching Steam")
    subparsers.add_parser("verify-private", help="Verify the existing private candidate")
    subparsers.add_parser("diff-check", help="Verify private scope and authoring whitespace")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "profile":
            return command_profile()
        if args.command == "build":
            return command_build()
        if args.command == "verify-private":
            return command_verify_private()
        if args.command == "diff-check":
            return command_diff_check()
        raise CandidateError(f"unsupported command: {args.command}")
    except (CandidateError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
