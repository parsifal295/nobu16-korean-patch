#!/usr/bin/env python3
"""Build a private direct-PC candidate for reviewed PK event tag reflow A.

This script reads only the exact installed W45 Korean PK event table, its
pristine PC Japanese counterpart, and the active PC event font.  It changes
exactly the ten literals reviewed in pc_event_tag_reflow_batch_a_v1 and writes
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
REVIEW_REPORT = REPO / "workstreams" / "pc_event_tag_reflow_batch_a_v1" / "README_KO.md"

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


SCHEMA = "nobu16.kr.pc-event-tag-reflow-batch-a-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-tag-reflow-batch-a-candidate-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-tag-reflow-batch-a-candidate-manifest.v1"
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
    994_755,
    "BE5734E36B18153622A6306006F3BCE7A9C217FCF856E006A7D5C32D4CFCB676",
    990_844,
    "2FE6B65545B921A21CA65EFBE676FDCE98E4E2E3D591C8BAE74F0CA3204BDCD1",
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
    4057: 4057,
    4257: 4257,
    4323: 4323,
    4436: 4436,
    4726: 4726,
    4737: 4737,
    4792: 4792,
    4880: 4880,
    4895: 4895,
    5182: 5182,
}


# These are the exact final literals from pc_event_tag_reflow_batch_a_v1.
# In particular 5182 deliberately starts "그건 그렇다 치고, 이렇게".
CHANGES = (
    Change(
        4057,
        "3C2C4EAF3F91E8B7A8DB0BA4A03D63FC1DF7117FE6DE9CFF3DD5212FFFCB5244",
        "\x1bCB다케다군\x1bCZ에 가담한\n"
        "\x1bCA사나다 유키타카\x1bCZ의 조략으로,\n"
        "가신들이 잇달아 배신한 것이다……",
        "0544512810E2974EED7C55CD77BA365EF27846DA462E1F875E0F078594D6F672",
        4057,
        "9D25F2260895F4C461660B63EE1028B8C68F6881C214104B428447A1DCB07573",
        ("武田軍", "真田幸隆", "調略", "寝返り"),
        (408, 648, 792),
        "다케다군 가담·사나다 유키타카의 조략·가신들의 배신을 유지하며 인명 색상 span을 완결했다.",
    ),
    Change(
        4257,
        "1CAD6D4118F990A8BD3E72CFD4AAC690AF8461C262F59B71A7E4002C01E29661",
        "\x1bCA우에스기 데루토라\x1bCZ는\n"
        "‘\x1bCA우에스기 겐신\x1bCZ’으로 개명하고,\n"
        "불문에 더욱 깊이 귀의했다.",
        "E104E041F6295BEDCF401700DF9C77BEF436BC2A6D5EAF95C18729A6FFD5D0E0",
        4257,
        "B321862B3ED14BD9AE416A9C0CD0A59952888D83BEDFF3C0E02D0F7C86866F1B",
        ("上杉輝虎", "上杉謙信", "改名", "仏門"),
        (456, 744, 624),
        "개명과 불문 귀의의 인과를 유지하면서 개명한 이름 span을 한 줄에 두었다.",
    ),
    Change(
        4323,
        "6CEB2B56253078E6D3F1D0B78AB16E66D4DE4F87788D528689CEB6A856D475F5",
        "\x1bCA하야시 히데사다\x1bCZ와 그 아우\n"
        "\x1bCA미마사카노카미\x1bCZ, 그리고\n"
        "\x1bCA시바타 곤로쿠 가쓰이에\x1bCZ 등입니다……",
        "BB65FB857CFCEA4C0C33D090F39D634FE4B36AC741832DBD9E8F51EBE01D8F71",
        4323,
        "0D357FDC67C37D821739BD927BAF5AC176A7043DACB8D3382DF682A687B1B805",
        ("林秀貞", "美作守", "柴田権六勝家"),
        (600, 528, 840),
        "세 인명과 하야시 히데사다의 아우라는 관계를 유지하고 마지막 인명 span을 완결했다.",
    ),
    Change(
        4436,
        "F28CDE55CD2E4A3E29DFC7D5AE7DAD5F1F03F61983F6B5DF987C920B9648BFFC",
        "너는 히다 고쿠시 \x1bCB아네가코지 가문\x1bCZ의\n"
        "이름을 이어, 이제부터\n"
        "\x1bCA아네가코지 요리쓰나\x1bCZ라 하라!",
        "0229348A51270C1DAFE32FC3D41DB55D265F374F52EE518888102B21E260FF03",
        4436,
        "27C8E6D47DBD07DDA606867B3C03EC9D28E70F995A2297B5F3746A6EF0A8A368",
        ("飛騨国司", "姉小路家", "姉小路頼綱"),
        (816, 504, 648),
        "히다 고쿠시·가문 명적 계승·새 이름 선언을 유지하고 가문명 및 인명 span을 완결했다.",
    ),
    Change(
        4726,
        "D09F69C626DEF2CBEAC10E5C437870B061079EC1B77DE6D7C4EFFDA24091C428",
        "오니미노라 불린 \x1bCA바바 노부하루\x1bCZ가\n"
        "맹공을 퍼부었지만, \x1bCA가게모치\x1bCZ는\n"
        "가까스로 이를 물리쳤다.",
        "C5A96644F9C7029F02C5849F759F3A201E4F6C5343E9CDDAE617611644FFADBB",
        4726,
        "3FE698B03C31099252BD5554ADE449FCFC6959B415EB1A41D73ADB5F9FCDCCC5",
        ("鬼美濃", "馬場信春", "景持", "退けた"),
        (744, 696, 552),
        "오니미노, 바바 노부하루의 맹공, 가게모치의 격퇴라는 대비를 문장 단위로 유지했다.",
    ),
    Change(
        4737,
        "230C03049459BAF5F2BB7CDE2C331466375788273196D663F49ADC4C7CB302C1",
        "\x1bCA가게모치\x1bCZ의 예상대로, \x1bCA바바 노부하루\x1bCZ가\n"
        "세 번째 공격을 시작했다.",
        "32CFA6698F1B779CB807A31EAB66D47FD77DCBFDEE5C46E78E2DA784B38C22C9",
        4737,
        "146D2C4F0D361F05DBBE7465F811361D55BD37C0AC251F6A98860BB5E69E2E9C",
        ("景持", "馬場信春", "三度目の攻撃"),
        (864, 576),
        "가게모치의 예상과 바바 노부하루의 세 번째 공격을 두 문맥 단위로 끊었다.",
    ),
    Change(
        4792,
        "221133482DBD2810592DCA100A1771E85BC3B7D3DC275C365E4EA21E06FA5F4B",
        "……그랬지. 좋아! 이제부터 나는\n"
        "\x1bCA아네가코지 주나곤 요시요리\x1bCZ다!",
        "83F428FDCA2FFC3C05D40DC58BF02BAE291BF224CD0AE145D62A836A4D650B17",
        4792,
        "8C5CF68424C8869399F1A792EA8269833BCAAED33D94BA09BC04CF8C45F8BCBD",
        ("そうであったな", "よし", "姉小路中納言良頼"),
        (744, 696),
        "감탄과 자칭 선언을 분리하고 관위 포함 이름 span 전체를 보존했다.",
    ),
    Change(
        4880,
        "12C08F550C8389DCC93FA66B40A758EA547FEBBE48E2E4644CD567E14BC71813",
        "또 한 명의 아우 \x1bCA아타기 후유야스\x1bCZ님에게\n"
        "만일의 일이 생긴다면……\n"
        "어찌한단 말인가.",
        "AB3EE0FAD7B9A7B290B599DFE4ECB0C2358432C3B43BD898623884C1E284E901",
        4880,
        "72AA314FB3FCF96083DCC1DFF98FD7299D112A1CCC864626D69792CFA74788EC",
        ("もう一人のご舎弟", "安宅冬康", "万一"),
        (888, 576, 384),
        "또 한 명의 아우와 만일의 사태라는 조건절을 보존하고 인명 span을 완결했다.",
    ),
    Change(
        4895,
        "3FB51A8C34FB7C6BEC9CFC6B23520DBE89BF2B27553204E94AA0F8A931255036",
        "오늘부터 \x1bCA가쓰요리\x1bCZ라 칭하라.\n"
        "\x1bCA스와 시로 가쓰요리\x1bCZ,\n"
        "그것이 네 이름이다.",
        "D65935A49A24D8AEE6823DCD0E245095D565748969EDE32BBB0A03FDEEAB80FD",
        4895,
        "24745D5DBA455B7A5C374C9E2209B230FAB73256F59403604D0188C70C1EAD91",
        ("勝頼", "諏訪四郎勝頼", "おぬしの名"),
        (648, 456, 456),
        "가쓰요리라는 새 이름과 정식 이름을 알리는 순서를 유지했다.",
    ),
    Change(
        5182,
        "748DD12DC12DB6B59AB0CADE0816B89E8DC455639599FB5277552B41106EEFB3",
        "그건 그렇다 치고, 이렇게 \x1bCB다테 가문\x1bCZ과\n"
        "\x1bCB모가미 가문\x1bCZ은 혼인으로 인척이 되어,\n"
        "혼인이 \x1bCC오슈\x1bCZ의 운명을 크게 바꿔 간다.",
        "2CD0DFD0A6DABD5949A0EE4C76929EAA24E9FC398A0AAB852C6A89C6EA92A0C2",
        5182,
        "7FA166F075FCBDD535872B59FCD9CEC8530D23B1B81DFDCA8978C753738A8BBB",
        ("それはともかく", "こうして", "伊達家", "最上家", "姻戚関係", "奥州", "変えていく"),
        (864, 840, 864),
        "화제 전환·혼인 인척 관계·오슈의 운명을 바꿔 가는 진행성을 보존한 root-corrected literal이다.",
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
    spec = importlib.util.spec_from_file_location("tag_reflow_batch_a_event_font", W31_WIDTH_UTILITY)
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


def reviewed_literal(value: str) -> str:
    """Represent raw ESC for the committed human-review report."""
    return value.replace("\x1b", r"\x1b")


def require_report_literals() -> None:
    require(REVIEW_REPORT.is_file(), "committed batch A review report is absent")
    report = REVIEW_REPORT.read_text(encoding="utf-8")
    for change in CHANGES:
        displayed = "\n".join(f"    {line}" for line in reviewed_literal(change.target).splitlines())
        require(displayed in report, f"{change.entry_id} final target differs from review report")
    corrected = r"그건 그렇다 치고, 이렇게 \x1bCB다테 가문\x1bCZ과"
    require(corrected in report, "5182 root-corrected review literal is absent")


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
    expected_ids = (4057, 4257, 4323, 4436, 4726, 4737, 4792, 4880, 4895, 5182)
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
                "committed_direct_pc_batch_a_review_report",
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
