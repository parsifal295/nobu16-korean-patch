#!/usr/bin/env python3
"""Build a private Steam-PC-only semantic event reflow candidate.

The candidate starts from the exact installed W45 Korean PK event table and
changes exactly eight reviewed records.  It has no Steam write, transaction,
Git, network, or release operation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_DIRNAME = "candidate"

# The only game inputs opened by this workstream are Steam PC's current Korean
# table and the separately preserved pristine Steam-PC Japanese table.
STEAM_PC_KO_EVENT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin")
PRISTINE_PC_JP_EVENT = Path(
    r"F:\Games\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
    r"\jp-runtime-wave05-20260715-v1\originals\MSG_PK\JP\msgev.bin"
)
W31_WIDTH_UTILITY = REPO / "workstreams" / "pc_event_quality_wave31_static_v1" / "build_pc_event_quality_wave31_static_v1.py"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-semantic-reflow.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-semantic-reflow-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-semantic-reflow-manifest.v1"
PK_MAX_LINE_PX = 912
W45_RECORD_COUNT = 17_916
PRISTINE_JP_RECORD_COUNT = 17_910
W31_WIDTH_UTILITY_SHA256 = "71F88ECA04D74BEB2A31B56A27889E6B59FF217A673582AF0FE0AFAB15390A7A"
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]")


class CandidateError(RuntimeError):
    """Raised when a source pin, target contract, or output guard drifts."""


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class Change:
    entry_id: int
    current_utf16le_sha256: str
    target: str
    target_utf16le_sha256: str
    jp_index: int
    jp_utf16le_sha256: str
    jp_anchors: tuple[str, ...]
    target_line_widths_px: tuple[int, int, int]
    rationale: str


@dataclass(frozen=True)
class TableResource:
    packed: bytes
    header: Any
    raw: bytes
    table: Any


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    raw: bytes
    output_profile: Profile
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Exact installed W45 Steam PC Korean PK event table.
W45_INPUT_PROFILE = Profile(
    994_739,
    "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    990_828,
    "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
)

# Pristine Steam-PC Japanese evidence table.  The eight reviewed event rows
# use the explicit same-index map below; this does not claim a global table map.
PRISTINE_PC_JP_PROFILE = Profile(
    555_784,
    "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002",
    890_428,
    "4A916CA6837C4F8FC2D8B6254ECBEF26339558D2DDFEBF5A1637F8426F5918DE",
)

# Exact packed/raw result of applying only CHANGES to W45_INPUT_PROFILE.
# It is intentionally a private-candidate profile, not a path to a Steam file.
EXPECTED_OUTPUT_PROFILE = Profile(
    994_735,
    "30CED81B2F9B3B02FE0F8EFFEA1D9CF05E513E854CCAC3B84C6B7213947EB429",
    990_824,
    "E2F6BA4CEFD9CE9CE670F62D91631073F228C8CF53306433397C701D63648D22",
)

PC_JP_INDEX_MAP = {
    3202: 3202,
    3900: 3900,
    3934: 3934,
    4140: 4140,
    8510: 8510,
    8723: 8723,
    9359: 9359,
    10045: 10045,
}

# Exact reviewed literals.  Every target has three physical lines; every
# manual LF sits between (not inside) complete color spans.
CHANGES = (
    Change(
        3202,
        "62C01D917F0F75C89170B82B6ABA01A7220AD8BD7748B3B6B789EB19C98C86CC",
        "\x1bCB카이 겐지\x1bCZ의 강호, \x1bCB다케다\x1bCZ.\n\x1bCB아시카가 일문\x1bCZ의 명문, \x1bCB이마가와\x1bCZ.\n\x1bCA이마가와\x1bCZ에서 독립해 \x1bCC간토\x1bCZ로 나선 \x1bCB호조\x1bCZ.",
        "2E361E2177EA5237AB694D484883BC156FA100555C62D1EB85723962798F42A9",
        3202,
        "4BDFEAF56DC981D976E02B4DFF695AE2AAAA4A55EFDDF3BC9220D3597C12D28A",
        ("甲斐源氏", "武田家", "今川家", "北条家"),
        (600, 744, 888),
        "색상 태그 내부의 수동 개행을 문장 경계로 옮기고, 원문의 가문·독립·간토 진출 관계를 자연스럽게 정리했다.",
    ),
    Change(
        3900,
        "BB1ED13F218AA142A2E2836CFAB571FAD32518BA83DF270E1384763EB99069E3",
        "\x1bCB오토모 가문\x1bCZ 제20대 당주,\n\x1bCA오토모 요시아키\x1bCZ의 적자. 다재다능하나,\n태어날 때부터 병약한 인물이었다.",
        "4E10CA2FFF0190527AE7513667B08E073020DD7D8A974D05F1DFF35B8BE0DD0A",
        3900,
        "24A3840D12A7DE2E9952EAF97B9DB598D717E9C7E8B2A0605B7BCE07264FC746",
        ("大友家", "大友義鑑", "生来病弱"),
        (576, 888, 768),
        "인물 소개의 당주·적자·병약이라는 핵심 정보를 보존하면서 이름 태그를 한 줄에 완결했다.",
    ),
    Change(
        3934,
        "E59DD8E0F89D20A74F299509963E101E658FF52C6CAB4F3CBCAB6EFBC3D913E6",
        "\x1bCA무라카미 요시키요\x1bCZ만 쓰러뜨리면,\n\x1bCC시나노 중부\x1bCZ와 \x1bCC시나노 북부\x1bCZ의 세력은\n내게 따른다. \x1bCA요시키요\x1bCZ를 짓밟아 주마!",
        "23B46CFB83B9BA014B992581EF2C8D05780E29A405FCD98CAE795C2532BAD59C",
        3934,
        "9F93A3E7A6B8220B21EF6885F4CA44A3A01FDE7BCD915586930D7BCDD456F7DE",
        ("村上義清", "中信", "北信", "完膚なきまで"),
        (744, 816, 864),
        "중신·북신 세력의 귀속 관계와 위협의 어조를 유지하고 모든 지명·인명 색상 범위를 온전하게 유지했다.",
    ),
    Change(
        4140,
        "DB689CB44B755D06FED92A1D6A3028E2980E2C1BF77BB16CD6DD06CAAD26BA54",
        "\x1bCB아사쿠라 가문\x1bCZ 당주·\n\x1bCA아사쿠라 요시카게\x1bCZ의 증조부의 형제이며,\n가문의 군사를 총괄한 중진이었다.",
        "127B5A503DA31D02EA1CD9F0AE23880BBF9DDA06E71C4B3B1634FB3CC0F36DB7",
        4140,
        "F41E6C1E422046F7B629A100D0A923A10AAED5050D9DFC59B3767FDDBBD6B937",
        ("朝倉家", "朝倉義景", "軍事を一手に司る"),
        (480, 912, 768),
        "가계 관계와 군사 총괄 역할을 유지하되 이름 색상 범위의 내부 개행을 제거했다.",
    ),
    Change(
        8510,
        "B959531E17BD32E2900FCD742D441A4B44457F82780EC2110069FD20BB869A7C",
        "겐페이토키쓰의 명가 위에\n\x1bCB도요토미 가문\x1bCZ이 군림하는\n\x1bCA히데요시\x1bCZ가 만든 새 시대의 시작이었다.",
        "60ADD2DA67A98CEAD703F26F344AE5CE432D8827B2734A2C76055E7FC0C7739B",
        8510,
        "C96D01D17E76E7A5309CE4833B15CE64E81D4DBCCE77AB6E2FA329D7F33EF3EC",
        ("源平藤橘", "豊臣家", "秀吉", "が作った"),
        (576, 576, 888),
        "주어와 관형 관계를 바로잡아 ‘히데요시가 만든 새 시대’라는 원문 의미를 복원하고 색상 태그를 완결했다.",
    ),
    Change(
        8723,
        "7FC999B2CF115C7DBC2BA3894FC82E9B3D7FF59C96C73B9B43BDB9064FD16A46",
        "\x1bCB아시나 가문\x1bCZ 18대 당주,\n\x1bCA아시나 모리타카\x1bCZ는 \x1bCB니카이도 가문\x1bCZ 출신.\n아내는 \x1bCA다테 데루무네\x1bCZ의 여동생이다.",
        "5E2A6515D1DF157877C21868A5ACB27D58779D1AE24A2A3066E525B1B36E5DC1",
        8723,
        "0D0EBBCACBF0B3F2B747399E3B95EA7FA72C903C0B9153C15E7970066FCB4A58",
        ("蘆名家", "蘆名盛隆", "二階堂家", "伊達輝宗"),
        (528, 888, 816),
        "가문 출신과 혼인 관계를 두 문장으로 명확히 하고 모든 고유명사 태그를 단위로 유지했다.",
    ),
    Change(
        9359,
        "223A8676CA720026DAAC471FAE35B2A1EE1204DD5982FCCDE9BB51413B5D136C",
        "실례하였소이다. 소인은 \x1bCC미노\x1bCZ 출신이오.\n\x1bCA아케치 주베에 미쓰히데\x1bCZ라 하오.\n\x1bCB에치젠 아사쿠라가\x1bCZ에 의탁 중이오.",
        "25A5E813E02B3A3F711769188186C9D728C72C491AB2CE75D10D750E7CED0091",
        9359,
        "6DCDC20B2511316B623CB3CDC1531E43340A8D0E3DE385BAA2D9396DDB82A136",
        ("美濃", "明智十兵衛光秀", "越前朝倉家"),
        (888, 720, 768),
        "자기소개·출신·의탁 관계를 원문 순서로 복원하고 색상 범위 안의 강제 개행을 제거했다.",
    ),
    Change(
        10045,
        "FE5241A59E7F9149FFA47935F6BA097CA66D19245564B348E17889B703111B7D",
        "그리고 \x1bCB다테\x1bCZ·\x1bCB사타케\x1bCZ를 규합하고\n\x1bCB오우의 여러 장수\x1bCZ까지 모은다면,\n\x1bCA내대신\x1bCZ과 일전을 벌일 수도 있겠지.",
        "EBE7780FCDF20D434295731E14872E48259B5D1D8A66C148C6C16D69B9DF10D9",
        10045,
        "B7A2579FF45842DD22A1B5822F4CC63F23E3A8CE552B5F72CE9D5985D1F557A4",
        ("伊達", "佐竹", "奥羽諸将", "内府"),
        (720, 720, 792),
        "다테·사타케·오우 제장의 규합이라는 원문 병렬 구조를 복원하고 태그 경계를 분리했다.",
    ),
)


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
    require(len(packed) == profile.size, f"{label} packed size differs")
    require(sha256_bytes(packed) == profile.sha256, f"{label} packed SHA-256 differs")
    require(len(raw) == profile.raw_size, f"{label} raw size differs")
    require(sha256_bytes(raw) == profile.raw_sha256, f"{label} raw SHA-256 differs")


def require_private(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise CandidateError(f"{label} escapes private tmp root: {resolved}") from exc
    require(resolved != root, f"{label} must be below private tmp root")
    return resolved


def load_table(
    path: Path,
    profile: Profile,
    record_count: int,
    label: str,
    *,
    require_packed_round_trip: bool,
) -> TableResource:
    require(path.is_file(), f"{label} is absent")
    packed = path.read_bytes()
    try:
        header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise CandidateError(f"{label} is not a valid wrapped message table") from exc
    require_profile(packed, raw, profile, label)
    require(len(table.texts) == record_count, f"{label} record count differs")
    require(rebuild_message_table(table, table.texts) == raw, f"{label} parse/rebuild identity differs")
    if require_packed_round_trip:
        require(recompress_wrapper(raw, header) == packed, f"{label} LZ4 round-trip differs")
    return TableResource(packed, header, raw, table)


def load_width_utility() -> Any:
    require(W31_WIDTH_UTILITY.is_file(), "pinned PC event-font utility is absent")
    require(sha256_path(W31_WIDTH_UTILITY) == W31_WIDTH_UTILITY_SHA256, "PC event-font utility hash differs")
    spec = importlib.util.spec_from_file_location("wave54_event_font", W31_WIDTH_UTILITY)
    if spec is None or spec.loader is None:
        raise CandidateError("cannot load pinned PC event-font utility")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def protected_nonlayout_signature(value: str) -> dict[str, Any]:
    """Keep every renderer/runtime control token while allowing semantic text edits."""
    escapes: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at offset {cursor}")
            escapes.append(token)
            cursor += 3
            continue
        if character not in ("\r", "\n") and unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        cursor += 1
    printf = list(PRINTF_RE.finditer(value))
    percent_offsets = {match.start() for match in printf}
    return {
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "esc_tokens": escapes,
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in percent_offsets
        ),
        "controls": controls,
    }


def assert_color_spans_complete_and_lf_external(value: str, entry_id: int) -> None:
    """Require C[A-C]...CZ spans to be complete and never contain a manual LF."""
    active: str | None = None
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"{entry_id} malformed ESC token")
            if token == "\x1bCZ":
                require(active is not None, f"{entry_id} has an unmatched color close")
                active = None
            else:
                require(token in ("\x1bCA", "\x1bCB", "\x1bCC"), f"{entry_id} has unsupported color token")
                require(active is None, f"{entry_id} nests color spans")
                active = token
            cursor += 3
            continue
        if character == "\n":
            require(active is None, f"{entry_id} has an LF inside a color span")
        elif character == "\r":
            raise CandidateError(f"{entry_id} has CR line breaks")
        elif unicodedata.category(character) == "Cc":
            raise CandidateError(f"{entry_id} has unexpected control U+{ord(character):04X}")
        cursor += 1
    require(active is None, f"{entry_id} leaves a color span open")


def validate_change(
    change: Change,
    current: TableResource,
    jp: TableResource,
    width_utility: Any,
    advance: Callable[[str], int],
) -> tuple[int, int, int]:
    require(change.entry_id in PC_JP_INDEX_MAP, f"{change.entry_id} lacks explicit PC JP map")
    require(PC_JP_INDEX_MAP[change.entry_id] == change.jp_index, f"{change.entry_id} JP map differs")
    require(change.entry_id < len(current.table.texts), f"{change.entry_id} is outside W45")
    require(change.jp_index < len(jp.table.texts), f"{change.entry_id} is outside pristine PC JP")
    before = current.table.texts[change.entry_id]
    jp_text = jp.table.texts[change.jp_index]
    require(text_hash(before) == change.current_utf16le_sha256, f"{change.entry_id} W45 preimage differs")
    require(text_hash(change.target) == change.target_utf16le_sha256, f"{change.entry_id} target hash differs")
    require(text_hash(jp_text) == change.jp_utf16le_sha256, f"{change.entry_id} PC JP evidence differs")
    for anchor in change.jp_anchors:
        require(anchor in jp_text, f"{change.entry_id} lacks PC JP anchor {anchor!r}")
    require(
        protected_nonlayout_signature(before) == protected_nonlayout_signature(change.target),
        f"{change.entry_id} changes ESC/runtime/printf/control/outer-whitespace signature",
    )
    require(change.target.count("\n") == 2 and "\r" not in change.target, f"{change.entry_id} must be exactly three LF lines")
    assert_color_spans_complete_and_lf_external(change.target, change.entry_id)
    widths = width_utility.line_widths(change.target, advance)
    require(len(widths) == 3, f"{change.entry_id} is not three lines after width parsing")
    require(max(widths) <= PK_MAX_LINE_PX, f"{change.entry_id} exceeds {PK_MAX_LINE_PX}px")
    require(widths == change.target_line_widths_px, f"{change.entry_id} actual font widths differ")
    return widths


def prepare_candidate() -> CandidateBundle:
    change_ids = tuple(change.entry_id for change in CHANGES)
    require(change_ids == tuple(sorted(change_ids)), "candidate IDs must be sorted")
    require(change_ids == (3202, 3900, 3934, 4140, 8510, 8723, 9359, 10045), "candidate IDs differ from reviewed scope")
    require(len(change_ids) == len(set(change_ids)) == 8, "candidate must contain exactly eight unique records")
    require(set(PC_JP_INDEX_MAP) == set(change_ids), "PC JP map scope differs")

    current = load_table(
        STEAM_PC_KO_EVENT,
        W45_INPUT_PROFILE,
        W45_RECORD_COUNT,
        "W45 Steam PC Korean event",
        require_packed_round_trip=True,
    )
    jp = load_table(
        PRISTINE_PC_JP_EVENT,
        PRISTINE_PC_JP_PROFILE,
        PRISTINE_JP_RECORD_COUNT,
        "pristine Steam PC Japanese event",
        require_packed_round_trip=False,
    )
    width_utility = load_width_utility()
    advance, font_evidence = width_utility.load_event_font()
    target_texts = list(current.table.texts)
    records: list[dict[str, Any]] = []

    for change in CHANGES:
        widths = validate_change(change, current, jp, width_utility, advance)
        target_texts[change.entry_id] = change.target
        records.append(
            {
                "id": change.entry_id,
                "jp_index": change.jp_index,
                "pc_jp_utf16le_sha256": change.jp_utf16le_sha256,
                "current_ko_utf16le_sha256": change.current_utf16le_sha256,
                "target_ko_utf16le_sha256": change.target_utf16le_sha256,
                "jp_text": jp.table.texts[change.jp_index],
                "current_ko_text": current.table.texts[change.entry_id],
                "target_ko_text": change.target,
                "pc_jp_anchors": list(change.jp_anchors),
                "target_line_widths_px": list(widths),
                "manual_lf_inside_color_span": False,
                "rationale": change.rationale,
            }
        )

    raw = rebuild_message_table(current.table, tuple(target_texts))
    packed = recompress_wrapper(raw, current.header)
    header, reparsed_raw = decompress_wrapper(packed)
    reparsed = parse_message_table(reparsed_raw)
    require(reparsed_raw == raw, "candidate decompression differs")
    require(rebuild_message_table(reparsed, reparsed.texts) == raw, "candidate parse/rebuild differs")
    require(recompress_wrapper(reparsed_raw, header) == packed, "candidate LZ4 re-compression differs")
    require(reparsed.texts == tuple(target_texts), "candidate text table differs")
    changed_ids = tuple(
        index for index, (before, after) in enumerate(zip(current.table.texts, reparsed.texts)) if before != after
    )
    require(changed_ids == change_ids, "candidate changed ID scope differs")

    output_profile = observed_profile(packed, raw)
    require_profile(packed, raw, EXPECTED_OUTPUT_PROFILE, "candidate output")
    audit = {
        "schema": AUDIT_SCHEMA,
        "candidate_only": True,
        "source_policy": {
            "platform": "Steam PC",
            "inputs_opened": ["installed_w45_korean_pk_event", "pristine_pc_japanese_event", "active_pc_event_font"],
            "non_pc_sources_opened": False,
            "steam_game_resource_written": False,
            "transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
        },
        "font": dict(font_evidence),
        "layout_validation": {
            "required_line_count": 3,
            "max_line_px": PK_MAX_LINE_PX,
            "all_manual_lf_outside_color_spans": True,
        },
        "input": profile_dict(W45_INPUT_PROFILE),
        "pc_jp_evidence": profile_dict(PRISTINE_PC_JP_PROFILE),
        "output": profile_dict(output_profile),
        "changed_ids": list(change_ids),
        "changed_cell_count": len(change_ids),
        "records": records,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": {
            "relative": "MSG_PK/JP/msgev.bin",
            "input": profile_dict(W45_INPUT_PROFILE),
            "output": profile_dict(output_profile),
            "changed_ids": list(change_ids),
        },
        "changed_cell_count": len(change_ids),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
    }
    return CandidateBundle(packed, raw, output_profile, audit, manifest)


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_candidate(bundle: CandidateBundle, output_root: Path) -> dict[str, Any]:
    output_root = require_private(output_root, "candidate output")
    require(not output_root.exists(), f"refusing to overwrite candidate output: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    staging = require_private(output_root.parent / f".{output_root.name}.staging-{uuid.uuid4().hex}", "candidate staging")
    try:
        event_path = staging / "MSG_PK" / "JP" / "msgev.bin"
        atomic_write(event_path, bundle.packed)
        require(sha256_path(event_path) == bundle.output_profile.sha256, "written candidate event hash differs")
        atomic_write(staging / "audit.v1.json", canonical_json(bundle.audit))
        atomic_write(staging / "candidate_manifest.v1.json", canonical_json(bundle.manifest))
        require(sha256_path(staging / "audit.v1.json") == bundle.manifest["audit_sha256"], "written audit hash differs")
        os.replace(staging, output_root)
    except Exception:
        if staging.exists():
            require_private(staging, "candidate staging cleanup")
            shutil.rmtree(staging)
        raise
    return {
        "candidate_root": output_root.relative_to(REPO).as_posix(),
        "changed_cell_count": len(CHANGES),
        "output": profile_dict(bundle.output_profile),
        "steam_game_resource_written": False,
    }


def verify_private(candidate_root: Path) -> dict[str, Any]:
    candidate_root = require_private(candidate_root, "candidate root")
    bundle = prepare_candidate()
    require(candidate_root.is_dir(), "candidate root is absent")
    event_path = candidate_root / "MSG_PK" / "JP" / "msgev.bin"
    require(event_path.is_file(), "candidate event resource is absent")
    require(event_path.read_bytes() == bundle.packed, "candidate event bytes differ")
    require((candidate_root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require(
        (candidate_root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "candidate manifest differs",
    )
    expected_files = {
        Path("MSG_PK/JP/msgev.bin"),
        Path("audit.v1.json"),
        Path("candidate_manifest.v1.json"),
    }
    actual_files = {path.relative_to(candidate_root) for path in candidate_root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, "candidate contains an unexpected file")
    return {
        "candidate_root": candidate_root.relative_to(REPO).as_posix(),
        "changed_cell_count": len(CHANGES),
        "output": profile_dict(bundle.output_profile),
        "steam_game_resource_written": False,
    }


def profile_report() -> dict[str, Any]:
    bundle = prepare_candidate()
    return {
        "input": profile_dict(W45_INPUT_PROFILE),
        "output": profile_dict(bundle.output_profile),
        "changed_ids": [change.entry_id for change in CHANGES],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / CANDIDATE_DIRNAME)
    verify_parser = subparsers.add_parser("verify-private")
    verify_parser.add_argument("--candidate-root", type=Path, default=TMP_ROOT / CANDIDATE_DIRNAME)
    subparsers.add_parser("profile")
    args = parser.parse_args()
    if args.command == "build":
        print(json.dumps(write_candidate(prepare_candidate(), args.output_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "verify-private":
        print(json.dumps(verify_private(args.candidate_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    print(json.dumps(profile_report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
