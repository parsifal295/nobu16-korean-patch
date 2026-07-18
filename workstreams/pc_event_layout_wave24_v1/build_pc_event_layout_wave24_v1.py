#!/usr/bin/env python3
"""Build the private Wave 24 PC event-layout candidate.

Only five static cells in ``MSG_PK/JP/msgev.bin`` are reflowed.  The sole
input is the complete Wave 23 candidate; this builder has no Steam write,
transaction, Git, network, or release capability.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
import unicodedata
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
PREDECESSOR_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave23_static_inflection_v1" / "candidate"
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
TOOLS = REPO / "tools"

PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
RESOURCE = "MSG_PK/JP/msgev.bin"
FONT_RESOURCE = STEAM_ROOT / "RES_JP" / "res_lang.bin"
MAX_LINES = 3
MAX_LINE_PX = 912
EXPECTED_STRING_COUNT = 17_916

INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    "MSG/JP/msggame.bin": "A5B688C4DF72F9796759A13FBEDB30C30C47873DF9228B9566127877AFD5F810",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "D922E7C2B0BD4078A5DB14C87973ECB7BB1A62A4CA2EA30A03A231AB40C1E86B",
    "MSG_PK/JP/msggame.bin": "432B4F9D3DEF80DDF8288AE82AB1A245EE44585776FC368658A47CBBD826EB8B",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
INPUT_SIZES = {
    "MSG/JP/ev_strdata.bin": 928_123,
    "MSG/JP/msggame.bin": 1_504_691,
    "MSG/JP/strdata.bin": 957_204,
    "MSG_PK/JP/msgbre.bin": 484_068,
    "MSG_PK/JP/msgdata.bin": 496_995,
    "MSG_PK/JP/msgev.bin": 994_727,
    "MSG_PK/JP/msggame.bin": 1_806_795,
    "MSG_PK/JP/msgire.bin": 23_128,
    "MSG_PK/JP/msgstf.bin": 17_341,
    "MSG_PK/JP/msgstf_ce.bin": 18_767,
    "MSG_PK/JP/msgui.bin": 122_733,
}
TARGET_SHA256 = {**INPUT_SHA256, RESOURCE: "91F4C99B1C4D21CE9A3529CB174AA1EFD9E198E8FEB6F90F5AD507CEBB4B8C4F"}
TARGET_SIZES = {**INPUT_SIZES, RESOURCE: 994_731}
INPUT_RAW_SHA256 = "86E45EA2C485FED6E1D24F74EE4E085479683C7C1269EB77710484762439B7F2"
INPUT_RAW_SIZE = 990_816
TARGET_RAW_SHA256 = "F4BF7100C40A2D227672866901E095DE87C0DD7F0891D2E07F6C22CB477A2DA1"
TARGET_RAW_SIZE = 990_820

LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
FOREIGN_CJK_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uf900-\ufaff]")


class Wave24Error(ValueError):
    """A pinned input, source anchor, or layout invariant drifted."""


@dataclass(frozen=True)
class SourceSpec:
    language: str
    path: Path
    packed_sha256: str
    packed_size: int
    raw_sha256: str
    raw_size: int


@dataclass(frozen=True)
class Change:
    entry_id: int
    current_sha256: str
    target: str
    target_sha256: str
    widths_px: tuple[int, ...]
    source_hashes: Mapping[str, str]
    rationale: str


@dataclass(frozen=True)
class LoadedTable:
    packed: bytes
    header: Any
    raw: bytes
    table: Any


SOURCE_SPECS = {
    "JP": SourceSpec(
        "JP",
        STEAM_ROOT / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals" / RESOURCE,
        "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        562_226,
        "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
        894_800,
    ),
    "EN": SourceSpec(
        "EN", STEAM_ROOT / "MSG_PK/EN/msgev.bin", "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E", 762_196,
        "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911", 1_878_836,
    ),
    "SC": SourceSpec(
        "SC", STEAM_ROOT / "MSG_PK/SC/msgev.bin", "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA", 522_177,
        "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E", 754_708,
    ),
    "TC": SourceSpec(
        "TC", STEAM_ROOT / "MSG_PK/TC/msgev.bin", "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6", 524_909,
        "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6", 744_212,
    ),
}

CHANGES = (
    Change(3725, "83674B629AD3C456EA9192E137816E8806DCAC8FF702A3A51AB6158F677E8DEA", "이 난세에는 힘없는 자는\n멸망할 뿐이다…… 너와 함께\n검술을 배우는 것도 그 때문이다.", "F397E2D588E81096BFF3D4B7C344A86DAF24703F6EAF0D689CC6A69DAF4AB609", (552, 648, 744), {"JP": "B6ADADC59A991D64C0FB9AD83621477A9C2F3C76C141EE3027C00E5608DF3908", "EN": "4D6707D644CF59DA0F999E6092F9760DAE7991468A75A2E791788D5207855590", "SC": "07577525F7431E3EBD799F704FE73F6E02C645B0243A3BF6D5DFF8691DB33A4F", "TC": "55DB95993BE914C133FC92D5D19CB94FEF00400D01FF6F8B42C2B0E9D9939149"}, "문맥상 난세의 이유와 검술 수련의 동기를 각각 읽히도록 재배치한다."),
    Change(4208, "7BF48669A7E2FA2E1729B79634BED8B67200A6F8420F2A048F4517BD21035ECF", "(영리한 두 아우에게 가려 있었지만,\n그는 착실히 당주로서의 자질을\n보이고 있었다……)", "B332EAF2564A7CD7F909ED541A5DC6579A784F765471F179DD81AD91932F02E7", (816, 696, 432), {"JP": "587BDD8A317C7C1C1A1F3DA24F2FDD5ED5EC8DB225AD31218CA947DBD9D0DABA", "EN": "3031C84AE788A66D6A63BACA436A6B33268B5484EA9548ECCF3FA33FADB85E6A", "SC": "5CC86039FD67F43E6E574A0F392DBBF2E3CD86186B59E9683EE07722B292A432", "TC": "06D2F908692F233EC64C9B57F02213AB8028AD73721B8CB29FDF9E02A5B6CEB9"}, "당주의 그릇이라는 직역투를 PC 4언어 문맥에 맞는 당주로서의 자질로 보정한다."),
    Change(4677, "5561F2598E218220674701B1538DB943FB8571D00AF16A803A2EFA69DE191408", "어디의 누군지도 모를 자에게\n넘어갈 바에는,\n자네 같은 사내에게 넘기고 싶군.", "4E55B9E79C164D3F179A9177C9659D0848E6B6B206C22BC9E14205D08CA38304", (648, 336, 744), {"JP": "8426E8E8DF7F1478CDDC0A1B782B1B61E9AFA0B869AB73C94E1DB659580C6476", "EN": "23F49D6526CA5DADEB54516BBA7E84DF383A01EA688733420EEF3CB9C642C56D", "SC": "FD37B7014BE5BA05BAF1694913F6BB34DA701EFE1AFA6EDAF4DE4C42755DEF6D", "TC": "19904B5D9991A8338AD9B29BE80D3C1DD44E6965FF3192058899F7539EDF8271"}, "모르는 자에게 넘어가는 경우와 상대를 택하는 결론을 분리한다."),
    Change(4918, "FCD758B94FFABCC6A392611C23EA9EAEFF0257ABFD68F84C946AF0D409747566", "계책이 많으면 이기고, 적으면\n진다…… 인가. 아버님, 못난 아들을\n용서해 주십시오……", "3C8AAEE00883C40F08EB872DE64A509A0FD9BC8A02B0C88CBA8920A6B8FD8B52", (672, 816, 456), {"JP": "A4CE1C829FA3FDB6EA4A4B7C01901962ADD6F1B4B07D4C7109975234B9E24FF8", "EN": "81DE9E7213D2C12DD4C8F25E14C8CFEDB54CA0344B526470FB97565E7EE17D69", "SC": "85D3753DC088DBFEF12765157EBB5ACC2E598422C610CA3060E897056A90CA68", "TC": "03D74F27C76D5AEE166223FE6FE942AC7C10F38CDCDFCADC345F2D28246786CE"}, "PC JP/SC/TC의 대조 쉼표와 아버지에게 드리는 청원을 보존한다."),
    Change(5351, "5DD0456D832C04848B7E89A49251214C01AB9C1E7015ACCA50CCEA37B0E26015", "그의 약진에는 미카와 무사들의\n강인함과 동족 의식에서 나온 결속이\n크게 이바지했다.", "E69436C22D563AB986970E6D9ACB41C8472EE90925FD6505BB319D37B8C9C322", (696, 816, 384), {"JP": "361517A9068DA1F53B9DEE269F48B6BBBE7E59930D06CFAAAB17FAFF23D12CD4", "EN": "EFC28A4A7E73F97E9A849F07B95610F3A8C2A42130D16D8E8E22190ECE426E8D", "SC": "8FAB40E6FE2842851F9BC0F35239E7E781F6440A043754010BF49A5251849983", "TC": "31D663C852797E002359E4F0D1C674377C0AEA9C9B47301DD2A37B603EA38D97"}, "미카와 무사들의 강인함·결속과 약진의 인과를 세 줄로 읽히게 한다."),
)
RETAINED_WAVE18_IDS = (11007, 14040, 14386, 14391, 14403, 14623, 14648, 14651)

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave24Error(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_tmp(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    if resolved == root or root not in resolved.parents:
        raise Wave24Error(f"{label} must be below {root}: {resolved}")
    return resolved


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave24Error(f"Nintendo Switch Korean path is forbidden: {label}")
    return resolved


def profile_hashes(root: Path) -> dict[str, str]:
    return {relative: sha256_path((root / relative).resolve(strict=True)) for relative in PROFILE_PATHS}


def profile_sizes(root: Path) -> dict[str, int]:
    return {relative: (root / relative).resolve(strict=True).stat().st_size for relative in PROFILE_PATHS}


def assert_profile(root: Path, hashes: Mapping[str, str], sizes: Mapping[str, int], label: str) -> None:
    root = root.resolve(strict=True)
    require(profile_hashes(root) == dict(hashes), f"{label} hash profile differs")
    require(profile_sizes(root) == dict(sizes), f"{label} size profile differs")


def load_table(path: Path, *, expected_hash: str, expected_size: int, expected_raw_hash: str | None = None, expected_raw_size: int | None = None, label: str) -> LoadedTable:
    path = path.resolve(strict=True)
    packed = path.read_bytes()
    require(len(packed) == expected_size, f"{label} packed size differs")
    require(sha256_bytes(packed) == expected_hash, f"{label} packed SHA-256 differs")
    header, raw = decompress_wrapper(packed)
    if expected_raw_hash is not None:
        require(sha256_bytes(raw) == expected_raw_hash, f"{label} raw SHA-256 differs")
    if expected_raw_size is not None:
        require(len(raw) == expected_raw_size, f"{label} raw size differs")
    table = parse_message_table(raw)
    require(table.string_count == EXPECTED_STRING_COUNT, f"{label} string count differs")
    require(rebuild_message_table(table, table.texts) == raw, f"{label} raw table does not round-trip")
    return LoadedTable(packed, header, raw, table)


def load_predecessor() -> tuple[dict[str, bytes], LoadedTable]:
    root = PREDECESSOR_ROOT.resolve(strict=True)
    require(root != REPO.resolve(), "predecessor must be a private candidate")
    assert_profile(root, INPUT_SHA256, INPUT_SIZES, "Wave 23 predecessor")
    files = {relative: (root / relative).read_bytes() for relative in PROFILE_PATHS}
    current = load_table(
        root / RESOURCE,
        expected_hash=INPUT_SHA256[RESOURCE], expected_size=INPUT_SIZES[RESOURCE],
        expected_raw_hash=INPUT_RAW_SHA256, expected_raw_size=INPUT_RAW_SIZE, label="Wave 23 PK msgev",
    )
    return files, current


def load_sources() -> dict[str, LoadedTable]:
    sources: dict[str, LoadedTable] = {}
    for language, spec in SOURCE_SPECS.items():
        path = reject_switch_path(spec.path, f"PC {language} source")
        sources[language] = load_table(
            path, expected_hash=spec.packed_sha256, expected_size=spec.packed_size,
            expected_raw_hash=spec.raw_sha256, expected_raw_size=spec.raw_size, label=f"PC {language} msgev",
        )
    return sources


def load_font() -> tuple[Any, dict[str, Any]]:
    """Reuse the pinned active-PC event-font decoder from the prior event workstream."""
    source = REPO / "workstreams" / "pc_event_static_labels_wave18_v1" / "build_pc_event_static_labels_wave18_v1.py"
    spec = importlib.util.spec_from_file_location("wave24_font_contract", source)
    if spec is None or spec.loader is None:
        raise Wave24Error("cannot load active event-font contract")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    advance, evidence = module.load_event_font_advance()
    require(Path(FONT_RESOURCE).is_file(), "active event font is absent")
    return advance, dict(evidence)


def text_signature(value: str) -> dict[str, Any]:
    escapes: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, "malformed ESC token")
            escapes.append(token)
            cursor += 3
            continue
        if character not in ("\r", "\n") and unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        cursor += 1
    printf = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf}
    return {
        "linebreak_vector": LINEBREAK_RE.findall(value),
        "esc": escapes,
        "printf": [match.group(0) for match in printf],
        "runtime": RUNTIME_RE.findall(value),
        "unknown_percent_count": sum(1 for index, character in enumerate(value) if character == "%" and index not in printf_offsets),
        "controls": controls,
        "space_count": value.count(" "),
        "tab_count": value.count("\t"),
    }


def line_widths(value: str, advance: Any) -> tuple[int, ...]:
    widths: list[int] = []
    for line in LINEBREAK_RE.sub("\n", value).split("\n"):
        width = 0
        cursor = 0
        while cursor < len(line):
            character = line[cursor]
            if character == "\x1b":
                token = line[cursor : cursor + 3]
                require(ESC_RE.fullmatch(token) is not None, "malformed ESC token in layout")
                cursor += 3
                continue
            require(unicodedata.category(character) != "Cc", f"unexpected control U+{ord(character):04X}")
            width += int(advance(character))
            cursor += 1
        widths.append(width)
    return tuple(widths)


def validate_change(change: Change, current: LoadedTable, sources: Mapping[str, LoadedTable], advance: Any) -> dict[str, Any]:
    require(change.entry_id < current.table.string_count, f"{change.entry_id}: current ID is absent")
    current_text = current.table.texts[change.entry_id]
    require(text_hash(current_text) == change.current_sha256, f"{change.entry_id}: current text hash differs")
    require(text_hash(change.target) == change.target_sha256, f"{change.entry_id}: target text hash differs")
    require("\x00" not in change.target and "\ufffd" not in change.target, f"{change.entry_id}: unsafe target character")
    require(FOREIGN_CJK_RE.search(change.target) is None, f"{change.entry_id}: foreign CJK residue")
    current_signature = text_signature(current_text)
    target_signature = text_signature(change.target)
    require(current_signature == target_signature, f"{change.entry_id}: token, control, whitespace, or manual-break signature differs")
    widths = line_widths(change.target, advance)
    require(widths == change.widths_px, f"{change.entry_id}: target font widths differ")
    require(1 <= len(widths) <= MAX_LINES and all(width <= MAX_LINE_PX for width in widths), f"{change.entry_id}: target layout exceeds limits")
    anchor_hashes: dict[str, str] = {}
    for language, source in sources.items():
        observed = text_hash(source.table.texts[change.entry_id])
        require(observed == change.source_hashes[language], f"{change.entry_id}: PC {language} anchor differs")
        anchor_hashes[language] = observed
    return {
        "id": change.entry_id,
        "current_utf16le_sha256": change.current_sha256,
        "target_utf16le_sha256": change.target_sha256,
        "pc_reference_utf16le_sha256": anchor_hashes,
        "manual_line_count": len(widths),
        "target_line_widths_px": list(widths),
        "signature_preserved": True,
        "rationale": change.rationale,
    }


def prepare_candidate() -> tuple[dict[str, bytes], dict[str, Any], dict[str, Any]]:
    files, current = load_predecessor()
    sources = load_sources()
    advance, font_evidence = load_font()
    target_texts = list(current.table.texts)
    records: list[dict[str, Any]] = []
    retained_labels = {entry_id: current.table.texts[entry_id] for entry_id in RETAINED_WAVE18_IDS}
    for change in CHANGES:
        records.append(validate_change(change, current, sources, advance))
        target_texts[change.entry_id] = change.target
    raw_a = rebuild_message_table(current.table, target_texts)
    raw_b = rebuild_message_table(current.table, target_texts)
    require(raw_a == raw_b, "event raw rebuild is not deterministic")
    require(len(raw_a) == TARGET_RAW_SIZE and sha256_bytes(raw_a) == TARGET_RAW_SHA256, "target raw profile differs")
    packed_a = recompress_wrapper(raw_a, current.header)
    packed_b = recompress_wrapper(raw_a, current.header)
    require(packed_a == packed_b, "event compression is not deterministic")
    require(len(packed_a) == TARGET_SIZES[RESOURCE] and sha256_bytes(packed_a) == TARGET_SHA256[RESOURCE], "target PK msgev profile differs")
    header, checked_raw = decompress_wrapper(packed_a)
    checked = parse_message_table(checked_raw)
    require(checked_raw == raw_a and header.prefix == current.header.prefix, "candidate wrapper changed unexpectedly")
    require(tuple(checked.texts) == tuple(target_texts), "candidate text table differs")
    changed_ids = tuple(index for index, pair in enumerate(zip(current.table.texts, checked.texts)) if pair[0] != pair[1])
    expected_ids = tuple(change.entry_id for change in CHANGES)
    require(changed_ids == expected_ids, f"unexpected changed event IDs: {changed_ids}")
    require(all(checked.texts[entry_id] == value for entry_id, value in retained_labels.items()), "Wave 18 event labels drifted")
    files[RESOURCE] = packed_a
    require({relative: sha256_bytes(value) for relative, value in files.items()} == TARGET_SHA256, "full target hash profile differs")
    require({relative: len(value) for relative, value in files.items()} == TARGET_SIZES, "full target size profile differs")
    audit = {
        "schema": "nobu16.kr.pc-event-layout-wave24.audit.v1",
        "source_policy": {
            "predecessor": "complete Wave 23 eleven-file candidate",
            "pristine_pc_japanese_read": True,
            "pc_pk_en_sc_tc_context_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "changed_resource": RESOURCE,
        "changed_ids": list(expected_ids),
        "records": records,
        "font": font_evidence,
        "input_sha256": INPUT_SHA256,
        "input_sizes": INPUT_SIZES,
        "target_sha256": TARGET_SHA256,
        "target_sizes": TARGET_SIZES,
        "retained_wave18_label_ids": list(RETAINED_WAVE18_IDS),
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-layout-wave24.manifest.v1",
        "candidate_only": True,
        "profile_paths": list(PROFILE_PATHS),
        "input_sha256": INPUT_SHA256,
        "input_sizes": INPUT_SIZES,
        "target_sha256": TARGET_SHA256,
        "target_sizes": TARGET_SIZES,
        "changed_resource": RESOURCE,
        "changed_ids": list(expected_ids),
        "source_policy": audit["source_policy"],
    }
    return files, audit, manifest


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with temporary.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def write_private(files: Mapping[str, bytes], audit: Mapping[str, Any], manifest: Mapping[str, Any], output_root: Path) -> dict[str, str]:
    output_root = require_tmp(output_root, "candidate root")
    require(not output_root.exists(), f"refusing to overwrite candidate root: {output_root}")
    audit_path = require_tmp(TMP_ROOT / "audit.v1.json", "audit")
    manifest_path = require_tmp(TMP_ROOT / "build_manifest.v1.json", "manifest")
    require(not audit_path.exists() and not manifest_path.exists(), "refusing to overwrite Wave 24 evidence")
    stage = require_tmp(output_root.parent / f".{output_root.name}.stage-{uuid.uuid4().hex}", "candidate staging root")
    try:
        for relative in PROFILE_PATHS:
            target = stage / relative
            atomic_write(target, files[relative])
        os.replace(stage, output_root)
        atomic_write(audit_path, canonical_json(audit))
        atomic_write(manifest_path, canonical_json(manifest))
    except Exception:
        if stage.exists():
            for child in sorted(stage.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            stage.rmdir()
        raise
    return {"candidate_root": output_root.relative_to(REPO).as_posix(), "audit": audit_path.relative_to(REPO).as_posix(), "manifest": manifest_path.relative_to(REPO).as_posix()}


def verify_private(candidate_root: Path) -> None:
    candidate_root = candidate_root.resolve(strict=True)
    require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, TARGET_SIZES, "private Wave 24 candidate")
    expected_files, audit, manifest = prepare_candidate()
    for relative in PROFILE_PATHS:
        require((candidate_root / relative).read_bytes() == expected_files[relative], f"private candidate bytes differ: {relative}")
    audit_path = require_tmp(TMP_ROOT / "audit.v1.json", "audit")
    manifest_path = require_tmp(TMP_ROOT / "build_manifest.v1.json", "manifest")
    require(audit_path.is_file() and audit_path.read_bytes() == canonical_json(audit), "private audit differs")
    require(manifest_path.is_file() and manifest_path.read_bytes() == canonical_json(manifest), "private manifest differs")


def command_hash(_args: argparse.Namespace) -> int:
    files, audit, _manifest = prepare_candidate()
    print(json.dumps({"status": "ok", "changed_ids": audit["changed_ids"], "target_sha256": {relative: sha256_bytes(value) for relative, value in files.items()}, "steam_write_capability": "absent"}, ensure_ascii=True, sort_keys=True))
    return 0


def command_build(args: argparse.Namespace) -> int:
    files, audit, manifest = prepare_candidate()
    result = write_private(files, audit, manifest, args.output_root)
    print(json.dumps({"status": "ok", **result, "steam_write_capability": "absent"}, ensure_ascii=True, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    verify_private(args.candidate_root)
    print(json.dumps({"status": "ok", "candidate_root": str(args.candidate_root), "steam_write_capability": "absent"}, ensure_ascii=True, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("hash").set_defaults(func=command_hash)
    build = commands.add_parser("build")
    build.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    build.set_defaults(func=command_build)
    verify = commands.add_parser("verify-private")
    verify.add_argument("--candidate-root", type=Path, required=True)
    verify.set_defaults(func=command_verify)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, Wave24Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
