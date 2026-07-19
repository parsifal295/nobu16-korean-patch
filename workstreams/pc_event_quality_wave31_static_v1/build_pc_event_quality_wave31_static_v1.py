#!/usr/bin/env python3
"""Build a private, current-Steam PC event wording candidate for Wave 31.

This workstream repairs four high-confidence static event narratives in both
the Base and PK tables.  It reads only the current Steam Korean input and
pinned PC JP/EN/SC/TC reference tables.  It has no Steam write, transaction,
Git, network, or release capability.
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
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

for root in (TOOLS,):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-quality-wave31-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-quality-wave31-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-quality-wave31-static-manifest.v1"
MAX_LINES = 3
PK_MAX_LINE_PX = 912
BASE_TEXT_MESSAGE_LOGICAL_SIZE = (448, 100)

LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)


class Wave31Error(RuntimeError):
    """Raised when a pinned input, anchor, or private-output guard drifts."""


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
class Change:
    resource: str
    entry_id: int
    current_utf16le_sha256: str
    target: str
    target_utf16le_sha256: str
    source_utf16le_sha256: Mapping[str, str]
    target_widths_px: tuple[int, ...]
    rationale: str


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
    928_111,
    "10C42695E074E803A62FE840EBD7E65FA00CD3BFBFD64F403B06744A9CA1B57C",
    924_460,
    "627AC004D006F456A9BBD9D41E9F0DEB6311ED0BC3CCB5424FF18365964D0B8C",
)
PK = ResourceSpec(
    "pk",
    "MSG_PK/JP/msgev.bin",
    STEAM_ROOT / "MSG_PK" / "JP" / "msgev.bin",
    994_727,
    "AEE0D9992B963E17B3C118AA54DACC60390936FF48876674CA7675A2A11A3668",
    990_816,
    "70DEE3B7AB40B77C99120FF39B549A9073F8807C57EB574FB68808CAC49C7408",
    994_743,
    "8B92021D1F672161607BF9F7664F025759D58EAB3C0C36C9981692D6FBA880A1",
    990_832,
    "A5920A3826926DD461CA590A53A6635B45E896C0DCFAA7FAFCC0AE3D87F3632A",
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

# All strings below are project-authored Korean targets.  Reference text is
# never embedded; it is checked only by its PC-table and UTF-16LE hashes.
CHANGES = (
    Change(
        "base",
        3898,
        "BC1E7285EC15504DF482CF5C02688F14E937FB6E0C3D53FDD0A47F869C74C51D",
        "양부 \x1bCA오키쓰네\x1bCZ에 뒤지지 않을\n주고쿠 제일의 무예를 지녀,\n\x1bCB모리 가문\x1bCZ를 떠받치게 된다.",
        "25A837124FC7CCEC660FA313F79899F25AD9081AE5B09A9761D342729498CB1A",
        {
            "JP": "4FE8554C3FF45D642A50B85EAABCEC6437BF6584A7E2B7E0618A0EBF12EC089C",
            "SC": "09C2AD252EBAB675F81B39F0236311499402F038BF424B12CB7144A07392085C",
            "TC": "2EE7585A13334966F38F212D7207C90B3855514CED1094ACB814223050267AAD",
        },
        (648, 624, 624),
        "양부·무예·가문 관계를 자연스러운 서술로 바로잡는다.",
    ),
    Change(
        "pk",
        3898,
        "FBD03FD9C52B78BCDED267A1019463F4DAE72D8A3778F575D73FEC67A1940141",
        "양부 \x1bCA오키쓰네\x1bCZ에 뒤지지 않을\n주고쿠 제일의 무예를 지녀,\n\x1bCB모리 가문\x1bCZ를 떠받치게 된다.",
        "25A837124FC7CCEC660FA313F79899F25AD9081AE5B09A9761D342729498CB1A",
        {
            "JP": "4FE8554C3FF45D642A50B85EAABCEC6437BF6584A7E2B7E0618A0EBF12EC089C",
            "EN": "98C46392B04352B54B437D1BECE950A4DC5DB1AFA00C1590F408E6C8F4D5820D",
            "SC": "09C2AD252EBAB675F81B39F0236311499402F038BF424B12CB7144A07392085C",
            "TC": "2EE7585A13334966F38F212D7207C90B3855514CED1094ACB814223050267AAD",
        },
        (648, 624, 624),
        "Base와 같은 원문 문맥으로 고정 인명·서술을 일치시킨다.",
    ),
    Change(
        "base",
        4507,
        "69CBBD87DDD27D488B0D75DF67B4BCC1998BAF488F7EC0C5763E6C4B90E84E84",
        "　에이로쿠 3년 5월 19일\n 요시모토 토벌 때 그가 지닌 칼에 새김\n   오다 오와리노카미 노부나가",
        "50D43B45D6D642AB487D9FD9626DB45C2BAB146464696EF778D4262D125DF5B3",
        {
            "JP": "0F02B99805B3A319A2FB2FE69D601D70D61C820FE30F4E47D3FA6C33EC0A14CF",
            "SC": "5B78D473B91BA700A5AB9BAD07587B1A10978A40BFECA67AD1508C52358290B9",
            "TC": "70FB5CD8E8EE6F67986E77779196704CDB2F1A61B3A02838F32C57DF54FEF5C4",
        },
        (552, 888, 696),
        "칼의 명문이 문장으로 완결되도록 보정한다.",
    ),
    Change(
        "pk",
        4507,
        "BCE0D2C26EACA5415A8D683388B82A3D9BB362EDE90BD9B6C7955AF059D761A5",
        "　에이로쿠 3년 5월 19일\n 요시모토 토벌 때 그가 지닌 칼에 새김\n   오다 오와리노카미 노부나가",
        "50D43B45D6D642AB487D9FD9626DB45C2BAB146464696EF778D4262D125DF5B3",
        {
            "JP": "0F02B99805B3A319A2FB2FE69D601D70D61C820FE30F4E47D3FA6C33EC0A14CF",
            "EN": "95AB850AFF1039F027EB03332DABB45A5002569610E2FD3A0E78F00E742B015B",
            "SC": "5B78D473B91BA700A5AB9BAD07587B1A10978A40BFECA67AD1508C52358290B9",
            "TC": "70FB5CD8E8EE6F67986E77779196704CDB2F1A61B3A02838F32C57DF54FEF5C4",
        },
        (552, 888, 696),
        "Base와 동일한 명문 문맥으로 모호한 대명사를 해소한다.",
    ),
    Change(
        "base",
        5528,
        "FF495C8B98BF3AC07ED7FB0AB5B00A6465252E9DF130165A9A3294B16137A683",
        "예?\n아니, 아니. 칭찬에 익숙지 않은지라\n그저 부끄러울 따름이네만…",
        "7347D3BD240605048238C563C0815B1D333C82D48CBE01A14BFC321938761E34",
        {
            "JP": "89AF516D006832027095504E124A922678656253154AC7E82F0D3D1EF222DAD1",
            "SC": "3B55B08A1FC183492A79B04D541ECEFAF8868D402326E792EFE32F9F53898298",
            "TC": "975E55C536BBE7977F605A0910C0EA493625949681BFB6B5AEB4C74573DAEC33",
        },
        (72, 816, 624),
        "어색한 첫 감탄사와 구어체 연결을 화자의 격식에 맞춘다.",
    ),
    Change(
        "pk",
        5528,
        "FEB7224CEA9A740FEDEE223FB4B9355136221F732C74F84037D47E1EEC04092E",
        "예?\n아니, 아니. 칭찬에 익숙지 않은지라\n그저 부끄러울 따름이네만…",
        "7347D3BD240605048238C563C0815B1D333C82D48CBE01A14BFC321938761E34",
        {
            "JP": "89AF516D006832027095504E124A922678656253154AC7E82F0D3D1EF222DAD1",
            "EN": "8D08FBFCDAEB50E23613162319A1CFA0589538A0BED68BE6A02D3993B9052E80",
            "SC": "3B55B08A1FC183492A79B04D541ECEFAF8868D402326E792EFE32F9F53898298",
            "TC": "975E55C536BBE7977F605A0910C0EA493625949681BFB6B5AEB4C74573DAEC33",
        },
        (72, 816, 624),
        "같은 화자의 말투를 Base와 일관되게 보정한다.",
    ),
    Change(
        "base",
        6379,
        "AE87A54A440DA9C2DD361671AB267F45C93229C0F0D18FD764223FA4DD144525",
        "일찍이 형제의 조부 \x1bCA조소카베 가네쓰구\x1bCZ가\n\x1bCB모토야마 가문\x1bCZ에 멸망하자, 고아가 된\n\x1bCA쿠니치카\x1bCZ를 \x1bCA이치조 후사이에\x1bCZ가 보호했다.",
        "2647CCCCD0613E285A3CD0DE15533509703208CECD670C892521F0BC5D3D68DE",
        {
            "JP": "21AF1EED4B45A461EACD0F9CEA17F424EAD6414E36F6B8939AE6E9F367712363",
            "SC": "0DFC2B2127B6F34234B67F56BCFE3F7006FF71B3CB0B00CF5EE4D391AABFEE5C",
            "TC": "D32205F7801F98165E8DB4D5944A69924C0A2E3A90038380975AB60835D08FF2",
        },
        (912, 840, 912),
        "가문·유아 보호 관계를 빠짐없이 자연스러운 한국어로 바로잡는다.",
    ),
    Change(
        "pk",
        6379,
        "BD27299F653FD353A63108782CBDC2A677952BCCA3E33AF2131F5A0264DBA121",
        "일찍이 형제의 조부 \x1bCA조소카베 가네쓰구\x1bCZ가\n\x1bCB모토야마 가문\x1bCZ에 멸망하자, 고아가 된\n\x1bCA쿠니치카\x1bCZ를 \x1bCA이치조 후사이에\x1bCZ가 보호했다.",
        "2647CCCCD0613E285A3CD0DE15533509703208CECD670C892521F0BC5D3D68DE",
        {
            "JP": "21AF1EED4B45A461EACD0F9CEA17F424EAD6414E36F6B8939AE6E9F367712363",
            "EN": "DEDFF39DCBAB6D85988EFBC55554A6CAFEAD626025F6E57ABB84FECFBB3B5B69",
            "SC": "0DFC2B2127B6F34234B67F56BCFE3F7006FF71B3CB0B00CF5EE4D391AABFEE5C",
            "TC": "D32205F7801F98165E8DB4D5944A69924C0A2E3A90038380975AB60835D08FF2",
        },
        (912, 840, 912),
        "Base와 함께 서술 주체·고아 보호 관계를 일치시킨다.",
    ),
)

CHANGE_BY_RESOURCE = {
    key: tuple(change for change in CHANGES if change.resource == key)
    for key in RESOURCES
}
if sum(len(changes) for changes in CHANGE_BY_RESOURCE.values()) != len(CHANGES):
    raise RuntimeError("Wave 31 changes are not bound to known resources")
if len({(change.resource, change.entry_id) for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 31 has duplicate resource/id changes")


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave31Error(label)


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


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave31Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave31Error(f"Nintendo Switch path is forbidden: {label}")
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
                raise Wave31Error(f"malformed ESC token at offset {cursor}")
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
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in percent_offsets
        ),
        "controls": controls,
    }


def protected_nonlayout_signature(value: str) -> dict[str, Any]:
    """Return immutable runtime/control tokens while allowing an explicit reflow."""
    signature = protected_signature(value)
    del signature["line_breaks"]
    return signature


def load_table(spec: ResourceSpec | SourceSpec, label: str) -> TableResource:
    path = reject_switch(spec.path, label)
    packed = path.read_bytes()
    expected_size = spec.size if isinstance(spec, SourceSpec) else spec.input_size
    require(len(packed) == expected_size, f"{label} packed size differs")
    expected_hash = spec.sha256 if isinstance(spec, SourceSpec) else spec.input_sha256
    require(sha256_bytes(packed) == expected_hash, f"{label} packed SHA-256 differs")
    try:
        header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise Wave31Error(f"{label} cannot be parsed as a wrapped message table") from exc
    require(rebuild_message_table(table, table.texts) == raw, f"{label} parse/rebuild identity differs")
    if isinstance(spec, ResourceSpec):
        require(len(raw) == spec.input_raw_size, f"{label} raw size differs")
        require(sha256_bytes(raw) == spec.input_raw_sha256, f"{label} raw SHA-256 differs")
        require(recompress_wrapper(raw, header) == packed, f"{label} LZ4 representation differs")
    return TableResource(spec, packed, header, raw, table)


def load_event_font() -> tuple[Callable[[str], int], Mapping[str, Any]]:
    source = REPO / "workstreams" / "pc_event_layout_wave24_v1" / "build_pc_event_layout_wave24_v1.py"
    module_spec = importlib.util.spec_from_file_location("wave31_font_contract", source)
    if module_spec is None or module_spec.loader is None:
        raise Wave31Error("cannot import current PC event-font contract")
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
                    raise Wave31Error("malformed event ESC token")
                cursor += 3
                continue
            if unicodedata.category(character) == "Cc":
                raise Wave31Error(f"unexpected event control U+{ord(character):04X}")
            width += advance(character)
            cursor += 1
        widths.append(width)
    return tuple(widths)


def build_manifest(audit: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            spec.relative: {
                "input": {"size": spec.input_size, "sha256": spec.input_sha256},
                "output": {"size": spec.target_size, "sha256": spec.target_sha256},
                "changed_ids": [change.entry_id for change in CHANGE_BY_RESOURCE[key]],
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
    }


def prepare_candidate() -> CandidateBundle:
    current = {key: load_table(spec, f"current Steam {spec.relative}") for key, spec in RESOURCES.items()}
    sources = {
        key: {language: load_table(spec, f"PC {language} {RESOURCES[key].relative}") for language, spec in language_specs.items()}
        for key, language_specs in SOURCES.items()
    }
    advance, font = load_event_font()
    target_texts = {key: list(resource.table.texts) for key, resource in current.items()}
    record_audit: list[dict[str, Any]] = []

    for key, resource in current.items():
        require(all(source.table.string_count == resource.table.string_count for source in sources[key].values()), f"{key} PC source string count differs")

    for change in CHANGES:
        resource = current[change.resource]
        require(change.entry_id < resource.table.string_count, f"{change.resource}:{change.entry_id} is absent")
        before = resource.table.texts[change.entry_id]
        require(text_hash(before) == change.current_utf16le_sha256, f"{change.resource}:{change.entry_id} current text differs")
        require(text_hash(change.target) == change.target_utf16le_sha256, f"{change.resource}:{change.entry_id} target declaration differs")
        require(set(change.source_utf16le_sha256) == set(sources[change.resource]), f"{change.resource}:{change.entry_id} source set differs")
        for language, source in sources[change.resource].items():
            require(change.entry_id < source.table.string_count, f"{change.resource}:{change.entry_id} absent from {language}")
            require(
                text_hash(source.table.texts[change.entry_id]) == change.source_utf16le_sha256[language],
                f"{change.resource}:{change.entry_id} {language} anchor differs",
            )
        require(
            protected_nonlayout_signature(before) == protected_nonlayout_signature(change.target),
            f"{change.resource}:{change.entry_id} controls differ",
        )
        require(
            tuple(protected_signature(change.target)["line_breaks"])
            == ("\n",) * (len(change.target_widths_px) - 1),
            f"{change.resource}:{change.entry_id} target linebreak declaration differs from its line widths",
        )
        widths = line_widths(change.target, advance)
        require(widths == change.target_widths_px, f"{change.resource}:{change.entry_id} font widths differ")
        require(len(widths) <= MAX_LINES, f"{change.resource}:{change.entry_id} exceeds {MAX_LINES} lines")
        if change.resource == PK.key:
            require(max(widths) <= PK_MAX_LINE_PX, f"{change.resource}:{change.entry_id} exceeds {PK_MAX_LINE_PX}px")
        target_texts[change.resource][change.entry_id] = change.target
        record_audit.append(
            {
                "resource": RESOURCES[change.resource].relative,
                "id": change.entry_id,
                "current_utf16le_sha256": change.current_utf16le_sha256,
                "target_utf16le_sha256": change.target_utf16le_sha256,
                "pc_source_utf16le_sha256": dict(change.source_utf16le_sha256),
                "target_line_widths_px": list(widths),
                "rationale": change.rationale,
            }
        )

    packed: dict[str, bytes] = {}
    raw: dict[str, bytes] = {}
    for key, spec in RESOURCES.items():
        candidate_raw = rebuild_message_table(current[key].table, tuple(target_texts[key]))
        candidate_packed = recompress_wrapper(candidate_raw, current[key].header)
        require(len(candidate_raw) == spec.target_raw_size, f"{spec.relative} target raw size differs")
        require(sha256_bytes(candidate_raw) == spec.target_raw_sha256, f"{spec.relative} target raw SHA-256 differs")
        require(len(candidate_packed) == spec.target_size, f"{spec.relative} target packed size differs")
        require(sha256_bytes(candidate_packed) == spec.target_sha256, f"{spec.relative} target packed SHA-256 differs")
        header, decoded = decompress_wrapper(candidate_packed)
        candidate_table = parse_message_table(decoded)
        require(rebuild_message_table(candidate_table, candidate_table.texts) == decoded, f"{spec.relative} candidate round-trip differs")
        require(recompress_wrapper(decoded, header) == candidate_packed, f"{spec.relative} candidate LZ4 representation differs")
        require(candidate_table.texts == tuple(target_texts[key]), f"{spec.relative} candidate texts differ")
        changed = [index for index, (before, after) in enumerate(zip(current[key].table.texts, candidate_table.texts)) if before != after]
        require(changed == [change.entry_id for change in CHANGE_BY_RESOURCE[key]], f"{spec.relative} changed ID scope differs")
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
                "string_count": current[key].table.string_count,
            }
            for key, spec in RESOURCES.items()
        },
        "changed_cell_count": len(CHANGES),
        "records": record_audit,
    }
    return CandidateBundle(packed, raw, audit, build_manifest(audit))


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
    if output_root.exists():
        raise Wave31Error(f"refusing to overwrite candidate output: {output_root}")
    staging = require_private(output_root.parent / f".{output_root.name}.staging-{uuid.uuid4().hex}", "candidate staging")
    try:
        for key, spec in RESOURCES.items():
            path = staging / spec.relative
            atomic_write(path, bundle.packed[key])
            require(sha256_path(path) == spec.target_sha256, f"written {spec.relative} hash differs")
        atomic_write(staging / "audit.v1.json", canonical_json(bundle.audit))
        atomic_write(staging / "candidate_manifest.v1.json", canonical_json(bundle.manifest))
        require(sha256_path(staging / "audit.v1.json") == bundle.manifest["audit_sha256"], "written audit hash differs")
        os.replace(staging, output_root)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return {
        "candidate_root": output_root.relative_to(REPO).as_posix(),
        "changed_cell_count": len(CHANGES),
        "steam_game_resource_written": False,
    }


def verify_private(candidate_root: Path) -> dict[str, Any]:
    candidate_root = require_private(candidate_root, "candidate root")
    bundle = prepare_candidate()
    require(candidate_root.is_dir(), "candidate root is absent")
    for key, spec in RESOURCES.items():
        path = candidate_root / spec.relative
        require(path.is_file(), f"candidate resource is absent: {spec.relative}")
        require(sha256_path(path) == spec.target_sha256, f"candidate resource hash differs: {spec.relative}")
        require(path.read_bytes() == bundle.packed[key], f"candidate resource bytes differ: {spec.relative}")
    require((candidate_root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((candidate_root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return {
        "candidate_root": candidate_root.relative_to(REPO).as_posix(),
        "changed_cell_count": len(CHANGES),
        "resources": {spec.relative: spec.target_sha256 for spec in RESOURCES.values()},
        "steam_game_resource_written": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    verify_parser = subparsers.add_parser("verify-private")
    verify_parser.add_argument("--candidate-root", type=Path, default=TMP_ROOT / "candidate")
    args = parser.parse_args()
    if args.command == "build":
        print(json.dumps(write_candidate(prepare_candidate(), args.output_root), ensure_ascii=True, indent=2, sort_keys=True))
        return 0
    print(json.dumps(verify_private(args.candidate_root), ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
