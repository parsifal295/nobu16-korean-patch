#!/usr/bin/env python3
"""Build the PC-only private Wave 26 static-inflection candidate.

The only Korean preimage is the complete Wave 25 eleven-file private
candidate.  Exactly twenty reviewed Base-to-PK dialogue pairs are rebuilt;
only their complete static ``01 43`` commands are removed.  Output is limited
to this workstream's private tmp directory.
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
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
PREDECESSOR_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave25_static_consistency_v1" / "candidate"
PREDECESSOR_AUDIT = REPO / "tmp" / "pc_dialogue_quality_wave25_static_consistency_v1" / "audit.v1.json"
PREDECESSOR_MANIFEST = REPO / "tmp" / "pc_dialogue_quality_wave25_static_consistency_v1" / "build_manifest.v1.json"
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

for root in (TOOLS, MSGGAME_TOOLS):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402
from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_raw_msggame,
)


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave26-static-inflection.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave26-static-inflection-audit.v1"
BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
CHANGED_PATHS = (BASE_MSGGAME, PK_MSGGAME)
PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    BASE_MSGGAME,
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    PK_MSGGAME,
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
RECORD_TERMINATOR = b"\x05\x05\x05"
MORPHOLOGY_PREFIX = b"\x01\x43"
DIALOGUE_MAX_LINE_PX = 912
FONT_PATH = "RES_JP/res_lang.bin"
FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
FONT_ENTRY = 6
WIDE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]")

# Exact Wave 25 candidate profile, including its Wave 24 msgev preservation
# and Wave 25 PK msggame change.  No Steam game directory is a preimage.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "A5B688C4DF72F9796759A13FBEDB30C30C47873DF9228B9566127877AFD5F810",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "91F4C99B1C4D21CE9A3529CB174AA1EFD9E198E8FEB6F90F5AD507CEBB4B8C4F",
    PK_MSGGAME: "70FB0AB6EB2B07795CB37DEEB8941635184DC3C48246A6F45C25B59CD75559BC",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
INPUT_SIZES = {
    "MSG/JP/ev_strdata.bin": 928123,
    BASE_MSGGAME: 1504691,
    "MSG/JP/strdata.bin": 957204,
    "MSG_PK/JP/msgbre.bin": 484068,
    "MSG_PK/JP/msgdata.bin": 496995,
    "MSG_PK/JP/msgev.bin": 994731,
    PK_MSGGAME: 1806811,
    "MSG_PK/JP/msgire.bin": 23128,
    "MSG_PK/JP/msgstf.bin": 17341,
    "MSG_PK/JP/msgstf_ce.bin": 18767,
    "MSG_PK/JP/msgui.bin": 122733,
}
TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_MSGGAME: "031BD5C425FA0259624524E78DB99D4F54B16A43D96A43FE850C2A51500D779A",
    PK_MSGGAME: "828559146ACE4F456E9E764A69C5E36B88B34F969E108B9E3177614083E9C760",
}
TARGET_SIZES = {**INPUT_SIZES, BASE_MSGGAME: 1504747, PK_MSGGAME: 1806867}
WAVE25_EVIDENCE = {
    "audit": {"path": PREDECESSOR_AUDIT, "size": 12804, "sha256": "6352ECECCC8973AF74841EA8BA60196BAE9010A9FF47D7400085B5AB0A1DD9E8"},
    "manifest": {"path": PREDECESSOR_MANIFEST, "size": 4512, "sha256": "5529A76757B33D021A6BEBBF4959C2CFE7386BB039FCC5FBD898770CDF14BFD6"},
}

# All language anchors below are PC files.  This source list deliberately has
# no Switch path or Korean alternate-platform input.
PC_REFERENCE_PATHS = {
    "BASE_JP": (Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root\MSG\JP\msggame.bin"), "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"),
    "PK_JP": (DEFAULT_STEAM_ROOT / "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin", "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"),
    "EN": (DEFAULT_STEAM_ROOT / "MSG_PK/EN/msggame.bin", "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916"),
    "SC": (DEFAULT_STEAM_ROOT / "MSG_PK/SC/msggame.bin", "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802"),
    "TC": (DEFAULT_STEAM_ROOT / "MSG_PK/TC/msggame.bin", "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23"),
}


class Wave26Error(RuntimeError):
    """A pinned source, structural guard, or private-output contract failed."""


@dataclass(frozen=True)
class Family:
    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    target_literals: tuple[str, ...]


FAMILIES = (
    Family("receive_order", (15, 2204), (15, 2234), ("분부를 받들겠습니다. ", "\n충실히 소임을 다하겠습니다.")),
    Family("military_studies", (15, 2205), (15, 2235), ("병학을 닦은 성과를 보여 드리겠습니다. ", "\n곧 낭보를 전해 올리겠습니다.")),
    Family("clan_prosperity", (15, 2206), (15, 2236), ("주가의 번영을 위해 사력을 다하리다.\n공명을 얻도록 달에 기원하리다.",)),
    Family("literary_martial_skill", (15, 2207), (15, 2237), ("귀한 분부를 받들게 되었으니\n제 문무의 진수를 보여 드리겠습니다.",)),
    Family("right_hand_loyalty", (15, 2209), (15, 2239), ("현명한 결단에 감사드리며\n주군의 오른팔 되어 충성을 다하리다.",)),
    Family("monk_stratagem", (15, 2211), (15, 2241), ("이 중이 소매를 걷어붙이고 ", "\n배워 익힌 묘책을 보여 드리겠습니다.")),
    Family("encirclement_retreat", (15, 2213), (15, 2243), ("우리 부대가 협격을 받고 있사옵니다. ", "\n일단 물러나 전열을 정비해야 하옵니다.")),
    Family("permission_to_retreat", (15, 2214), (15, 2244), ("적의 협격을 받았습니다", "…\n일시 후퇴를 허락해 주십시오!")),
    Family("forced_retreat", (15, 2215), (15, 2245), ("방심하여 협격을 당했습니다", "!\n여기서는 후퇴할 수밖에 없습니다.")),
    Family("suggest_encirclement", (15, 2216), (15, 2246), ("지금 적 부대를 협격할 수 있습니다. ", "\n아군 부대에 지시를 내려 보시는 것은\n어떻겠습니까?")),
    Family("encirclement_opportunity", (15, 2217), (15, 2247), ("적을 협격할 절호의 기회입니다. ", "\n부대에 지시를 내리십시오!")),
    Family("encirclement_damage", (15, 2218), (15, 2248), ("적 부대를 협격하면\n큰 피해를 입힐 수 있습니다.",)),
    Family("retreat_permission", (15, 2222), (15, 2252), ("이 싸움은 승산이 없습니다. ", "\n철수하도록 허락해 주시겠습니까?")),
    Family("heavy_heart_retreat", (15, 2223), (15, 2253), ("…마음이 무겁사오나 ", "\n이번 싸움은 승산이 희박하니\n철수할 때인 듯하옵니다.")),
    Family("urge_retreat", (15, 2225), (15, 2255), ("이 싸움은 승산이 없사옵니다. ", "\n공연히 피해만 키우기 전에\n철수를 진언드리옵니다.")),
    Family("wait_for_opportunity", (15, 2238), (15, 2268), ("지금은 움직일 때가 아니옵니다. ", "\n기회를 엿보는 편이 ", "좋겠사옵니다.")),
    Family("favorable_battle", (15, 2240), (15, 2270), ("전황은 우리 쪽이 우세합니다. ", "\n우선 눈앞의 싸움에서 승리를 거두고\n착실히 세력을 넓혀 나가야 합니다.")),
    Family("unfavorable_battle", (15, 2241), (15, 2271), ("전황은 결코 우세하지 않습니다. ", "\n피해가 커질 듯하면\n물러날 때를 가늠하는 것도 긴요합니다.")),
    Family("base_development", (15, 2246), (15, 2276), ("본거지 개발도 아직 진행 중이라면\n군 개발을 명해 보시겠습니까?",)),
    Family("castle_development", (15, 2247), (15, 2277), ("아직 개발할 성이 남아 있습니다. ", "\n석고 증강을 명해 보시겠습니까?")),
)
if len({family.base_coordinate for family in FAMILIES}) != len(FAMILIES) or len({family.pk_coordinate for family in FAMILIES}) != len(FAMILIES):
    raise RuntimeError("duplicate Wave 26 coordinate")

# Independent per-record target pins.  Base and PK target records converge
# byte-for-byte after their platform-specific complete static 0143 commands
# are removed; each pin is therefore asserted for both members of the pair.
TARGET_RECORD_PINS = {
    "receive_order": ("C3505EE0F4A4869597DB8E333DB4F65191C5F3E2407C49D7D96855F03CC9F12A", 71, (504, 648)),
    "military_studies": ("6F63B1584309E7BD20239C851B600539BE6C528D13569C350BE0513DB3F78F8A", 93, (912, 672)),
    "clan_prosperity": ("421722083821DF4815583FDBD0C580C45F98B4897DAE48A49F8B3F11F3E94BF4", 85, (840, 720)),
    "literary_martial_skill": ("6361CED3EB8D4CF433043931F12D663C5F94830E734A4EFF94E962DA829ED0C1", 81, (648, 840)),
    "right_hand_loyalty": ("22D54CD377900297D7D6D74310D4C37701239B4E3C7A272E09044120D3A24A10", 77, (576, 840)),
    "monk_stratagem": ("ADB9DFC113E0310933B915E49B0D55FE729257CD3D28A5F4DE787EBBCD60E10E", 87, (624, 840)),
    "encirclement_retreat": ("173F5D01B2D3A1E70B20939FD722C2A7AFA9798301EF18428D41BEE002F7916B", 101, (864, 888)),
    "permission_to_retreat": ("2141FAA0AC35D68DAE616B582F9FA4CD91D25D587F88E082A795BEB4BFB4EDFE", 75, (576, 672)),
    "forced_retreat": ("CFCBE874FA81094518B901961D4891A5F5AB8170768A3FE336DEFED77090953A", 83, (648, 768)),
    "suggest_encirclement": ("148EC150A074D35D60C98001B744A2B0984ABCF5A770046AB4D5EE140C2DEAC0", 115, (840, 840, 312)),
    "encirclement_opportunity": ("4AC5F1B2422908F73C86889174964A2853628FA65593F26B0148B47060730D3B", 81, (744, 600)),
    "encirclement_damage": ("F83316844FA64E2A26B6CB87D1B6CD391ECE64048191C2A3A8EC3FD25EDC8B58", 63, (432, 648)),
    "retreat_permission": ("7D508B41DE822E00A57482DF59C027C8AFD6CC31C1B9AED83AABD7D0767F8231", 83, (648, 744)),
    "heavy_heart_retreat": ("BF5CA042DBA979BE3A1527C479C132A1D22AFE4A0493BE87A609D89B5FA7E2EA", 97, (480, 648, 552)),
    "urge_retreat": ("9F456ABCFEF3BD8BC73CFDB51E138EC3F52D995CFF68016FFA36457E1B766FD9", 105, (696, 600, 528)),
    "wait_for_opportunity": ("7A66121D0A3C0A9FA75C834BBB22E75077D7039786DAFAD327C14F84EBE01411", 95, (744, 768)),
    "favorable_battle": ("0E406CA549AE3B496FB4F47B978A36E587144B5908371D2505D5A0D8928159AB", 129, (696, 816, 792)),
    "unfavorable_battle": ("3B55BF4BE084329733489678DBA28AAF1B1733EA44924D627A908E1503E51CAA", 117, (744, 432, 888)),
    "base_development": ("CCE917A143D514129513ADA23CE57246E86EB391D64B4F90105A49CCBFBCB249", 79, (768, 672)),
    "castle_development": ("7520EE71190C1AEA48C79A8475F9E2825AFCDEEAB9B63AC9CA89F6B7FDE0ED0F", 89, (768, 720)),
}
if set(TARGET_RECORD_PINS) != {family.name for family in FAMILIES}:
    raise RuntimeError("incomplete Wave 26 target record pins")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    return {(record.block_id, record.record_id): record for block in parse_packed_msggame(packed).archive.blocks for record in block.records}


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(item.text for item in parse_record_literals(record))


def opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    cursor = 0
    result: list[bytes] = []
    for item in parse_record_literals(record):
        result.append(record.data[cursor:item.marker_offset])
        cursor = item.marker_end
    result.append(record.data[cursor:])
    return tuple(result)


def marker_topology(record: MsgGameRecord) -> tuple[tuple[bytes, bytes], ...]:
    return tuple((record.data[item.marker_offset:item.marker_offset + len(LITERAL_START)], record.data[item.marker_end - len(LITERAL_END):item.marker_end]) for item in parse_record_literals(record))


def complete_0143_commands(spans: tuple[bytes, ...]) -> tuple[str, ...]:
    commands: list[str] = []
    for span in spans:
        cursor = 0
        while cursor < len(span):
            if span[cursor:cursor + 2] == MORPHOLOGY_PREFIX:
                if cursor + 6 > len(span):
                    raise Wave26Error("truncated 01 43 command")
                commands.append(span[cursor:cursor + 6].hex().upper())
                cursor += 6
            else:
                cursor += 1
    return tuple(commands)


def strip_complete_0143(span: bytes) -> bytes:
    result = bytearray()
    cursor = 0
    while cursor < len(span):
        if span[cursor:cursor + 2] == MORPHOLOGY_PREFIX:
            if cursor + 6 > len(span):
                raise Wave26Error("truncated 01 43 command")
            cursor += 6
        else:
            result.append(span[cursor])
            cursor += 1
    return bytes(result)


def stripped_opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    return tuple(strip_complete_0143(span) for span in opaque_spans(record))


def profile(root: Path) -> tuple[dict[str, str], dict[str, int]]:
    hashes: dict[str, str] = {}
    sizes: dict[str, int] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave26Error(f"missing profile resource: {relative}")
        hashes[relative] = sha256_path(path)
        sizes[relative] = path.stat().st_size
    return hashes, sizes


def assert_profile(root: Path, expected_hashes: Mapping[str, str], expected_sizes: Mapping[str, int], label: str) -> None:
    actual_hashes, actual_sizes = profile(root)
    if actual_hashes != dict(expected_hashes) or actual_sizes != dict(expected_sizes):
        raise Wave26Error(f"{label} profile differs")


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave26Error(f"Switch input is forbidden: {label}")
    return resolved


def require_predecessor_root(root: Path) -> Path:
    expected = PREDECESSOR_ROOT.resolve(strict=True)
    checked = reject_switch_path(root, "Wave 25 private candidate")
    if checked != expected:
        raise Wave26Error("input must be the unique Wave 25 private candidate")
    return checked


def validate_wave25_evidence(root: Path) -> dict[str, Any]:
    for name, spec in WAVE25_EVIDENCE.items():
        path = Path(spec["path"])
        if not path.is_file() or path.stat().st_size != spec["size"] or sha256_path(path) != spec["sha256"]:
            raise Wave26Error(f"Wave 25 {name} evidence differs")
    try:
        audit = json.loads(PREDECESSOR_AUDIT.read_text(encoding="utf-8"))
        manifest = json.loads(PREDECESSOR_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Wave26Error("Wave 25 evidence JSON is invalid") from exc
    if (
        audit.get("target_sha256") != INPUT_SHA256
        or audit.get("target_sizes") != INPUT_SIZES
        or manifest.get("output_sha256") != INPUT_SHA256
        or manifest.get("output_sizes") != INPUT_SIZES
        or manifest.get("candidate_only") is not True
    ):
        raise Wave26Error("Wave 25 evidence contract differs")
    return {name: {"path": str(spec["path"]), "size": spec["size"], "sha256": spec["sha256"]} for name, spec in WAVE25_EVIDENCE.items()}


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    header, raw = decompress_wrapper(packed)
    if rebuild_raw_msggame(parse_packed_msggame(packed).archive) != raw:
        raise Wave26Error(f"{label} raw parse/rebuild differs")
    _header, restored = decompress_wrapper(recompress_wrapper(raw, header))
    if restored != raw:
        raise Wave26Error(f"{label} wrapper round-trip differs")


def record_report(record: MsgGameRecord) -> dict[str, Any]:
    values = literal_texts(record)
    spans = opaque_spans(record)
    return {
        "record_sha256": sha256_bytes(record.data),
        "record_size": len(record.data),
        "literal_utf16le_sha256": [text_sha256(value) for value in values],
        "opaque_spans_hex": [span.hex().upper() for span in spans],
        "complete_0143_commands_hex": list(complete_0143_commands(spans)),
        "manual_line_count": "".join(values).count("\n") + 1,
    }


def validate_pc_anchors() -> dict[str, Any]:
    archives: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    source_hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_REFERENCE_PATHS.items():
        checked = reject_switch_path(path, f"PC {language}")
        if sha256_path(checked) != expected_hash:
            raise Wave26Error(f"PC {language} reference profile differs")
        archives[language] = records_by_coordinate(checked.read_bytes())
        source_hashes[language] = expected_hash
    rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        base = archives["BASE_JP"].get(family.base_coordinate)
        pk = archives["PK_JP"].get(family.pk_coordinate)
        contexts = {language: archives[language].get(family.pk_coordinate) for language in ("EN", "SC", "TC")}
        if base is None or pk is None or any(value is None for value in contexts.values()):
            raise Wave26Error(f"PC anchor coordinate missing: {family.name}")
        if literal_texts(base) != literal_texts(pk):
            raise Wave26Error(f"PC Base/PK JP source differs: {family.name}")
        if not base.data.endswith(RECORD_TERMINATOR) or not pk.data.endswith(RECORD_TERMINATOR) or any(not value.data.endswith(RECORD_TERMINATOR) for value in contexts.values()):
            raise Wave26Error(f"PC anchor terminator differs: {family.name}")
        rows.append({
            "family": family.name,
            "base_coordinate": f"{family.base_coordinate[0]}:{family.base_coordinate[1]}",
            "pk_coordinate": f"{family.pk_coordinate[0]}:{family.pk_coordinate[1]}",
            "BASE_JP": record_report(base),
            "PK_JP": record_report(pk),
            "contexts": {language: record_report(record) for language, record in contexts.items()},
        })
    return {"reference_packed_sha256": source_hashes, "families": rows}


def validate_literal(value: str, label: str) -> None:
    if not value or "\x1b" in value or "%" in value:
        raise Wave26Error(f"invalid target literal: {label}")
    encoded = value.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave26Error(f"reserved marker in target: {label}")
    if any(unicodedata.category(char) == "Cc" and char not in "\n\r" for char in value):
        raise Wave26Error(f"control in target: {label}")


def load_font_advance() -> tuple[Callable[[str], tuple[int, bool]], dict[str, Any]]:
    path = reject_switch_path(DEFAULT_STEAM_ROOT / FONT_PATH, "active PC JP font")
    if sha256_path(path) != FONT_SHA256:
        raise Wave26Error("active PC JP font profile differs")
    archive = parse_link(path.read_bytes())
    _header, raw = decompress_wrapper(archive.entries[FONT_ENTRY].data)
    with tempfile.TemporaryDirectory(prefix="nobu16_wave26_font_") as directory:
        temp = Path(directory) / "font.g1n"
        temp.write_bytes(raw)
        parsed = g1n.parse_g1n(temp)
    if parsed.structural_errors or not parsed.tables:
        raise Wave26Error("active PC JP font cannot be parsed")
    table = parsed.tables[0]

    def advance(char: str) -> tuple[int, bool]:
        ordinal = table.mapping[ord(char)] if ord(char) < len(table.mapping) else 0
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(char):
                return 48, True
            raise Wave26Error(f"font lacks glyph U+{ord(char):04X}")
        glyph = table.records[ordinal]
        if glyph.width != glyph.advance or glyph.advance not in (24, 48):
            raise Wave26Error(f"font metric differs U+{ord(char):04X}")
        return glyph.advance, False

    return advance, {"resource": FONT_PATH, "entry": FONT_ENTRY, "packed_sha256": FONT_SHA256, "table_count": len(parsed.tables)}


def line_layout(values: tuple[str, ...], advance: Callable[[str], tuple[int, bool]]) -> dict[str, Any]:
    widths: list[int] = []
    fallback: set[str] = set()
    for line in "".join(values).split("\n"):
        width = 0
        for char in line:
            if unicodedata.category(char) == "Cc":
                raise Wave26Error(f"control in font layout U+{ord(char):04X}")
            glyph_width, used_fallback = advance(char)
            width += glyph_width
            if used_fallback:
                fallback.add(f"U+{ord(char):04X}")
        widths.append(width)
    return {"line_count": len(widths), "line_widths_px": widths, "max_width_px": max(widths, default=0), "wide_fallback_codepoints": sorted(fallback)}


def rebuild_static_record(source: MsgGameRecord, target_literals: tuple[str, ...]) -> bytes:
    source_spans = opaque_spans(source)
    if len(source_spans) != len(target_literals) + 1:
        raise Wave26Error("literal-marker count changes")
    payload = bytearray()
    for span, value in zip(source_spans, target_literals):
        payload.extend(strip_complete_0143(span))
        payload.extend(LITERAL_START)
        payload.extend(value.encode("utf-16-le"))
        payload.extend(LITERAL_END)
    payload.extend(strip_complete_0143(source_spans[-1]))
    return bytes(payload)


def validate_change(family: Family, resource: str, source: MsgGameRecord, advance: Callable[[str], tuple[int, bool]]) -> tuple[bytes, dict[str, Any]]:
    current_values = literal_texts(source)
    source_spans = opaque_spans(source)
    commands = complete_0143_commands(source_spans)
    if len(current_values) != len(family.target_literals) or not commands or not source.data.endswith(RECORD_TERMINATOR):
        raise Wave26Error(f"input static command/marker guard differs: {family.name} {resource}")
    if any(not command.startswith("0143") or len(command) != 12 for command in commands):
        raise Wave26Error(f"non-complete 0143 command: {family.name} {resource}")
    for index, value in enumerate(family.target_literals):
        validate_literal(value, f"{family.name}:{index}")
    current_text = "".join(current_values)
    target_text = "".join(family.target_literals)
    if current_text.count("\n") != target_text.count("\n") or target_text.count("\n") + 1 > 3:
        raise Wave26Error(f"manual line count differs: {family.name} {resource}")
    layout = line_layout(family.target_literals, advance)
    target_sha256, target_size, target_widths = TARGET_RECORD_PINS[family.name]
    if (
        tuple(layout["line_widths_px"]) != target_widths
        or layout["max_width_px"] > DIALOGUE_MAX_LINE_PX
        or layout["wide_fallback_codepoints"]
    ):
        raise Wave26Error(f"font layout differs: {family.name} {resource}")
    target_data = rebuild_static_record(source, family.target_literals)
    target = MsgGameRecord(source.block_id, source.record_id, source.relative_offset, target_data)
    if (
        sha256_bytes(target.data) != target_sha256
        or len(target.data) != target_size
        or literal_texts(target) != family.target_literals
        or opaque_spans(target) != stripped_opaque_spans(source)
        or complete_0143_commands(opaque_spans(target))
        or marker_topology(target) != marker_topology(source)
        or not target.data.endswith(RECORD_TERMINATOR)
    ):
        raise Wave26Error(f"target structural guard differs: {family.name} {resource}")
    return target_data, {
        "family": family.name,
        "resource": resource,
        "coordinate": f"{source.block_id}:{source.record_id}",
        "input_record": record_report(source),
        "target_record": record_report(target),
        "target_record_pin": {
            "record_sha256": target_sha256,
            "record_size": target_size,
            "font_line_widths_px": list(target_widths),
        },
        "target_literals": list(family.target_literals),
        "removed_complete_0143_commands_hex": list(commands),
        "target_has_no_0143": True,
        "manual_line_count": {"current": current_text.count("\n") + 1, "target": target_text.count("\n") + 1},
        "font_layout": layout,
    }


def expected_coordinate_sets() -> dict[str, set[tuple[int, int]]]:
    return {BASE_MSGGAME: {family.base_coordinate for family in FAMILIES}, PK_MSGGAME: {family.pk_coordinate for family in FAMILIES}}


def validate_output_records(output: Mapping[str, bytes]) -> None:
    records = {resource: records_by_coordinate(data) for resource, data in output.items()}
    for family in FAMILIES:
        for resource, coordinate in ((BASE_MSGGAME, family.base_coordinate), (PK_MSGGAME, family.pk_coordinate)):
            record = records[resource].get(coordinate)
            target_sha256, target_size, _target_widths = TARGET_RECORD_PINS[family.name]
            if (
                record is None
                or sha256_bytes(record.data) != target_sha256
                or len(record.data) != target_size
                or literal_texts(record) != family.target_literals
                or complete_0143_commands(opaque_spans(record))
                or not record.data.endswith(RECORD_TERMINATOR)
            ):
                raise Wave26Error(f"output record differs: {family.name} {resource}")


def prepare_candidate(input_root: Path = PREDECESSOR_ROOT) -> tuple[dict[str, bytes], dict[str, Any]]:
    input_root = require_predecessor_root(input_root)
    evidence = validate_wave25_evidence(input_root)
    assert_profile(input_root, INPUT_SHA256, INPUT_SIZES, "Wave 25 predecessor")
    before = {resource: (input_root / resource).read_bytes() for resource in CHANGED_PATHS}
    for resource, packed in before.items():
        validate_raw_roundtrip(packed, f"Wave 25 {resource}")
    anchors = validate_pc_anchors()
    advance, font = load_font_advance()
    current = {resource: records_by_coordinate(data) for resource, data in before.items()}
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in CHANGED_PATHS}
    rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        for resource, coordinate in ((BASE_MSGGAME, family.base_coordinate), (PK_MSGGAME, family.pk_coordinate)):
            record = current[resource].get(coordinate)
            if record is None or coordinate in replacements[resource]:
                raise Wave26Error(f"replacement coordinate differs: {family.name} {resource}")
            target, row = validate_change(family, resource, record, advance)
            replacements[resource][coordinate] = target
            rows.append(row)
    output: dict[str, bytes] = {}
    expected = expected_coordinate_sets()
    for resource in CHANGED_PATHS:
        candidate = rebuild_packed_msggame(before[resource], replacements[resource])
        if sha256_bytes(candidate) != TARGET_SHA256[resource] or len(candidate) != TARGET_SIZES[resource]:
            raise Wave26Error(f"target packed profile differs: {resource}")
        validate_raw_roundtrip(candidate, f"Wave 26 {resource}")
        old_records = current[resource]
        new_records = records_by_coordinate(candidate)
        changed = {coordinate for coordinate in old_records if old_records[coordinate].data != new_records[coordinate].data}
        if old_records.keys() != new_records.keys() or changed != expected[resource]:
            raise Wave26Error(f"unexpected changed record set: {resource}")
        output[resource] = candidate
    validate_output_records(output)
    target_hashes = {**INPUT_SHA256, **{resource: sha256_bytes(data) for resource, data in output.items()}}
    target_sizes = {**INPUT_SIZES, **{resource: len(data) for resource, data in output.items()}}
    if target_hashes != TARGET_SHA256 or target_sizes != TARGET_SIZES:
        raise Wave26Error("full output profile differs")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "predecessor": "exact Wave 25 eleven-file private candidate",
            "wave25_full_profile_required": True,
            "pc_base_pk_jp_and_en_sc_tc_anchors_read": True,
            "active_pc_jp_font_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor_candidate_root": str(input_root),
        "predecessor_evidence": evidence,
        "input_sha256": INPUT_SHA256,
        "input_sizes": INPUT_SIZES,
        "target_sha256": TARGET_SHA256,
        "target_sizes": TARGET_SIZES,
        "pc_anchors": anchors,
        "font": font,
        "records": rows,
        "changed_record_count": len(rows),
        "changed_literal_count": sum(len(family.target_literals) * 2 for family in FAMILIES),
    }
    return output, audit


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave26Error(f"{label} must remain below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, TARGET_SIZES, "Wave 26 private candidate")
    expected, _audit = prepare_candidate(PREDECESSOR_ROOT)
    for resource in CHANGED_PATHS:
        actual = (candidate_root / resource).read_bytes()
        if actual != expected[resource]:
            raise Wave26Error(f"candidate bytes differ: {resource}")


def remove_stage(stage: Path) -> None:
    if stage.exists():
        require_tmp(stage, "candidate stage")
        shutil.rmtree(stage)


def build_candidate(input_root: Path, output_root: Path, audit_path: Path, manifest_path: Path) -> dict[str, Any]:
    input_root = require_predecessor_root(input_root)
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave26Error("candidate output, audit, or manifest already exists")
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
                shutil.copy2(input_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, TARGET_SIZES, "Wave 26 staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave26-static-inflection-v1",
            "candidate_only": True,
            "predecessor_candidate_root": str(input_root),
            "predecessor_evidence": evidence_for_manifest(),
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "coordinates": [f"{BASE_MSGGAME}:{family.base_coordinate[0]}:{family.base_coordinate[1]}" for family in FAMILIES] + [f"{PK_MSGGAME}:{family.pk_coordinate[0]}:{family.pk_coordinate[1]}" for family in FAMILIES],
            "input_sha256": INPUT_SHA256,
            "input_sizes": INPUT_SIZES,
            "output_sha256": TARGET_SHA256,
            "output_sizes": TARGET_SIZES,
            "audit_sha256": sha256_bytes(audit_bytes),
            "record_count": len(FAMILIES) * 2,
            "steam_write_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
            "real_game_qa_required_before_release": True,
        }
        atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        return manifest
    except Exception:
        remove_stage(stage)
        raise


def evidence_for_manifest() -> dict[str, Any]:
    return {name: {"path": str(spec["path"]), "size": spec["size"], "sha256": spec["sha256"]} for name, spec in WAVE25_EVIDENCE.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("hash", "build"):
        current = sub.add_parser(name)
        current.add_argument("--input-root", type=Path, default=PREDECESSOR_ROOT)
        if name == "build":
            current.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
            current.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
            current.add_argument("--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    verify = sub.add_parser("verify-private")
    verify.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            _output, audit = prepare_candidate(args.input_root)
            print(json.dumps({"status": "ok", "target_sha256": audit["target_sha256"], "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        elif args.command == "verify-private":
            verify_private_candidate(args.candidate_root)
            print(json.dumps({"status": "ok", "candidate_root": str(args.candidate_root), "steam_write_capability": "absent"}, ensure_ascii=False, sort_keys=True))
        else:
            manifest = build_candidate(args.input_root, args.output_root, args.audit_path, args.manifest_path)
            print(json.dumps({"status": "ok", "manifest": manifest, "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, Wave26Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
