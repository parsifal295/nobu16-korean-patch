#!/usr/bin/env python3
"""Build a private PC-only MSGGAME B06 quality candidate.

Only the two high-confidence PK dialogue defects established in the direct-PC
B06 audit are eligible.  The builder reads four pinned PC files, writes only
under its own private ``tmp`` root, and deliberately has no Steam-apply, Git,
network, or release operation.
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
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate"

sys.path.insert(0, str(REPO / "workstreams" / "msggame"))
sys.path.insert(0, str(REPO / "tools"))

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameArchive,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
)
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402


class CandidateError(RuntimeError):
    """Raised when a source, scope, or private-output invariant fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_non_pc_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    require(
        not any("switch" in part.casefold() for part in resolved.parts),
        f"forbidden non-PC path: {label}",
    )
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise CandidateError(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


@dataclass(frozen=True)
class InputSpec:
    label: str
    path: Path
    packed_size: int
    packed_sha256: str
    block_records: int
    block_literals: int


@dataclass(frozen=True)
class Proposal:
    record_id: int
    old: str
    new: str
    pk_jp: str
    base_record_id: int
    base_ko: str
    base_jp: str
    reason: str

    @property
    def slot(self) -> str:
        return f"6:{self.record_id}:0"


STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
INPUTS: Mapping[str, InputSpec] = {
    "base_ko_w45": InputSpec(
        "Base current Steam-PC Korean W45",
        STEAM_ROOT / "MSG" / "JP" / "msggame.bin",
        1_504_410,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        4_659,
        6_635,
    ),
    "base_jp_pc": InputSpec(
        "Base pristine PC Japanese",
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        610_163,
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        4_659,
        6_635,
    ),
    "pk_ko_w45": InputSpec(
        "PK current Steam-PC Korean W45",
        STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        1_806_538,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        4_960,
        7_556,
    ),
    "pk_jp_pc": InputSpec(
        "PK pristine PC Japanese",
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin",
        721_304,
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        4_960,
        7_556,
    ),
}

PK_RESOURCE = "MSG_PK/JP/msggame.bin"
SCHEMA = "nobu16.kr.pc-b06-static-quality-candidate.v1"

# Both replacements retain their existing manual line structure.  The source
# comparison and same-JP Base PC wording are recorded below, but only PK is
# rebuilt.
PROPOSALS: tuple[Proposal, ...] = (
    Proposal(
        3144,
        "전투는 잠시 끝났습니다\n잘 받아들여 주셨습니다",
        "전투는 잠시 끝났습니다\n부디 승복해 주십시오",
        "これにて戦は一旦終わり\nよくよくご承服あれ",
        3137,
        "이것으로 싸움은 일단 끝\n부디 승복하시오",
        "これにて戦は一旦終わり\nよくよくご承服あれ",
        "completed-form mistranslation changed the source request into a completion",
    ),
    Proposal(
        3455,
        "공훈 1위는 기쁘지만,\n이 자리는 아직 제게 과분합니다.\n더욱 노력하겠습니다.",
        "공훈 1위는 기쁘지만,\n이 자리는 아직 제게는 모자랍니다.\n더욱 노력하겠습니다.",
        "勲功一位なのは嬉しいが\n地位はまだまだ役不足よ\n励まねばな",
        3448,
        "훈공 1위는 기쁘다만\n지위는 아직 내 그릇에 못 미치는군\n더 힘써야겠다",
        "勲功一位なのは嬉しいが\n地位はまだまだ役不足よ\n励まねばな",
        "role-is-beneath-ability direction was reversed as 'too much for me'",
    ),
)
EXPECTED_SLOTS = frozenset((6, proposal.record_id, 0) for proposal in PROPOSALS)
EXPECTED_RECORDS = frozenset((6, proposal.record_id) for proposal in PROPOSALS)

# Filled after the read-only derive-pins pass.  build, verification, and tests
# refuse to use an unpinned candidate.
TARGET_OUTPUT_PROFILE: Mapping[str, Any] = {
    "packed_size": 1_806_538,
    "packed_sha256": "A5316297C0E8EE51B8E0DBBCDF62B1B28F93446C729BCF24E922D507146E3F47",
    "raw_size": 1_799_456,
    "raw_sha256": "00AECBD9458BD9B575539B77949328A93569415B2AD630F77CE246DCDF06C5B5",
}


@dataclass(frozen=True)
class CheckedInput:
    packed: bytes
    archive: MsgGameArchive
    profile: Mapping[str, Any]


@dataclass(frozen=True)
class Bundle:
    current: CheckedInput
    candidate_packed: bytes
    candidate_raw: bytes
    candidate_archive: MsgGameArchive
    inputs: Mapping[str, Mapping[str, Any]]
    output_profile: Mapping[str, Any]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def block_literals(archive: MsgGameArchive) -> int:
    return sum(len(parse_record_literals(record)) for record in archive.blocks[6].records)


def checked_input(spec: InputSpec) -> CheckedInput:
    path = reject_non_pc_path(spec.path, spec.label)
    require(path.stat().st_size == spec.packed_size, f"input size drift: {spec.label}")
    require(sha256_path(path) == spec.packed_sha256, f"input hash drift: {spec.label}")
    packed = path.read_bytes()
    parsed = parse_packed_msggame(packed)
    require(len(parsed.archive.blocks) > 6, f"missing B06: {spec.label}")
    require(len(parsed.archive.blocks[6].records) == spec.block_records, f"B06 record drift: {spec.label}")
    require(block_literals(parsed.archive) == spec.block_literals, f"B06 literal drift: {spec.label}")
    header, raw = decompress_wrapper(packed)
    require(rebuild_raw_msggame(parsed.archive) == raw, f"raw parser roundtrip drift: {spec.label}")
    recompressed = recompress_wrapper(raw, header)
    require(decompress_wrapper(recompressed)[1] == raw, f"LZ4 roundtrip drift: {spec.label}")
    profile = {
        "path": str(path),
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "block6_records": len(parsed.archive.blocks[6].records),
        "block6_literals": block_literals(parsed.archive),
    }
    return CheckedInput(packed=packed, archive=parsed.archive, profile=profile)


def texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in parse_record_literals(record))


def text_at(archive: MsgGameArchive, record_id: int, literal_id: int = 0) -> str:
    return texts(archive.blocks[6].records[record_id])[literal_id]


def opaque_skeleton(record: MsgGameRecord) -> bytes:
    """Keep every non-text byte and literal topology unchanged."""
    data = record.data
    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        text_start = literal.marker_offset + len(LITERAL_START)
        output.extend(data[cursor:text_start])
        output.extend(b"<UTF16_LITERAL>")
        output.extend(data[literal.marker_end - len(LITERAL_END) : literal.marker_end])
        cursor = literal.marker_end
    output.extend(data[cursor:])
    return bytes(output)


def output_profile(packed: bytes) -> Mapping[str, Any]:
    header, raw = decompress_wrapper(packed)
    parsed = parse_packed_msggame(packed)
    require(rebuild_raw_msggame(parsed.archive) == raw, "candidate raw parser roundtrip drift")
    recompressed = rebuild_packed_msggame(packed)
    require(decompress_wrapper(recompressed)[1] == raw, "candidate LZ4 roundtrip drift")
    require(header == parse_packed_msggame(packed).header, "candidate wrapper header drift")
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
    }


def build_unpinned() -> Bundle:
    base_ko = checked_input(INPUTS["base_ko_w45"])
    base_jp = checked_input(INPUTS["base_jp_pc"])
    current = checked_input(INPUTS["pk_ko_w45"])
    pk_jp = checked_input(INPUTS["pk_jp_pc"])
    require(
        len(base_ko.archive.blocks[6].records) == len(base_jp.archive.blocks[6].records),
        "Base PC JP/KO B06 record topology differs",
    )
    require(
        len(current.archive.blocks[6].records) == len(pk_jp.archive.blocks[6].records),
        "PK PC JP/KO B06 record topology differs",
    )

    replacements: dict[tuple[int, int, int], str] = {}
    rows: list[Mapping[str, Any]] = []
    for proposal in PROPOSALS:
        slot = (6, proposal.record_id, 0)
        current_text = text_at(current.archive, proposal.record_id)
        require(current_text == proposal.old, f"current literal preimage drift: {proposal.slot}")
        require(sha256_bytes(current_text.encode("utf-16-le")) in {
            "FEAC017F10E0F29896208B152E11F784923E554177D554C4F816F8EEED626225",
            "7B4D464587E7813095794E490E2F3C6643E7C686AE0EFFDAFAEAAB1CCCFC6C02",
        }, f"current literal audit hash drift: {proposal.slot}")
        require(text_at(pk_jp.archive, proposal.record_id) == proposal.pk_jp, f"PK JP reference drift: {proposal.slot}")
        require(
            text_at(base_jp.archive, proposal.base_record_id) == proposal.base_jp,
            f"Base JP reference drift: {proposal.slot}",
        )
        require(
            text_at(base_ko.archive, proposal.base_record_id) == proposal.base_ko,
            f"Base KO reference drift: {proposal.slot}",
        )
        require(proposal.old.count("\n") == proposal.new.count("\n"), f"manual LF count drift: {proposal.slot}")
        replacements[slot] = proposal.new

    require(set(replacements) == EXPECTED_SLOTS, "proposal slot allowlist drift")
    candidate_packed = rebuild_packed_with_literals(current.packed, replacements)
    _header, candidate_raw = decompress_wrapper(candidate_packed)
    candidate_archive = parse_packed_msggame(candidate_packed).archive
    require(rebuild_raw_msggame(candidate_archive) == candidate_raw, "candidate raw rebuild drift")

    changed_records: set[tuple[int, int]] = set()
    for block_id, (before_block, after_block) in enumerate(zip(current.archive.blocks, candidate_archive.blocks)):
        require(len(before_block.records) == len(after_block.records), f"record count drift: block {block_id}")
        for before, after in zip(before_block.records, after_block.records):
            coordinate = (block_id, before.record_id)
            if before.data != after.data:
                changed_records.add(coordinate)
                require(coordinate in EXPECTED_RECORDS, f"out-of-scope record changed: {coordinate}")
            else:
                require(coordinate not in EXPECTED_RECORDS, f"target record did not change: {coordinate}")
    require(changed_records == EXPECTED_RECORDS, "changed-record scope differs from two-record allowlist")

    for proposal in PROPOSALS:
        before = current.archive.blocks[6].records[proposal.record_id]
        after = candidate_archive.blocks[6].records[proposal.record_id]
        before_texts = texts(before)
        after_texts = texts(after)
        require(len(before_texts) == len(after_texts) == 1, f"literal topology drift: {proposal.slot}")
        require(before_texts[0] == proposal.old, f"old target mismatch: {proposal.slot}")
        require(after_texts[0] == proposal.new, f"new target mismatch: {proposal.slot}")
        require(opaque_skeleton(before) == opaque_skeleton(after), f"opaque/control drift: {proposal.slot}")
        rows.append(
            {
                "slot": proposal.slot,
                "reason": proposal.reason,
                "current": proposal.old,
                "target": proposal.new,
                "pk_jp": proposal.pk_jp,
                "base_pc_reference": {
                    "record": f"6:{proposal.base_record_id}:0",
                    "ko": proposal.base_ko,
                    "jp": proposal.base_jp,
                },
                "current_utf16le_sha256": sha256_bytes(proposal.old.encode("utf-16-le")),
                "target_utf16le_sha256": sha256_bytes(proposal.new.encode("utf-16-le")),
                "manual_lf_count": proposal.old.count("\n"),
                "opaque_skeleton_unchanged": True,
            }
        )

    output = output_profile(candidate_packed)
    inputs = {
        "base_ko_w45": base_ko.profile,
        "base_jp_pc": base_jp.profile,
        "pk_ko_w45": current.profile,
        "pk_jp_pc": pk_jp.profile,
    }
    audit = {
        "schema": SCHEMA,
        "source_policy": {
            "platform": "Steam PC only",
            "pc_japanese_reference_only": True,
            "non_pc_paths_read": False,
            "steam_game_resource_written": False,
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "inputs": inputs,
        "output": output,
        "changed_record_count": 2,
        "changed_literal_count": 2,
        "changed_slots": [proposal.slot for proposal in PROPOSALS],
        "manual_lf_policy": "both targets retain their existing manual LF count",
        "opaque_controls_and_placeholders_immutable": True,
        "rows": rows,
    }
    manifest = {
        "schema": SCHEMA,
        "candidate_only": True,
        "candidate_root": CANDIDATE_ROOT.relative_to(REPO).as_posix(),
        "resource": PK_RESOURCE,
        "inputs": inputs,
        "output": output,
        "changed_record_count": 2,
        "changed_literal_count": 2,
        "changed_slots": [proposal.slot for proposal in PROPOSALS],
        "steam_apply": "not implemented",
        "git": "not implemented",
        "network": "not implemented",
        "release": "not implemented",
    }
    return Bundle(
        current=current,
        candidate_packed=candidate_packed,
        candidate_raw=candidate_raw,
        candidate_archive=candidate_archive,
        inputs=inputs,
        output_profile=output,
        audit=audit,
        manifest=manifest,
    )


def output_pins_ready() -> bool:
    return (
        TARGET_OUTPUT_PROFILE["packed_size"] > 0
        and bool(TARGET_OUTPUT_PROFILE["packed_sha256"])
        and TARGET_OUTPUT_PROFILE["raw_size"] > 0
        and bool(TARGET_OUTPUT_PROFILE["raw_sha256"])
    )


def prepare_candidate() -> Bundle:
    require(output_pins_ready(), "target output profile is not pinned; run derive-pins then embed it")
    bundle = build_unpinned()
    require(bundle.output_profile == TARGET_OUTPUT_PROFILE, "candidate output profile differs from pin")
    return bundle


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT, "candidate root")
    require(not output.exists(), "private candidate already exists; do not overwrite it")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        resource = stage / PK_RESOURCE
        resource.parent.mkdir(parents=True, exist_ok=True)
        resource.write_bytes(bundle.candidate_packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> Mapping[str, Any]:
    bundle = prepare_candidate()
    output = require_private(CANDIDATE_ROOT, "candidate root")
    require(output.is_dir(), "private candidate has not been built")
    require((output / PK_RESOURCE).read_bytes() == bundle.candidate_packed, "candidate packed resource drift")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit drift")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest drift")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": 2,
        "changed_literal_count": 2,
        "steam_game_resource_written": False,
    }


def diff_check() -> Mapping[str, Any]:
    bundle = prepare_candidate()
    output = require_private(CANDIDATE_ROOT, "candidate root")
    require(output.is_dir(), "private candidate has not been built")
    candidate = parse_packed_msggame((output / PK_RESOURCE).read_bytes()).archive
    changed: list[tuple[int, int]] = []
    for block_id, (before_block, after_block) in enumerate(zip(bundle.current.archive.blocks, candidate.blocks)):
        for before, after in zip(before_block.records, after_block.records):
            if before.data != after.data:
                changed.append((block_id, before.record_id))
            else:
                require(
                    (block_id, before.record_id) not in EXPECTED_RECORDS,
                    f"target record unchanged in private candidate: {block_id}:{before.record_id}",
                )
    require(frozenset(changed) == EXPECTED_RECORDS, "private candidate changed-record scope drift")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_records": [f"{block}:{record}" for block, record in sorted(changed)],
        "changed_record_count": len(changed),
        "changed_literal_count": 2,
        "opaque_controls_and_placeholders_immutable": True,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("derive-pins", "build", "verify-private", "diff-check"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        bundle = build_unpinned()
        result: Mapping[str, Any] = {"target_output_profile": bundle.output_profile}
    elif args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": 2,
            "changed_literal_count": 2,
            "steam_game_resource_written": False,
        }
    elif args.command == "verify-private":
        result = verify_private()
    else:
        result = diff_check()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
