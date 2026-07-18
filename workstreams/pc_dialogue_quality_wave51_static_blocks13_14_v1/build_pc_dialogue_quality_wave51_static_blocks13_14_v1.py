#!/usr/bin/env python3
"""Build a private, PC-only static candidate for msggame blocks 13–14.

The candidate contains only source-paired Steam-PC Korean corrections whose
current and pristine PC-Japanese records have no ``02xx`` runtime opcode and
no ``01 43`` morphology command.  It deliberately does not apply anything to
Steam, transact, use Git, access a network, or publish a release.  Its only
write target is this workstream's private ``tmp`` directory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)

# PC Japanese is the only translation authority.  The PK reference is the
# exact original backed up before the W45-installed Korean resources.
BASE_PC_JP_SOURCE = Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin")
PK_PC_JP_SOURCE = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / PK_RESOURCE
)

W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave51-static-blocks13-14.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave51-static-blocks13-14-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave51-static-blocks13-14-manifest.v1"


class Wave51Error(RuntimeError):
    """Raised when a pinned source, record contract, or private output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave51Error(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    require(not any("switch" in part.casefold() for part in resolved.parts), f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave51Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 format helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "Wave 27 format helper differs")
    spec = importlib.util.spec_from_file_location("wave51_pinned_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave51Error("cannot load Wave 27 format helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()
Coordinate = tuple[int, int]


@dataclass(frozen=True)
class ResourceSpec:
    resource: str
    current_path: Path
    pc_jp_source: Path
    w45_current_profile: Mapping[str, Any]
    pc_jp_profile: Mapping[str, Any]


@dataclass(frozen=True)
class Replacement:
    category: str
    resource: str
    coordinate: Coordinate
    old: str
    new: str
    expected_occurrences: int
    pc_jp_anchor: str
    reason: str


@dataclass(frozen=True)
class Change:
    resource: str
    coordinate: Coordinate
    replacements: tuple[Replacement, ...]

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Exact installed W45 Korean input.  Any drift is rejected before a private
# candidate is composed.
RESOURCE_SPECS = {
    BASE_RESOURCE: ResourceSpec(
        resource=BASE_RESOURCE,
        current_path=STEAM_ROOT / BASE_RESOURCE,
        pc_jp_source=BASE_PC_JP_SOURCE,
        w45_current_profile={
            "size": 1_504_410,
            "sha256": "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        },
        pc_jp_profile={
            "size": 610_163,
            "sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        },
    ),
    PK_RESOURCE: ResourceSpec(
        resource=PK_RESOURCE,
        current_path=STEAM_ROOT / PK_RESOURCE,
        pc_jp_source=PK_PC_JP_SOURCE,
        w45_current_profile={
            "size": 1_806_538,
            "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        },
        pc_jp_profile={
            "size": 721_304,
            "sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        },
    ),
}

# Filled once with ``derive-pins`` before build/verify are accepted.  The
# record-evidence hash pins every row's current/PC-JP/target record hashes,
# marker topology, opaque spans, terminator, and font-width evidence.
TARGET_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "size": 1_504_366,
        "sha256": "1803983A23DB63ED4FEDF67D5929786CCA8E6BF2A7F2932DA363DF95A7B2D57E",
        "raw_size": 1_498_464,
        "raw_sha256": "5A7FFC7BFF777662EEBAC68E844C35BF3FFD7B05D7723AD6F60B9C03C669203F",
    },
    PK_RESOURCE: {
        "size": 1_806_482,
        "sha256": "905DE32B79EB59BAD8B7B656B434D494F5D29271042A31B1DADFFADFE1A77FC8",
        "raw_size": 1_799_400,
        "raw_sha256": "0D2A599230CB78AEC780E80DABEE4CF07733DF7D98FD9A283EC5659DC9D00832",
    },
}
RECORD_EVIDENCE_SHA256 = "5E1ABBAC8DDD608EB48504C1EC6E3C573639C0F7939B4141F9E79BE639422634"
RECORD_EVIDENCE_COUNT = 54


def pair(block: int, record_ids: tuple[int, ...] | list[int]) -> tuple[Coordinate, ...]:
    return tuple((block, record_id) for record_id in record_ids)


def placements(
    category: str,
    resource: str,
    coordinates: tuple[Coordinate, ...],
    old: str,
    new: str,
    pc_jp_anchor: str,
    reason: str,
    counts: Mapping[Coordinate, int] | None = None,
) -> tuple[Replacement, ...]:
    expected = counts or {}
    return tuple(
        Replacement(category, resource, coordinate, old, new, expected.get(coordinate, 1), pc_jp_anchor, reason)
        for coordinate in coordinates
    )


RANK_REORDER_OLD = "아랫사람부터 차례로\n구미가시라, 아시가루대장, 사무라이대장, 부장, 가로, 숙로\n의 여섯 신분이 있사옵니다"
RANK_REORDER_NEW = "아랫사람부터 차례로\n조두·아시가루대장·사무라이대장·\n부장·가로·숙로까지 여섯 신분입니다."

REPLACEMENTS = (
    # 組頭: standardize to the already used Korean term 조두.  The two
    # ordinary dialogue records are deliberately reflowed inside three lines
    # so the shorter terminology does not retain a Japanese-width list wrap.
    *placements(
        "rank_term_reflow",
        BASE_RESOURCE,
        pair(13, (83, 174)),
        RANK_REORDER_OLD,
        RANK_REORDER_NEW,
        "組頭",
        "組頭 terminology and static three-line reflow",
    ),
    *placements(
        "rank_term_reflow",
        PK_RESOURCE,
        pair(13, (83, 174)),
        RANK_REORDER_OLD,
        RANK_REORDER_NEW,
        "組頭",
        "組頭 terminology and static three-line reflow",
    ),
    *placements(
        "rank_term",
        BASE_RESOURCE,
        pair(13, (383,)),
        "구미가시라",
        "조두",
        "組頭",
        "組頭 terminology",
    ),
    *placements(
        "rank_term",
        BASE_RESOURCE,
        pair(14, (32, 113, 117)),
        "조장",
        "조두",
        "組頭",
        "組頭 terminology",
    ),
    *placements(
        "rank_term",
        PK_RESOURCE,
        pair(14, (48, 51)),
        "조장",
        "조두",
        "組頭",
        "組頭 terminology",
    ),
    # 制度改新 is a named policy, not a generic reform.
    *placements(
        "policy_name",
        BASE_RESOURCE,
        pair(13, (444, 445, 446, 447, 483, 504, 505)),
        "제도 개혁",
        "제도 개신",
        "制度改新",
        "制度改新 policy name",
    ),
    *placements(
        "policy_name",
        PK_RESOURCE,
        pair(13, (362, 482, 483, 484, 485, 491, 492, 527, 548, 549, 580, 581, 582, 583, 584, 585, 597)),
        "제도 개혁",
        "제도 개신",
        "制度改新",
        "制度改新 policy name",
        {(13, 362): 2},
    ),
    # 解放 here means feature/command unlock.  Prisoner and retainer release
    # records are intentionally not in this set.
    *placements(
        "ui_unlock",
        BASE_RESOURCE,
        pair(13, (338, 360, 445, 447, 481, 505)) + pair(14, (16,)),
        "해방",
        "해금",
        "解放",
        "UI unlock sense of 解放",
    ),
    *placements(
        "ui_unlock",
        PK_RESOURCE,
        pair(13, (361, 392, 483, 485, 525, 549)) + pair(14, (23,)),
        "해방",
        "해금",
        "解放",
        "UI unlock sense of 解放",
        {(14, 23): 2},
    ),
    # Keep the icon as a separate literal; only repair the Korean object
    # particle around it.  PK 14:228 also contains duplicated selection text.
    *placements(
        "icon_particle",
        BASE_RESOURCE,
        pair(14, (34, 109)),
        ")를 선택",
        ")을 선택",
        "選択",
        "icon-selected object particle",
    ),
    *placements(
        "icon_particle",
        PK_RESOURCE,
        pair(14, (52, 53, 151, 229)),
        ")를 선택",
        ")을 선택",
        "選択",
        "icon-selected object particle",
    ),
    *placements(
        "icon_duplicate",
        PK_RESOURCE,
        pair(14, (228,)),
        "무장을 선택하면(",
        "무장(",
        "武将選択時",
        "remove duplicated selection clause before icon",
    ),
    *placements(
        "icon_particle",
        PK_RESOURCE,
        pair(14, (228,)),
        ")를 선택하면",
        ")을 선택하면",
        "選択",
        "icon-selected object particle",
    ),
    *placements(
        "typo",
        PK_RESOURCE,
        pair(14, (9, 10)),
        "헌책",
        "헌언",
        "献言",
        "献言 typo",
    ),
    *placements(
        "particle",
        PK_RESOURCE,
        pair(14, (112,)),
        '"이벤트 합전"가',
        '"이벤트 합전"이',
        "イベント合戦",
        "quoted event-battle subject particle",
    ),
    *placements(
        "typo",
        PK_RESOURCE,
        pair(14, (233,)),
        "병력력",
        "병력",
        "兵力",
        "duplicated 병력 syllable",
    ),
    *placements(
        "particle",
        PK_RESOURCE,
        pair(14, (242,)),
        "예정를",
        "예정을",
        "行動予定",
        "object particle after 행동 예정",
    ),
)


def collect_changes() -> tuple[Change, ...]:
    grouped: dict[tuple[str, Coordinate], list[Replacement]] = defaultdict(list)
    for replacement in REPLACEMENTS:
        grouped[(replacement.resource, replacement.coordinate)].append(replacement)
    changes = tuple(
        Change(resource, coordinate, tuple(replacements))
        for (resource, coordinate), replacements in sorted(
            grouped.items(), key=lambda item: (RESOURCE_ORDER.index(item[0][0]), item[0][1])
        )
    )
    require(len(changes) == RECORD_EVIDENCE_COUNT, "static candidate scope count differs")
    require(sum(change.resource == BASE_RESOURCE for change in changes) == 19, "Base scope count differs")
    require(sum(change.resource == PK_RESOURCE for change in changes) == 35, "PK scope count differs")
    require(len({(change.resource, change.coordinate) for change in changes}) == len(changes), "duplicate candidate coordinate")
    return changes


CHANGES = collect_changes()

# These coordinates remain deliberately outside this builder even where a
# Korean issue exists.  The README explains the full hold inventory.
EXCLUDED_HOLDS = {
    "terminology_policy": {
        BASE_RESOURCE: ["13:185", "13:341", "13:344", "13:409-412", "14:71"],
        PK_RESOURCE: ["13:185", "13:365", "13:368", "13:444-447", "14:97-98"],
    },
    "dialogue_reflow": {
        BASE_RESOURCE: ["13:213"],
        PK_RESOURCE: ["13:213"],
    },
    "help_or_table_ui_qa": {
        BASE_RESOURCE: ["13:8", "14:57"],
        PK_RESOURCE: ["13:8", "14:81", "14:156-157"],
    },
    "semantic_retranslation": {
        PK_RESOURCE: ["13:563", "13:573", "13:590", "14:97-98", "14:221"],
    },
    "runtime_or_morphology": {
        BASE_RESOURCE: ["13:15-16", "13:22", "13:25-26", "13:51", "13:53-54", "13:75", "13:77", "13:93-94", "13:105", "13:112-115", "13:117-119", "13:123-126", "13:129", "13:141", "13:162-164", "13:171", "13:182"],
        PK_RESOURCE: ["13:15-16", "13:22", "13:25-26", "13:51", "13:53-54", "13:75", "13:77", "13:93-94", "13:105", "13:112-115", "13:117-119", "13:123-126", "13:129", "13:141", "13:162-164", "13:171", "13:182", "14:109"],
    },
}


def literal_hashes(record: Any) -> list[str]:
    return [sha256_bytes(text.encode("utf-16-le")) for text in W27.literal_texts(record)]


def opaque_hexes(record: Any) -> list[str]:
    return [span.hex().upper() for span in W27.opaque_spans(record)]


def marker_topology_hex(record: Any) -> list[list[str]]:
    return [[start.hex().upper(), end.hex().upper()] for start, end in W27.marker_topology(record)]


def runtime_02xx_opcodes(record: Any) -> list[str]:
    opcodes: list[str] = []
    for span in W27.opaque_spans(record):
        for index, byte in enumerate(span[:-1]):
            if byte == 0x02:
                opcodes.append(span[index : index + 2].hex().upper())
    return opcodes


def validate_target_literal(value: str, label: str) -> None:
    require(value != "", f"empty target literal: {label}")
    encoded = value.encode("utf-16-le")
    require(W27.LITERAL_START not in encoded and W27.LITERAL_END not in encoded, f"reserved marker in target: {label}")
    require(all(ord(character) >= 0x20 or character in "\n\r" for character in value), f"control character in target: {label}")


def load_inputs() -> tuple[
    Mapping[str, bytes],
    Mapping[str, Mapping[Coordinate, Any]],
    Mapping[str, Mapping[Coordinate, Any]],
]:
    packed_by_resource: dict[str, bytes] = {}
    current_by_resource: dict[str, Mapping[Coordinate, Any]] = {}
    pc_jp_by_resource: dict[str, Mapping[Coordinate, Any]] = {}
    for resource in RESOURCE_ORDER:
        spec = RESOURCE_SPECS[resource]
        current_path = reject_switch(spec.current_path, f"W45 current Steam PC {resource}")
        source_path = reject_switch(spec.pc_jp_source, f"pristine PC Japanese {resource}")
        current = current_path.read_bytes()
        source = source_path.read_bytes()
        require(
            len(current) == spec.w45_current_profile["size"] and sha256_bytes(current) == spec.w45_current_profile["sha256"],
            f"W45 current profile differs: {resource}",
        )
        require(
            len(source) == spec.pc_jp_profile["size"] and sha256_bytes(source) == spec.pc_jp_profile["sha256"],
            f"PC Japanese source profile differs: {resource}",
        )
        W27.validate_raw_roundtrip(current, f"Wave 51 W45 current {resource}")
        W27.validate_raw_roundtrip(source, f"Wave 51 PC Japanese {resource}")
        packed_by_resource[resource] = current
        current_by_resource[resource] = W27.records_by_coordinate(current)
        pc_jp_by_resource[resource] = W27.records_by_coordinate(source)
    return packed_by_resource, current_by_resource, pc_jp_by_resource


def apply_replacements(change: Change, before: Any, pc_jp: Any) -> tuple[tuple[str, ...], list[dict[str, Any]]]:
    label = f"{change.resource}:{change.coordinate_text}"
    current_literals = W27.literal_texts(before)
    source_text = "".join(W27.literal_texts(pc_jp))
    target_literals = list(current_literals)
    evidence: list[dict[str, Any]] = []
    for replacement in change.replacements:
        require(source_text.count(replacement.pc_jp_anchor) >= 1, f"PC Japanese anchor missing: {label}:{replacement.category}")
        occurrences = sum(value.count(replacement.old) for value in target_literals)
        require(
            occurrences == replacement.expected_occurrences,
            f"current replacement occurrence differs: {label}:{replacement.category} expected {replacement.expected_occurrences}, got {occurrences}",
        )
        target_literals = [value.replace(replacement.old, replacement.new) for value in target_literals]
        evidence.append(
            {
                "category": replacement.category,
                "reason": replacement.reason,
                "current_fragment": replacement.old,
                "target_fragment": replacement.new,
                "current_occurrences": occurrences,
                "pc_jp_anchor": replacement.pc_jp_anchor,
            }
        )
    return tuple(target_literals), evidence


def validate_change(change: Change, before: Any, pc_jp: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    label = f"{change.resource}:{change.coordinate_text}"
    require(change.coordinate == (before.block_id, before.record_id), f"current coordinate differs: {label}")
    require(change.coordinate == (pc_jp.block_id, pc_jp.record_id), f"PC Japanese coordinate differs: {label}")
    current_literals = W27.literal_texts(before)
    source_literals = W27.literal_texts(pc_jp)
    require(len(current_literals) == len(source_literals), f"literal slot count differs: {label}")
    require(W27.marker_topology(before) == W27.marker_topology(pc_jp), f"PC Japanese marker topology differs: {label}")
    require(W27.opaque_spans(before) == W27.opaque_spans(pc_jp), f"PC Japanese opaque spans differ: {label}")
    for record, record_label in ((before, "current"), (pc_jp, "PC Japanese")):
        require(record.data.endswith(W27.RECORD_TERMINATOR), f"{record_label} terminator differs: {label}")
        require(not runtime_02xx_opcodes(record), f"{record_label} 02xx runtime opcode is forbidden: {label}")
        require(not W27.complete_0143_commands(W27.opaque_spans(record)), f"{record_label} 0143 command is forbidden: {label}")

    target_literals, replacement_evidence = apply_replacements(change, before, pc_jp)
    require(target_literals != current_literals, f"target is unchanged: {label}")
    require(len(target_literals) == len(current_literals), f"target literal slot count differs: {label}")
    require("".join(target_literals).count("\n") == "".join(current_literals).count("\n"), f"manual LF count differs: {label}")
    for literal in target_literals:
        validate_target_literal(literal, label)

    current_layout = W27.line_layout(current_literals, advance)
    target_layout = W27.line_layout(target_literals, advance)
    require(target_layout["line_count"] == current_layout["line_count"], f"line count differs: {label}")
    require(target_layout["max_width_px"] <= current_layout["max_width_px"], f"target text expands width: {label}")
    require(not target_layout["wide_fallback_codepoints"], f"target fallback glyph: {label}")

    rebuilt = W27.rebuild_static_record(before, target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == target_literals, f"target literal differs after rebuild: {label}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"target marker topology differs: {label}")
    require(W27.opaque_spans(after) == W27.opaque_spans(before), f"target opaque spans differ: {label}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {label}")
    require(not runtime_02xx_opcodes(after), f"target runtime opcode appears: {label}")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), f"target 0143 command appears: {label}")

    return rebuilt, {
        "resource": change.resource,
        "coordinate": change.coordinate_text,
        "categories": sorted({replacement.category for replacement in change.replacements}),
        "replacements": replacement_evidence,
        "current_record": {
            "sha256": sha256_bytes(before.data),
            "size": len(before.data),
            "literal_utf16le_sha256": literal_hashes(before),
            "marker_topology_hex": marker_topology_hex(before),
            "opaque_spans_hex": opaque_hexes(before),
            "terminator": before.data.endswith(W27.RECORD_TERMINATOR),
            "runtime_02xx_opcodes": runtime_02xx_opcodes(before),
            "complete_0143_commands": list(W27.complete_0143_commands(W27.opaque_spans(before))),
            "manual_lf_count": "".join(current_literals).count("\n"),
            "line_widths_px": list(current_layout["line_widths_px"]),
            "max_line_px": current_layout["max_width_px"],
            "wide_fallback_codepoints": list(current_layout["wide_fallback_codepoints"]),
        },
        "pc_jp_record": {
            "sha256": sha256_bytes(pc_jp.data),
            "size": len(pc_jp.data),
            "literal_utf16le_sha256": literal_hashes(pc_jp),
            "marker_topology_hex": marker_topology_hex(pc_jp),
            "opaque_spans_hex": opaque_hexes(pc_jp),
            "terminator": pc_jp.data.endswith(W27.RECORD_TERMINATOR),
            "runtime_02xx_opcodes": runtime_02xx_opcodes(pc_jp),
            "complete_0143_commands": list(W27.complete_0143_commands(W27.opaque_spans(pc_jp))),
        },
        "target_record": {
            "sha256": sha256_bytes(after.data),
            "size": len(after.data),
            "literal_utf16le_sha256": literal_hashes(after),
            "marker_topology_hex": marker_topology_hex(after),
            "opaque_spans_hex": opaque_hexes(after),
            "terminator": after.data.endswith(W27.RECORD_TERMINATOR),
            "runtime_02xx_opcodes": runtime_02xx_opcodes(after),
            "complete_0143_commands": list(W27.complete_0143_commands(W27.opaque_spans(after))),
            "manual_lf_count": "".join(target_literals).count("\n"),
            "line_widths_px": list(target_layout["line_widths_px"]),
            "max_line_px": target_layout["max_width_px"],
            "wide_fallback_codepoints": list(target_layout["wide_fallback_codepoints"]),
            "literals": list(target_literals),
        },
    }


def observed_profile(packed: bytes, raw: bytes) -> dict[str, Any]:
    return {
        "size": len(packed),
        "sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
    }


def build_unpinned() -> tuple[CandidateBundle, list[dict[str, Any]]]:
    current_packed, current_by_resource, pc_jp_by_resource = load_inputs()
    advance, font = W27.load_font_advance()
    replacements_by_resource: dict[str, dict[Coordinate, bytes]] = {resource: {} for resource in RESOURCE_ORDER}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current_by_resource[change.resource].get(change.coordinate)
        pc_jp = pc_jp_by_resource[change.resource].get(change.coordinate)
        require(before is not None and pc_jp is not None, f"candidate record is absent: {change.resource}:{change.coordinate_text}")
        require(change.coordinate not in replacements_by_resource[change.resource], f"duplicate replacement coordinate: {change.resource}:{change.coordinate_text}")
        replacement, row = validate_change(change, before, pc_jp, advance)
        replacements_by_resource[change.resource][change.coordinate] = replacement
        rows.append(row)

    packed_output: dict[str, bytes] = {}
    raw_output: dict[str, bytes] = {}
    for resource in RESOURCE_ORDER:
        candidate = W27.rebuild_packed_msggame(current_packed[resource], replacements_by_resource[resource])
        W27.validate_raw_roundtrip(candidate, f"Wave 51 private candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        after = W27.records_by_coordinate(candidate)
        changed = {
            coordinate
            for coordinate, current_record in current_by_resource[resource].items()
            if current_record.data != after[coordinate].data
        }
        expected = {change.coordinate for change in CHANGES if change.resource == resource}
        require(changed == expected and set(after) == set(current_by_resource[resource]), f"changed record scope differs: {resource}")
        packed_output[resource] = candidate
        raw_output[resource] = raw

    output_profiles = {
        resource: observed_profile(packed_output[resource], raw_output[resource])
        for resource in RESOURCE_ORDER
    }
    record_evidence_sha256 = sha256_bytes(canonical_json(rows))
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "pc_jp_primary": True,
            "switch_korean_read": False,
            "runtime_02xx_records": "forbidden",
            "0143_command_records": "forbidden",
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "pinned_format_helper_sha256": W27_HELPER_SHA256,
        "font": font,
        "width_policy": {
            "target_line_count_equals_current": True,
            "target_max_line_px_must_not_expand": True,
            "target_fallback_glyphs": "forbidden",
            "rank_reflow_coordinates": ["13:83", "13:174"],
            "rank_reflow_target_max_px": 888,
        },
        "w45_inputs": {resource: RESOURCE_SPECS[resource].w45_current_profile for resource in RESOURCE_ORDER},
        "pc_jp_sources": {resource: RESOURCE_SPECS[resource].pc_jp_profile for resource in RESOURCE_ORDER},
        "outputs": output_profiles,
        "changed_record_count": len(CHANGES),
        "changed_record_count_by_resource": {
            resource: sum(change.resource == resource for change in CHANGES)
            for resource in RESOURCE_ORDER
        },
        "record_evidence_sha256": record_evidence_sha256,
        "excluded_holds": EXCLUDED_HOLDS,
        "records": rows,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": list(RESOURCE_ORDER),
        "w45_inputs": {resource: RESOURCE_SPECS[resource].w45_current_profile for resource in RESOURCE_ORDER},
        "outputs": output_profiles,
        "changed_coordinates": {
            resource: [change.coordinate_text for change in CHANGES if change.resource == resource]
            for resource in RESOURCE_ORDER
        },
        "changed_record_count": len(CHANGES),
        "changed_record_count_by_resource": {
            resource: sum(change.resource == resource for change in CHANGES)
            for resource in RESOURCE_ORDER
        },
        "record_evidence_sha256": record_evidence_sha256,
        "excluded_holds": EXCLUDED_HOLDS,
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_output, raw_output, audit, manifest), rows


def require_pins() -> None:
    require(set(TARGET_PROFILES) == set(RESOURCE_ORDER), "target profile resources differ")
    for resource in RESOURCE_ORDER:
        require(
            {"size", "sha256", "raw_size", "raw_sha256"} <= set(TARGET_PROFILES[resource]),
            f"target packed/raw pin is absent: {resource}",
        )
    require(len(RECORD_EVIDENCE_SHA256) == 64, "record evidence hash pin is absent")


def derive_pins() -> dict[str, Any]:
    bundle, rows = build_unpinned()
    return {
        "target_profiles": {
            resource: observed_profile(bundle.packed[resource], bundle.raw[resource])
            for resource in RESOURCE_ORDER
        },
        "record_evidence_count": len(rows),
        "record_evidence_sha256": sha256_bytes(canonical_json(rows)),
    }


def prepare_candidate() -> CandidateBundle:
    require_pins()
    bundle, rows = build_unpinned()
    for resource in RESOURCE_ORDER:
        expected = TARGET_PROFILES[resource]
        actual = observed_profile(bundle.packed[resource], bundle.raw[resource])
        require(actual == expected, f"target packed/raw profile differs: {resource}")
    require(len(rows) == RECORD_EVIDENCE_COUNT, "record evidence count differs")
    require(sha256_bytes(canonical_json(rows)) == RECORD_EVIDENCE_SHA256, "per-record evidence profile differs")
    require(bundle.audit["record_evidence_sha256"] == RECORD_EVIDENCE_SHA256, "audit record evidence differs")
    return bundle


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource in RESOURCE_ORDER:
            destination = stage / resource
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(bundle.packed[resource])
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            require_private(output, "existing candidate output")
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    require(output.is_dir(), f"private candidate is absent: {output}")
    for resource in RESOURCE_ORDER:
        path = output / resource
        require(path.is_file() and path.read_bytes() == bundle.packed[resource], f"private candidate resource differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "changed_record_count_by_resource": {
            resource: sum(change.resource == resource for change in CHANGES)
            for resource in RESOURCE_ORDER
        },
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("derive-pins", "build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        result = derive_pins()
    elif args.command == "build":
        output = write_candidate(prepare_candidate())
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": len(CHANGES),
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
