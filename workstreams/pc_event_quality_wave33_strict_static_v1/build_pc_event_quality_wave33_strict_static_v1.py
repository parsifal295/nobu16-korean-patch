#!/usr/bin/env python3
"""Build a private PC-only strict static-event correction candidate for Wave 33.

The candidate contains thirteen Base/PK event pairs (26 cells).  It has no
Steam-write, transaction, Git, network, or release capability.  Every target
is tied to current Steam Korean and PC JP/EN/SC/TC source hashes only.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

for root in (TOOLS,):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-quality-wave33-strict-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-quality-wave33-strict-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-quality-wave33-strict-static-manifest.v1"
MAX_LINES = 3
PK_MAX_LINE_PX = 912
BASE_TEXT_MESSAGE_LOGICAL_SIZE = (448, 100)

LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)


class Wave33Error(RuntimeError):
    """Raised when a source, layout, or private-candidate contract differs."""


@dataclass(frozen=True)
class SourceSpec:
    path: Path
    size: int
    sha256: str


@dataclass(frozen=True)
class ResourceSpec:
    key: str
    relative: str
    path: Path
    input_size: int
    input_sha256: str
    input_raw_size: int
    input_raw_sha256: str
    target_size: int
    target_sha256: str
    target_raw_size: int
    target_raw_sha256: str


@dataclass(frozen=True)
class PairSpec:
    name: str
    base_id: int
    pk_id: int
    target: str
    base_current_utf16le_sha256: str
    pk_current_utf16le_sha256: str
    target_utf16le_sha256: str
    target_widths_px: tuple[int, ...]
    rationale: str
    base_real_game_qa_required: bool = False
    relation_context_8799: bool = False


@dataclass(frozen=True)
class Change:
    resource: str
    entry_id: int
    peer_resource: str
    peer_entry_id: int
    current_utf16le_sha256: str
    target: str
    target_utf16le_sha256: str
    target_widths_px: tuple[int, ...]
    rationale: str
    base_real_game_qa_required: bool
    context_ids: tuple[int, ...]


@dataclass(frozen=True)
class TableResource:
    spec: ResourceSpec | SourceSpec
    packed: bytes
    header: Any
    raw: bytes
    table: Any


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


BASE = ResourceSpec(
    "base",
    "MSG/JP/ev_strdata.bin",
    STEAM_ROOT / "MSG" / "JP" / "ev_strdata.bin",
    928_119,
    "02AC90B818E8F75683CD5BACF277E91048D4510E448A8699242D3B19299FE067",
    924_468,
    "15C07B60BDBDA884FD0894135CA38235A575A728307858CA363DBD4C3505F706",
    928_115,
    "ECB0E80945BE7D04AFC3DF2E1F46CE9753B14AC25BF38CB441B2664ECCB0F18F",
    924_464,
    "E225F2174B9012676A5AFD7D768CC4B3642A934190873378BFC162605B9C3BA7",
)
PK = ResourceSpec(
    "pk",
    "MSG_PK/JP/msgev.bin",
    STEAM_ROOT / "MSG_PK" / "JP" / "msgev.bin",
    994_727,
    "AEE0D9992B963E17B3C118AA54DACC60390936FF48876674CA7675A2A11A3668",
    990_816,
    "70DEE3B7AB40B77C99120FF39B549A9073F8807C57EB574FB68808CAC49C7408",
    994_727,
    "66542919D6414CF6CFCA260B1672AADF1FD06FA5D450C18E9C8F64A9AE32C541",
    990_816,
    "40AAA31BA73BEA9EE3B069BCC78FEC9DE6A469EF3C1F0303A1F159A10FC085A9",
)
RESOURCES = {BASE.key: BASE, PK.key: PK}

SOURCES: Mapping[str, Mapping[str, SourceSpec]] = {
    "base": {
        "JP": SourceSpec(
            Path(r"F:\Games\NOBU16\MSG\JP\ev_strdata.bin"),
            496_819,
            "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
        ),
        "SC": SourceSpec(
            STEAM_ROOT / "MSG" / "SC" / "ev_strdata.bin",
            461_651,
            "77E87C6FEC67859543FCB4134660A7274A2374F6881B956421B561E61BD7B685",
        ),
        "TC": SourceSpec(
            STEAM_ROOT / "MSG" / "TC" / "ev_strdata.bin",
            460_929,
            "9E9346B942CAFA99432D675F6BA74DD04D48F56095F35F46392697011D9CFEF3",
        ),
    },
    "pk": {
        "JP": SourceSpec(
            STEAM_ROOT
            / "KR_PATCH_BACKUP"
            / "file_only_transaction"
            / "steam-jp-1.1.7-v0.6.0"
            / "originals"
            / "MSG_PK"
            / "JP"
            / "msgev.bin",
            562_226,
            "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        ),
        "EN": SourceSpec(
            STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
            762_196,
            "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
        ),
        "SC": SourceSpec(
            STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin",
            522_177,
            "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
        ),
        "TC": SourceSpec(
            STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin",
            524_909,
            "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
        ),
    },
}


# Korean targets are project-authored.  PC source text is not embedded here.
PAIRS = (
    PairSpec("officer_style_typo", 3719, 10825, "예! 맡겨 주십시오!", "4E659EED9339B05865404CBA6C5383682164D66C947AF41CC48FAB9629D8B051", "4E659EED9339B05865404CBA6C5383682164D66C947AF41CC48FAB9629D8B051", "65ECC47D43CECF060318C967FA7313FB84D5EBCC0CC3B15245AB58BFA7B02DD6", (432,), "확정된 중복 존대 오탈자를 바로잡는다."),
    PairSpec("soldier_loss", 6772, 6772, "이런이런… 말이 통하지 않는 분이로다.\n소중한 병사를 무모한 싸움에\n잃는 건 사양이오.", "EC3FD23E24027896014CA0429AC19C89FC727DEA8ADE37CD0EA5A89117506F0A", "E59128A2D4EB1F23864F4D59A9921C7EF5C819E0D0A67E2FFD962AA5C0B3E5F7", "3FB2EA80631F8A384D39981E4D3D9CF5798D93C8463D5DA81A62F985AFDBD409", (888, 648, 408), "무모한 싸움으로 병사를 잃고 싶지 않다는 뜻으로 보정한다.", True),
    PairSpec("portrait_subject", 6941, 6941, "신경 쓰지 마라, 누구나\n듣게 되는 이야기다\n그보다 형님, 이 그림의 인물은 누구요?", "5A30C8007DCF9543ADA8AEC27A8F2FB440C8FA1D0B99B991FD096F6F1C9B7794", "F7850E3C40C1671EE1D4522A3607127B4F4D8DAD0B615AA43DB7D95FD2FDE7F3", "EE7C8318F7FF6BD76A927752FBEAA93C82BFDC5435B56273ACA5E4D4A32030A5", (528, 432, 888), "그림 자체가 아니라 그림 속 인물을 묻는 뜻으로 보정한다.", True),
    PairSpec("yoshiaki_uncle_01", 8769, 8769, "그거야말로 바라던 바.\n외숙부님의 목을 베면\n마침내 \x1bCC오우\x1bCZ의 모든 것이 우리 것이다.", "E627524362AC430BCE3C6BF0C91E7484036C3BD2BA34C60EFD206485CB6AACD7", "E627524362AC430BCE3C6BF0C91E7484036C3BD2BA34C60EFD206485CB6AACD7", "E21FA9FD9918E42CF4E0DDFA38953B28AA48B5B0302FA954184985269D0C07AE", (504, 480, 864), "모친의 친오빠 관계를 외숙부로 바로잡는다.", False, True),
    PairSpec("yoshiaki_uncle_02", 8776, 8776, "\x1bCA마사무네\x1bCZ가 영토 확장을 노려 \x1bCB오사키가\x1bCZ에\n병사를 낸다면, 외숙부와 조카 사이라도\n칼을 맞댈 수밖에 없는 상황이었다.", "6660744536CA121646A7ACAD354DF786844FC3B58E882169A1E7F2DCD57542D0", "1EBF563B40BF5EA0F448334440ADAF29049F2C65170048CF30C193DE2118AFA0", "B836C18B8C5F677EC129B190C8F984944C91083367F508CF1BF822BEB15AFA6F", (912, 888, 792), "모친의 친오빠 관계를 외숙부로 바로잡는다.", True, True),
    PairSpec("yoshiaki_uncle_03", 8780, 8780, "드디어, 외숙부님이 상대인가\n후후, 재미있게 되었군.", "0BBECAEEB357539356542C8D9F07C7EFAEA5B058BDE73DF5CC0CA7E239775557", "0BBECAEEB357539356542C8D9F07C7EFAEA5B058BDE73DF5CC0CA7E239775557", "5FDBC76C2E11F217044D710AF106CAFA98F5A827216CAB0F6DE17826033748D3", (648, 528), "모친의 친오빠 관계를 외숙부로 바로잡는다.", False, True),
    PairSpec("yoshiaki_uncle_04", 8783, 8783, "가마…?\n외숙부님이 가마를 타고 오셨는가?\n\x1bCA이마가와 요시모토\x1bCZ도 아니거늘.", "622536724E74B4DD4DACA4B35F48C0B44A17477F4E09312204ADA1269893E91E", "622536724E74B4DD4DACA4B35F48C0B44A17477F4E09312204ADA1269893E91E", "75336F4925AB4B4078E61BF0096EAFCDC2EA789E3BB3D0FC4BB58AD899DF5B4F", (168, 768, 696), "모친의 친오빠 관계를 외숙부로 바로잡는다.", False, True),
    PairSpec("yoshiaki_uncle_05", 8790, 8790, "외숙부님…!\n어머님, 이 어인 생각이시옵니까!?", "BCBC209A7AAC8E839E5A4837FA29263B3A410CAE66CA7849205E5AF004548720", "BCBC209A7AAC8E839E5A4837FA29263B3A410CAE66CA7849205E5AF004548720", "A5C087DF113E1C6F055FEA83A6E17934A91583FB165E5ABD752F2972320D5123", (264, 768), "모친의 친오빠 관계를 외숙부로 바로잡는다.", False, True),
    PairSpec("yoshiaki_uncle_06", 8797, 8797, "지껄이는군!\n외숙부님이야말로 목이 붙어 있는 것을\n어머님께 감사하시지!", "EA93A7F0A040A8ABAE6A7F1CB54B6AD231204673320593E4B8EAF7A4AC7BACDD", "EA93A7F0A040A8ABAE6A7F1CB54B6AD231204673320593E4B8EAF7A4AC7BACDD", "AD291861A7B6FD764EF61096DFC3E4D997844790991581132ABFA9E9B34A8AB1", (264, 864, 480), "모친의 친오빠 관계를 외숙부로 바로잡는다.", False, True),
    PairSpec("yoshiaki_uncle_07", 8803, 8803, "과연 나의 어머님, 당당하신 모습이로다\n비열한 외숙부님과는\n조금도 닮지 않으셨다.", "656B84D55EE70104E4A5A89F4C6ADD13849A3C37D6B5C5565BCA3BBF78A4E1F3", "65D0D9269546A7FE57BCCF9CE61F79A877C852EC974F15149BA48D300F43891A", "89C327D83484A458F1482E3813393A93DB00378355DE97F137FEA6E1E77065EA", (888, 456, 504), "모친의 친오빠 관계를 외숙부로 바로잡는다.", True, True),
    PairSpec("yoshiaki_uncle_08", 8805, 8805, "…결판은 언젠가 내겠소, 외숙부님!", "9EDE0CAAECE794BA0C9A728C22916671214A05E5D8A23B161F5E57237ED247D6", "9EDE0CAAECE794BA0C9A728C22916671214A05E5D8A23B161F5E57237ED247D6", "14F2819BFA0512891DDDD28A6828CC79B159B812FBD7EE08C8072CCDA99ADE21", (792,), "모친의 친오빠 관계를 외숙부로 바로잡는다.", False, True),
    PairSpec("arrow_distribution", 8947, 8947, "어느 자가 임종 때 스무 명의\n자식을 불러 각자 화살 한 대를\n내놓으라 명했다.", "7A360B584FB4AD26ABBA6E43EB2790693BAD50EA85ABD2A1AFA02F04C0874C70", "6090AB5654009B777E00D72C23C9E493385078A6069471F61380642FABCEA1DA", "E3A9337891EF46774EEAA95490C4A2BEDCD6AA5CEB45A17C97E8CF0684AEE41D", (648, 696, 384), "스무 자녀가 각자 화살 한 대씩 내는 수식을 바로잡는다.", True),
    PairSpec("meeting_close", 9292, 9292, "화기애애하면서도 어딘가\n긴장을 품은 회담은\n한 시진 남짓 만에 막을 내렸다.", "E9BF504084A00D91353F6B2716A906AFE7D3A0BE89016D6B9F48EF7BCAB14681", "4E61D56CB91A8A85BF33D292A75123B106AB506A56B74B61ACFE93CD0CD23638", "B62F99D34270F90C828208C329D5C906E6970CEC4EC6076888BF21B6BA2A411D", (552, 432, 720), "중복된 종결 표현을 회담 종료 의미로 보정한다.", True),
)


def make_changes() -> tuple[Change, ...]:
    output: list[Change] = []
    for pair in PAIRS:
        context_ids = (8799,) if pair.relation_context_8799 else ()
        output.extend(
            (
                Change("base", pair.base_id, "pk", pair.pk_id, pair.base_current_utf16le_sha256, pair.target, pair.target_utf16le_sha256, pair.target_widths_px, pair.rationale, pair.base_real_game_qa_required, context_ids),
                Change("pk", pair.pk_id, "base", pair.base_id, pair.pk_current_utf16le_sha256, pair.target, pair.target_utf16le_sha256, pair.target_widths_px, pair.rationale, False, context_ids),
            )
        )
    return tuple(output)


CHANGES = make_changes()
CHANGE_BY_RESOURCE = {key: tuple(change for change in CHANGES if change.resource == key) for key in RESOURCES}
if len(PAIRS) != 13 or len(CHANGES) != 26 or len({(change.resource, change.entry_id) for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 33 pair/cell scope differs")


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave33Error(label)


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


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave33Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave33Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def protected_signature(value: str) -> dict[str, Any]:
    escapes: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is None:
                raise Wave33Error(f"malformed ESC token at offset {cursor}")
            escapes.append(token)
            cursor += 3
            continue
        if character not in ("\r", "\n") and unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        cursor += 1
    printf = list(PRINTF_RE.finditer(value))
    percent_offsets = {match.start() for match in printf}
    return {
        "line_breaks": LINEBREAK_RE.findall(value),
        "leading_whitespace": value[: len(value) - len(value.lstrip())],
        "trailing_whitespace": value[len(value.rstrip()) :],
        "esc_tokens": escapes,
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf],
        "unknown_percent_count": sum(1 for offset, character in enumerate(value) if character == "%" and offset not in percent_offsets),
        "controls": controls,
    }


def protected_nonlayout_signature(value: str) -> dict[str, Any]:
    signature = protected_signature(value)
    del signature["line_breaks"]
    return signature


def load_table(spec: ResourceSpec | SourceSpec, label: str) -> TableResource:
    path = reject_switch(spec.path, label)
    packed = path.read_bytes()
    expected_size = spec.size if isinstance(spec, SourceSpec) else spec.input_size
    expected_hash = spec.sha256 if isinstance(spec, SourceSpec) else spec.input_sha256
    require(len(packed) == expected_size and sha256_bytes(packed) == expected_hash, f"{label} packed profile differs")
    try:
        header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise Wave33Error(f"{label} cannot be parsed as a wrapped message table") from exc
    require(rebuild_message_table(table, table.texts) == raw, f"{label} parse/rebuild identity differs")
    if isinstance(spec, ResourceSpec):
        require(len(raw) == spec.input_raw_size and sha256_bytes(raw) == spec.input_raw_sha256, f"{label} raw profile differs")
        require(recompress_wrapper(raw, header) == packed, f"{label} LZ4 representation differs")
    return TableResource(spec, packed, header, raw, table)


def load_event_font() -> tuple[Callable[[str], int], Mapping[str, Any]]:
    source = REPO / "workstreams" / "pc_event_layout_wave24_v1" / "build_pc_event_layout_wave24_v1.py"
    module_spec = importlib.util.spec_from_file_location("wave33_font_contract", source)
    if module_spec is None or module_spec.loader is None:
        raise Wave33Error("cannot import current PC event-font contract")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)
    return module.load_font()


def line_widths(value: str, advance: Callable[[str], int]) -> tuple[int, ...]:
    widths: list[int] = []
    for line in LINEBREAK_RE.sub("\n", value).split("\n"):
        width = 0
        cursor = 0
        while cursor < len(line):
            character = line[cursor]
            if character == "\x1b":
                token = line[cursor : cursor + 3]
                if ESC_RE.fullmatch(token) is None:
                    raise Wave33Error("malformed event ESC token")
                cursor += 3
                continue
            if unicodedata.category(character) == "Cc":
                raise Wave33Error(f"unexpected event control U+{ord(character):04X}")
            width += advance(character)
            cursor += 1
        widths.append(width)
    return tuple(widths)


def source_anchor(change: Change, sources: Mapping[str, Mapping[str, TableResource]]) -> dict[str, Any]:
    own = sources[change.resource]
    peer = sources[change.peer_resource]
    require(change.entry_id < own["JP"].table.string_count and change.peer_entry_id < peer["JP"].table.string_count, f"{change.resource}:{change.entry_id} Japanese anchor absent")
    own_jp = own["JP"].table.texts[change.entry_id]
    peer_jp = peer["JP"].table.texts[change.peer_entry_id]
    require(own_jp == peer_jp, f"{change.resource}:{change.entry_id} paired Japanese source differs")
    cell_hashes = {language: text_hash(resource.table.texts[change.entry_id]) for language, resource in own.items()}
    context_hashes = {
        str(context_id): {language: text_hash(resource.table.texts[context_id]) for language, resource in own.items()}
        for context_id in change.context_ids
    }
    return {
        "paired_jp_utf16le_sha256": text_hash(own_jp),
        "cell_utf16le_sha256": cell_hashes,
        "context_utf16le_sha256": context_hashes,
    }


def prepare_candidate() -> CandidateBundle:
    current = {key: load_table(spec, f"current Steam {spec.relative}") for key, spec in RESOURCES.items()}
    sources = {key: {language: load_table(spec, f"PC {language} {RESOURCES[key].relative}") for language, spec in language_specs.items()} for key, language_specs in SOURCES.items()}
    advance, font = load_event_font()
    target_texts = {key: list(resource.table.texts) for key, resource in current.items()}
    rows: list[dict[str, Any]] = []
    for key, resource in current.items():
        require(all(source.table.string_count == resource.table.string_count for source in sources[key].values()), f"{key} source string count differs")
    for change in CHANGES:
        resource = current[change.resource]
        require(change.entry_id < resource.table.string_count, f"{change.resource}:{change.entry_id} is absent")
        before = resource.table.texts[change.entry_id]
        require(text_hash(before) == change.current_utf16le_sha256, f"{change.resource}:{change.entry_id} current text differs")
        require(text_hash(change.target) == change.target_utf16le_sha256, f"{change.resource}:{change.entry_id} target declaration differs")
        require(protected_nonlayout_signature(before) == protected_nonlayout_signature(change.target), f"{change.resource}:{change.entry_id} protected controls differ")
        require(tuple(protected_signature(change.target)["line_breaks"]) == ("\n",) * (len(change.target_widths_px) - 1), f"{change.resource}:{change.entry_id} target linebreak declaration differs")
        widths = line_widths(change.target, advance)
        require(widths == change.target_widths_px, f"{change.resource}:{change.entry_id} font widths differ")
        require(len(widths) <= MAX_LINES, f"{change.resource}:{change.entry_id} exceeds declared line count")
        if change.resource == PK.key:
            require(max(widths) <= PK_MAX_LINE_PX, f"{change.resource}:{change.entry_id} exceeds verified PK event width")
        target_texts[change.resource][change.entry_id] = change.target
        rows.append({
            "resource": RESOURCES[change.resource].relative,
            "id": change.entry_id,
            "peer": f"{RESOURCES[change.peer_resource].relative}:{change.peer_entry_id}",
            "current_utf16le_sha256": change.current_utf16le_sha256,
            "target_utf16le_sha256": change.target_utf16le_sha256,
            "target_line_widths_px": list(widths),
            "base_real_game_qa_required": change.base_real_game_qa_required,
            "source_anchor": source_anchor(change, sources),
            "rationale": change.rationale,
        })
    packed: dict[str, bytes] = {}
    raw: dict[str, bytes] = {}
    for key, spec in RESOURCES.items():
        candidate_raw = rebuild_message_table(current[key].table, tuple(target_texts[key]))
        candidate_packed = recompress_wrapper(candidate_raw, current[key].header)
        require(len(candidate_raw) == spec.target_raw_size and sha256_bytes(candidate_raw) == spec.target_raw_sha256, f"{spec.relative} target raw profile differs")
        require(len(candidate_packed) == spec.target_size and sha256_bytes(candidate_packed) == spec.target_sha256, f"{spec.relative} target packed profile differs")
        header, decoded = decompress_wrapper(candidate_packed)
        candidate_table = parse_message_table(decoded)
        require(rebuild_message_table(candidate_table, candidate_table.texts) == decoded and recompress_wrapper(decoded, header) == candidate_packed, f"{spec.relative} target round-trip differs")
        changed = [index for index, (before, after) in enumerate(zip(current[key].table.texts, candidate_table.texts)) if before != after]
        require(changed == sorted(change.entry_id for change in CHANGE_BY_RESOURCE[key]), f"{spec.relative} changed ID scope differs")
        packed[key] = candidate_packed
        raw[key] = candidate_raw
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "pc_jp_en_sc_tc_only": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "font": dict(font),
        "layout_validation": {
            "pk": {"max_line_px": PK_MAX_LINE_PX, "renderer_width_bound_verified": True},
            "base": {
                "text_message_logical_size": list(BASE_TEXT_MESSAGE_LOGICAL_SIZE),
                "renderer_width_bound_verified": False,
                "width_threshold_enforced": None,
                "note": "Base target widths are recorded, but Steam PC renderer scale, wrap mode, and maximum visible lines are not statically proven.",
            },
        },
        "resources": {
            spec.relative: {
                "input": {"size": spec.input_size, "sha256": spec.input_sha256, "raw_size": spec.input_raw_size, "raw_sha256": spec.input_raw_sha256},
                "output": {"size": spec.target_size, "sha256": spec.target_sha256, "raw_size": spec.target_raw_size, "raw_sha256": spec.target_raw_sha256},
            }
            for spec in RESOURCES.values()
        },
        "records": rows,
        "changed_cell_count": len(rows),
        "base_real_game_qa_required_ids": [row["id"] for row in rows if row["resource"] == BASE.relative and row["base_real_game_qa_required"]],
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            spec.relative: {
                "input": {"size": spec.input_size, "sha256": spec.input_sha256},
                "output": {"size": spec.target_size, "sha256": spec.target_sha256},
                "changed_ids": sorted(change.entry_id for change in CHANGE_BY_RESOURCE[key]),
            }
            for key, spec in RESOURCES.items()
        },
        "changed_cell_count": len(CHANGES),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed, raw, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    require_private(TMP_ROOT, "tmp root")
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for key, spec in RESOURCES.items():
            path = stage / spec.relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bundle.packed[key])
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "build_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    for key, spec in RESOURCES.items():
        path = output / spec.relative
        require(path.is_file() and path.read_bytes() == bundle.packed[key], f"private candidate differs: {spec.relative}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {"candidate_root": output.relative_to(REPO).as_posix(), "changed_cell_count": len(CHANGES), "base_real_game_qa_required": True, "steam_game_resource_written": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {"candidate_root": output.relative_to(REPO).as_posix(), "changed_cell_count": len(CHANGES), "base_real_game_qa_required": True, "steam_game_resource_written": False}
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
