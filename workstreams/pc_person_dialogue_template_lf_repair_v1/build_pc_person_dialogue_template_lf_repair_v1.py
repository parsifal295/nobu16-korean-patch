#!/usr/bin/env python3
"""Build a candidate-only repair for two joined Korean person-message templates.

Only literal 0 of twenty pinned block-8 records changes: an LF is restored
immediately before the pre-existing ``02 32`` runtime token.  The builder is
deliberately read-only with respect to Steam; it writes two candidate resources
and a manifest below this workstream's ignored ``tmp`` directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
MSGGAME_ROOT = REPO / "workstreams" / "msggame"
sys.path.insert(0, str(MSGGAME_ROOT))

from msggame_format import (  # noqa: E402
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
    structural_summary,
)


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"
DEFAULT_BASE_JP_SOURCE = Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin")
DEFAULT_PK_JP_SOURCE = (
    DEFAULT_STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)

SCHEMA = "nobu16.kr.pc-person-dialogue-template-lf-repair.v1"
BASE_RELATIVE = "MSG/JP/msggame.bin"
PK_RELATIVE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RELATIVE, PK_RELATIVE)
LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"


class TemplateLfRepairError(ValueError):
    """The pinned source, record, or candidate contract differs."""


@dataclass(frozen=True)
class ResourceContract:
    relative: str
    source_sha256: str
    source_raw_sha256: str
    source_raw_size: int
    jp_source_sha256: str
    output_sha256: str
    output_raw_sha256: str
    output_raw_size: int
    harvest_records: tuple[int, ...]
    damage_records: tuple[int, ...]
    harvest_record_sha256: str
    damage_record_sha256: str
    harvest_opaque: tuple[bytes, ...]
    damage_opaque: tuple[bytes, ...]


@dataclass(frozen=True)
class Target:
    relative: str
    block_id: int
    record_id: int
    family: str
    source_record_sha256: str
    expected_opaque: tuple[bytes, ...]

    @property
    def coordinate(self) -> tuple[int, int, int]:
        return self.block_id, self.record_id, 0


FAMILY_KO_LITERALS: dict[str, tuple[str, str, str]] = {
    "harvest": (
        "등의 풍작이 되었다",
        "군에서\n병량 수입이 증가하",
        "\n백성들도 기뻐하며",
    ),
    "damage": (
        "등의 피해가 있었다",
        "군에서\n연공미가 감소",
        "이(가) 논의 쇠퇴를 억제하여\n민심도 그리 저하되지 않을 듯",
    ),
}
FAMILY_JP_LITERALS: dict[str, tuple[str, str, str]] = {
    "harvest": (
        "など豊作となった",
        "郡で\n兵糧収入が増加し",
        "\n民も喜んで",
    ),
    "damage": (
        "など被害があった",
        "郡で\n年貢米が減",
        "が田の衰えは抑えられ\n民忠もさほど低下せずに済みそう",
    ),
}

# Each tuple is every byte outside the UTF-16 literal payloads.  It includes
# the dynamic 0232 token, every 0143 command, and the 050505 terminator.
BASE_HARVEST_OPAQUE = (
    bytes.fromhex("029632"),
    bytes.fromhex("0232"),
    bytes.fromhex("014314020000"),
    bytes.fromhex("0143B2000000050505"),
)
BASE_DAMAGE_OPAQUE = (
    bytes.fromhex("029632"),
    bytes.fromhex("0232"),
    bytes.fromhex("014336040000"),
    bytes.fromhex("01431A020000050505"),
)
PK_HARVEST_OPAQUE = (
    bytes.fromhex("029632"),
    bytes.fromhex("0232"),
    bytes.fromhex("01431A020000"),
    bytes.fromhex("0143B2000000050505"),
)
PK_DAMAGE_OPAQUE = (
    bytes.fromhex("029632"),
    bytes.fromhex("0232"),
    bytes.fromhex("014342040000"),
    bytes.fromhex("014326020000050505"),
)

CONTRACTS: dict[str, ResourceContract] = {
    BASE_RELATIVE: ResourceContract(
        relative=BASE_RELATIVE,
        source_sha256="F7E3705E421556DCF0BBF1F99562762471FA8E7563E5DFDC0F53BDDC0E24E969",
        source_raw_sha256="6B3777F916CBBC1138856B95BC26C21B9B746F7A6C579F47FB7083037FE13ED6",
        source_raw_size=1_498_552,
        jp_source_sha256="EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        output_sha256="4E74E5241485E6DEDD290B81781259010D9D49EA9F76DE7166B090657C535374",
        output_raw_sha256="51A0BE049FAA9A752F237AAA26355F68990EF8251E3373DF9301714C20112501",
        output_raw_size=1_498_572,
        harvest_records=(258, 259, 260, 261, 262),
        damage_records=(268, 269, 270, 271, 272),
        harvest_record_sha256="72ADFC6A0873F0FB1473A8F4C8C6C0099C91F50DA69B8148EA072C1DB7FE507B",
        damage_record_sha256="FCD49906671904A1EDFD04747C67ECB2932DF7C8419F8EE1D248AAA2F3155E10",
        harvest_opaque=BASE_HARVEST_OPAQUE,
        damage_opaque=BASE_DAMAGE_OPAQUE,
    ),
    PK_RELATIVE: ResourceContract(
        relative=PK_RELATIVE,
        source_sha256="06EC887CB3772D765501A5C270E6301344799585BACB47834873580CEB975747",
        source_raw_sha256="ADD199EA6B378F5F408497FBC544FA573118C6A4F08734EF5E165D1338500876",
        source_raw_size=1_799_488,
        jp_source_sha256="31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        output_sha256="A8983770FF9026F018042D94F44AF7D0E67B6A7E01F42891B74386B32078791D",
        output_raw_sha256="A395885A2FC8CCDD1CF26F92D0B9F1C8B4D62EBE8ACE8D3B17B1DCE501C90CE8",
        output_raw_size=1_799_508,
        harvest_records=(264, 265, 266, 267, 268),
        damage_records=(274, 275, 276, 277, 278),
        harvest_record_sha256="BC0B67E788FE32082357F75A859D14AC3A1D1E97C5913D55A495320E305A678C",
        damage_record_sha256="402D304783D8F35BB3FA24F1D08F94CC55FBDA5EAA16D6F194F74584BDAB8F5B",
        harvest_opaque=PK_HARVEST_OPAQUE,
        damage_opaque=PK_DAMAGE_OPAQUE,
    ),
}

# These two values were supplied before this workstream existed, but no binary
# candidate, raw profile, or reproducible recipe remains to verify them.  They
# are intentionally not acceptance pins.
STALE_UNVERIFIABLE_OUTPUT_SHA256 = {
    BASE_RELATIVE: "69F1D52721CCA830EC348C45B3C81249C58E9D5F11B2A33CBFEBA56CDFDED655",
    PK_RELATIVE: "D1AE06647B61BB6034B98E6D1F279B73698AC6E7F25669A622D5BD5D6F2C7373",
}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TemplateLfRepairError(message)


def require_file(path: Path, label: str) -> Path:
    path = path.resolve()
    require(path.is_file(), f"{label} is not a file: {path}")
    return path


def require_under(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise TemplateLfRepairError(f"{label} escapes its allowed root: {path}") from exc
    return path


def target_list() -> tuple[Target, ...]:
    values: list[Target] = []
    for relative in RESOURCE_ORDER:
        contract = CONTRACTS[relative]
        for record_id in contract.harvest_records:
            values.append(
                Target(
                    relative,
                    8,
                    record_id,
                    "harvest",
                    contract.harvest_record_sha256,
                    contract.harvest_opaque,
                )
            )
        for record_id in contract.damage_records:
            values.append(
                Target(
                    relative,
                    8,
                    record_id,
                    "damage",
                    contract.damage_record_sha256,
                    contract.damage_opaque,
                )
            )
    result = tuple(values)
    coordinates = [(target.relative, target.block_id, target.record_id) for target in result]
    require(len(result) == 20, f"expected 20 physical targets, got {len(result)}")
    require(len(coordinates) == len(set(coordinates)), "target coordinates are not unique")
    return result


TARGETS = target_list()


def targets_for(relative: str) -> tuple[Target, ...]:
    return tuple(target for target in TARGETS if target.relative == relative)


def record_at(archive, block_id: int, record_id: int):
    try:
        return archive.blocks[block_id].records[record_id]
    except IndexError as exc:
        raise TemplateLfRepairError(f"missing block {block_id} record {record_id}") from exc


def opaque_spans(record) -> tuple[bytes, ...]:
    """Return exact byte spans that lie outside all literal payloads/markers."""
    cursor = 0
    spans: list[bytes] = []
    for literal in parse_record_literals(record):
        spans.append(record.data[cursor:literal.marker_offset])
        cursor = literal.marker_end
    spans.append(record.data[cursor:])
    return tuple(spans)


def marker_signature(record) -> tuple[tuple[bytes, bytes], ...]:
    return tuple(
        (
            record.data[literal.marker_offset : literal.marker_offset + len(LITERAL_START)],
            record.data[literal.marker_end - len(LITERAL_END) : literal.marker_end],
        )
        for literal in parse_record_literals(record)
    )


def literal_texts(record) -> tuple[str, ...]:
    return tuple(literal.text for literal in parse_record_literals(record))


def assert_literal_structure(record, target: Target, label: str) -> tuple[str, ...]:
    texts = literal_texts(record)
    require(
        texts == FAMILY_KO_LITERALS[target.family],
        f"{label} Korean literal contract differs at {target.relative}@8:{target.record_id}: {texts!r}",
    )
    require(
        tuple(literal.literal_id for literal in parse_record_literals(record)) == (0, 1, 2),
        f"{label} literal marker order differs at {target.relative}@8:{target.record_id}",
    )
    require(
        marker_signature(record) == ((LITERAL_START, LITERAL_END),) * 3,
        f"{label} literal marker bytes differ at {target.relative}@8:{target.record_id}",
    )
    return texts


def assert_jp_control_skeleton(jp_archive, target: Target) -> None:
    record = record_at(jp_archive, target.block_id, target.record_id)
    texts = literal_texts(record)
    require(
        texts == FAMILY_JP_LITERALS[target.family],
        f"Japanese source literals differ at {target.relative}@8:{target.record_id}: {texts!r}",
    )
    require(
        tuple(literal.literal_id for literal in parse_record_literals(record)) == (0, 1, 2),
        f"Japanese source literal marker order differs at {target.relative}@8:{target.record_id}",
    )
    require(
        marker_signature(record) == ((LITERAL_START, LITERAL_END),) * 3,
        f"Japanese source marker bytes differ at {target.relative}@8:{target.record_id}",
    )
    require(
        opaque_spans(record) == target.expected_opaque,
        f"Japanese control skeleton differs at {target.relative}@8:{target.record_id}",
    )


def validate_source_resource(source: bytes, jp_source: bytes, relative: str) -> None:
    contract = CONTRACTS[relative]
    require(sha256(source) == contract.source_sha256, f"current Steam source hash drift: {relative}")
    require(sha256(jp_source) == contract.jp_source_sha256, f"pristine Japanese source hash drift: {relative}")
    archive = parse_packed_msggame(source).archive
    jp_archive = parse_packed_msggame(jp_source).archive
    source_summary = structural_summary(source)
    require(archive.raw_size == contract.source_raw_size, f"current raw size drift: {relative}")
    require(
        source_summary["raw_sha256"] == contract.source_raw_sha256,
        f"current raw hash drift: {relative}",
    )
    for target in targets_for(relative):
        record = record_at(archive, target.block_id, target.record_id)
        require(
            sha256(record.data) == target.source_record_sha256,
            f"target source record hash drift: {relative}@8:{target.record_id}",
        )
        assert_literal_structure(record, target, "source")
        require(
            opaque_spans(record) == target.expected_opaque,
            f"source opaque/control bytes differ at {relative}@8:{target.record_id}",
        )
        assert_jp_control_skeleton(jp_archive, target)
        require(
            opaque_spans(record) == opaque_spans(record_at(jp_archive, 8, target.record_id)),
            f"current/Japanese control skeleton mismatch at {relative}@8:{target.record_id}",
        )


def replacements_for(relative: str) -> dict[tuple[int, int, int], str]:
    return {
        target.coordinate: FAMILY_KO_LITERALS[target.family][0] + "\n"
        for target in targets_for(relative)
    }


def target_key_set(relative: str) -> set[tuple[int, int]]:
    return {(target.block_id, target.record_id) for target in targets_for(relative)}


def validate_candidate_resource(source: bytes, candidate: bytes, jp_source: bytes, relative: str) -> dict[str, object]:
    """Require exact 20-target scope and LZ4-reparse of one candidate file."""
    contract = CONTRACTS[relative]
    validate_source_resource(source, jp_source, relative)
    before = parse_packed_msggame(source).archive
    after = parse_packed_msggame(candidate).archive
    candidate_summary = structural_summary(candidate)
    require(sha256(candidate) == contract.output_sha256, f"candidate packed hash differs: {relative}")
    require(after.raw_size == contract.output_raw_size, f"candidate raw size differs: {relative}")
    require(
        candidate_summary["raw_sha256"] == contract.output_raw_sha256,
        f"candidate raw hash differs: {relative}",
    )
    require(
        after.raw_size - before.raw_size == 20,
        f"candidate raw size must grow by 20 bytes: {relative}",
    )
    require(len(before.blocks) == len(after.blocks), f"candidate block count differs: {relative}")
    targets = {target.record_id: target for target in targets_for(relative)}
    changed_target_count = 0
    untouched_record_count = 0
    for before_block, after_block in zip(before.blocks, after.blocks, strict=True):
        require(
            len(before_block.records) == len(after_block.records),
            f"candidate record count differs: {relative} block {before_block.block_id}",
        )
        for old_record, new_record in zip(before_block.records, after_block.records, strict=True):
            target = targets.get(old_record.record_id) if old_record.block_id == 8 else None
            if target is None:
                require(
                    old_record.data == new_record.data,
                    f"candidate changed non-target record: {relative}@{old_record.block_id}:{old_record.record_id}",
                )
                untouched_record_count += 1
                continue
            changed_target_count += 1
            old_texts = assert_literal_structure(old_record, target, "source")
            new_texts = literal_texts(new_record)
            require(
                new_texts[0] == old_texts[0] + "\n",
                f"candidate literal 0 differs beyond the one LF: {relative}@8:{target.record_id}",
            )
            require(
                new_texts[1:] == old_texts[1:],
                f"candidate changed literal 1 or 2: {relative}@8:{target.record_id}",
            )
            require(
                tuple(literal.literal_id for literal in parse_record_literals(new_record)) == (0, 1, 2),
                f"candidate literal marker order differs: {relative}@8:{target.record_id}",
            )
            require(
                marker_signature(new_record) == marker_signature(old_record),
                f"candidate marker bytes differ: {relative}@8:{target.record_id}",
            )
            require(
                opaque_spans(new_record) == opaque_spans(old_record) == target.expected_opaque,
                f"candidate opaque 02xx/0143/050505 bytes differ: {relative}@8:{target.record_id}",
            )
            jp_record = record_at(parse_packed_msggame(jp_source).archive, 8, target.record_id)
            require(
                opaque_spans(new_record) == opaque_spans(jp_record),
                f"candidate/Japanese control skeleton mismatch: {relative}@8:{target.record_id}",
            )
            require(
                len(new_record.data) == len(old_record.data) + 2,
                f"candidate target record size differs: {relative}@8:{target.record_id}",
            )
    require(
        changed_target_count == 10,
        f"candidate target count differs for {relative}: {changed_target_count}",
    )
    return {
        "path": relative,
        "source_sha256": sha256(source),
        "candidate_sha256": sha256(candidate),
        "source_packed_size": len(source),
        "candidate_packed_size": len(candidate),
        "source_raw_sha256": contract.source_raw_sha256,
        "candidate_raw_sha256": contract.output_raw_sha256,
        "source_raw_size": before.raw_size,
        "candidate_raw_size": after.raw_size,
        "raw_size_delta": after.raw_size - before.raw_size,
        "target_record_count": changed_target_count,
        "untouched_record_count": untouched_record_count,
        "source_japanese_control_skeleton": "PASS",
        "literal_1_2_unchanged": "PASS",
        "opaque_02xx_0143_050505_unchanged": "PASS",
        "marker_count_and_order": "PASS",
        "non_target_record_byte_identity": "PASS",
        "lz4_reparse": "PASS",
    }


def source_paths(steam_root: Path) -> dict[str, Path]:
    return {relative: require_file(steam_root / relative, f"Steam source {relative}") for relative in RESOURCE_ORDER}


def candidate_paths(output_root: Path) -> dict[str, Path]:
    return {relative: output_root / relative for relative in RESOURCE_ORDER}


def files_under(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def verify_candidate(
    steam_root: Path,
    output_root: Path,
    base_jp_source: Path,
    pk_jp_source: Path,
) -> dict[str, object]:
    steam_root = steam_root.resolve(strict=True)
    output_root = output_root.resolve(strict=True)
    expected_files = set(RESOURCE_ORDER)
    require(files_under(output_root) == expected_files, "candidate must contain exactly two msggame files")
    jp_sources = {
        BASE_RELATIVE: require_file(base_jp_source, "Base pristine Japanese source").read_bytes(),
        PK_RELATIVE: require_file(pk_jp_source, "PK pristine Japanese source").read_bytes(),
    }
    entries = []
    for relative in RESOURCE_ORDER:
        source = require_file(steam_root / relative, f"Steam source {relative}").read_bytes()
        candidate = require_file(output_root / relative, f"candidate {relative}").read_bytes()
        entries.append(validate_candidate_resource(source, candidate, jp_sources[relative], relative))
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "candidate_only": True,
        "steam_write": False,
        "target_physical_record_count": len(TARGETS),
        "changed_literal_count": len(TARGETS),
        "scope": "literal 0 only; one LF appended before existing 0232 runtime token",
        "stale_unverifiable_prior_packed_sha256": STALE_UNVERIFIABLE_OUTPUT_SHA256,
        "prior_pin_disposition": "not used: no candidate binary, raw profile, or reproducible recipe",
        "entries": entries,
    }


def build(
    steam_root: Path,
    output_root: Path,
    manifest_path: Path,
    base_jp_source: Path,
    pk_jp_source: Path,
) -> dict[str, object]:
    steam_root = steam_root.resolve(strict=True)
    output_root = output_root.resolve()
    allowed = (REPO / "tmp" / WORKSTREAM.name).resolve()
    require_under(allowed, output_root, "candidate output")
    source = {relative: path.read_bytes() for relative, path in source_paths(steam_root).items()}
    jp_source = {
        BASE_RELATIVE: require_file(base_jp_source, "Base pristine Japanese source").read_bytes(),
        PK_RELATIVE: require_file(pk_jp_source, "PK pristine Japanese source").read_bytes(),
    }
    for relative in RESOURCE_ORDER:
        validate_source_resource(source[relative], jp_source[relative], relative)

    output_root.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="candidate-", dir=output_root.parent))
    try:
        for relative in RESOURCE_ORDER:
            destination = temporary / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            candidate = rebuild_packed_with_literals(source[relative], replacements_for(relative))
            destination.write_bytes(candidate)
        if output_root.exists():
            shutil.rmtree(output_root)
        os.replace(temporary, output_root)
        report = verify_candidate(steam_root, output_root, base_jp_source, pk_jp_source)
        manifest_path = manifest_path.resolve()
        require_under(allowed, manifest_path, "manifest output")
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(canonical_json(report))
        return report
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--base-jp-source", type=Path, default=DEFAULT_BASE_JP_SOURCE)
    parser.add_argument("--pk-jp-source", type=Path, default=DEFAULT_PK_JP_SOURCE)
    parser.add_argument("--verify-only", action="store_true", help="verify an existing candidate only")
    args = parser.parse_args(argv)
    try:
        if args.verify_only:
            report = verify_candidate(
                args.steam_root,
                args.output_root,
                args.base_jp_source,
                args.pk_jp_source,
            )
        else:
            report = build(
                args.steam_root,
                args.output_root,
                args.manifest,
                args.base_jp_source,
                args.pk_jp_source,
            )
    except (OSError, ValueError, TemplateLfRepairError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
