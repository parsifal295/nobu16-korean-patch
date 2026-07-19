#!/usr/bin/env python3
"""Build a private PC-only B11~B13 static-quality candidate.

This builder only implements the eight B13 literal corrections established by
the clean direct-PC audit.  It reads four pinned PC resources and writes only
under this workstream's private ``tmp`` root.  Steam apply, Git, network, and
release operations are intentionally absent.
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
    """Raised when a PC-source, scope, or private-output invariant fails."""


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
    block_profiles: Mapping[int, tuple[int, int]]


@dataclass(frozen=True)
class Proposal:
    scope: str
    record_id: int
    old: str
    new: str
    jp: str
    reason: str

    @property
    def slot(self) -> str:
        return f"13:{self.record_id}:0"

    @property
    def record_coordinate(self) -> tuple[int, int]:
        return (13, self.record_id)


@dataclass(frozen=True)
class PairBlockProfile:
    record_count_equal: bool
    literal_topology_mismatch_records: tuple[int, ...]
    manual_lf_difference_slots: tuple[str, ...]
    opaque_control_skeleton_mismatch_records: tuple[int, ...]


@dataclass(frozen=True)
class CheckedInput:
    packed: bytes
    archive: MsgGameArchive
    profile: Mapping[str, Any]


@dataclass(frozen=True)
class ResourceBundle:
    scope: str
    current: CheckedInput
    jp: CheckedInput
    candidate_packed: bytes
    candidate_raw: bytes
    candidate_archive: MsgGameArchive
    changed_records: frozenset[tuple[int, int]]
    rows: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class Bundle:
    inputs: Mapping[str, Mapping[str, Any]]
    resources: Mapping[str, ResourceBundle]
    output_profiles: Mapping[str, Mapping[str, Any]]
    pair_profiles: Mapping[str, Mapping[int, PairBlockProfile]]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
BLOCKS = (11, 12, 13)
BASE_KO_BLOCKS = {11: (4, 2), 12: (69, 145), 13: (517, 608)}
BASE_JP_BLOCKS = {11: (4, 2), 12: (69, 145), 13: (517, 625)}
PK_KO_BLOCKS = {11: (4, 2), 12: (71, 147), 13: (647, 748)}
PK_JP_BLOCKS = {11: (4, 2), 12: (71, 147), 13: (647, 765)}

INPUTS: Mapping[str, InputSpec] = {
    "base_ko_w45": InputSpec(
        "Base current Steam-PC Korean W45",
        STEAM_ROOT / "MSG" / "JP" / "msggame.bin",
        1_504_410,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        BASE_KO_BLOCKS,
    ),
    "base_jp_pc": InputSpec(
        "Base pristine PC Japanese",
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        610_163,
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        BASE_JP_BLOCKS,
    ),
    "pk_ko_w45": InputSpec(
        "PK current Steam-PC Korean W45",
        STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        1_806_538,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        PK_KO_BLOCKS,
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
        PK_JP_BLOCKS,
    ),
}

RESOURCE_PATHS = {
    "base": "MSG/JP/msggame.bin",
    "pk": "MSG_PK/JP/msggame.bin",
}
INPUT_KEYS = {
    "base": ("base_ko_w45", "base_jp_pc"),
    "pk": ("pk_ko_w45", "pk_jp_pc"),
}
SCHEMA = "nobu16.kr.pc-b11-b13-static-quality-candidate.v1"

PROPOSALS: tuple[Proposal, ...] = (
    Proposal("base", 258, "「건언」", "「헌언」", "「献言」", "献言 menu title"),
    Proposal(
        "base",
        260,
        "화면 우측 상단의 「건의」",
        "화면 우측 상단의 「헌언」",
        "画面右上の「献言」",
        "献言 menu reference",
    ),
    Proposal("pk", 260, "「건언」", "「헌언」", "「献言」", "献言 menu title"),
    Proposal(
        "pk",
        262,
        "화면 우측 상단의 「건의」",
        "화면 우측 상단의 「헌언」",
        "画面右上の「献言」",
        "献言 menu reference",
    ),
    Proposal(
        "pk",
        452,
        "【정리:외교와 군략】\n ·“친선”으로 다른 가문과의 관계를 개선\n ·“출진”으로 적의 성을 제압해 영토를 확대\n\n【무엇을 해야 할지 모를 때】\n ·화면 오른쪽 위 메뉴의 “건의”를 눌러 가신에게 물어봄",
        "【정리:외교와 군략】\n ·“친선”으로 다른 가문과의 관계를 개선\n ·“출진”으로 적의 성을 제압해 영토를 확대\n\n【무엇을 해야 할지 모를 때】\n ·화면 오른쪽 위 메뉴의 “헌언”을 눌러 가신에게 물어봄",
        "【まとめ：外交と軍略】\n　・「親善」で他家との関係を改善することが可能\n　・「出陣」して敵城を制圧することで領土を拡大\n\n【やるべきことがわからなければ】\n　・画面右上部のメニューの「献言」で家臣に助言をもらう",
        "献言 menu reference",
    ),
    Proposal(
        "pk",
        353,
        "【요지】\n전장 곳곳의 중요 지점입니다. 많이 제압할수록 전투가 유리해집니다.\n ·부대의 공격을 받아 내구가 0이 되면 「제압」됨\n ·제압한 측의 모든 부대 능력이 상승하고 진영의 총사기가 오름\n\n요지 중에는 발동 효과가 있는 「특수 요지」가 있습니다.\n제압하고 잠시 지나면 요지 위 버튼으로 특별한 효과를 발동할 수 있습니다.",
        "【요충지】\n전장 곳곳의 중요 지점입니다. 많이 제압할수록 전투가 유리해집니다.\n ·부대의 공격을 받아 내구가 0이 되면 「제압」됨\n ·제압한 측의 모든 부대 능력이 상승하고 진영의 총사기가 오름\n\n요충지 중에는 발동 효과가 있는 「특수 요충지」가 있습니다.\n제압하고 잠시 지나면 요충지 위 버튼으로 특별한 효과를 발동할 수 있습니다.",
        "【要所】\n戦場に散らばる重要地点です。多く制圧するほど戦いが有利になります。\n　・部隊の攻撃を受けて耐久が０になると「制圧」となる\n　・制圧した側の全部隊の能力が上昇し、陣営の総士気が上がる\n\n要所の中には発動効果を持つ「特殊要所」が存在します。\n制圧してしばらくすると、要所上のボタンから特別な効果を発動できます。",
        "要所 terminology must match 요충지 UI label",
    ),
    Proposal(
        "pk",
        575,
        "【부대】\n적 부대와 퇴각 지점, 요지를 공격합니다.\n ·전장에 표시된 선 위를 이동하고 적 부대와 접촉하면 공격\n ·보통 스스로 판단해 이동/공격하지만 플레이어가 지시할 수도 있음\n ·지시할 때 ㌘㎝㍑로 경유지를 설정할 수 있음",
        "【부대】\n적 부대와 퇴각 지점, 요충지를 공격합니다.\n ·전장에 표시된 선 위를 이동하고 적 부대와 접촉하면 공격\n ·보통 스스로 판단해 이동/공격하지만 플레이어가 지시할 수도 있음\n ·지시할 때 ㌘㎝㍑로 경유지를 설정할 수 있음",
        "【部隊】\n敵部隊や退き口、要所を攻撃します。\n　・戦場に表示される線の上を移動し、敵部隊に接触すると攻撃する\n　・通常は自己判断で移動／攻撃するが、プレイヤーが指示することもできる\n　・指示を出す際、㌘㎝㍑で中継点を設定できる",
        "要所 terminology must match 요충지 UI label",
    ),
    Proposal(
        "pk",
        615,
        "신분이 일정 이상인 무장을 「가재」나 「봉행」에 임명합니다.\n임명된 무장은 세력 전체를 관장해 다양한 혜택을 줍니다.\n또한 종속 세력의 다이묘를 외양 가재로 최대 2명 임명할 수 있습니다.\n\n「가재」는 가로 이상, 「봉행」은 부장 이상의 신분이 필요합니다.\n※「가재」나 「봉행」에서 해임된 무장은 다이묘가 교체되거나,\n 정책 「재량권 이양」 LV2 이상 발령 후 일정 기간이 지나야 재임명할 수 있습니다.",
        "신분이 일정 이상인 무장을 「가재」나 「봉행」에 임명합니다.\n임명된 무장은 세력 전체를 관장해 다양한 혜택을 줍니다.\n또한 종속 세력의 다이묘를 도자마 가재로 최대 2명 임명할 수 있습니다.\n\n「가재」는 가로 이상, 「봉행」은 부장 이상의 신분이 필요합니다.\n※「가재」나 「봉행」에서 해임된 무장은 다이묘가 교체되거나,\n 정책 「재량권 이양」 LV2 이상 발령 후 일정 기간이 지나야 재임명할 수 있습니다.",
        "身分が一定以上の武将を「家宰」や「奉行」に任命します。\n任命された武将は勢力全体を取り仕切り、様々な恩恵を与えます。\nまた、従属勢力の大名を外様家宰として最大２人まで任命できます。\n\n「家宰」には家老以上、「奉行」には部将以上の身分が必要です。\n※「家宰」や「奉行」を解任された武将は、大名の代替わりか、\n　政策「裁量権移譲」LV2以上の発令で一定期間経過後に再任できます。",
        "外様家宰 terminology must match adjacent 도자마 가재 label",
    ),
)

EXPECTED_RECORDS = {
    "base": frozenset({(13, 258), (13, 260)}),
    "pk": frozenset({(13, 260), (13, 262), (13, 353), (13, 452), (13, 575), (13, 615)}),
}

_B13_TOPOLOGY = (9, 17, 24, 27, 28, 30, 40, 55, 108, 110, 116, 122, 127, 128, 136, 142)
_B12_SKELETON = (18, 21, 24, 26, 28, *range(45, 63))
_B13_SKELETON = (9, 17, 23, 24, 27, 28, 30, 32, 33, 36, 40, 46, 49, 55, 85, 87, 106, 107, 108, 110, 116, 121, 122, 127, 128, 136, 142, 176, 178)
_B13_LF_BASE = tuple(f"13:{record}:0" for record in (9, 17, 24, 27, 28, 30, 55, 108, 110, 116, 122, 127, 128, 136, 142))
_B13_LF_PK = tuple(f"13:{record}:0" for record in (9, 17, 24, 27, 28, 30, 36, 55, 108, 110, 116, 122, 127, 128, 136, 142))

PAIR_EXPECTED = {
    "base": {
        11: PairBlockProfile(True, (), (), ()),
        12: PairBlockProfile(True, (), (), _B12_SKELETON),
        13: PairBlockProfile(True, _B13_TOPOLOGY, _B13_LF_BASE, _B13_SKELETON),
    },
    "pk": {
        11: PairBlockProfile(True, (), (), ()),
        12: PairBlockProfile(True, (), (), _B12_SKELETON),
        13: PairBlockProfile(True, _B13_TOPOLOGY, _B13_LF_PK, _B13_SKELETON),
    },
}

# Filled after the read-only derive-pins pass.  All build and verification
# commands reject an unpinned output profile.
TARGET_OUTPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    "base": {
        "packed_size": 1_504_410,
        "packed_sha256": "FFD9B5A53EE6B7F3B491B98441A68A0F26319AF947F4202829734722D99E6D97",
        "raw_size": 1_498_508,
        "raw_sha256": "CDB4D8D9E1D0EC401CB4C9ABE493F9D9ABF17FCC943F1D1458E3F3AB4059FD17",
    },
    "pk": {
        "packed_size": 1_806_550,
        "packed_sha256": "8D1D7F08D92ACB0BF128E46953749A096339C7C33BF26F7DEFB584A459618697",
        "raw_size": 1_799_468,
        "raw_sha256": "1C7BCF821EC9D3991CCA1AE3733B6B86EB12649385976B5DDA5F0FD06D8FBC1B",
    },
}


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in parse_record_literals(record))


def opaque_skeleton(record: MsgGameRecord) -> bytes:
    """Preserve every control byte while replacing literal text by a sentinel."""
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


def block_literal_count(archive: MsgGameArchive, block_id: int) -> int:
    return sum(len(parse_record_literals(record)) for record in archive.blocks[block_id].records)


def checked_input(spec: InputSpec) -> CheckedInput:
    path = reject_non_pc_path(spec.path, spec.label)
    require(path.stat().st_size == spec.packed_size, f"input size drift: {spec.label}")
    require(sha256_path(path) == spec.packed_sha256, f"input hash drift: {spec.label}")
    packed = path.read_bytes()
    parsed = parse_packed_msggame(packed)
    header, raw = decompress_wrapper(packed)
    require(rebuild_raw_msggame(parsed.archive) == raw, f"raw parser roundtrip drift: {spec.label}")
    require(decompress_wrapper(recompress_wrapper(raw, header))[1] == raw, f"LZ4 roundtrip drift: {spec.label}")
    for block_id, (expected_records, expected_literals) in spec.block_profiles.items():
        require(len(parsed.archive.blocks) > block_id, f"missing B{block_id:02}: {spec.label}")
        require(
            len(parsed.archive.blocks[block_id].records) == expected_records,
            f"B{block_id:02} record drift: {spec.label}",
        )
        require(
            block_literal_count(parsed.archive, block_id) == expected_literals,
            f"B{block_id:02} literal drift: {spec.label}",
        )
    profile = {
        "path": str(path),
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "block_profiles": {
            str(block_id): {
                "records": len(parsed.archive.blocks[block_id].records),
                "literals": block_literal_count(parsed.archive, block_id),
            }
            for block_id in BLOCKS
        },
    }
    return CheckedInput(packed=packed, archive=parsed.archive, profile=profile)


def pair_profile(ko: MsgGameArchive, jp: MsgGameArchive) -> Mapping[int, PairBlockProfile]:
    result: dict[int, PairBlockProfile] = {}
    for block_id in BLOCKS:
        ko_records = ko.blocks[block_id].records
        jp_records = jp.blocks[block_id].records
        topology: list[int] = []
        manual_lf: list[str] = []
        skeleton: list[int] = []
        for record_id, (ko_record, jp_record) in enumerate(zip(ko_records, jp_records)):
            ko_literals = parse_record_literals(ko_record)
            jp_literals = parse_record_literals(jp_record)
            if len(ko_literals) != len(jp_literals):
                topology.append(record_id)
            if opaque_skeleton(ko_record) != opaque_skeleton(jp_record):
                skeleton.append(record_id)
            for literal_id, (ko_literal, jp_literal) in enumerate(zip(ko_literals, jp_literals)):
                if ko_literal.text.count("\n") != jp_literal.text.count("\n"):
                    manual_lf.append(f"{block_id}:{record_id}:{literal_id}")
        result[block_id] = PairBlockProfile(
            len(ko_records) == len(jp_records),
            tuple(topology),
            tuple(manual_lf),
            tuple(skeleton),
        )
    return result


def require_pair_profile(scope: str, ko: MsgGameArchive, jp: MsgGameArchive, label: str) -> Mapping[int, PairBlockProfile]:
    actual = pair_profile(ko, jp)
    require(actual == PAIR_EXPECTED[scope], f"B11~B13 pair profile drift: {label}")
    return actual


def candidate_output_profile(packed: bytes) -> Mapping[str, Any]:
    header, raw = decompress_wrapper(packed)
    archive = parse_packed_msggame(packed).archive
    require(rebuild_raw_msggame(archive) == raw, "candidate raw parser roundtrip drift")
    require(decompress_wrapper(recompress_wrapper(raw, header))[1] == raw, "candidate LZ4 roundtrip drift")
    require(decompress_wrapper(rebuild_packed_msggame(packed))[1] == raw, "candidate archive rebuild drift")
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
    }


def proposals_for(scope: str) -> tuple[Proposal, ...]:
    chosen = tuple(proposal for proposal in PROPOSALS if proposal.scope == scope)
    require(len(chosen) == len(EXPECTED_RECORDS[scope]), f"proposal count drift: {scope}")
    require(
        {proposal.record_coordinate for proposal in chosen} == EXPECTED_RECORDS[scope],
        f"record allowlist drift: {scope}",
    )
    return chosen


def changed_record_coordinates(before: MsgGameArchive, after: MsgGameArchive) -> frozenset[tuple[int, int]]:
    require(len(before.blocks) == len(after.blocks), "candidate block count drift")
    changed: set[tuple[int, int]] = set()
    for block_id, (before_block, after_block) in enumerate(zip(before.blocks, after.blocks)):
        require(len(before_block.records) == len(after_block.records), f"record count drift: block {block_id}")
        for before_record, after_record in zip(before_block.records, after_block.records):
            require(before_record.record_id == after_record.record_id, f"record id drift: block {block_id}")
            if before_record.data != after_record.data:
                changed.add((block_id, before_record.record_id))
    return frozenset(changed)


def build_resource(scope: str, current: CheckedInput, jp: CheckedInput) -> ResourceBundle:
    require_pair_profile(scope, current.archive, jp.archive, f"{scope} current")
    proposals = proposals_for(scope)
    replacements: dict[tuple[int, int, int], str] = {}
    for proposal in proposals:
        current_texts = literal_texts(current.archive.blocks[13].records[proposal.record_id])
        jp_texts = literal_texts(jp.archive.blocks[13].records[proposal.record_id])
        require(len(current_texts) == len(jp_texts) == 1, f"target literal topology drift: {scope} {proposal.slot}")
        require(current_texts[0] == proposal.old, f"current preimage drift: {scope} {proposal.slot}")
        require(jp_texts[0] == proposal.jp, f"JP reference drift: {scope} {proposal.slot}")
        require(proposal.old.count("\n") == proposal.new.count("\n"), f"manual LF count drift: {scope} {proposal.slot}")
        replacements[(13, proposal.record_id, 0)] = proposal.new
    require(len(replacements) == len(proposals), f"replacement uniqueness drift: {scope}")

    candidate_packed = rebuild_packed_with_literals(current.packed, replacements)
    _candidate_header, candidate_raw = decompress_wrapper(candidate_packed)
    candidate_archive = parse_packed_msggame(candidate_packed).archive
    require(rebuild_raw_msggame(candidate_archive) == candidate_raw, f"candidate raw drift: {scope}")
    require_pair_profile(scope, candidate_archive, jp.archive, f"{scope} candidate")

    changed = changed_record_coordinates(current.archive, candidate_archive)
    require(changed == EXPECTED_RECORDS[scope], f"changed record scope drift: {scope}")
    rows: list[Mapping[str, Any]] = []
    for proposal in proposals:
        before = current.archive.blocks[13].records[proposal.record_id]
        after = candidate_archive.blocks[13].records[proposal.record_id]
        before_texts = literal_texts(before)
        after_texts = literal_texts(after)
        require(before_texts == (proposal.old,), f"old target mismatch: {scope} {proposal.slot}")
        require(after_texts == (proposal.new,), f"new target mismatch: {scope} {proposal.slot}")
        require(opaque_skeleton(before) == opaque_skeleton(after), f"opaque/control drift: {scope} {proposal.slot}")
        rows.append(
            {
                "scope": scope,
                "resource": RESOURCE_PATHS[scope],
                "slot": proposal.slot,
                "reason": proposal.reason,
                "current": proposal.old,
                "target": proposal.new,
                "pc_jp": proposal.jp,
                "current_utf16le_sha256": sha256_bytes(proposal.old.encode("utf-16-le")),
                "target_utf16le_sha256": sha256_bytes(proposal.new.encode("utf-16-le")),
                "manual_lf_count": proposal.old.count("\n"),
                "opaque_skeleton_unchanged": True,
            }
        )
    for block_id, (before_block, after_block) in enumerate(zip(current.archive.blocks, candidate_archive.blocks)):
        for before_record, after_record in zip(before_block.records, after_block.records):
            if (block_id, before_record.record_id) not in EXPECTED_RECORDS[scope]:
                require(
                    before_record.data == after_record.data,
                    f"out-of-scope record data changed: {scope} {block_id}:{before_record.record_id}",
                )
    return ResourceBundle(
        scope=scope,
        current=current,
        jp=jp,
        candidate_packed=candidate_packed,
        candidate_raw=candidate_raw,
        candidate_archive=candidate_archive,
        changed_records=changed,
        rows=tuple(rows),
    )


def output_pins_ready() -> bool:
    return all(
        profile["packed_size"] > 0
        and bool(profile["packed_sha256"])
        and profile["raw_size"] > 0
        and bool(profile["raw_sha256"])
        for profile in TARGET_OUTPUT_PROFILES.values()
    )


def build_unpinned() -> Bundle:
    checked = {name: checked_input(spec) for name, spec in INPUTS.items()}
    resources: dict[str, ResourceBundle] = {}
    pair_profiles: dict[str, Mapping[int, PairBlockProfile]] = {}
    for scope, (ko_key, jp_key) in INPUT_KEYS.items():
        resources[scope] = build_resource(scope, checked[ko_key], checked[jp_key])
        pair_profiles[scope] = require_pair_profile(scope, checked[ko_key].archive, checked[jp_key].archive, f"{scope} input")
    outputs = {scope: candidate_output_profile(resource.candidate_packed) for scope, resource in resources.items()}
    inputs = {name: item.profile for name, item in checked.items()}
    rows = [row for scope in ("base", "pk") for row in resources[scope].rows]
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
        "source_pair_profiles": {
            scope: {
                str(block_id): {
                    "record_count_equal": profile.record_count_equal,
                    "literal_topology_mismatch_records": list(profile.literal_topology_mismatch_records),
                    "manual_lf_difference_slots": list(profile.manual_lf_difference_slots),
                    "opaque_control_skeleton_mismatch_records": list(profile.opaque_control_skeleton_mismatch_records),
                }
                for block_id, profile in profiles.items()
            }
            for scope, profiles in pair_profiles.items()
        },
        "outputs": outputs,
        "changed_record_count": 8,
        "changed_literal_count": 8,
        "changed_records": {
            scope: [f"{block}:{record}" for block, record in sorted(resource.changed_records)]
            for scope, resource in resources.items()
        },
        "manual_lf_policy": "all eight target literals retain their existing manual LF count",
        "opaque_controls_and_placeholders_immutable": True,
        "rows": rows,
    }
    manifest = {
        "schema": SCHEMA,
        "candidate_only": True,
        "candidate_root": CANDIDATE_ROOT.relative_to(REPO).as_posix(),
        "resources": RESOURCE_PATHS,
        "inputs": inputs,
        "outputs": outputs,
        "changed_record_count": 8,
        "changed_literal_count": 8,
        "changed_records": audit["changed_records"],
        "steam_apply": "not implemented",
        "git": "not implemented",
        "network": "not implemented",
        "release": "not implemented",
    }
    return Bundle(inputs, resources, outputs, pair_profiles, audit, manifest)


def prepare_candidate() -> Bundle:
    require(output_pins_ready(), "target output profiles are not pinned; run derive-pins then embed them")
    bundle = build_unpinned()
    require(bundle.output_profiles == TARGET_OUTPUT_PROFILES, "candidate output profiles differ from pins")
    return bundle


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT, "candidate root")
    require(not output.exists(), "private candidate already exists; do not overwrite it")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for scope, resource in bundle.resources.items():
            target = stage / RESOURCE_PATHS[scope]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(resource.candidate_packed)
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
    for scope, resource in bundle.resources.items():
        require(
            (output / RESOURCE_PATHS[scope]).read_bytes() == resource.candidate_packed,
            f"candidate packed resource drift: {scope}",
        )
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit drift")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest drift")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": 8,
        "changed_literal_count": 8,
        "steam_game_resource_written": False,
    }


def diff_check() -> Mapping[str, Any]:
    bundle = prepare_candidate()
    output = require_private(CANDIDATE_ROOT, "candidate root")
    require(output.is_dir(), "private candidate has not been built")
    result: dict[str, Any] = {}
    total = 0
    for scope, resource in bundle.resources.items():
        candidate = parse_packed_msggame((output / RESOURCE_PATHS[scope]).read_bytes()).archive
        changed = changed_record_coordinates(resource.current.archive, candidate)
        require(changed == EXPECTED_RECORDS[scope], f"private candidate changed-record scope drift: {scope}")
        for block_id, (before_block, after_block) in enumerate(zip(resource.current.archive.blocks, candidate.blocks)):
            for before_record, after_record in zip(before_block.records, after_block.records):
                if (block_id, before_record.record_id) not in EXPECTED_RECORDS[scope]:
                    require(
                        before_record.data == after_record.data,
                        f"out-of-scope private record drift: {scope} {block_id}:{before_record.record_id}",
                    )
        result[scope] = [f"{block}:{record}" for block, record in sorted(changed)]
        total += len(changed)
    require(total == 8, "total changed-record count drift")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_records": result,
        "changed_record_count": total,
        "changed_literal_count": 8,
        "opaque_controls_and_placeholders_immutable": True,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("derive-pins", "build", "verify-private", "diff-check"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        result: Mapping[str, Any] = {"target_output_profiles": build_unpinned().output_profiles}
    elif args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": 8,
            "changed_literal_count": 8,
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
