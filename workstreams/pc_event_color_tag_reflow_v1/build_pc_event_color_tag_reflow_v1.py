#!/usr/bin/env python3
"""Build a private PC-only PK event color-tag LF reflow candidate.

This is deliberately a seven-record, literal-target candidate.  It starts
from the exact installed W45 Steam PC table and allows only the reviewed
whitespace/line-break topology of those records to move.  It has no Steam
write, transaction, Git, network, or release capability.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_DIRNAME = "candidate"
STEAM_PK_EVENT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin")
PRISTINE_PC_JP_EVENT = Path(
    r"F:\Games\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
    r"\jp-runtime-wave05-20260715-v1\originals\MSG_PK\JP\msgev.bin"
)
W49_STATIC_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_static_quality_wave49_v1"
    / "build_pc_event_static_quality_wave49_v1.py"
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


SCHEMA = "nobu16.kr.pc-event-color-tag-reflow.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-color-tag-reflow-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-color-tag-reflow-manifest.v1"
PK_MAX_LINE_PX = 912
INPUT_RECORD_COUNT = 17_916
PRISTINE_JP_RECORD_COUNT = 17_910
W31_WIDTH_UTILITY_SHA256 = "71F88ECA04D74BEB2A31B56A27889E6B59FF217A673582AF0FE0AFAB15390A7A"
W49_STATIC_BUILDER_SHA256 = "1DBCE43D5E826AE47EF6ED82044733B82BA448043E264CA19C31A1E9AD4C6065"
W49_STATIC_IDS_SHA256 = "93B0358F50C40FBE32420A1072C4218D32CC51D735D7EBFADA06A48E9C9CFD4D"
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
LAYOUT_WHITESPACE_RE = re.compile(r"\s+")


class ColorTagReflowError(RuntimeError):
    """Raised when a pin, source constraint, or private-output guard drifts."""


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class SourceSpec:
    path: Path
    profile: Profile
    record_count: int
    role: str


@dataclass(frozen=True)
class Change:
    entry_id: int
    current_utf16le_sha256: str
    target: str
    target_utf16le_sha256: str
    pc_source_utf16le_sha256: Mapping[str, str]
    pc_jp_anchors: tuple[str, ...]
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
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Exact installed W45 Steam PC Korean input.  Any byte drift stops the build.
W45_INPUT_PROFILE = Profile(
    994_739,
    "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    990_828,
    "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
)

# Exact packed/raw result of applying only CHANGES to W45_INPUT_PROFILE.
TARGET_PROFILE = Profile(
    994_743,
    "AC1398EA909295AFA966D29E98F49F4F1B6C65D0BA870A51024721F91AB30D79",
    990_832,
    "1A65DB1B7206B98D5A2600261064862A2E49DE52409DEB18EB4D07B955F25EC9",
)

PC_SOURCE_SPECS: Mapping[str, SourceSpec] = {
    "JP": SourceSpec(
        PRISTINE_PC_JP_EVENT,
        Profile(
            555_784,
            "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002",
            890_428,
            "4A916CA6837C4F8FC2D8B6254ECBEF26339558D2DDFEBF5A1637F8426F5918DE",
        ),
        PRISTINE_JP_RECORD_COUNT,
        "reading_and_natural_clause_boundary_review",
    ),
    "EN": SourceSpec(
        Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin"),
        Profile(
            762_196,
            "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
            1_878_836,
            "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
        ),
        INPUT_RECORD_COUNT,
        "context_evidence_only",
    ),
    "SC": SourceSpec(
        Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin"),
        Profile(
            522_177,
            "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
            754_708,
            "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
        ),
        INPUT_RECORD_COUNT,
        "context_evidence_only",
    ),
    "TC": SourceSpec(
        Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin"),
        Profile(
            524_909,
            "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
            744_212,
            "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
        ),
        INPUT_RECORD_COUNT,
        "context_evidence_only",
    ),
}

# This is the actual active-PC event-font evidence returned by the pinned
# width utility.  Target width values below are measured from this font.
FONT_EVIDENCE = {
    "g1n_size": 21_720_288,
    "g1n_table": 0,
    "outer_entry": 6,
    "resource": "RES_JP/res_lang.bin",
    "sha256": "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7",
    "size": 161_428_458,
    "table0_record_count": 8_372,
}


# The literals are intentional; there is no blanket or algorithmic reflow.
# Each target is the supplied review result, not text derived at runtime.
CHANGES = (
    Change(
        3237,
        "0251CAB54717B96163B3F9B37BBBF06C862C508BF841A234DE1A5D2DCDEA4E25",
        "아니, 적으로 돌아섰다는 말은\n정확하지 않다. 원래부터 \x1bCC아자이 가문\x1bCZ은\n\x1bCC아사쿠라\x1bCZ와 오랜 맹우였다.",
        "A27BBB67C5C04728EA406DD96B8BA60BBC9A5D3737E49610366752037BECC5E6",
        {
            "JP": "91566A7E99E4152B388991DE4A5F0CA5D933754DF8906CA68F08DCCA2AA023F4",
            "EN": "ED8A7CA32A2253D8F040AAFDC11E2D083A2DA3980FDF685076E294A0EE67DDE8",
            "SC": "70F2A064EBA63D0C049D0801CB35EE2F766A704141B88FC2FB51DC75DFA18C86",
            "TC": "46524B718B0DCB00668D999C9A4CF5CA54D9C91C0D70F87C220A77F101964849",
        },
        ("寝返り", "浅井家", "朝倉"),
        (672, 888, 600),
        "아자이 가문과 아사쿠라의 맹우 관계를 절 안에서 끊지 않는다.",
    ),
    Change(
        3477,
        "DB1E1DF343B776C02DFACB68DD5A052377D06138283D984F9F691C3D450C4D3F",
        "없다. 전에도 말했을 텐데.\n내가 보는 것은 \x1bCB오다 가문\x1bCZ이 아니다.\n천하다!",
        "22E378CC6182FF04F194C98993561FB89839ECCD3914E91A5E0BFA94B9D98E2A",
        {
            "JP": "C5D8A487C113DAFE9DB76FE1D796B99B9428DD02DF02512329D401F19BEEA33C",
            "EN": "FC777D2F0876714533304ACF4BBFD70B4FAA13EFDB61E905A8861444B9CB61E7",
            "SC": "CEF82648423EF31A15E8FEB6ED110AD625109AE19B0E9BF69D29D471F2F3C494",
            "TC": "A5196095F0173D2841ABFD85D7978ED32EAF4B5A6CE20B2C243E6BC2A6EE8B59",
        },
        ("織田家", "天下だ"),
        (600, 816, 168),
        "오다 가문과 천하를 대조하는 발화의 마침을 보존한다.",
    ),
    Change(
        3832,
        "AA66634ED0E9E93A16FCBE3E89F651F8C9C60FF0F5E1BA671D2AAA5329F04725",
        "……그렇군요. 그럼\n\x1bCA호소카와 하루모토\x1bCZ가\n주군이 아니면 됩니까?",
        "CE9E82E962482F076400E7A73C841681C76C60D9CB3784E5826C8A58D8CB8EB6",
        {
            "JP": "A5E9E5EE93B1FCC50F2F159850543A1707A82F9F99C9027107B1ECC8CA09C17D",
            "EN": "DA6D0506A6E77EF40A229D7E1FA200797EE298D27ADEE6C728DA555E3DDFC3C7",
            "SC": "9D399BF0B31D2D854DD0E10ACF159C2374EFC3FA2931099052AC43C5EF01E119",
            "TC": "60983CC4B40AACAC2A6E0F9C364E44A0BC1F7EEA00181E258B43E1514D0B03B8",
        },
        ("細川晴元", "主"),
        (432, 456, 504),
        "호소카와 하루모토라는 색상 태그 안의 인명을 한 줄에 유지한다.",
    ),
    Change(
        3896,
        "50B5C65E97CEAB235EBD82C11AA9ABB0CDB46885F65E50A87D405FB4378C57C4",
        "\x1bCA모토하루\x1bCZ는 아버지의 명을 따라,\n\x1bCB깃카와\x1bCZ의 양자가 되어\n\x1bCA깃카와 모토하루\x1bCZ로 이름을 바꿨다.",
        "A491D3981BE362B352DA8D77780B689D543892584F9DBEAFE6D6A32BC9433C65",
        {
            "JP": "84FC328F3D9E081A6635B404E377F66585C8AB846E4C21BEDBBBAB363C1C97FB",
            "EN": "CDBAF85A6DA218E2B51335BEBFD25B1FD5073A679C1EF3F2AEAF622B726504D0",
            "SC": "4C72F308BD4FD61747CE87EE801E0C1BB5FBF04236EB795C43EE00361F01FC93",
            "TC": "5CA01BFDAEC740E9DF96E041E9D00A779E1A6510078BACD4888F779C80E46860",
        },
        ("元春", "吉川家", "吉川元春"),
        (720, 480, 768),
        "양자 입적 뒤 개명이라는 원문 절 경계를 보존한다.",
    ),
    Change(
        3919,
        "08518874A82B80A1642AD9DBB24BF59419769829380A47A8045DD20F49F31B94",
        "\x1bCB고바야카와 가문\x1bCZ의 무력을 다시\n살리려고, \x1bCA모토나리\x1bCZ는\n\x1bCA오우치 요시타카\x1bCZ까지 끌어들여 움직였다.",
        "1E19617282E2AEB254544CDFCBF1EE20B20B7FD38573B8AA81088DE4C2EEA6DD",
        {
            "JP": "2E4FE98BA98CC5FB8BCBF2D86A8F5AC04076E1F0E9128488C54BBA121CD8A28F",
            "EN": "3B2FAC16E42554893A23D1FE328E27941CA5661AADBF30A146B8C2DFD48E5C2E",
            "SC": "DD977A5225E2F83851B545C073CDE30E9B98A3C04FC3F95EC124B11E4F2FF825",
            "TC": "04732A48171040BDF891D1D73F1A628D933BCECBBB80ABBAFAE928452CC4E930",
        },
        ("小早川家", "元就", "大内義隆"),
        (696, 480, 912),
        "고바야카와 무력 활용과 오우치 요시타카 연루라는 순서를 유지한다.",
    ),
    Change(
        4011,
        "D6B1B05152AA4FDEC01DE266D8523A1ECAFD8BA41488D49E504A199831336B1B",
        "그리하여 세력으로서의\n'\x1bCB호소카와 가문\x1bCZ'은,\n'\x1bCB미요시 가문\x1bCZ'으로 탈바꿈해 갔다.",
        "24868072A9BCBCAB9652B1742D66C799D3DF42EA62D3F46D92E9E5DEDAB0BCC1",
        {
            "JP": "37D4C731809ECA54334B1AE4C31655940C6F0D57609843CC321C994B540A84E6",
            "EN": "7AEFBA6C57F67D5D66B854C85F1F2A64D40DA8D488A2156FB518D6BE0C3B3CDC",
            "SC": "8A8E1D1CA9DA80584F3C28EC0E7D9195294F9B8A003C7F7DDFF825CC9D4BED00",
            "TC": "15C53D29C72798F95D728BCEEACE509CD48DD5141367220A30D8B7A9026348E2",
        },
        ("細川家", "三好家"),
        (504, 432, 768),
        "호소카와 가문에서 미요시 가문으로의 탈바꿈을 두 인용구 단위로 둔다.",
    ),
    Change(
        4020,
        "0BA4B6B757BD5498DBBBD61ED96D4C4091FA58121E1FA96F4EB7CB3D09537480",
        "'오와리의 호랑이'\n\x1bCA오다 노부히데\x1bCZ가 세상을 떠났다.\n그 죽음은 \x1bCB오다 가문\x1bCZ을 크게 뒤흔들었다.",
        "F704E8AA4F5BB10107D3F9DC0A176EAB256C801C40CE40D55DC8F9095494B591",
        {
            "JP": "4AD594F844E46B56B705C463C44C8469C20FCC0A874C9A667992FABD33E75F93",
            "EN": "01E5C4F24E4DE9F87068350A8EEA64D9511F5F6C2FA42252A8FC153A08EDFE32",
            "SC": "D5D3FB3D6CA583432D51AE3EDF779D46ABAC5A190179C0CD6348DDDC0CD8912B",
            "TC": "FDCAC5E531738084EACE278C1B38F26E948A15BDC3986542BB32DEB2FB9A73E5",
        },
        ("尾張の虎", "織田信秀", "織田家"),
        (408, 720, 912),
        "오와리의 호랑이, 오다 노부히데의 죽음, 오다 가문의 동요를 절 단위로 둔다.",
    ),
)

# These records stay out of this candidate even though several were part of
# W49's broader tag-internal LF audit.  8510 is a semantic hold, not a reflow.
HARD_HOLD_IDS = (3202, 3900, 3934, 4140, 8723, 9359, 10045)
SEMANTIC_HOLD_IDS = (8510,)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ColorTagReflowError(message)


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


def require_profile(packed: bytes, raw: bytes, profile: Profile, label: str) -> None:
    require(len(packed) == profile.size, f"{label} packed size differs")
    require(sha256_bytes(packed) == profile.sha256, f"{label} packed SHA-256 differs")
    require(len(raw) == profile.raw_size, f"{label} raw size differs")
    require(sha256_bytes(raw) == profile.raw_sha256, f"{label} raw SHA-256 differs")


def reject_switch(path: Path, label: str) -> Path:
    """Refuse any Nintendo Switch path before it can be read."""
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise ColorTagReflowError(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ColorTagReflowError(f"{label} escapes private tmp root: {resolved}") from exc
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
    checked = reject_switch(path, label)
    packed = checked.read_bytes()
    try:
        header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise ColorTagReflowError(f"{label} cannot be parsed as a wrapped message table") from exc
    require_profile(packed, raw, profile, label)
    require(len(table.texts) == record_count, f"{label} record count differs")
    require(rebuild_message_table(table, table.texts) == raw, f"{label} raw table round-trip differs")
    if require_packed_round_trip:
        require(recompress_wrapper(raw, header) == packed, f"{label} packed round-trip differs")
    return TableResource(packed, header, raw, table)


def load_width_utility() -> Any:
    require(W31_WIDTH_UTILITY.is_file(), "W31 actual-font utility is absent")
    require(
        sha256_path(W31_WIDTH_UTILITY) == W31_WIDTH_UTILITY_SHA256,
        "W31 actual-font utility hash differs",
    )
    spec = importlib.util.spec_from_file_location("color_tag_reflow_width_utility", W31_WIDTH_UTILITY)
    if spec is None or spec.loader is None:
        raise ColorTagReflowError("cannot load W31 actual-font utility")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def w49_id_hash(ids: tuple[int, ...]) -> str:
    return sha256_bytes((json.dumps(list(ids), separators=(",", ":")) + "\n").encode("utf-8"))


def load_w49_static_ids() -> frozenset[int]:
    """Load only W49's declared ID set; it never opens its candidate/output."""
    require(W49_STATIC_BUILDER.is_file(), "W49 static builder is absent")
    require(
        sha256_path(W49_STATIC_BUILDER) == W49_STATIC_BUILDER_SHA256,
        "W49 static builder hash differs",
    )
    spec = importlib.util.spec_from_file_location("color_tag_reflow_w49_ids", W49_STATIC_BUILDER)
    if spec is None or spec.loader is None:
        raise ColorTagReflowError("cannot load W49 static ID declaration")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    ids = tuple(int(change.entry_id) for change in module.CHANGES)
    require(w49_id_hash(ids) == W49_STATIC_IDS_SHA256, "W49 static ID declaration differs")
    require(len(ids) == len(set(ids)), "W49 static ID declaration contains duplicates")
    return frozenset(ids)


def layout_whitespace_stripped(value: str) -> str:
    """Retain every non-whitespace code point while allowing reviewed LF moves."""
    return LAYOUT_WHITESPACE_RE.sub("", value)


def validate_change_declaration(
    change: Change,
    current: TableResource,
    width: Any,
    advance: Any,
    sources: Mapping[str, TableResource],
) -> tuple[int, int, int]:
    require(text_hash(change.target) == change.target_utf16le_sha256, f"{change.entry_id} target hash differs")
    require(set(change.pc_source_utf16le_sha256) == set(sources), f"{change.entry_id} source hash set differs")
    for language, source in sources.items():
        require(change.entry_id < len(source.table.texts), f"{change.entry_id} outside {language} source table")
        require(
            text_hash(source.table.texts[change.entry_id]) == change.pc_source_utf16le_sha256[language],
            f"{change.entry_id} {language} source text hash differs",
        )
    jp_text = sources["JP"].table.texts[change.entry_id]
    for anchor in change.pc_jp_anchors:
        require(anchor in jp_text, f"{change.entry_id} lacks PC JP reading/context anchor {anchor!r}")

    # ESC sequence, runtime tokens, printf tokens, C0 controls, and outer
    # whitespace are immutable.  Only internal layout whitespace may differ.
    before = current.table.texts[change.entry_id]
    require(text_hash(before) == change.current_utf16le_sha256, f"{change.entry_id} W45 preimage differs")
    require(
        width.protected_nonlayout_signature(before) == width.protected_nonlayout_signature(change.target),
        f"{change.entry_id} changes ESC/runtime/printf/control/outer whitespace",
    )
    require(
        layout_whitespace_stripped(before) == layout_whitespace_stripped(change.target),
        f"{change.entry_id} changes a non-whitespace character",
    )
    require("\r" not in before and "\r" not in change.target, f"{change.entry_id} has CR line-break topology")
    widths = width.line_widths(change.target, advance)
    require(len(widths) == 3, f"{change.entry_id} must remain exactly three lines")
    require(max(widths) <= PK_MAX_LINE_PX, f"{change.entry_id} exceeds {PK_MAX_LINE_PX}px")
    require(widths == change.target_line_widths_px, f"{change.entry_id} actual font widths differ")
    return widths


def source_evidence_manifest() -> dict[str, Any]:
    return {
        language: {
            "path": str(spec.path),
            **profile_dict(spec.profile),
            "record_count": spec.record_count,
            "role": spec.role,
        }
        for language, spec in PC_SOURCE_SPECS.items()
    }


def prepare_candidate() -> CandidateBundle:
    change_ids = tuple(change.entry_id for change in CHANGES)
    require(len(CHANGES) == 7, "candidate must contain exactly seven records")
    require(change_ids == tuple(sorted(change_ids)), "candidate IDs must be sorted")
    require(len(change_ids) == len(set(change_ids)), "candidate has duplicate IDs")
    held_ids = set(HARD_HOLD_IDS) | set(SEMANTIC_HOLD_IDS)
    require(not (set(change_ids) & held_ids), "a hard or semantic hold entered the candidate")
    w49_static_ids = load_w49_static_ids()
    require(not (set(change_ids) & w49_static_ids), "candidate overlaps W49 static IDs")

    current = load_table(
        STEAM_PK_EVENT,
        W45_INPUT_PROFILE,
        INPUT_RECORD_COUNT,
        "W45 Steam PC PK event input",
        require_packed_round_trip=True,
    )
    sources = {
        language: load_table(
            spec.path,
            spec.profile,
            spec.record_count,
            f"PC {language} source/context evidence",
            require_packed_round_trip=False,
        )
        for language, spec in PC_SOURCE_SPECS.items()
    }
    width = load_width_utility()
    advance, font = width.load_event_font()
    require(dict(font) == FONT_EVIDENCE, "actual PC event-font evidence differs")

    target_texts = list(current.table.texts)
    record_audit: list[dict[str, Any]] = []
    for change in CHANGES:
        widths = validate_change_declaration(change, current, width, advance, sources)
        target_texts[change.entry_id] = change.target
        record_audit.append(
            {
                "id": change.entry_id,
                "current_utf16le_sha256": change.current_utf16le_sha256,
                "target_utf16le_sha256": change.target_utf16le_sha256,
                "pc_source_utf16le_sha256": dict(change.pc_source_utf16le_sha256),
                "pc_jp_anchors": list(change.pc_jp_anchors),
                "target_line_widths_px": list(widths),
                "target_reading_and_clause_boundary_rechecked_with_pc_jp": True,
                "rationale": change.rationale,
            }
        )

    candidate_raw = rebuild_message_table(current.table, tuple(target_texts))
    candidate_packed = recompress_wrapper(candidate_raw, current.header)
    require_profile(candidate_packed, candidate_raw, TARGET_PROFILE, "candidate target")
    header, decoded = decompress_wrapper(candidate_packed)
    candidate_table = parse_message_table(decoded)
    require(rebuild_message_table(candidate_table, candidate_table.texts) == decoded, "candidate raw round-trip differs")
    require(recompress_wrapper(decoded, header) == candidate_packed, "candidate packed round-trip differs")
    changed_ids = tuple(
        index
        for index, (before, after) in enumerate(zip(current.table.texts, candidate_table.texts))
        if before != after
    )
    require(changed_ids == change_ids, "candidate changed ID scope differs")
    for held_id in (*HARD_HOLD_IDS, *SEMANTIC_HOLD_IDS):
        require(
            current.table.texts[held_id] == candidate_table.texts[held_id],
            f"held ID {held_id} changed",
        )

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "pristine_pc_jp_backup_same_resource": True,
            "pc_jp_role": PC_SOURCE_SPECS["JP"].role,
            "pc_en_sc_tc_role": "context_evidence_only",
            "switch_path_or_file_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "input": {
            "relative": "MSG_PK/JP/msgev.bin",
            **profile_dict(W45_INPUT_PROFILE),
        },
        "pc_source_evidence": source_evidence_manifest(),
        "font": dict(font),
        "pk_max_line_px": PK_MAX_LINE_PX,
        "target": {
            "relative": "MSG_PK/JP/msgev.bin",
            **profile_dict(TARGET_PROFILE),
        },
        "changed_record_count": len(CHANGES),
        "changed_ids": list(change_ids),
        "hard_holds": list(HARD_HOLD_IDS),
        "semantic_holds": list(SEMANTIC_HOLD_IDS),
        "w49_static_overlap_guard": {
            "builder_sha256": W49_STATIC_BUILDER_SHA256,
            "declared_ids_sha256": W49_STATIC_IDS_SHA256,
            "overlap": [],
        },
        "reflow_policy": {
            "literal_reviewed_targets_only": True,
            "blind_or_algorithmic_reflow": "forbidden",
            "immutable": ["ESC", "runtime", "printf", "control", "outer_whitespace"],
            "allowed": "reviewed internal whitespace and LF topology only",
        },
        "records": record_audit,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": {
            "relative": "MSG_PK/JP/msgev.bin",
            "input": profile_dict(W45_INPUT_PROFILE),
            "output": profile_dict(TARGET_PROFILE),
            "changed_ids": list(change_ids),
        },
        "changed_record_count": len(CHANGES),
        "hard_holds": list(HARD_HOLD_IDS),
        "semantic_holds": list(SEMANTIC_HOLD_IDS),
        "w49_static_overlap_guard": audit["w49_static_overlap_guard"],
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(candidate_packed, candidate_raw, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(not output.exists(), f"candidate output already exists: {output}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = require_private(Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT)), "candidate staging output")
    try:
        resource_path = stage / "MSG_PK" / "JP" / "msgev.bin"
        resource_path.parent.mkdir(parents=True, exist_ok=True)
        resource_path.write_bytes(bundle.packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(stage, output)
    finally:
        if stage.exists():
            require_private(stage, "candidate staging cleanup")
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(output.is_dir(), "private candidate is absent")
    expected_files = {
        "MSG_PK/JP/msgev.bin",
        "audit.v1.json",
        "candidate_manifest.v1.json",
    }
    actual_files = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }
    require(actual_files == expected_files, "private candidate file set differs")
    require(
        (output / "MSG_PK" / "JP" / "msgev.bin").read_bytes() == bundle.packed,
        "private event candidate differs",
    )
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require(
        (output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "private manifest differs",
    )
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_ids": [change.entry_id for change in CHANGES],
        "candidate_sha256": TARGET_PROFILE.sha256,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_ids": [change.entry_id for change in CHANGES],
            "candidate_sha256": TARGET_PROFILE.sha256,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
