#!/usr/bin/env python3
"""Build the PC-only private Wave 29 NPC-name quality candidate.

The sole Korean preimage is the complete eleven-file PC Wave 27 candidate.
This workstream changes the 23 approved dynamic NPC components in both
presentation tables and six complete event-name labels in both event tables.
It writes only a private candidate below this release worktree's ``tmp``
directory; it has no Steam-apply, Git, or release-publishing capability.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
PREDECESSOR_ROOT = Path(
    r"F:\Games\NOBU16\KR_PATCH_WORK\tmp\pc_dialogue_quality_wave27_static_quality_v1\candidate"
)
PC_REFERENCE_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

TOOLS = REPO / "tools"
STRDATA_TOOLS = REPO / "workstreams" / "strdata"
for root in (TOOLS, STRDATA_TOOLS):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402
from strdata_format import StrdataArchive, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


SCHEMA = "nobu16.kr.pc-npc-name-quality-wave29.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-npc-name-quality-wave29-audit.v1"
BUILD_SCHEMA = "nobu16.kr.pc-npc-name-quality-wave29-build.v1"

BASE_STRDATA = "MSG/JP/strdata.bin"
PK_MSGDATA = "MSG_PK/JP/msgdata.bin"
BASE_EV = "MSG/JP/ev_strdata.bin"
PK_MSEV = "MSG_PK/JP/msgev.bin"
CHANGED_PATHS = (BASE_STRDATA, PK_MSGDATA, BASE_EV, PK_MSEV)
PROFILE_PATHS = (
    BASE_EV,
    "MSG/JP/msggame.bin",
    BASE_STRDATA,
    "MSG_PK/JP/msgbre.bin",
    PK_MSGDATA,
    PK_MSEV,
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)

# The exact complete Wave 27 profile.  The builder never uses an installed JP
# file as a Korean preimage and rejects any root other than this candidate.
INPUT_SHA256 = {
    BASE_EV: "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    "MSG/JP/msggame.bin": "4D6460F1B717FD8D424229ABD619DE4093C21929F6C42B061BAD62E163C5D3CB",
    BASE_STRDATA: "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    PK_MSGDATA: "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    PK_MSEV: "91F4C99B1C4D21CE9A3529CB174AA1EFD9E198E8FEB6F90F5AD507CEBB4B8C4F",
    "MSG_PK/JP/msggame.bin": "AD3F6DD64C0AD360C5A8C7A4747ABFCE9B2D72BFFDD3D44940781A68AC2DE8D1",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
INPUT_SIZES = {
    BASE_EV: 928_123,
    "MSG/JP/msggame.bin": 1_504_526,
    BASE_STRDATA: 957_204,
    "MSG_PK/JP/msgbre.bin": 484_068,
    PK_MSGDATA: 496_995,
    PK_MSEV: 994_731,
    "MSG_PK/JP/msggame.bin": 1_806_647,
    "MSG_PK/JP/msgire.bin": 23_128,
    "MSG_PK/JP/msgstf.bin": 17_341,
    "MSG_PK/JP/msgstf_ce.bin": 18_767,
    "MSG_PK/JP/msgui.bin": 122_733,
}

# Produced from the exact predecessor and the fixed mapping below.  The seven
# retain-only resources must remain byte-identical to INPUT_*.
TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_STRDATA: "37A1F6280B2663A7FF055C6A2105B5658CA62065582A66213C6D4D4AE2A79E0A",
    PK_MSGDATA: "8282F12A667E11F54054856035415C7297385ADD16EC261BD952BEBB8658952A",
    BASE_EV: "02AC90B818E8F75683CD5BACF277E91048D4510E448A8699242D3B19299FE067",
    PK_MSEV: "AEE0D9992B963E17B3C118AA54DACC60390936FF48876674CA7675A2A11A3668",
}
TARGET_SIZES = {
    **INPUT_SIZES,
    BASE_STRDATA: 957_200,
    PK_MSGDATA: 496_991,
    BASE_EV: 928_119,
    PK_MSEV: 994_727,
}


@dataclass(frozen=True)
class ComponentFix:
    entry_id: int
    base_before: str
    pk_before: str
    after: str


@dataclass(frozen=True)
class StaticFix:
    entry_id: int
    before: str
    after: str


class Wave29Error(RuntimeError):
    """A source, structural, policy, or private-output contract changed."""


# The strings intentionally retain the required directional spaces.  They are
# composition fragments, so a trailing/leading space is part of the contract.
COMPONENT_FIXES = (
    ComponentFix(87, "남자의", "남자의", "사내"),
    ComponentFix(89, "여자의", "여자의", "여자"),
    ComponentFix(93, "가상", "가공", "가공 "),
    ComponentFix(147, "고", "고", "호"),
    ComponentFix(174, "자비", "자비", "하비"),
    ComponentFix(182, "시게", "시게", "중"),
    ComponentFix(185, "오시", "오시", "닌"),
    ComponentFix(194, "시로", "시로", "흰"),
    ComponentFix(195, "시로", "시로", "흰"),
    ComponentFix(209, "오이와", "오이와", "다이간 "),
    ComponentFix(327, "마을", "마을", "성읍 "),
    ComponentFix(349, "무라", "무라", "마을 "),
    ComponentFix(445, "가문", "가문", "가"),
    ComponentFix(757, "나가", "초 ", "부족"),
    ComponentFix(774, "철포", "철포", "철포 "),
    ComponentFix(2164, "가시라", "가시라", "장"),
    ComponentFix(2168, "노", "노", "로"),
    ComponentFix(2175, "에루", "에루", "에르"),
    ComponentFix(2180, "스케무", "스케무", "유무"),
    ComponentFix(2181, "딸", "딸", "처녀"),
    ComponentFix(2182, "딸", "딸", "처녀"),
    ComponentFix(2184, "쓰카사", "쓰카사", " 대표"),
    ComponentFix(2187, "자", "자", "장"),
)
STATIC_FIXES = (
    StaticFix(2832, "우에무라 요리카도", "우에무라 라이렌"),
    StaticFix(2874, "다테 히사무네", "다테 나오무네"),
    StaticFix(2883, "나가노 미치후지", "나가노 미치히사"),
    StaticFix(2892, "후쿠시마 마사노부", "쿠시마 마사노부"),
    StaticFix(2910, "미즈노 다다치카", "미즈노 다다와케"),
    StaticFix(2916, "야마나 무네토요", "야마나 오키토요"),
)

# PC-only multilingual context anchors.  EN has only PK copies for these
# table classes; SC and TC provide both Base and PK paths.  They are read-only
# semantic witnesses and are not used as Korean translation input.
PC_REFERENCE_SPECS = {
    "EN_PK_MSGDATA": ("MSG_PK/EN/msgdata.bin", "BDE25DFD7265C5B6E765F2FA2A8F800E171C6C2B23FB8A66F05AE239BF71E033", "message", "component"),
    "EN_PK_MSEV": ("MSG_PK/EN/msgev.bin", "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E", "message", "static"),
    "SC_BASE_STRDATA": ("MSG/SC/strdata.bin", "93F88D71210B96783749CEB948E0713D7E6552F764F644092B71A5FD0C994B88", "strdata", "component"),
    "SC_PK_MSGDATA": ("MSG_PK/SC/msgdata.bin", "A3A0260B74191D4676C43403B587BB4EC676A7D96E56725844F24C8107B1604E", "message", "component"),
    "SC_BASE_EV": ("MSG/SC/ev_strdata.bin", "77E87C6FEC67859543FCB4134660A7274A2374F6881B956421B561E61BD7B685", "message", "static"),
    "SC_PK_MSEV": ("MSG_PK/SC/msgev.bin", "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA", "message", "static"),
    "TC_BASE_STRDATA": ("MSG/TC/strdata.bin", "16481F0B4B1E544F8F7C0B1C92210D13592560470AC062847DA32375B77DA861", "strdata", "component"),
    "TC_PK_MSGDATA": ("MSG_PK/TC/msgdata.bin", "E266A9C43AAE09BEEA739812AD8E3E8DDDBC4710EF5A81E174A9D215D6B03676", "message", "component"),
    "TC_BASE_EV": ("MSG/TC/ev_strdata.bin", "9E9346B942CAFA99432D675F6BA74DD04D48F56095F35F46392697011D9CFEF3", "message", "static"),
    "TC_PK_MSEV": ("MSG_PK/TC/msgev.bin", "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6", "message", "static"),
}

# Issue #61's previously repaired literal-percent cells.  They are far from
# all Wave 29 component slots, but get an explicit token/literal guard rather
# than being protected only incidentally by the non-target slot comparison.
ISSUE61_PK_PERCENT_IDS = frozenset((
    22506, 22507, 22509, 22510, 22512, 22514, 22515, 22526, 22527, 22531,
    22532, 22533, 22534, 22535, 22536, 22537, 22540, 22541, 22543, 22548,
    22553, 22554, 22555, 22556, 22558, 22560, 22563, 22564, 22581, 22585,
    22599, 22605, 22606, 22614, 22624, 22628, 22629, 22630, 22631, 22632,
    22635, 22644, 22647, 22648, 22653, 22656, 22662, 22664, 22666,
))
ISSUE61_SHARED_PERCENT_SLOTS = frozenset((
    22254, 22255, 22257, 22258, 22260, 22262, 22263, 22274, 22275, 22279,
    22280, 22281, 22283, 22284, 22285, 22288, 22289, 22291, 22296, 22303,
    22304, 22306, 22308, 22312, 22329, 22333, 22347, 22353, 22354, 22362,
    22372, 22376, 22377, 22378, 22379, 22380, 22381, 22382, 22383,
))
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_sha256(text: str) -> str:
    return sha256_bytes(text.encode("utf-16-le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch_path(path: Path, label: str) -> Path:
    """Reject an alternate-platform path before it can be resolved or read."""

    if any("switch" in part.casefold() for part in path.parts):
        raise Wave29Error(f"alternate-platform Korean input is forbidden: {label}")
    return path.resolve(strict=True)


def require_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve(strict=False)
    resolved_path = path.resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave29Error(f"{label} escapes its allowed root: {resolved_path}") from exc
    return resolved_path


def require_tmp(path: Path, label: str) -> Path:
    checked = require_under(TMP_ROOT, path, label)
    if checked == TMP_ROOT.resolve(strict=False):
        raise Wave29Error(f"{label} cannot be the private tmp root")
    return checked


def profile(root: Path) -> tuple[dict[str, str], dict[str, int]]:
    root = reject_switch_path(root, "profile root")
    hashes: dict[str, str] = {}
    sizes: dict[str, int] = {}
    for relative in PROFILE_PATHS:
        path = require_under(root, root / relative, f"profile resource {relative}")
        if not path.is_file():
            raise Wave29Error(f"missing profile resource: {relative}")
        hashes[relative] = sha256_path(path)
        sizes[relative] = path.stat().st_size
    return hashes, sizes


def assert_profile(
    root: Path,
    expected_hashes: Mapping[str, str],
    expected_sizes: Mapping[str, int],
    label: str,
) -> None:
    hashes, sizes = profile(root)
    if hashes != dict(expected_hashes) or sizes != dict(expected_sizes):
        mismatch = {
            relative: {
                "expected_hash": expected_hashes.get(relative),
                "actual_hash": hashes.get(relative),
                "expected_size": expected_sizes.get(relative),
                "actual_size": sizes.get(relative),
            }
            for relative in PROFILE_PATHS
            if hashes.get(relative) != expected_hashes.get(relative)
            or sizes.get(relative) != expected_sizes.get(relative)
        }
        raise Wave29Error(f"{label} profile differs: {mismatch}")


def require_predecessor_root(root: Path) -> Path:
    expected = reject_switch_path(PREDECESSOR_ROOT, "Wave 27 predecessor")
    checked = reject_switch_path(root, "Wave 29 input")
    if checked != expected:
        raise Wave29Error("input must be the exact complete Wave 27 private candidate")
    return checked


def assert_spec() -> None:
    component_ids = tuple(fix.entry_id for fix in COMPONENT_FIXES)
    static_ids = tuple(fix.entry_id for fix in STATIC_FIXES)
    if len(COMPONENT_FIXES) != 23 or len(set(component_ids)) != 23:
        raise Wave29Error("expected exactly 23 unique dynamic component IDs")
    if len(STATIC_FIXES) != 6 or len(set(static_ids)) != 6:
        raise Wave29Error("expected exactly 6 unique static label IDs")
    if set(component_ids) & set(static_ids):
        raise Wave29Error("dynamic and static ID sets unexpectedly overlap")
    if len(ISSUE61_PK_PERCENT_IDS) != 49 or len(ISSUE61_SHARED_PERCENT_SLOTS) != 39:
        raise Wave29Error("Issue #61 percent-policy scope differs")
    if len(COMPONENT_FIXES) * 2 + len(STATIC_FIXES) * 2 != 58:
        raise Wave29Error("Wave 29 must change exactly 58 logical slots")
    if tuple(INPUT_SHA256) != PROFILE_PATHS or tuple(INPUT_SIZES) != PROFILE_PATHS:
        raise Wave29Error("predecessor profile order differs")
    if tuple(TARGET_SHA256) != PROFILE_PATHS or tuple(TARGET_SIZES) != PROFILE_PATHS:
        raise Wave29Error("target profile order differs")


def unpack_common(source: bytes, label: str) -> tuple[object, MessageTable]:
    wrapper, raw = decompress_wrapper(source)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise Wave29Error(f"{label} common table does not byte-round-trip")
    return wrapper, table


def unpack_strdata(source: bytes, label: str) -> tuple[object, StrdataArchive]:
    wrapper, raw = decompress_wrapper(source)
    archive = parse_raw_strdata(raw)
    if rebuild_raw_strdata(archive) != raw:
        raise Wave29Error(f"{label} strdata archive does not byte-round-trip")
    return wrapper, archive


def slot_bytes(table: MessageTable, entry_id: int) -> bytes:
    if not 0 <= entry_id < table.string_count:
        raise Wave29Error(f"slot outside table: {entry_id}")
    start = table.table_offset + table.string_offsets[entry_id]
    end = (
        table.table_offset + table.string_offsets[entry_id + 1]
        if entry_id + 1 < table.string_count
        else table.logical_end
    )
    return table.blob[start:end]


def parse_component_texts(resource: str, packed: bytes) -> tuple[Sequence[str], MessageTable | None, StrdataArchive | None]:
    if resource == BASE_STRDATA:
        _wrapper, archive = unpack_strdata(packed, resource)
        return archive.blocks[0].texts, archive.blocks[0].table, archive
    if resource == PK_MSGDATA:
        _wrapper, table = unpack_common(packed, resource)
        return table.texts, table, None
    raise Wave29Error(f"not a component resource: {resource}")


def parse_static_texts(resource: str, packed: bytes) -> tuple[Sequence[str], MessageTable]:
    if resource not in {BASE_EV, PK_MSEV}:
        raise Wave29Error(f"not a static-label resource: {resource}")
    _wrapper, table = unpack_common(packed, resource)
    return table.texts, table


def patch_base_strdata(source: bytes) -> bytes:
    wrapper, archive = unpack_strdata(source, BASE_STRDATA)
    texts = list(archive.blocks[0].texts)
    for fix in COMPONENT_FIXES:
        if texts[fix.entry_id] != fix.base_before:
            raise Wave29Error(
                f"unexpected Base component preimage #0:{fix.entry_id}: {texts[fix.entry_id]!r}"
            )
        texts[fix.entry_id] = fix.after
    rebuilt = rebuild_raw_strdata(archive, {0: texts})
    checked = parse_raw_strdata(rebuilt)
    if checked.blocks[0].texts != tuple(texts):
        raise Wave29Error("Base strdata rebuilt table failed parse verification")
    return recompress_wrapper(rebuilt, wrapper)


def patch_pk_msgdata(source: bytes) -> bytes:
    wrapper, table = unpack_common(source, PK_MSGDATA)
    texts = list(table.texts)
    for fix in COMPONENT_FIXES:
        if texts[fix.entry_id] != fix.pk_before:
            raise Wave29Error(
                f"unexpected PK component preimage #{fix.entry_id}: {texts[fix.entry_id]!r}"
            )
        texts[fix.entry_id] = fix.after
    rebuilt = rebuild_message_table(table, texts)
    checked = parse_message_table(rebuilt)
    if checked.texts != tuple(texts):
        raise Wave29Error("PK msgdata rebuilt table failed parse verification")
    return recompress_wrapper(rebuilt, wrapper)


def patch_static(resource: str, source: bytes) -> bytes:
    wrapper, table = unpack_common(source, resource)
    texts = list(table.texts)
    for fix in STATIC_FIXES:
        if texts[fix.entry_id] != fix.before:
            raise Wave29Error(
                f"unexpected static preimage {resource}#{fix.entry_id}: {texts[fix.entry_id]!r}"
            )
        texts[fix.entry_id] = fix.after
    rebuilt = rebuild_message_table(table, texts)
    checked = parse_message_table(rebuilt)
    if checked.texts != tuple(texts):
        raise Wave29Error(f"{resource} rebuilt table failed parse verification")
    return recompress_wrapper(rebuilt, wrapper)


def patch_resource(resource: str, source: bytes) -> bytes:
    if resource == BASE_STRDATA:
        return patch_base_strdata(source)
    if resource == PK_MSGDATA:
        return patch_pk_msgdata(source)
    if resource in {BASE_EV, PK_MSEV}:
        return patch_static(resource, source)
    raise Wave29Error(f"unsupported target resource: {resource}")


def changed_slot_ids(resource: str) -> frozenset[int]:
    if resource in {BASE_STRDATA, PK_MSGDATA}:
        return frozenset(fix.entry_id for fix in COMPONENT_FIXES)
    if resource in {BASE_EV, PK_MSEV}:
        return frozenset(fix.entry_id for fix in STATIC_FIXES)
    raise Wave29Error(f"unsupported changed resource: {resource}")


def assert_non_target_slot_bytes_unchanged(
    source: MessageTable,
    candidate: MessageTable,
    changed: frozenset[int],
    label: str,
) -> None:
    if source.string_count != candidate.string_count:
        raise Wave29Error(f"{label} slot count changed")
    for entry_id in range(source.string_count):
        if entry_id not in changed and slot_bytes(source, entry_id) != slot_bytes(candidate, entry_id):
            raise Wave29Error(f"{label} changed non-target record bytes at #{entry_id}")


def percent_policy_signature(text: str) -> dict[str, Any]:
    tokens = [match.group(0) for match in PRINTF_RE.finditer(text)]
    token_indexes = {
        index
        for match in PRINTF_RE.finditer(text)
        for index in range(match.start(), match.end())
    }
    return {
        "utf16le_sha256": text_sha256(text),
        "printf_tokens": tokens,
        "ascii_percent_literal_indexes": [
            index for index, char in enumerate(text) if char == "%" and index not in token_indexes
        ],
        "fullwidth_percent_indexes": [
            index for index, char in enumerate(text) if char == "％"
        ],
    }


def assert_issue61_policy_unchanged(
    source_base: MessageTable,
    candidate_base: MessageTable,
    source_pk: MessageTable,
    candidate_pk: MessageTable,
) -> dict[str, Any]:
    rows: dict[str, list[dict[str, Any]]] = {BASE_STRDATA: [], PK_MSGDATA: []}
    for resource, before, after, ids in (
        (BASE_STRDATA, source_base, candidate_base, ISSUE61_SHARED_PERCENT_SLOTS),
        (PK_MSGDATA, source_pk, candidate_pk, ISSUE61_PK_PERCENT_IDS),
    ):
        for entry_id in sorted(ids):
            before_text = before.texts[entry_id]
            after_text = after.texts[entry_id]
            before_signature = percent_policy_signature(before_text)
            after_signature = percent_policy_signature(after_text)
            if before_signature != after_signature or slot_bytes(before, entry_id) != slot_bytes(after, entry_id):
                raise Wave29Error(f"Issue #61 percent-policy literal/token changed: {resource}#{entry_id}")
            if before_signature["ascii_percent_literal_indexes"]:
                raise Wave29Error(f"Issue #61 predecessor has unsafe ASCII percent: {resource}#{entry_id}")
            if not before_signature["fullwidth_percent_indexes"]:
                raise Wave29Error(f"Issue #61 literal percent is absent: {resource}#{entry_id}")
            rows[resource].append({"id": entry_id, **before_signature})
    return {
        "shared_slot_count": len(rows[BASE_STRDATA]),
        "pk_id_count": len(rows[PK_MSGDATA]),
        "literal_tokens_byte_identical": True,
        "resources": rows,
    }


def validate_pc_anchors() -> dict[str, Any]:
    """Hash-gate read-only PC EN/SC/TC witnesses with no alternate input."""

    root = reject_switch_path(PC_REFERENCE_ROOT, "PC EN/SC/TC anchor root")
    loaded: dict[str, Sequence[str]] = {}
    report: dict[str, Any] = {}
    for name, (relative, expected_hash, kind, category) in PC_REFERENCE_SPECS.items():
        path = reject_switch_path(require_under(root, root / relative, name), name)
        if not path.is_file() or sha256_path(path) != expected_hash:
            actual = sha256_path(path) if path.is_file() else "MISSING"
            raise Wave29Error(f"PC anchor profile differs: {name} expected={expected_hash} actual={actual}")
        packed = path.read_bytes()
        if kind == "strdata":
            _wrapper, archive = unpack_strdata(packed, name)
            texts = archive.blocks[0].texts
        else:
            _wrapper, table = unpack_common(packed, name)
            texts = table.texts
        ids = (
            tuple(fix.entry_id for fix in COMPONENT_FIXES)
            if category == "component"
            else tuple(fix.entry_id for fix in STATIC_FIXES)
        )
        values = {entry_id: texts[entry_id] for entry_id in ids}
        if any(not value for value in values.values()):
            raise Wave29Error(f"PC anchor has empty target slot: {name}")
        loaded[name] = texts
        report[name] = {
            "path": relative,
            "sha256": expected_hash,
            "target_slot_utf16le_sha256": {str(key): text_sha256(value) for key, value in values.items()},
        }
    for language in ("SC", "TC"):
        for kind, base_name, pk_name in (
            ("component", f"{language}_BASE_STRDATA", f"{language}_PK_MSGDATA"),
            ("static", f"{language}_BASE_EV", f"{language}_PK_MSEV"),
        ):
            ids = (
                tuple(fix.entry_id for fix in COMPONENT_FIXES)
                if kind == "component"
                else tuple(fix.entry_id for fix in STATIC_FIXES)
            )
            if any(loaded[base_name][entry_id] != loaded[pk_name][entry_id] for entry_id in ids):
                raise Wave29Error(f"PC {language} Base/PK {kind} anchors differ")
    return report


def validate_changed_records(source: Mapping[str, bytes], candidate: Mapping[str, bytes]) -> dict[str, Any]:
    """Validate the exact 58 semantic slots plus all non-target record bytes."""

    source_base_texts, source_base_table, source_base_archive = parse_component_texts(BASE_STRDATA, source[BASE_STRDATA])
    candidate_base_texts, candidate_base_table, candidate_base_archive = parse_component_texts(BASE_STRDATA, candidate[BASE_STRDATA])
    source_pk_texts, source_pk_table, _ = parse_component_texts(PK_MSGDATA, source[PK_MSGDATA])
    candidate_pk_texts, candidate_pk_table, _ = parse_component_texts(PK_MSGDATA, candidate[PK_MSGDATA])
    assert source_base_table is not None and candidate_base_table is not None
    assert source_base_archive is not None and candidate_base_archive is not None
    assert source_pk_table is not None and candidate_pk_table is not None

    component_ids = changed_slot_ids(BASE_STRDATA)
    assert_non_target_slot_bytes_unchanged(source_base_table, candidate_base_table, component_ids, "Base strdata block 0")
    assert_non_target_slot_bytes_unchanged(source_pk_table, candidate_pk_table, component_ids, "PK msgdata")
    for source_block, candidate_block in zip(source_base_archive.blocks[1:], candidate_base_archive.blocks[1:], strict=True):
        if source_block.table.blob != candidate_block.table.blob:
            raise Wave29Error(f"Base strdata changed retain-only block {source_block.block_id}")

    component_rows: list[dict[str, Any]] = []
    for fix in COMPONENT_FIXES:
        if source_base_texts[fix.entry_id] != fix.base_before or source_pk_texts[fix.entry_id] != fix.pk_before:
            raise Wave29Error(f"component source differs at #{fix.entry_id}")
        if candidate_base_texts[fix.entry_id] != fix.after or candidate_pk_texts[fix.entry_id] != fix.after:
            raise Wave29Error(f"component target differs at #{fix.entry_id}")
        component_rows.append(
            {
                "id": fix.entry_id,
                "base_before_utf16le_sha256": text_sha256(fix.base_before),
                "pk_before_utf16le_sha256": text_sha256(fix.pk_before),
                "after_utf16le_sha256": text_sha256(fix.after),
            }
        )

    static_rows: list[dict[str, Any]] = []
    for resource in (BASE_EV, PK_MSEV):
        source_texts, source_table = parse_static_texts(resource, source[resource])
        candidate_texts, candidate_table = parse_static_texts(resource, candidate[resource])
        static_ids = changed_slot_ids(resource)
        assert_non_target_slot_bytes_unchanged(source_table, candidate_table, static_ids, resource)
        for fix in STATIC_FIXES:
            if source_texts[fix.entry_id] != fix.before or candidate_texts[fix.entry_id] != fix.after:
                raise Wave29Error(f"static label differs: {resource}#{fix.entry_id}")
        static_rows.append(
            {
                "resource": resource,
                "ids": [fix.entry_id for fix in STATIC_FIXES],
                "after_utf16le_sha256": {
                    str(fix.entry_id): text_sha256(fix.after) for fix in STATIC_FIXES
                },
            }
        )

    issue61 = assert_issue61_policy_unchanged(
        source_base_table,
        candidate_base_table,
        source_pk_table,
        candidate_pk_table,
    )
    return {
        "dynamic_component_slot_count": len(COMPONENT_FIXES) * 2,
        "static_label_slot_count": len(STATIC_FIXES) * 2,
        "changed_slot_count": len(COMPONENT_FIXES) * 2 + len(STATIC_FIXES) * 2,
        "non_target_record_bytes_identical": True,
        "component_rows": component_rows,
        "static_rows": static_rows,
        "issue61_percent_policy": issue61,
    }


def prepare_candidate(input_root: Path = PREDECESSOR_ROOT) -> tuple[dict[str, bytes], dict[str, Any]]:
    assert_spec()
    input_root = require_predecessor_root(input_root)
    assert_profile(input_root, INPUT_SHA256, INPUT_SIZES, "Wave 27 predecessor")
    pc_anchors = validate_pc_anchors()
    source = {relative: (input_root / relative).read_bytes() for relative in CHANGED_PATHS}
    output = {relative: patch_resource(relative, source[relative]) for relative in CHANGED_PATHS}
    hashes = {**INPUT_SHA256, **{relative: sha256_bytes(payload) for relative, payload in output.items()}}
    sizes = {**INPUT_SIZES, **{relative: len(payload) for relative, payload in output.items()}}
    if hashes != TARGET_SHA256 or sizes != TARGET_SIZES:
        raise Wave29Error("target eleven-file profile differs")
    changes = validate_changed_records(source, output)
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "predecessor": "exact complete PC Wave 27 eleven-file private candidate",
            "pc_jp_predecessor_read": True,
            "pc_en_sc_tc_anchor_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor_candidate_root": str(input_root),
        "input_sha256": INPUT_SHA256,
        "input_sizes": INPUT_SIZES,
        "target_sha256": TARGET_SHA256,
        "target_sizes": TARGET_SIZES,
        "pc_anchors": pc_anchors,
        "changes": changes,
    }
    return output, audit


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def remove_stage(path: Path) -> None:
    if path.exists():
        require_tmp(path, "private staging path")
        shutil.rmtree(path)


def verify_private_candidate(candidate_root: Path) -> dict[str, Any]:
    candidate_root = require_tmp(candidate_root, "candidate root")
    if not candidate_root.is_dir():
        raise Wave29Error(f"private candidate is absent: {candidate_root}")
    files = {
        path.relative_to(candidate_root).as_posix()
        for path in candidate_root.rglob("*")
        if path.is_file()
    }
    if files != set(PROFILE_PATHS):
        raise Wave29Error("private candidate must contain exactly the eleven-file profile")
    assert_profile(candidate_root, TARGET_SHA256, TARGET_SIZES, "Wave 29 private candidate")
    expected, audit = prepare_candidate(PREDECESSOR_ROOT)
    for relative in CHANGED_PATHS:
        if (candidate_root / relative).read_bytes() != expected[relative]:
            raise Wave29Error(f"private candidate bytes differ: {relative}")
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "candidate_root": str(candidate_root),
        "profile_sha256": TARGET_SHA256,
        "changed_path_count": len(CHANGED_PATHS),
        "changed_slot_count": audit["changes"]["changed_slot_count"],
        "non_target_record_bytes_identical": audit["changes"]["non_target_record_bytes_identical"],
        "issue61_percent_policy": {
            "shared_slot_count": audit["changes"]["issue61_percent_policy"]["shared_slot_count"],
            "pk_id_count": audit["changes"]["issue61_percent_policy"]["pk_id_count"],
            "literal_tokens_byte_identical": audit["changes"]["issue61_percent_policy"]["literal_tokens_byte_identical"],
        },
    }


def build_candidate(
    input_root: Path,
    output_root: Path,
    audit_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    input_root = require_predecessor_root(input_root)
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave29Error("candidate output, audit, or manifest already exists")
    output, audit = prepare_candidate(input_root)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative in output:
                destination.write_bytes(output[relative])
            else:
                shutil.copyfile(input_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, TARGET_SIZES, "Wave 29 staging")
        os.replace(stage, output_root)
        verified = verify_private_candidate(output_root)
        atomic_write(audit_path, canonical_json(audit))
        manifest = {
            "schema": BUILD_SCHEMA,
            "candidate_only": True,
            "output_root": str(output_root),
            "audit_path": str(audit_path),
            "input_sha256": INPUT_SHA256,
            "input_sizes": INPUT_SIZES,
            "output_sha256": TARGET_SHA256,
            "output_sizes": TARGET_SIZES,
            "changed_paths": list(CHANGED_PATHS),
            "changed_slot_count": verified["changed_slot_count"],
            "non_target_record_bytes_identical": True,
            "issue61_percent_policy_unchanged": True,
            "steam_write_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
        }
        atomic_write(manifest_path, canonical_json(manifest))
        return manifest
    except Exception:
        remove_stage(stage)
        raise


def command_hash(_args: argparse.Namespace) -> int:
    assert_spec()
    _output, audit = prepare_candidate(PREDECESSOR_ROOT)
    print(json.dumps({"status": "ok", "target_sha256": TARGET_SHA256, "target_sizes": TARGET_SIZES, "changed_slot_count": audit["changes"]["changed_slot_count"]}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_build(args: argparse.Namespace) -> int:
    manifest = build_candidate(args.input_root, args.output_root, args.audit_path, args.manifest_path)
    print(json.dumps({"status": "ok", "manifest": manifest, "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_verify_private(args: argparse.Namespace) -> int:
    report = verify_private_candidate(args.output_root)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("hash", help="derive and verify the pinned private target profile")
    build = commands.add_parser("build", help="write the complete eleven-file private candidate")
    build.add_argument("--input-root", type=Path, default=PREDECESSOR_ROOT)
    build.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    build.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
    build.add_argument("--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    verify = commands.add_parser("verify-private", help="rebuild and compare the private candidate")
    verify.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            return command_hash(args)
        if args.command == "build":
            return command_build(args)
        if args.command == "verify-private":
            return command_verify_private(args)
        raise Wave29Error(f"unknown command: {args.command}")
    except (OSError, ValueError, Wave29Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
