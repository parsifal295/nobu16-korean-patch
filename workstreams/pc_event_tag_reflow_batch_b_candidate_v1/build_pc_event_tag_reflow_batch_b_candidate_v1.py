#!/usr/bin/env python3
"""Build a private direct-PC candidate for reviewed PK event tag reflow B.

This script reads only the exact installed W45 Korean PK event table, its
pristine PC Japanese counterpart, and the active PC event font.  It changes
exactly the ten literals reviewed in pc_event_tag_reflow_batch_b_v1 and writes
only a private candidate below tmp/.  It cannot write a Steam resource, run a
transaction, call Git, use a network, or publish a release.
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
REVIEW_REPORT = REPO / "workstreams" / "pc_event_tag_reflow_batch_b_v1" / "README_KO.md"

# Direct PC inputs only.  No Switch path, resource, or translation is opened.
STEAM_PC_KO_EVENT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin")
PRISTINE_PC_JP_EVENT = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
)
W31_WIDTH_UTILITY = (
    REPO
    / "workstreams"
    / "pc_event_quality_wave31_static_v1"
    / "build_pc_event_quality_wave31_static_v1.py"
)

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-tag-reflow-batch-b-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-tag-reflow-batch-b-candidate-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-tag-reflow-batch-b-candidate-manifest.v1"
PK_MAX_LINE_PX = 912
W45_RECORD_COUNT = 17_916
PRISTINE_PC_JP_RECORD_COUNT = 17_916
W31_WIDTH_UTILITY_SHA256 = "71F88ECA04D74BEB2A31B56A27889E6B59FF217A673582AF0FE0AFAB15390A7A"
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)


class CandidateError(RuntimeError):
    """Raised when a pinned input, reviewed literal, or private guard drifts."""


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
    target_line_widths_px: tuple[int, ...]
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


# Exact installed W45 Steam PC Korean input.  Any drift stops the build.
W45_INPUT_PROFILE = Profile(
    994_739,
    "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    990_828,
    "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
)

# Exact direct-PC pristine Japanese evidence table.  The explicit map below
# is per reviewed record; it does not assert a global table-ID equivalence.
PRISTINE_PC_JP_PROFILE = Profile(
    562_226,
    "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    894_800,
    "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
)

# Exact result of applying only CHANGES to W45_INPUT_PROFILE.
EXPECTED_OUTPUT_PROFILE = Profile(
    994_695,
    "5325EE8C902CE834A2C18D243A23D40393873ED167D925FF7F105E8CDA6299AF",
    990_784,
    "5AF0C7070FB7543F00329DCCC10469A6D5AC5A69DD2EF1E1E83928D3D711C45D",
)

FONT_EVIDENCE = {
    "g1n_size": 21_720_288,
    "g1n_table": 0,
    "outer_entry": 6,
    "resource": "RES_JP/res_lang.bin",
    "sha256": "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7",
    "size": 161_428_458,
    "table0_record_count": 8_372,
}

PC_JP_INDEX_MAP = {
    5297: 5297,
    5302: 5302,
    5817: 5817,
    5857: 5857,
    5884: 5884,
    6300: 6300,
    6396: 6396,
    6501: 6501,
    7735: 7735,
    7779: 7779,
}


# Exact final literals from the committed direct-PC Batch B report.
# 5302 and 5884 use the root-revised formulations.
CHANGES = (
    Change(
        5297,
        "111E8DA4B00136C305A6ABB438E9FE35159A086FD97E316154596964D21470A6",
        "\x1bCA하루마사\x1bCZ의 숙부인\n"
        "\x1bCA이시카와 다카노부\x1bCZ는 용장이었고,\n"
        "\x1bCB난부 가문\x1bCZ의 발전에 크게 이바지했다.",
        "9EBB11CDB5D9D40963D0DC5353FF076998C3B54EED190B5C438A7A2C536E2F14",
        5297,
        "7ADF222E8FBF6300266C34CB06E69B971A811A9521DF459CEA1F9890C1E37897",
        ("晴政", "石川高信", "勇将", "南部家"),
        (408, 744, 840),
        "하루마사의 숙부 이시카와 다카노부와 난부 가문 발전 기여를 보존했다.",
    ),
    Change(
        5302,
        "E2DBBCD9B16A1028E6C75F7264B8C0A2EC1B51836D941EB8BCE9304473AFCF1C",
        "그러나 \x1bCB오다 가문\x1bCZ과 \x1bCB사이토 가문\x1bCZ의\n"
        "화친이 깨져, \x1bCA노부나가\x1bCZ는\n"
        "상경하지 못했다.",
        "1D91D4494BFAEBA694F5D5981658F41B0FFC25E4ACB3E63463207ED9D782054B",
        5302,
        "9C6379017FA7E15940E5C78D3B43C9E855FDD04A4AAD79CBD22BFDBCE0B9C3B3",
        ("織田家", "斎藤家", "和睦", "信長", "上洛"),
        (768, 552, 384),
        "root-revised literal: 두 가문의 화친 결렬과 노부나가 상경 불발의 인과를 보존했다.",
    ),
    Change(
        5817,
        "D2837E4CBE574A44407F1EC0F1C113BB478CD855AED9DAA28903279061EB4593",
        "이날 \x1bCB모가미 가문\x1bCZ 당주\n"
        "\x1bCA모가미 요시모리\x1bCZ가 은거하고, 적자\n"
        "\x1bCA모가미 요시아키\x1bCZ가 새 당주가 되었다.",
        "02C5898CC5EE2378ACE2241880030504DD6335E8182D6411AD8A64C750C60913",
        5817,
        "9CE1C4BD85AF486B26849713F82C72E564EC7C907175FE167D67E58A75498FB2",
        ("最上家", "最上義守", "嫡男", "最上義光"),
        (504, 768, 840),
        "은거한 당주, 적자, 새 당주라는 관계를 유지했다.",
    ),
    Change(
        5857,
        "A032E9B8A8A0C666ABC2C2E2272A0AEA75FE15EC0767EEA7BB8328276EAE834D",
        "그 와중에, \x1bCC히젠\x1bCZ에서 주가\n"
        "\x1bCB쇼니 가문\x1bCZ을 무너뜨리고 세력을 넓힌\n"
        "\x1bCA류조지 다카노부\x1bCZ가 두각을 드러냈다.",
        "24C67703F1FF86F4EDE1365EFD09E08305B15FA9EA122F7F7C64C80BD9F53F2D",
        5857,
        "AFDCCFC85D6DBCA1CF4A74206313EAB0370560B94C4F5DD234693AA86C769774",
        ("肥前", "少弐家", "龍造寺隆信", "勢力を拡大"),
        (576, 816, 816),
        "히젠, 주가 전복, 세력 확대, 류조지 다카노부의 두각을 보존했다.",
    ),
    Change(
        5884,
        "C84E5341BA65B70F2D787C7581EBBAC330AD9C65CDBF961DA3428DCDCB256DFA",
        "서로 불만을 품은 채였지만,\n"
        "\x1bCB다테 가문\x1bCZ의 덴분의 난은 끝났다.\n"
        "\x1bCA하루무네\x1bCZ를 당주로 새 출발을 맞았다……",
        "0CDDCBD019EAE7EA79A5FB8466CA82E1AC002DF025A66793BEB0362EFDA0BC5B",
        5884,
        "7C1FD4A91B07ED8F5CE0EE8442393C2C87CBA66F246B5556366532AEC381CFD2",
        ("伊達家", "天文の乱", "晴宗", "新たな歩み"),
        (624, 744, 912),
        "root-revised literal: 하루무네를 당주로 한 새 출발을 자연스러운 서술로 보존했다.",
    ),
    Change(
        6300,
        "6F9CC1D790B250D86D63A614A7427F7ECDF74A3BFF89D9DE0478F8598429A016",
        "\x1bCC에치젠\x1bCZ의 센고쿠 다이묘\n"
        "\x1bCB아사쿠라 가문\x1bCZ의 역사는\n"
        "이렇게 막을 내렸다.",
        "F4984DD22F3419C750580928B1CC9EF0CBE3FA163D5FA55EC801E5E4FCEB2C57",
        6300,
        "162A38B8A493FA018A841E109320D13F3F63425AB934A20D2F4098CC67026916",
        ("越前", "戦国大名", "朝倉家", "幕を閉じた"),
        (528, 528, 456),
        "에치젠의 센고쿠 다이묘 아사쿠라 가문 역사 종결을 보존했다.",
    ),
    Change(
        6396,
        "E91B1C15EB52F0FC544F3F70FDEE1B7D7F808E56EC326F75932E37DB8123EA4D",
        "\x1bCA가네사다\x1bCZ의 귀환을 바라는 이들도\n"
        "나타나, \x1bCB조소카베 가문\x1bCZ의 지배는\n"
        "흔들리고 있었다.",
        "8CD535360DCD73D493202545809539A22D29A15BE3CFB25E1ACAE2C83A17DB59",
        6396,
        "EF5F69DA944ED448C9FDE2C1FCC6B3196D0ADA095B0C4C8E76FA5AF692FE3EE3",
        ("兼定", "長宗我部家", "動揺"),
        (744, 720, 384),
        "가네사다 귀환 희망자와 조소카베 가문 지배의 동요를 보존했다.",
    ),
    Change(
        6501,
        "0FA3151A6D7A77CA4FBC947EAB2033713003F4D661BB6F217A47778408A21A8E",
        "나가시노 전투에서 대패한\n"
        "\x1bCA다케다 가쓰요리\x1bCZ는 소수의 측근만\n"
        "데리고 \x1bCC가이\x1bCZ로 향하고 있었다.",
        "A12AA04B4584401F2687F845BEBC0B7874836B1A6C33D9249FF5C9E6AA7E6FEC",
        6501,
        "6C601F512F1DFF6C3413F7E07221AFBFC7152E42DE22A3B3DE23410158285E97",
        ("長篠", "武田勝頼", "わずかな供回り", "甲斐"),
        (576, 744, 672),
        "나가시노 패배, 소수의 측근, 가이로 향함을 보존했다.",
    ),
    Change(
        7735,
        "A92E3E5466A294B1778DCB68A04C4FA8BD7EAF2B9A104DCE1A8AD21256AEB039",
        "거리도 짧고, 아내의 친정 \x1bCB호조 가\x1bCZ와도\n"
        "가까워 \x1bCA가쓰요리\x1bCZ는\n"
        "여기서 \x1bCC이와도노성\x1bCZ을 택한다…",
        "93EE82C6E72FA7BF5E15C6D2E0C51E3DF664B5A210EE897D822EF0ABD52EAC8C",
        7735,
        "44D75F0DEB16D89B020C9C723680E55BF170E3DFBEA5155828871E2CBFC9B19F",
        ("距離的な面", "北条家", "勝頼", "岩殿城"),
        (864, 408, 672),
        "거리와 아내 친정 호조 가문 근접성, 이와도노성 선택을 보존했다.",
    ),
    Change(
        7779,
        "CB903998B9614AA166A968216913344884A964DEBF210FCEE6E89DDA8EB472CA",
        "\x1bCC나가시노\x1bCZ 전투에서 대패한\n"
        "뒤, \x1bCA다케다 가쓰요리\x1bCZ는\n"
        "가문의 개혁을 서둘렀다.",
        "E6A7C01124574220B46E35C12D89872A7B272F496A6A904605FC715F6D444508",
        7779,
        "10E975129FB5C534086471B07885F6BC436100F34AFF9C1EFD0B9D5EF96C3223",
        ("長篠", "武田勝頼", "家中の改革"),
        (576, 504, 552),
        "나가시노 전투 대패 뒤 다케다 가쓰요리의 가문 개혁을 보존했다.",
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
    require(
        sha256_path(W31_WIDTH_UTILITY) == W31_WIDTH_UTILITY_SHA256,
        "pinned PC event-font utility hash differs",
    )
    spec = importlib.util.spec_from_file_location("tag_reflow_batch_b_event_font", W31_WIDTH_UTILITY)
    if spec is None or spec.loader is None:
        raise CandidateError("cannot load pinned PC event-font utility")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def protected_nonlayout_signature(value: str) -> dict[str, Any]:
    """Keep renderer/runtime tokens while allowing reviewed Korean wording edits."""
    escapes: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token at {cursor}")
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
    """Reject manual LF inside a complete C[A-C]...CZ span."""
    active: str | None = None
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"{entry_id} malformed ESC token")
            if token == "\x1bCZ":
                require(active is not None, f"{entry_id} has unmatched color close")
                active = None
            else:
                require(token in ("\x1bCA", "\x1bCB", "\x1bCC"), f"{entry_id} has unsupported color token")
                require(active is None, f"{entry_id} nests color spans")
                active = token
            cursor += 3
            continue
        if character == "\n":
            require(active is None, f"{entry_id} has LF inside a color span")
        elif character == "\r":
            raise CandidateError(f"{entry_id} has CR line break")
        elif unicodedata.category(character) == "Cc":
            raise CandidateError(f"{entry_id} has unexpected control U+{ord(character):04X}")
        cursor += 1
    require(active is None, f"{entry_id} leaves a color span open")


def report_display(value: str) -> str:
    return (
        value.replace("\x1bCA", "‹A›")
        .replace("\x1bCB", "‹B›")
        .replace("\x1bCC", "‹C›")
        .replace("\x1bCZ", "</>")
        .replace("\n", "⏎")
    )


def require_report_literals() -> None:
    require(REVIEW_REPORT.is_file(), "committed Batch B review report is absent")
    report = REVIEW_REPORT.read_text(encoding="utf-8")
    tick = chr(96)
    for change in CHANGES:
        expected = "- 권고 target: " + tick + report_display(change.target) + tick
        require(expected in report, f"{change.entry_id} target differs from committed review report")
    by_id = {change.entry_id: change for change in CHANGES}
    require(
        by_id[5302].target.startswith(
            "그러나 \x1bCB오다 가문\x1bCZ과 \x1bCB사이토 가문\x1bCZ의\n화친이 깨져,"
        ),
        "5302 is not root-revised literal",
    )
    require(
        by_id[5884].target.endswith("\x1bCA하루무네\x1bCZ를 당주로 새 출발을 맞았다……"),
        "5884 is not root-revised literal",
    )


def validate_change(
    change: Change,
    current: TableResource,
    jp: TableResource,
    width_utility: Any,
    advance: Callable[[str], int],
) -> tuple[int, ...]:
    require(change.entry_id in PC_JP_INDEX_MAP, f"{change.entry_id} lacks PC JP mapping")
    require(PC_JP_INDEX_MAP[change.entry_id] == change.jp_index, f"{change.entry_id} PC JP mapping differs")
    require(change.entry_id < len(current.table.texts), f"{change.entry_id} outside W45 table")
    require(change.jp_index < len(jp.table.texts), f"{change.entry_id} outside pristine PC JP table")
    current_text = current.table.texts[change.entry_id]
    jp_text = jp.table.texts[change.jp_index]
    require(text_hash(current_text) == change.current_utf16le_sha256, f"{change.entry_id} W45 preimage differs")
    require(text_hash(change.target) == change.target_utf16le_sha256, f"{change.entry_id} target hash differs")
    require(text_hash(jp_text) == change.jp_utf16le_sha256, f"{change.entry_id} PC JP evidence differs")
    for anchor in change.jp_anchors:
        require(anchor in jp_text, f"{change.entry_id} lacks PC JP anchor {anchor!r}")
    require(
        protected_nonlayout_signature(current_text) == protected_nonlayout_signature(change.target),
        f"{change.entry_id} changes ESC/runtime/printf/control/outer-whitespace signature",
    )
    line_count = change.target.count("\n") + 1
    require(1 <= line_count <= 3 and "\r" not in change.target, f"{change.entry_id} must have 1–3 LF lines")
    assert_color_spans_complete_and_lf_external(change.target, change.entry_id)
    widths = width_utility.line_widths(change.target, advance)
    require(len(widths) == line_count, f"{change.entry_id} width parser line count differs")
    require(max(widths) <= PK_MAX_LINE_PX, f"{change.entry_id} exceeds {PK_MAX_LINE_PX}px")
    require(widths == change.target_line_widths_px, f"{change.entry_id} actual font widths differ")
    return widths


def prepare_candidate() -> CandidateBundle:
    change_ids = tuple(change.entry_id for change in CHANGES)
    expected_ids = (5297, 5302, 5817, 5857, 5884, 6300, 6396, 6501, 7735, 7779)
    require(change_ids == expected_ids, "candidate IDs differ from reviewed scope")
    require(len(change_ids) == len(set(change_ids)) == 10, "candidate must contain exactly ten unique records")
    require(set(PC_JP_INDEX_MAP) == set(change_ids), "PC JP mapping scope differs")
    require_report_literals()

    current = load_table(
        STEAM_PC_KO_EVENT,
        W45_INPUT_PROFILE,
        W45_RECORD_COUNT,
        "W45 Steam PC Korean PK event",
        require_packed_round_trip=True,
    )
    jp = load_table(
        PRISTINE_PC_JP_EVENT,
        PRISTINE_PC_JP_PROFILE,
        PRISTINE_PC_JP_RECORD_COUNT,
        "pristine direct-PC Japanese PK event",
        require_packed_round_trip=False,
    )
    width_utility = load_width_utility()
    advance, font_evidence = width_utility.load_event_font()
    require(dict(font_evidence) == FONT_EVIDENCE, "active PC event-font evidence differs")

    target_texts = list(current.table.texts)
    records: list[dict[str, Any]] = []
    for change in CHANGES:
        widths = validate_change(change, current, jp, width_utility, advance)
        target_texts[change.entry_id] = change.target
        records.append(
            {
                "id": change.entry_id,
                "jp_index": change.jp_index,
                "current_ko_utf16le_sha256": change.current_utf16le_sha256,
                "target_ko_utf16le_sha256": change.target_utf16le_sha256,
                "pc_jp_utf16le_sha256": change.jp_utf16le_sha256,
                "pc_jp_anchors": list(change.jp_anchors),
                "current_ko_text": current.table.texts[change.entry_id],
                "target_ko_text": change.target,
                "pc_jp_text": jp.table.texts[change.jp_index],
                "target_line_widths_px": list(widths),
                "manual_lf_inside_color_span": False,
                "rationale": change.rationale,
            }
        )

    raw = rebuild_message_table(current.table, tuple(target_texts))
    packed = recompress_wrapper(raw, current.header)
    header, reparsed_raw = decompress_wrapper(packed)
    reparsed = parse_message_table(reparsed_raw)
    require(reparsed_raw == raw, "candidate LZ4 decompression differs")
    require(rebuild_message_table(reparsed, reparsed.texts) == raw, "candidate parser round-trip differs")
    require(recompress_wrapper(reparsed_raw, header) == packed, "candidate LZ4 re-compression differs")
    require(reparsed.texts == tuple(target_texts), "candidate table differs after round-trip")
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
            "inputs_opened": [
                "installed_w45_korean_pk_event",
                "pristine_direct_pc_japanese_pk_event",
                "active_pc_event_font",
                "committed_direct_pc_batch_b_review_report",
            ],
            "non_pc_sources_opened": False,
            "steam_game_resource_written": False,
            "transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
        },
        "font": dict(font_evidence),
        "layout_validation": {
            "min_line_count": 1,
            "max_line_count": 3,
            "max_line_px": PK_MAX_LINE_PX,
            "all_manual_lf_outside_color_spans": True,
            "tags_runtime_printf_controls_preserved": True,
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
    staging = require_private(
        output_root.parent / f".{output_root.name}.staging-{uuid.uuid4().hex}",
        "candidate staging",
    )
    try:
        event_path = staging / "MSG_PK" / "JP" / "msgev.bin"
        atomic_write(event_path, bundle.packed)
        require(sha256_path(event_path) == bundle.output_profile.sha256, "written candidate hash differs")
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
    require(actual_files == expected_files, "candidate contains unexpected files")
    return {
        "candidate_root": candidate_root.relative_to(REPO).as_posix(),
        "changed_cell_count": len(CHANGES),
        "output": profile_dict(bundle.output_profile),
        "steam_game_resource_written": False,
    }


def diff_check(candidate_root: Path) -> dict[str, Any]:
    candidate_root = require_private(candidate_root, "candidate root")
    current = load_table(
        STEAM_PC_KO_EVENT,
        W45_INPUT_PROFILE,
        W45_RECORD_COUNT,
        "W45 Steam PC Korean PK event",
        require_packed_round_trip=True,
    )
    candidate_path = candidate_root / "MSG_PK" / "JP" / "msgev.bin"
    require(candidate_path.is_file(), "candidate event resource is absent")
    packed = candidate_path.read_bytes()
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, "candidate parser round-trip differs")
    require(recompress_wrapper(raw, header) == packed, "candidate LZ4 round-trip differs")
    require_profile(packed, raw, EXPECTED_OUTPUT_PROFILE, "candidate output")
    changed_ids = tuple(
        index for index, (before, after) in enumerate(zip(current.table.texts, table.texts)) if before != after
    )
    expected_ids = tuple(change.entry_id for change in CHANGES)
    require(changed_ids == expected_ids, "candidate changed ID scope differs")
    for change in CHANGES:
        require(table.texts[change.entry_id] == change.target, f"{change.entry_id} candidate target differs")
    return {
        "candidate_root": candidate_root.relative_to(REPO).as_posix(),
        "changed_ids": list(changed_ids),
        "changed_cell_count": len(changed_ids),
        "output": profile_dict(EXPECTED_OUTPUT_PROFILE),
    }


def profile_report() -> dict[str, Any]:
    bundle = prepare_candidate()
    return {
        "input": profile_dict(W45_INPUT_PROFILE),
        "pc_jp_evidence": profile_dict(PRISTINE_PC_JP_PROFILE),
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
