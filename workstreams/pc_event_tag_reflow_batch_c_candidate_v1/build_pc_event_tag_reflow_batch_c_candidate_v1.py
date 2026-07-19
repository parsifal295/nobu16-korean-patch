#!/usr/bin/env python3
"""Build a private direct-PC candidate for reviewed PK event tag reflow C.

This script reads only the exact installed W45 Korean PK event table, its
pristine PC Japanese counterpart, and the active PC event font.  It changes
exactly the ten literals reviewed in pc_event_tag_reflow_batch_c_v1 and writes
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
REVIEW_REPORT = REPO / "workstreams" / "pc_event_tag_reflow_batch_c_v1" / "README_KO.md"

# Direct PC inputs only.  No Switch path, resource, or translation is opened.
STEAM_PC_KO_EVENT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin")
PRISTINE_PC_JP_EVENT = Path(
    r"F:\Games\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
    r"\jp-runtime-wave05-20260715-v1\originals\MSG_PK\JP\msgev.bin"
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


SCHEMA = "nobu16.kr.pc-event-tag-reflow-batch-c-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-tag-reflow-batch-c-candidate-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-tag-reflow-batch-c-candidate-manifest.v1"
PK_MAX_LINE_PX = 912
W45_RECORD_COUNT = 17_916
PRISTINE_PC_JP_RECORD_COUNT = 17_910
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
    555_784,
    "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002",
    890_428,
    "4A916CA6837C4F8FC2D8B6254ECBEF26339558D2DDFEBF5A1637F8426F5918DE",
)

# Exact result of applying only CHANGES to W45_INPUT_PROFILE.
EXPECTED_OUTPUT_PROFILE = Profile(
    994_727,
    "DE3B6899F82D7C9A0781AD54AF635EF2061C59BF8DFA0E6BFD984EB5343FD31A",
    990_816,
    "0F42CB7EBF50D147723586BE2EDECF403CA64E507D8E91CB1E581C7A9EDCC765",
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
    3960: 3960,
    8138: 8138,
    8451: 8451,
    8704: 8704,
    9131: 9131,
    9137: 9137,
    9795: 9795,
    9806: 9806,
    10534: 10534,
    10800: 10800,
    10803: 10803,
}


# Exact final literals from the committed direct-PC Batch C report.
# Record 3960 intentionally supersedes the name-only 3960 component.
CHANGES = (
    Change(
        3960,
        "A4CA9F96D908EB5D9DAA813B441303220C962AB7FB5BB7EF48E2B51AA9049055",
        "교묘한 수였으나, \u001bCA모토나리\u001bCZ의\n끝까지 비정한 결단으로 \u001bCB이노우에 일파\u001bCZ의\n가문 내 영향력은 일소되었다.",
        "E73C8511A443313D01FD3623882D2A2F6BE0E50CA500AF71B95835C922FA1326",
        3960,
        "F9E918FFD416C7437C74DEE3DA2A9370EBD8A82627F7FB25018F58D62F5E30C9",
        ("巧みではあったものの", "元就", "井上党", "一掃された"),
        (648, 912, 672),
        "root-revised 3960: 이노우에 일파 표기와 가문 내 영향력 일소를 함께 교정하며 이름 전용 3960을 대체한다.",
    ),
    Change(
        8138,
        "A2CDE224FC338890DCB5B5D832F5560B4E580A84CB3E5A26E018082C978E1F2C",
        "\u001bCB시마즈\u001bCZ 따위는 상관없다!\n적을 \u001bCC시마바라 반도\u001bCZ에 몰아넣으면\n도망갈 곳은 없으니 모조리 베면 된다.",
        "FE27AAF7D81B1A8F25CE8007437D4FD71B81DE239BF7220DB4E09054EB417100",
        8138,
        "1B076C5B69B95EE81ACE8725ECCC7F9D835D83764FFE15BE3E962B91CB45CB48",
        ("島津", "島原半島", "撫で斬り"),
        (552, 744, 864),
        "시마바라 반도 포위와 전멸의 뜻을 보존하고 지명 span을 완결했다.",
    ),
    Change(
        8451,
        "8EBF37413B32E44C952A5E034C2EA15F8947591C8D120F78C05CD0632F60D457",
        "\u001bCA노부유키\u001bCZ, 그대는\n\u001bCC도이시성\u001bCZ에 들어가라. \u001bCC야자와성\u001bCZ에는\n\u001bCA야자와 요리야스\u001bCZ를 배치하겠다.",
        "1A82271C0FC660EFAE8BEC4C2C46232C836E326E005466287C35AC771E6B9F83",
        8451,
        "72ACE2A784D30A19889D550D3769EC28EBD968BD8FDB924E46D0C9DD3B320FA2",
        ("信之", "砥石城", "矢沢城", "矢沢頼康"),
        (384, 792, 696),
        "두 성의 배치와 야자와 요리야스의 수비 배정을 보존했다.",
    ),
    Change(
        8704,
        "7A0270EC11C2E8B031678B243831E8629998951758557565FDDFBEFB7476E3A7",
        "주, 주군! 큰일이옵니다!\n\u001bCA오노사키 요시마사\u001bCZ 님이\n미천한 하인에게 찔렸사옵니다!",
        "635605D280134F9067F47F631DA8DE727CDA953D4D8341461EBC9EA2A083540F",
        8704,
        "C0D3467439A2B770E3E7BD1B07B77ED84D1C73E7BB115FC1E603B904B0F11A45",
        ("小野崎義昌", "下郎"),
        (552, 528, 696),
        "하인의 낮은 신분과 오노사키 요시마사의 피살을 보존했다.",
    ),
    Change(
        9131,
        "3E859F42C008D2658EE763EDD286BF2AC5372A91A2199FDE8ECF9E3D2F8D77AD",
        "\u001bCA도요쿠니\u001bCZ가 삭발한 시기는\n불분명하나, 입도한 뒤에는\n\u001bCA야마나 젠코\u001bCZ라 일컬었다고 전한다.",
        "F9BAEAC9CBF23435E41B06C27BAC5F45BE772933D72F3EC650B4557C1396CE72",
        9131,
        "2923A680DCEC1835C8CAC0EA10E1F9B90E77622601AB54583B1360146A6A2CA6",
        ("豊国", "山名禅高", "号した"),
        (576, 600, 768),
        "도요쿠니의 삭발 시기, 입도, 야마나 젠코라는 호를 보존했다.",
    ),
    Change(
        9137,
        "1CE660C7654563863D12B7EAEAC4116C94979D34E91A59AED93659EEB4433B3E",
        "\u001bCA아키이에\u001bCZ는 「\u001bCA사카자키 나오모리\u001bCZ」로\n개명해, 훗날 \u001bCA도쿠가와 이에야스\u001bCZ를\n섬겼다고 한다.",
        "F3ECC0B5E5457999585357AD2090340CFD0F9642BFCB70E2F6687B29836BDE76",
        9137,
        "9A81BB5DD90D2122B6E6C43FB9F9FFCBDD24E80EC8ED3B95546BB7CF65AA5381",
        ("詮家", "坂崎直盛", "徳川家康", "名を改め"),
        (816, 768, 336),
        "개명과 도쿠가와 이에야스 섬김을 보존하고 두 인명 span을 완결했다.",
    ),
    Change(
        9795,
        "C9147CA15358AE64D9765241D96CDEB614C22ADB7753930E7CCDD1174F610E24",
        "한쪽은 \u001bCA가토 기요마사\u001bCZ 등 군무를 맡은\n무단파, 다른 쪽은 \u001bCA이시다 미쓰나리\u001bCZ 등\n정무를 맡은 문치파였다.",
        "3898F5706E362D5ED5FF62C2F97517FCD9110CE9A7D72DC2C8F734B24E56DAF9",
        9795,
        "686B1F29F7E4D340322E7BB29D267C1C52A7D83FB9FD5FC215AD273B7417E100",
        ("加藤清正", "石田三成", "武断派", "吏僚派"),
        (840, 864, 552),
        "가토 기요마사·이시다 미쓰나리와 무단파/문치파 대립을 보존했다.",
    ),
    Change(
        9806,
        "DAEAAA23C2B60C931A11DD20126710A1126687C432F1ABE40B282817D3FE18EA",
        "\u001bCA다이코\u001bCZ 전하를 잃은 지\n얼마 되지도 않아 이 꼴이라니…\n\u001bCB도요토미 가문\u001bCZ의 결속도 참 약하구나.",
        "2DEC1248E7E0BB0770166CF194CDE3DAD33A7BDD962D55C45A38E4A2CFB3C5AF",
        9806,
        "7E6C2B257F63502D9230BB2F0BE04C48963FCAE4C91409B0601BA085054197AE",
        ("太閤", "豊家", "脆い"),
        (504, 720, 840),
        "태합 사후 곧바로 드러난 도요토미 가문의 약한 결속을 보존했다.",
    ),
    Change(
        10534,
        "00B113D22B4C76286F1CB3F2A93FC93EAB9B8C1CF48EB96B2DCD8943C0A7D9F2",
        "\u001bCA이에야스\u001bCZ여,\n\u001bCB도요토미 가문\u001bCZ을 업신여기다니!\n\u001bCA다이코\u001bCZ 전하의 은혜를 잊었는가!",
        "60D123724E0444A75B3014A9842B0BB5132C960742A867DBC9A4FB66E8CF34B1",
        10534,
        "D73ABC4128859D94AA659C81AF738E80BF2B82B00A6C6674F878DEC81764C0F9",
        ("家康", "豊臣家", "太閤", "御恩"),
        (264, 696, 720),
        "이에야스 호명, 도요토미 가문 질책, 태합의 은혜를 보존했다.",
    ),
    Change(
        10800,
        "57C4C14A97E7FF7653849BFCC64EBA8F51F1578CF893393F896E07C792C41B76",
        "하지만 정면으로 맞설 수는 없다……\n그렇다면 \u001bCA이마가와 요시모토\u001bCZ의\n본대를 기습한다!",
        "ED95647B8734EC67867DFC9D49078A3EFAC05C2C534D52A439F2298A68AFC7BA",
        10800,
        "0A297AFD767FB33687F1F5CCF6225190C1FE98A88C6E8A51FE8F6F116795AA36",
        ("今川義元", "本隊", "奇襲"),
        (816, 672, 384),
        "정면 대결 불가와 이마가와 요시모토 본대 기습을 보존했다.",
    ),
    Change(
        10803,
        "599ED80799971CE4A5CA14EC443AE999B65835B5EDE875AC5DEFB955491C1915",
        "\u001bCB오다 가문\u001bCZ의 운명은 이 한 싸움에\n달렸다! 노릴 것은 오직\n\u001bCA이마가와 요시모토\u001bCZ의 목뿐이다!",
        "493C1FDE64FAEFAD5E20D1CEFF471F61A9333253BEFD76572F7C4E9D011CCF7F",
        10803,
        "2F346F37AA7147C4256516FB1ADC2F73A24A05608C2C01FAC1B7E7A091CAF745",
        ("織田家", "今川義元", "命運", "首"),
        (744, 528, 696),
        "오다 가문의 운명과 이마가와 요시모토의 목 하나라는 목표를 보존했다.",
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
    spec = importlib.util.spec_from_file_location("tag_reflow_batch_c_event_font", W31_WIDTH_UTILITY)
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
        value.replace("\x1bCA", "<ESC>CA")
        .replace("\x1bCB", "<ESC>CB")
        .replace("\x1bCC", "<ESC>CC")
        .replace("\x1bCZ", "<ESC>CZ")
        .replace("\n", "<LF>")
    )


def require_report_literals() -> None:
    require(REVIEW_REPORT.is_file(), "committed Batch C review report is absent")
    report = REVIEW_REPORT.read_text(encoding="utf-8")
    tick = chr(96)
    for change in CHANGES:
        expected = "- 권고: " + tick + report_display(change.target) + tick
        require(expected in report, f"{change.entry_id} target differs from committed review report")
    by_id = {change.entry_id: change for change in CHANGES}
    require(
        by_id[3960].target
        == "교묘한 수였으나, \x1bCA모토나리\x1bCZ의\n"
        "끝까지 비정한 결단으로 \x1bCB이노우에 일파\x1bCZ의\n"
        "가문 내 영향력은 일소되었다.",
        "3960 is not root-revised literal",
    )
    require(
        by_id[3960].target_utf16le_sha256
        == "E73C8511A443313D01FD3623882D2A2F6BE0E50CA500AF71B95835C922FA1326",
        "3960 root-revised target hash differs",
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
    expected_ids = (3960, 8138, 8451, 8704, 9131, 9137, 9795, 9806, 10534, 10800, 10803)
    require(change_ids == expected_ids, "candidate IDs differ from reviewed scope")
    require(len(change_ids) == len(set(change_ids)) == 11, "candidate must contain exactly eleven unique records")
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
                "committed_direct_pc_batch_c_review_report",
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
        "scope_notes": {
            "3960": (
                "full semantic/name/reflow replacement; deliberately supersedes "
                "the name-only 3960 component and must not be applied together"
            )
        },
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
