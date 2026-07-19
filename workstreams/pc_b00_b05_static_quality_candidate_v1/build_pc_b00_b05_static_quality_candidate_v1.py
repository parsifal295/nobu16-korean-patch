#!/usr/bin/env python3
"""Build a private PC-only W45 candidate for the audited B00~B05 term fixes.

The builder reads the exact installed PC W45 Base/PK Korean MSGGAME files and
their pristine PC Japanese counterparts.  It changes only eight proved
``겐푸쿠`` literals to the already-used project term ``원복`` and writes only
under this workstream's private ``tmp`` root.  It has no Steam-apply, Git,
network, transaction, commit, or release operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
CANDIDATE_DIRNAME = "candidate"

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)
AUDITED_BLOCK_IDS = tuple(range(6))

MSGA_FORMAT = MSGGAME_TOOLS / "msggame_format.py"
MSGA_FORMAT_SHA256 = "5F2D8076335822BE49A4F84EC334254527F3766F046165C56B1BFB7E4DAE8458"
LZ4_HELPER = TOOLS / "nobu16_lz4.py"
LZ4_HELPER_SHA256 = "96E7E934355F1B7B1764FAFA1B2809BA7D165E4ADA1DE16EA15C089790E77CFB"

for root in (TOOLS, MSGGAME_TOOLS):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameArchive,
    MsgGameRecord,
    parse_packed_msggame,
    parse_raw_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


SCHEMA = "nobu16.kr.pc-b00-b05-static-quality-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-b00-b05-static-quality-candidate-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-b00-b05-static-quality-candidate-manifest.v1"

# Use escapes so the source stays robust under Windows console encodings.
OLD_TERM = "\uac90\ud478\ucfe0"  # 겐푸쿠
NEW_TERM = "\uc6d0\ubcf5"  # 원복
JP_TERM = "\u5143\u670d"  # 元服

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)


class CandidateError(RuntimeError):
    """Raised when a pinned PC source, target, or private guard drifts."""


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    relative: str
    ko_path: Path
    jp_path: Path
    ko_profile: Profile
    jp_profile: Profile
    output_profile: Profile
    expected_record_count: int
    expected_literal_count: int


@dataclass(frozen=True)
class Target:
    resource: str
    block_id: int
    record_id: int
    literal_id: int
    preimage_utf16le_sha256: str
    target_utf16le_sha256: str
    jp_utf16le_sha256: str

    @property
    def slot(self) -> tuple[int, int, int]:
        return (self.block_id, self.record_id, self.literal_id)

    @property
    def slot_text(self) -> str:
        return f"{self.block_id}:{self.record_id}:{self.literal_id}"


@dataclass(frozen=True)
class LoadedResource:
    spec: ResourceSpec
    packed: bytes
    raw: bytes
    archive: MsgGameArchive
    jp_packed: bytes
    jp_raw: bytes
    jp_archive: MsgGameArchive


@dataclass(frozen=True)
class ResourceCandidate:
    spec: ResourceSpec
    packed: bytes
    raw: bytes
    archive: MsgGameArchive
    changed_records: tuple[tuple[int, int], ...]
    changed_literals: tuple[tuple[int, int, int], ...]
    rows: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class CandidateBundle:
    sources: Mapping[str, LoadedResource]
    resources: Mapping[str, ResourceCandidate]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(profile: Profile) -> dict[str, Any]:
    return {
        "size": profile.size,
        "sha256": profile.sha256,
        "raw_size": profile.raw_size,
        "raw_sha256": profile.raw_sha256,
    }


def observed_profile(packed: bytes, raw: bytes) -> Profile:
    return Profile(len(packed), sha256_bytes(packed), len(raw), sha256_bytes(raw))


def require_profile(packed: bytes, raw: bytes, profile: Profile, label: str) -> None:
    actual = observed_profile(packed, raw)
    require(actual == profile, f"{label} profile differs")


def reject_non_pc_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    require(
        not any(part.casefold() in {"switch", "sc"} or "switch" in part.casefold() for part in resolved.parts),
        f"non-PC path is forbidden: {label}",
    )
    return resolved


def require_private(path: Path, label: str, *, strict: bool = False) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=strict)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise CandidateError(f"{label} escapes private tmp root: {resolved}") from exc
    require(resolved != root, f"{label} must be below private tmp root")
    return resolved


BASE_SPEC = ResourceSpec(
    "base",
    BASE_RESOURCE,
    Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"),
    Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
    Profile(
        1_504_410,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        1_498_508,
        "27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D",
    ),
    Profile(
        610_163,
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        1_337_548,
        "353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38",
    ),
    Profile(
        1_504_402,
        "7A60B8CFB105893569127A707422980AE60CACF5346AEEA46D2744E0F924E971",
        1_498_500,
        "C9A10DBFE98BF902E3C2D7EB940C4922454E6E47A6535C905A78D1634B955C22",
    ),
    5,
    5,
)

PK_SPEC = ResourceSpec(
    "pk",
    PK_RESOURCE,
    Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"),
    Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
        r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin"
    ),
    Profile(
        1_806_538,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        1_799_456,
        "737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E",
    ),
    Profile(
        721_304,
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        1_599_324,
        "F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8",
    ),
    Profile(
        1_806_530,
        "0121A40493D0A963F8685AB625E6922805C3DA56FEF42F49B337BBB584FC8DFF",
        1_799_448,
        "5D43C48E98BDD28CCFFBE883D70C03B1CE00B73D73EF505ECAC6141E523B3540",
    ),
    3,
    3,
)

RESOURCE_SPECS = (BASE_SPEC, PK_SPEC)
SPECS_BY_RESOURCE = {spec.relative: spec for spec in RESOURCE_SPECS}

TARGETS = (
    Target(
        BASE_RESOURCE,
        2,
        88,
        1,
        "8CD61B6645A11DF6F1A74A294319CD7E1BD4DAF9C244CDBAF19F92407D13308C",
        "D315CB8EB5A3A0E0E2EA68E49C46BDCAED61A1992A1182CCC8F16B86CC8D68E9",
        "CE5C9D9525B211B0FAF574A2FE7F3FE724026C6987F2E2F0A25B5C3C73F86218",
    ),
    Target(
        BASE_RESOURCE,
        2,
        89,
        1,
        "8CD61B6645A11DF6F1A74A294319CD7E1BD4DAF9C244CDBAF19F92407D13308C",
        "D315CB8EB5A3A0E0E2EA68E49C46BDCAED61A1992A1182CCC8F16B86CC8D68E9",
        "CE5C9D9525B211B0FAF574A2FE7F3FE724026C6987F2E2F0A25B5C3C73F86218",
    ),
    Target(
        BASE_RESOURCE,
        2,
        93,
        0,
        "C721A27C04B32A3C82EC419727D518F5C8AA2959DCAC4AF7AF0DD19E13A8BD57",
        "21659D1A4789041B6E62E214B96B9F62A605254DDF06EF5AB8DBF6D90F12BB38",
        "DC53D8CDEC8826626463460993325F33663D6835CC502D84BB5EB98BE95E11D9",
    ),
    Target(
        BASE_RESOURCE,
        2,
        105,
        0,
        "51B65C9BFBE23AC16959F78A39FC4D52D807868FDEB81A2F2D8494C420A4E431",
        "DD110D0820F44131C7BA0FE7B48540832FD03322A3C53EC7A4592E2D95143E56",
        "4B8A3DD75DDAF4C3D41A81A3697020498F9C4582DF1930EE3687C9E6B3DBF73B",
    ),
    Target(
        BASE_RESOURCE,
        2,
        106,
        0,
        "E03D8E951D5F32921497FDF2018AFC38CC774BD50D558A8A0EAC115BEC1F50B5",
        "2F13AF7C1AA8E4169937784E8AE6F8741EAB394B59D5A4A90A1B908C528EB3AA",
        "7885188F36B2BE604F219A04AAA8BF3EA91096AAC052023AC7E807127AE410D9",
    ),
    Target(
        PK_RESOURCE,
        2,
        99,
        0,
        "C721A27C04B32A3C82EC419727D518F5C8AA2959DCAC4AF7AF0DD19E13A8BD57",
        "21659D1A4789041B6E62E214B96B9F62A605254DDF06EF5AB8DBF6D90F12BB38",
        "DC53D8CDEC8826626463460993325F33663D6835CC502D84BB5EB98BE95E11D9",
    ),
    Target(
        PK_RESOURCE,
        2,
        111,
        0,
        "51B65C9BFBE23AC16959F78A39FC4D52D807868FDEB81A2F2D8494C420A4E431",
        "DD110D0820F44131C7BA0FE7B48540832FD03322A3C53EC7A4592E2D95143E56",
        "4B8A3DD75DDAF4C3D41A81A3697020498F9C4582DF1930EE3687C9E6B3DBF73B",
    ),
    Target(
        PK_RESOURCE,
        2,
        112,
        0,
        "E03D8E951D5F32921497FDF2018AFC38CC774BD50D558A8A0EAC115BEC1F50B5",
        "2F13AF7C1AA8E4169937784E8AE6F8741EAB394B59D5A4A90A1B908C528EB3AA",
        "7885188F36B2BE604F219A04AAA8BF3EA91096AAC052023AC7E807127AE410D9",
    ),
)


def literal_signature(value: str) -> dict[str, Any]:
    esc: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at {cursor}")
            esc.append(token)
            cursor += 3
            continue
        if character not in ("\r", "\n") and unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        cursor += 1
    printf = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf}
    return {
        "esc": esc,
        "runtime": RUNTIME_RE.findall(value),
        "printf": [match.group(0) for match in printf],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in printf_offsets
        ),
        "controls": controls,
        "manual_lf_count": value.count("\n"),
        "cr_count": value.count("\r"),
    }


def opaque_skeleton(record: MsgGameRecord) -> bytes:
    """Preserve all non-literal bytes and literal marker topology exactly."""
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


def load_archive(path: Path, profile: Profile, label: str) -> tuple[bytes, bytes, MsgGameArchive]:
    resolved = reject_non_pc_path(path, label)
    packed = resolved.read_bytes()
    header, raw = decompress_wrapper(packed)
    require_profile(packed, raw, profile, label)
    archive = parse_raw_msggame(raw)
    require(rebuild_raw_msggame(archive) == raw, f"{label} raw parser round-trip differs")
    require(
        decompress_wrapper(rebuild_packed_msggame(packed))[1] == raw,
        f"{label} packed parser round-trip differs",
    )
    require(header is not None and archive.record_count > 0, f"{label} archive is empty")
    return packed, raw, archive


def assert_topology(ko: MsgGameArchive, jp: MsgGameArchive, label: str) -> None:
    require(
        len(ko.blocks) > max(AUDITED_BLOCK_IDS) and len(jp.blocks) > max(AUDITED_BLOCK_IDS),
        f"{label} lacks audited B00~B05 blocks",
    )
    for block_id in AUDITED_BLOCK_IDS:
        ko_block = ko.blocks[block_id]
        jp_block = jp.blocks[block_id]
        require(ko_block.block_id == jp_block.block_id, f"{label} block ID differs from PC JP")
        require(
            tuple(record.record_id for record in ko_block.records)
            == tuple(record.record_id for record in jp_block.records),
            f"{label} record topology differs from PC JP at block {ko_block.block_id}",
        )
        for ko_record, jp_record in zip(ko_block.records, jp_block.records):
            require(
                len(parse_record_literals(ko_record)) == len(parse_record_literals(jp_record)),
                f"{label} literal topology differs from PC JP at {ko_block.block_id}:{ko_record.record_id}",
            )


def load_sources() -> dict[str, LoadedResource]:
    require(sha256_path(MSGA_FORMAT) == MSGA_FORMAT_SHA256, "MSGGAME parser helper hash differs")
    require(sha256_path(LZ4_HELPER) == LZ4_HELPER_SHA256, "LZ4 helper hash differs")
    result: dict[str, LoadedResource] = {}
    for spec in RESOURCE_SPECS:
        packed, raw, archive = load_archive(spec.ko_path, spec.ko_profile, f"W45 PC Korean {spec.name}")
        jp_packed, jp_raw, jp_archive = load_archive(spec.jp_path, spec.jp_profile, f"pristine PC Japanese {spec.name}")
        assert_topology(archive, jp_archive, spec.name)
        result[spec.relative] = LoadedResource(spec, packed, raw, archive, jp_packed, jp_raw, jp_archive)
    return result


def target_map(resource: str) -> dict[tuple[int, int, int], Target]:
    mapped = {target.slot: target for target in TARGETS if target.resource == resource}
    require(len(mapped) == len([target for target in TARGETS if target.resource == resource]), f"duplicate target {resource}")
    return mapped


def build_resource(source: LoadedResource) -> ResourceCandidate:
    spec = source.spec
    targets = target_map(spec.relative)
    require(len(targets) == spec.expected_literal_count, f"{spec.name} target literal count differs")
    replacements: dict[tuple[int, int, int], str] = {}
    rows: list[dict[str, Any]] = []
    for slot, target in sorted(targets.items()):
        block_id, record_id, literal_id = slot
        require(block_id < len(source.archive.blocks), f"{spec.name} block is outside source")
        ko_record = source.archive.blocks[block_id].records[record_id]
        jp_record = source.jp_archive.blocks[block_id].records[record_id]
        ko_literals = parse_record_literals(ko_record)
        jp_literals = parse_record_literals(jp_record)
        require(literal_id < len(ko_literals) == len(jp_literals), f"{target.slot_text} literal is outside source")
        current = ko_literals[literal_id].text
        jp_text = jp_literals[literal_id].text
        require(text_hash(current) == target.preimage_utf16le_sha256, f"{target.slot_text} W45 preimage differs")
        require(text_hash(jp_text) == target.jp_utf16le_sha256, f"{target.slot_text} PC JP evidence differs")
        require(JP_TERM in jp_text, f"{target.slot_text} no longer contains PC JP 元服 evidence")
        require(current.count(OLD_TERM) == 1, f"{target.slot_text} must contain exactly one 겐푸쿠")
        candidate = current.replace(OLD_TERM, NEW_TERM)
        require(OLD_TERM not in candidate and candidate.count(NEW_TERM) >= 1, f"{target.slot_text} term replacement differs")
        require(text_hash(candidate) == target.target_utf16le_sha256, f"{target.slot_text} target hash differs")
        require(literal_signature(current) == literal_signature(candidate), f"{target.slot_text} changes tag/control/LF signature")
        replacements[slot] = candidate
        rows.append(
            {
                "resource": spec.relative,
                "slot": target.slot_text,
                "current_ko": current,
                "target_ko": candidate,
                "pc_jp": jp_text,
                "current_ko_utf16le_sha256": target.preimage_utf16le_sha256,
                "target_ko_utf16le_sha256": target.target_utf16le_sha256,
                "pc_jp_utf16le_sha256": target.jp_utf16le_sha256,
                "manual_lf_count": current.count("\n"),
                "opaque_skeleton_unchanged": True,
                "rationale": "normalize 元服 terminology to the existing project term 원복",
            }
        )

    candidate_packed = rebuild_packed_with_literals(source.packed, replacements)
    _header, candidate_raw = decompress_wrapper(candidate_packed)
    candidate_archive = parse_raw_msggame(candidate_raw)
    require(rebuild_raw_msggame(candidate_archive) == candidate_raw, f"{spec.name} candidate raw round-trip differs")
    require(
        decompress_wrapper(rebuild_packed_msggame(candidate_packed))[1] == candidate_raw,
        f"{spec.name} candidate packed round-trip differs",
    )
    require_profile(candidate_packed, candidate_raw, spec.output_profile, f"{spec.name} candidate output")

    changed_records: list[tuple[int, int]] = []
    changed_literals: list[tuple[int, int, int]] = []
    require(
        len(source.archive.blocks) == len(candidate_archive.blocks),
        f"{spec.name} candidate whole-file block count differs",
    )
    for before_block, after_block in zip(source.archive.blocks, candidate_archive.blocks):
        require(before_block.block_id == after_block.block_id, f"{spec.name} candidate block alignment differs")
        require(
            len(before_block.records) == len(after_block.records),
            f"{spec.name} candidate whole-file record count differs at block {before_block.block_id}",
        )
        for before, after in zip(before_block.records, after_block.records):
            coordinate = (before.block_id, before.record_id)
            require(before.record_id == after.record_id, f"{spec.name} candidate record alignment differs")
            before_literals = parse_record_literals(before)
            after_literals = parse_record_literals(after)
            require(len(before_literals) == len(after_literals), f"{spec.name} candidate literal topology differs")
            expected_slots = {literal_id for block, record, literal_id in targets if (block, record) == coordinate}
            if before.data != after.data:
                changed_records.append(coordinate)
                require(expected_slots, f"{spec.name} changed an unapproved record {coordinate}")
                require(opaque_skeleton(before) == opaque_skeleton(after), f"{spec.name} changes opaque controls {coordinate}")
            else:
                require(not expected_slots, f"{spec.name} failed to change approved record {coordinate}")
            for before_literal, after_literal in zip(before_literals, after_literals):
                literal_slot = (before.block_id, before.record_id, before_literal.literal_id)
                if before_literal.text != after_literal.text:
                    changed_literals.append(literal_slot)
                    require(literal_slot in targets, f"{spec.name} changed unapproved literal {literal_slot}")
                    require(after_literal.text == replacements[literal_slot], f"{spec.name} target text differs {literal_slot}")
                    require(
                        literal_signature(before_literal.text) == literal_signature(after_literal.text),
                        f"{spec.name} changes tag/control/LF signature {literal_slot}",
                    )
                else:
                    require(literal_slot not in targets, f"{spec.name} failed to change target literal {literal_slot}")

    expected_literals = tuple(sorted(targets))
    expected_records = tuple(sorted({(block, record) for block, record, _literal in targets}))
    require(tuple(changed_literals) == expected_literals, f"{spec.name} changed literal scope differs")
    require(tuple(changed_records) == expected_records, f"{spec.name} changed record scope differs")
    require(len(changed_records) == spec.expected_record_count, f"{spec.name} changed record count differs")
    return ResourceCandidate(
        spec,
        candidate_packed,
        candidate_raw,
        candidate_archive,
        tuple(changed_records),
        tuple(changed_literals),
        tuple(rows),
    )


def prepare_candidate() -> CandidateBundle:
    expected_scope = (
        (BASE_RESOURCE, 2, 88, 1),
        (BASE_RESOURCE, 2, 89, 1),
        (BASE_RESOURCE, 2, 93, 0),
        (BASE_RESOURCE, 2, 105, 0),
        (BASE_RESOURCE, 2, 106, 0),
        (PK_RESOURCE, 2, 99, 0),
        (PK_RESOURCE, 2, 111, 0),
        (PK_RESOURCE, 2, 112, 0),
    )
    observed_scope = tuple((target.resource, *target.slot) for target in TARGETS)
    require(observed_scope == expected_scope, "target scope differs from audited B00~B05 finding")
    sources = load_sources()
    resources = {resource: build_resource(sources[resource]) for resource in RESOURCE_ORDER}
    rows = [row for resource in RESOURCE_ORDER for row in resources[resource].rows]
    changed_literals = [row["slot"] for row in rows]
    changed_records = {
        resource: [f"{block}:{record}" for block, record in resources[resource].changed_records]
        for resource in RESOURCE_ORDER
    }
    outputs = {resource: profile_dict(resources[resource].spec.output_profile) for resource in RESOURCE_ORDER}
    inputs = {resource: profile_dict(sources[resource].spec.ko_profile) for resource in RESOURCE_ORDER}
    jp_evidence = {resource: profile_dict(sources[resource].spec.jp_profile) for resource in RESOURCE_ORDER}
    audit: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "candidate_only": True,
        "source_policy": {
            "platform": "direct PC only",
            "inputs_opened": [
                "installed_w45_base_korean_msggame",
                "installed_w45_pk_korean_msggame",
                "pristine_pc_japanese_base_msggame",
                "pristine_pc_japanese_pk_msggame",
            ],
            "non_pc_sources_opened": False,
            "steam_game_resource_written": False,
            "transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "input": inputs,
        "pc_jp_evidence": jp_evidence,
        "output": outputs,
        "changed_literal_count": len(rows),
        "changed_record_count": sum(len(resources[resource].changed_records) for resource in RESOURCE_ORDER),
        "changed_literal_count_by_resource": {
            resource: len(resources[resource].changed_literals) for resource in RESOURCE_ORDER
        },
        "changed_record_count_by_resource": {
            resource: len(resources[resource].changed_records) for resource in RESOURCE_ORDER
        },
        "changed_literals": changed_literals,
        "changed_records": changed_records,
        "validation": {
            "exact_old_to_new": f"{OLD_TERM} -> {NEW_TERM}",
            "pc_jp_term": JP_TERM,
            "manual_lf_preserved": True,
            "opaque_controls_preserved": True,
            "other_literals_preserved": True,
            "other_records_preserved": True,
        },
        "records": rows,
    }
    manifest: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "input": inputs[resource],
                "output": outputs[resource],
                "changed_literals": [
                    target.slot_text for target in TARGETS if target.resource == resource
                ],
                "changed_records": changed_records[resource],
            }
            for resource in RESOURCE_ORDER
        },
        "changed_literal_count": len(rows),
        "changed_record_count": sum(len(resources[resource].changed_records) for resource in RESOURCE_ORDER),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(sources, resources, audit, manifest)


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def write_candidate(bundle: CandidateBundle, output_root: Path) -> dict[str, Any]:
    output_root = require_private(output_root, "candidate output")
    require(not output_root.exists(), f"refusing to overwrite candidate output: {output_root}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = require_private(Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT)), "candidate staging", strict=True)
    try:
        for resource in RESOURCE_ORDER:
            atomic_write(stage / Path(resource), bundle.resources[resource].packed)
        atomic_write(stage / "audit.v1.json", canonical_json(bundle.audit))
        atomic_write(stage / "candidate_manifest.v1.json", canonical_json(bundle.manifest))
        require(
            sha256_path(stage / "audit.v1.json") == bundle.manifest["audit_sha256"],
            "written audit hash differs",
        )
        os.replace(stage, output_root)
    except Exception:
        if stage.exists():
            require_private(stage, "candidate staging cleanup", strict=True)
            shutil.rmtree(stage)
        raise
    return result_summary(bundle, output_root)


def private_file_set(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def verify_private(candidate_root: Path) -> dict[str, Any]:
    candidate_root = require_private(candidate_root, "candidate root", strict=True)
    bundle = prepare_candidate()
    expected_files = set(RESOURCE_ORDER) | {"audit.v1.json", "candidate_manifest.v1.json"}
    require(private_file_set(candidate_root) == expected_files, "candidate file set differs")
    for resource in RESOURCE_ORDER:
        require(
            (candidate_root / Path(resource)).read_bytes() == bundle.resources[resource].packed,
            f"candidate resource differs: {resource}",
        )
    require((candidate_root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require(
        (candidate_root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "candidate manifest differs",
    )
    return result_summary(bundle, candidate_root)


def diff_check(candidate_root: Path) -> dict[str, Any]:
    candidate_root = require_private(candidate_root, "candidate root", strict=True)
    bundle = prepare_candidate()
    require(candidate_root.is_dir(), "candidate root is absent")
    changed: dict[str, list[str]] = {}
    for resource in RESOURCE_ORDER:
        source = bundle.sources[resource]
        packed = (candidate_root / Path(resource)).read_bytes()
        _header, raw = decompress_wrapper(packed)
        archive = parse_raw_msggame(raw)
        require_profile(packed, raw, source.spec.output_profile, f"diff candidate {resource}")
        literal_changes: list[str] = []
        record_changes: list[str] = []
        for before_block, after_block in zip(source.archive.blocks, archive.blocks):
            for before, after in zip(before_block.records, after_block.records):
                if before.data != after.data:
                    record_changes.append(f"{before.block_id}:{before.record_id}")
                for old, new in zip(parse_record_literals(before), parse_record_literals(after)):
                    if old.text != new.text:
                        literal_changes.append(f"{before.block_id}:{before.record_id}:{old.literal_id}")
        expected = [target.slot_text for target in TARGETS if target.resource == resource]
        require(literal_changes == expected, f"diff literal scope differs: {resource}")
        require(record_changes == bundle.manifest["resources"][resource]["changed_records"], f"diff record scope differs: {resource}")
        changed[resource] = literal_changes
    return {
        "candidate_root": candidate_root.relative_to(REPO).as_posix(),
        "changed_literals": changed,
        "changed_literal_count": sum(len(values) for values in changed.values()),
        "steam_game_resource_written": False,
    }


def result_summary(bundle: CandidateBundle, output_root: Path) -> dict[str, Any]:
    return {
        "candidate_root": output_root.relative_to(REPO).as_posix(),
        "changed_literal_count": bundle.audit["changed_literal_count"],
        "changed_record_count": bundle.audit["changed_record_count"],
        "outputs": bundle.audit["output"],
        "steam_game_resource_written": False,
    }


def profile_report() -> dict[str, Any]:
    bundle = prepare_candidate()
    return {
        "input": bundle.audit["input"],
        "pc_jp_evidence": bundle.audit["pc_jp_evidence"],
        "output": bundle.audit["output"],
        "changed_literals": bundle.audit["changed_literals"],
        "changed_literal_count": bundle.audit["changed_literal_count"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / CANDIDATE_DIRNAME)
    verify_parser = subparsers.add_parser("verify-private")
    verify_parser.add_argument("--candidate-root", type=Path, default=TMP_ROOT / CANDIDATE_DIRNAME)
    diff_parser = subparsers.add_parser("diff-check")
    diff_parser.add_argument("--candidate-root", type=Path, default=TMP_ROOT / CANDIDATE_DIRNAME)
    subparsers.add_parser("profile")
    args = parser.parse_args()
    if args.command == "build":
        result = write_candidate(prepare_candidate(), args.output_root)
    elif args.command == "verify-private":
        result = verify_private(args.candidate_root)
    elif args.command == "diff-check":
        result = diff_check(args.candidate_root)
    else:
        result = profile_report()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
