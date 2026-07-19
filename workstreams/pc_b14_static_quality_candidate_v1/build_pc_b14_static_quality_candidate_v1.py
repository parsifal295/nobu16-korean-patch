#!/usr/bin/env python3
"""Build a private, PC-only candidate for ten pinned B14 literal corrections.

It reads exact W45 PC Base/PK Korean resources and pristine PC Japanese
counterparts. It writes only below this workstream private tmp root.
No Steam apply, transaction, Git, network, commit, push, or release code exists.
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
TOOLS_ROOT = REPO / "tools"
MSGGAME_ROOT = REPO / "workstreams" / "msggame"

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)
AUDITED_BLOCK_ID = 14

MSGA_FORMAT = MSGGAME_ROOT / "msggame_format.py"
MSGA_FORMAT_SHA256 = "5F2D8076335822BE49A4F84EC334254527F3766F046165C56B1BFB7E4DAE8458"
LZ4_HELPER = TOOLS_ROOT / "nobu16_lz4.py"
LZ4_HELPER_SHA256 = "96E7E934355F1B7B1764FAFA1B2809BA7D165E4ADA1DE16EA15C089790E77CFB"

for root in (TOOLS_ROOT, MSGGAME_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameArchive,
    MsgGameRecord,
    parse_raw_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402

AUDIT_SCHEMA = "nobu16.kr.pc-b14-static-quality-candidate-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-b14-static-quality-candidate-manifest.v1"

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)


class CandidateError(RuntimeError):
    """Raised when a pinned input, target, or private-output guard drifts."""


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
    expected_b14_records: int
    expected_b14_literals: int
    expected_changed_records: int


@dataclass(frozen=True)
class Edit:
    old: str
    new: str
    expected_count: int


@dataclass(frozen=True)
class Target:
    resource: str
    block_id: int
    record_id: int
    literal_id: int
    edits: tuple[Edit, ...]
    preimage_utf16le_sha256: str
    target_utf16le_sha256: str
    jp_utf16le_sha256: str
    rationale: str

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
    require(observed_profile(packed, raw) == profile, f"{label} profile differs")


def require_pc_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    bad = {
        part
        for part in resolved.parts
        if part.casefold() == "sc" or "switch" in part.casefold()
    }
    require(not bad, f"non-PC path is forbidden for {label}: {resolved}")
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
    Profile(1_504_410, "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB", 1_498_508, "27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D"),
    Profile(610_163, "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4", 1_337_548, "353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38"),
    Profile(1_504_406, "1026BA0B43F7CFC172F49D2FB48FF9AC4B3B2511087BF0A2791BD82128B62675", 1_498_504, "86D3D55F53365AE0AA6A75C76955CCC4ABE9C2C1B9922DB0202B3314C45AF69D"),
    157,
    639,
    3,
)
PK_SPEC = ResourceSpec(
    "pk",
    PK_RESOURCE,
    Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"),
    Path(r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin"),
    Profile(1_806_538, "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092", 1_799_456, "737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E"),
    Profile(721_304, "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210", 1_599_324, "F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8"),
    Profile(1_806_530, "268E70CC0040A597E561E57972D7C68AD87329AFB3DBE4D36B62CB42BDEF815F", 1_799_448, "129BF95062EEE0251B9A5A04922AAAA20FF275FA99AC2D5B1CA6A4543DF7EA29"),
    247,
    1_043,
    7,
)
RESOURCE_SPECS = (BASE_SPEC, PK_SPEC)


def e(old: str, new: str, count: int = 1) -> Edit:
    return Edit(old, new, count)


TARGETS = (
    Target(BASE_RESOURCE, 14, 32, 3, (e("\u300c\uc870\uc7a5\u300d\uc73c\ub85c\uc11c", "\u300c\uc870\ub450\u300d\ub85c\uc11c"),), "897DEB5562DCD175F4B76262AB0AC9BBD50A19A38FACCFA3A137814E991443AC", "4D7E512018A55B4BCD9CF2918FA609657930E288381761A95449866F8A77EFB8", "C501192CAD2EF109C1EA69B2C9F191BC0DA8691D250408570034D12EDA948ED7", "normalize rank and particle"),
    Target(BASE_RESOURCE, 14, 113, 1, (e("\uc870\uc7a5", "\uc870\ub450"),), "AB6660E2270A8C249715356D8568490EE23B689622171E03CD84D4E3E0B3310D", "1D9E660A9460814B52CCBDA1BB2FAD69EEA119E1FE9F10EEEF788D6C72560961", "EC342DCF7E132CC340E6DA22FC83AABC2FC97CEECDEA7D7AF92551B71046500F", "normalize rank"),
    Target(BASE_RESOURCE, 14, 117, 3, (e("\u300c\uc870\uc7a5\u300d\uc73c\ub85c\uc11c", "\u300c\uc870\ub450\u300d\ub85c\uc11c"),), "22E083A797028E6749E915D20299BFE7C5815C16CC9BB32C804F3DD673BDC608", "40095CE7801C78FCD28C9AFFFFA80EC0A68FC8E903A0A8B3B951BA23791BAFBC", "DCF005D1DF37EE79DB6E5FCDB2CF8AAA8B5BA98767550F47F36CE7FAC0063124", "normalize rank and particle"),
    Target(PK_RESOURCE, 14, 48, 3, (e("\u300c\uc870\uc7a5\u300d\uc73c\ub85c\uc11c", "\u300c\uc870\ub450\u300d\ub85c\uc11c"),), "3B1967016B340C35CDF9E2D77D238E1E11050A4A42230C5743DD2C6B64432765", "5DC4A345DA6C3BFE8AA77CFF3EB61AD58FA5B710A3BB1B5B054A3AA94F65CC34", "C501192CAD2EF109C1EA69B2C9F191BC0DA8691D250408570034D12EDA948ED7", "normalize rank and particle"),
    Target(PK_RESOURCE, 14, 51, 1, (e("\uc870\uc7a5", "\uc870\ub450"),), "9168DC4AEDE2439054A6EDCCC6D979918A3E658D7EC76C2DDC5F29C126DFC160", "343B991A785A7A32DDD3A47F745394149A5F35281AF542325B4F80B4839D8E41", "7C86F310CE2C3E6DF342F4C2932EC1FFA6437B63DA94A0D85D8E0FB7A9419619", "normalize rank"),
    Target(PK_RESOURCE, 14, 156, 1, (e("\uc2dc\ub300\uc7a5", "\uc0ac\ubb34\ub77c\uc774\ub300\uc7a5"),), "75ED2D7217E74C8BA8CC5718F5BC5DA4A337123CA20B069490F1C835AFBBEC0A", "A697231FB54A7E1381E4CE043A60488E6A9391A4FF2340706472676ACB01BFEF", "EC342DCF7E132CC340E6DA22FC83AABC2FC97CEECDEA7D7AF92551B71046500F", "normalize rank"),
    Target(PK_RESOURCE, 14, 157, 1, (e("\uc871\uacbd\ub300\uc7a5", "\uc544\uc2dc\uac00\ub8e8\ub300\uc7a5"),), "D9A750F14EE42B875B16A49AF477C653DDDED672E77E2A40677DF528C77BAD47", "E03C9968386D2CD1F40EB1053BD0A8F2C9400FFFFB04DA576540D8074900F17D", "C5DC1CBFF899F13FEF383472F47991D164CB57837E01DEDF7F1672DB9317C049", "normalize rank"),
    Target(PK_RESOURCE, 14, 225, 1, (e("\uacf5\ud6c8\uc744 \uc5bb\uace0 ", ""),), "828D586B3CC0DADB3E87B07BB43CAD02A87AAFCBCFF52D289BCC45D650C8A05B", "77A652965A500BDD6AB1FF04EDA0C33A4F0FD15FC0A25151134D4B683103D62D", "0FD210925E966503EE3CD0D322084597734988AA2D06B58E94DE8251E712EA4E", "remove Korean-only effect"),
    Target(PK_RESOURCE, 14, 226, 1, (e("\ubcc4\uba85\uc744", "\ubcc4\ud638\ub97c", 3), e("\ubcc4\uba85\uc740", "\ubcc4\ud638\ub294"), e("\ubcc4\uba85\uc774", "\ubcc4\ud638\uac00"), e("\ubcc4\uba85\uc5d0", "\ubcc4\ud638\uc5d0"), e("\ubcc4\uba85\uacfc", "\ubcc4\ud638\uc640")), "70FA14C9507DDEA11510AA430A73582B7B8FA1E9845720669AB4C8C120FC5A05", "224E7BCF03F5D577B3A1C3A46C5BE3CA55FF78F7A34AD8DD09BEFA49C2FC274A", "1A96CE0A8B0091933F2A4A6F1302D18E5C273588E7F49E80324E6187B704D16C", "normalize epithet and particles"),
    Target(PK_RESOURCE, 14, 227, 1, (e("\uc774\uba85\uc744", "\ubcc4\ud638\ub97c", 2), e("\uc774\uba85 \ud6a8\uacfc", "\ubcc4\ud638 \ud6a8\uacfc")), "57A360EAF129DF713272947274C661689EEF38F456BA5E6AD616E1DAC8EF3E69", "D3D6A1FE43B06A7A89FE9CE6DF4FAD89FC8962CC7CB2E2FC91BD038FB5B004D3", "D784285B287CADF322DE8DF4C1E5431BB338EC543439F551032C2E2B942B1869", "normalize epithet and particles"),
)

EXCLUDED_SLOTS = (
    (PK_RESOURCE, 14, 69, 0),
    (PK_RESOURCE, 14, 163, 1),
    (PK_RESOURCE, 14, 140, 3),
)


def literal_signature(value: str) -> dict[str, Any]:
    esc: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        char = value[cursor]
        if char == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at {cursor}")
            esc.append(token)
            cursor += 3
            continue
        if char not in ("\r", "\n") and unicodedata.category(char) == "Cc":
            controls.append(f"U+{ord(char):04X}")
        cursor += 1
    printf = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf}
    return {
        "esc": esc,
        "runtime": RUNTIME_RE.findall(value),
        "printf": [match.group(0) for match in printf],
        "unknown_percent_count": sum(
            1 for offset, char in enumerate(value) if char == "%" and offset not in printf_offsets
        ),
        "controls": controls,
        "manual_lf_count": value.count("\n"),
        "cr_count": value.count("\r"),
    }


def opaque_skeleton(record: MsgGameRecord) -> bytes:
    data = record.data
    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        output.extend(data[cursor : literal.marker_offset + len(LITERAL_START)])
        output.extend(b"<UTF16_LITERAL>")
        output.extend(data[literal.marker_end - len(LITERAL_END) : literal.marker_end])
        cursor = literal.marker_end
    output.extend(data[cursor:])
    return bytes(output)


def load_archive(path: Path, profile: Profile, label: str) -> tuple[bytes, bytes, MsgGameArchive]:
    packed = require_pc_path(path, label).read_bytes()
    _header, raw = decompress_wrapper(packed)
    require_profile(packed, raw, profile, label)
    archive = parse_raw_msggame(raw)
    require(rebuild_raw_msggame(archive) == raw, f"{label} raw parser round-trip differs")
    require(decompress_wrapper(rebuild_packed_msggame(packed))[1] == raw, f"{label} packed parser round-trip differs")
    return packed, raw, archive


def assert_b14_topology(ko: MsgGameArchive, jp: MsgGameArchive, spec: ResourceSpec) -> None:
    require(len(ko.blocks) > AUDITED_BLOCK_ID and len(jp.blocks) > AUDITED_BLOCK_ID, f"{spec.name} lacks B14")
    ko_block, jp_block = ko.blocks[AUDITED_BLOCK_ID], jp.blocks[AUDITED_BLOCK_ID]
    require(len(ko_block.records) == len(jp_block.records) == spec.expected_b14_records, f"{spec.name} B14 record count differs")
    literal_count = 0
    for ko_record, jp_record in zip(ko_block.records, jp_block.records):
        require(ko_record.record_id == jp_record.record_id, f"{spec.name} record topology differs")
        ko_literals, jp_literals = parse_record_literals(ko_record), parse_record_literals(jp_record)
        require(len(ko_literals) == len(jp_literals), f"{spec.name} literal topology differs")
        require(opaque_skeleton(ko_record) == opaque_skeleton(jp_record), f"{spec.name} control skeleton differs")
        for ko_literal, jp_literal in zip(ko_literals, jp_literals):
            require(ko_literal.text.count("\n") == jp_literal.text.count("\n"), f"{spec.name} manual LF differs")
        literal_count += len(ko_literals)
    require(literal_count == spec.expected_b14_literals, f"{spec.name} B14 literal count differs")


def load_sources() -> dict[str, LoadedResource]:
    require(sha256_path(MSGA_FORMAT) == MSGA_FORMAT_SHA256, "MSGGAME parser helper hash differs")
    require(sha256_path(LZ4_HELPER) == LZ4_HELPER_SHA256, "LZ4 helper hash differs")
    loaded: dict[str, LoadedResource] = {}
    for spec in RESOURCE_SPECS:
        packed, raw, archive = load_archive(spec.ko_path, spec.ko_profile, f"W45 PC Korean {spec.name}")
        jp_packed, jp_raw, jp_archive = load_archive(spec.jp_path, spec.jp_profile, f"pristine PC Japanese {spec.name}")
        assert_b14_topology(archive, jp_archive, spec)
        loaded[spec.relative] = LoadedResource(spec, packed, raw, archive, jp_packed, jp_raw, jp_archive)
    return loaded


def target_map(resource: str) -> dict[tuple[int, int, int], Target]:
    mapped = {target.slot: target for target in TARGETS if target.resource == resource}
    require(len(mapped) == len([target for target in TARGETS if target.resource == resource]), f"duplicate target in {resource}")
    return mapped


def record_at(archive: MsgGameArchive, block_id: int, record_id: int, label: str) -> MsgGameRecord:
    require(block_id < len(archive.blocks), f"{label} block is outside source")
    block = archive.blocks[block_id]
    require(record_id < len(block.records), f"{label} record is outside source")
    record = block.records[record_id]
    require(record.record_id == record_id, f"{label} record topology differs")
    return record


def apply_edits(current: str, edits: tuple[Edit, ...], label: str) -> str:
    candidate = current
    for edit in edits:
        require(candidate.count(edit.old) == edit.expected_count, f"{label} fragment preimage differs")
        candidate = candidate.replace(edit.old, edit.new)
    require(candidate != current, f"{label} did not change")
    return candidate


def validate_scope(source: LoadedResource, candidate: MsgGameArchive, replacements: Mapping[tuple[int, int, int], str]) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int, int], ...]]:
    targets = target_map(source.spec.relative)
    changed_records: list[tuple[int, int]] = []
    changed_literals: list[tuple[int, int, int]] = []
    require(len(source.archive.blocks) == len(candidate.blocks), f"{source.spec.name} block count differs")
    for before_block, after_block in zip(source.archive.blocks, candidate.blocks):
        require(before_block.block_id == after_block.block_id, f"{source.spec.name} block alignment differs")
        require(len(before_block.records) == len(after_block.records), f"{source.spec.name} record count differs")
        for before, after in zip(before_block.records, after_block.records):
            coordinate = (before.block_id, before.record_id)
            old_literals, new_literals = parse_record_literals(before), parse_record_literals(after)
            require(len(old_literals) == len(new_literals), f"{source.spec.name} literal topology differs")
            allowed = {literal for block, record, literal in targets if (block, record) == coordinate}
            if before.data != after.data:
                changed_records.append(coordinate)
                require(allowed, f"{source.spec.name} changed unapproved record {coordinate}")
                require(opaque_skeleton(before) == opaque_skeleton(after), f"{source.spec.name} changed opaque bytecode")
            else:
                require(not allowed, f"{source.spec.name} did not change approved record {coordinate}")
            for old, new in zip(old_literals, new_literals):
                slot = (before.block_id, before.record_id, old.literal_id)
                if old.text != new.text:
                    changed_literals.append(slot)
                    require(slot in targets, f"{source.spec.name} changed unapproved literal {slot}")
                    require(new.text == replacements[slot], f"{source.spec.name} target differs at {slot}")
                    require(literal_signature(old.text) == literal_signature(new.text), f"{source.spec.name} changed LF/control signature")
                else:
                    require(slot not in targets, f"{source.spec.name} failed to change target {slot}")
    expected_literals = tuple(sorted(targets))
    expected_records = tuple(sorted({(block, record) for block, record, _ in targets}))
    require(tuple(changed_literals) == expected_literals, f"{source.spec.name} literal scope differs")
    require(tuple(changed_records) == expected_records, f"{source.spec.name} record scope differs")
    require(len(changed_records) == source.spec.expected_changed_records, f"{source.spec.name} changed record count differs")
    return tuple(changed_records), tuple(changed_literals)


def build_resource(source: LoadedResource) -> ResourceCandidate:
    replacements: dict[tuple[int, int, int], str] = {}
    rows: list[dict[str, Any]] = []
    for slot, target in sorted(target_map(source.spec.relative).items()):
        block_id, record_id, literal_id = slot
        ko_literals = parse_record_literals(record_at(source.archive, block_id, record_id, target.slot_text))
        jp_literals = parse_record_literals(record_at(source.jp_archive, block_id, record_id, target.slot_text))
        require(literal_id < len(ko_literals) == len(jp_literals), f"{target.slot_text} literal is outside source")
        current, jp_text = ko_literals[literal_id].text, jp_literals[literal_id].text
        require(text_hash(current) == target.preimage_utf16le_sha256, f"{target.slot_text} exact W45 KO preimage differs")
        require(text_hash(jp_text) == target.jp_utf16le_sha256, f"{target.slot_text} pristine PC JP evidence differs")
        target_text = apply_edits(current, target.edits, target.slot_text)
        require(text_hash(target_text) == target.target_utf16le_sha256, f"{target.slot_text} target hash differs")
        require(literal_signature(current) == literal_signature(target_text), f"{target.slot_text} changes control signature")
        replacements[slot] = target_text
        rows.append({
            "resource": source.spec.relative,
            "slot": target.slot_text,
            "current_ko": current,
            "target_ko": target_text,
            "pc_jp": jp_text,
            "edits": [{"from": edit.old, "to": edit.new, "count": edit.expected_count} for edit in target.edits],
            "current_ko_utf16le_sha256": target.preimage_utf16le_sha256,
            "target_ko_utf16le_sha256": target.target_utf16le_sha256,
            "pc_jp_utf16le_sha256": target.jp_utf16le_sha256,
            "manual_lf_count": current.count("\n"),
            "opaque_skeleton_unchanged": True,
            "rationale": target.rationale,
        })
    packed = rebuild_packed_with_literals(source.packed, replacements)
    _header, raw = decompress_wrapper(packed)
    archive = parse_raw_msggame(raw)
    require(rebuild_raw_msggame(archive) == raw, f"{source.spec.name} candidate raw round-trip differs")
    require(decompress_wrapper(rebuild_packed_msggame(packed))[1] == raw, f"{source.spec.name} candidate packed round-trip differs")
    require_profile(packed, raw, source.spec.output_profile, f"{source.spec.name} candidate")
    changed_records, changed_literals = validate_scope(source, archive, replacements)
    return ResourceCandidate(source.spec, packed, raw, archive, changed_records, changed_literals, tuple(rows))


def prepare_candidate() -> CandidateBundle:
    expected_scope = (
        (BASE_RESOURCE, 14, 32, 3), (BASE_RESOURCE, 14, 113, 1), (BASE_RESOURCE, 14, 117, 3),
        (PK_RESOURCE, 14, 48, 3), (PK_RESOURCE, 14, 51, 1), (PK_RESOURCE, 14, 156, 1),
        (PK_RESOURCE, 14, 157, 1), (PK_RESOURCE, 14, 225, 1), (PK_RESOURCE, 14, 226, 1),
        (PK_RESOURCE, 14, 227, 1),
    )
    observed_scope = tuple((target.resource, *target.slot) for target in TARGETS)
    require(observed_scope == expected_scope, "target scope differs from approved B14 scope")
    require(not set(expected_scope) & set(EXCLUDED_SLOTS), "approved target overlaps excluded B14 slot")
    sources = load_sources()
    resources = {resource: build_resource(sources[resource]) for resource in RESOURCE_ORDER}
    rows = [row for resource in RESOURCE_ORDER for row in resources[resource].rows]
    changed_records = {resource: [f"{block}:{record}" for block, record in resources[resource].changed_records] for resource in RESOURCE_ORDER}
    inputs = {resource: profile_dict(sources[resource].spec.ko_profile) for resource in RESOURCE_ORDER}
    jp_evidence = {resource: profile_dict(sources[resource].spec.jp_profile) for resource in RESOURCE_ORDER}
    outputs = {resource: profile_dict(resources[resource].spec.output_profile) for resource in RESOURCE_ORDER}
    audit: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "candidate_only": True,
        "source_policy": {
            "platform": "direct PC only",
            "inputs_opened": ["installed_w45_base_korean_msggame", "installed_w45_pk_korean_msggame", "pristine_pc_japanese_base_msggame", "pristine_pc_japanese_pk_msggame"],
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
        "changed_literal_count_by_resource": {resource: len(resources[resource].changed_literals) for resource in RESOURCE_ORDER},
        "changed_record_count_by_resource": {resource: len(resources[resource].changed_records) for resource in RESOURCE_ORDER},
        "changed_literals": [row["slot"] for row in rows],
        "changed_records": changed_records,
        "excluded_slots": [f"{resource}:{block}:{record}:{literal}" for resource, block, record, literal in EXCLUDED_SLOTS],
        "validation": {
            "manual_lf_preserved": True,
            "esc_runtime_printf_control_signature_preserved": True,
            "opaque_skeleton_preserved": True,
            "other_literals_preserved": True,
            "other_records_preserved": True,
            "whole_archive_scope_checked": True,
        },
        "records": rows,
    }
    manifest: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {resource: {
            "input": inputs[resource],
            "output": outputs[resource],
            "changed_literals": [target.slot_text for target in TARGETS if target.resource == resource],
            "changed_records": changed_records[resource],
        } for resource in RESOURCE_ORDER},
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
    require(not output_root.exists(), f"refusing to overwrite private candidate: {output_root}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = require_private(Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT)), "candidate staging", strict=True)
    try:
        for resource in RESOURCE_ORDER:
            atomic_write(stage / Path(resource), bundle.resources[resource].packed)
        atomic_write(stage / "audit.v1.json", canonical_json(bundle.audit))
        atomic_write(stage / "candidate_manifest.v1.json", canonical_json(bundle.manifest))
        require(sha256_path(stage / "audit.v1.json") == bundle.manifest["audit_sha256"], "written audit hash differs")
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
    expected = set(RESOURCE_ORDER) | {"audit.v1.json", "candidate_manifest.v1.json"}
    require(private_file_set(candidate_root) == expected, "candidate file set differs")
    for resource in RESOURCE_ORDER:
        require((candidate_root / Path(resource)).read_bytes() == bundle.resources[resource].packed, f"candidate resource differs: {resource}")
    require((candidate_root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((candidate_root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return result_summary(bundle, candidate_root)


def diff_check(candidate_root: Path) -> dict[str, Any]:
    candidate_root = require_private(candidate_root, "candidate root", strict=True)
    bundle = prepare_candidate()
    changed: dict[str, list[str]] = {}
    changed_records: dict[str, list[str]] = {}
    for resource in RESOURCE_ORDER:
        source = bundle.sources[resource]
        packed = (candidate_root / Path(resource)).read_bytes()
        _header, raw = decompress_wrapper(packed)
        archive = parse_raw_msggame(raw)
        require_profile(packed, raw, source.spec.output_profile, f"diff candidate {resource}")
        literals: list[str] = []
        records: list[str] = []
        for before_block, after_block in zip(source.archive.blocks, archive.blocks):
            for before, after in zip(before_block.records, after_block.records):
                if before.data != after.data:
                    records.append(f"{before.block_id}:{before.record_id}")
                for old, new in zip(parse_record_literals(before), parse_record_literals(after)):
                    if old.text != new.text:
                        literals.append(f"{before.block_id}:{before.record_id}:{old.literal_id}")
        expected_literals = [target.slot_text for target in TARGETS if target.resource == resource]
        expected_records = bundle.manifest["resources"][resource]["changed_records"]
        require(literals == expected_literals, f"diff literal scope differs: {resource}")
        require(records == expected_records, f"diff record scope differs: {resource}")
        changed[resource], changed_records[resource] = literals, records
    return {
        "candidate_root": candidate_root.relative_to(REPO).as_posix(),
        "changed_literals": changed,
        "changed_records": changed_records,
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
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    verify_parser = subparsers.add_parser("verify-private")
    verify_parser.add_argument("--candidate-root", type=Path, default=TMP_ROOT / "candidate")
    diff_parser = subparsers.add_parser("diff-check")
    diff_parser.add_argument("--candidate-root", type=Path, default=TMP_ROOT / "candidate")
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
