#!/usr/bin/env python3
"""Build the PC-only private Wave 27 static-quality candidate.

The only Korean preimage is the complete Wave 26 eleven-file private
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
PREDECESSOR_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave26_static_inflection_v1" / "candidate"
PREDECESSOR_AUDIT = REPO / "tmp" / "pc_dialogue_quality_wave26_static_inflection_v1" / "audit.v1.json"
PREDECESSOR_MANIFEST = REPO / "tmp" / "pc_dialogue_quality_wave26_static_inflection_v1" / "build_manifest.v1.json"
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


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave27-static-quality.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave27-static-quality-audit.v1"
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

# Exact Wave 26 candidate profile, including its Wave 24 msgev preservation
# and Wave 26 PK msggame change.  No Steam game directory is a preimage.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "031BD5C425FA0259624524E78DB99D4F54B16A43D96A43FE850C2A51500D779A",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "91F4C99B1C4D21CE9A3529CB174AA1EFD9E198E8FEB6F90F5AD507CEBB4B8C4F",
    PK_MSGGAME: "828559146ACE4F456E9E764A69C5E36B88B34F969E108B9E3177614083E9C760",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
INPUT_SIZES = {
    "MSG/JP/ev_strdata.bin": 928123,
    BASE_MSGGAME: 1504747,
    "MSG/JP/strdata.bin": 957204,
    "MSG_PK/JP/msgbre.bin": 484068,
    "MSG_PK/JP/msgdata.bin": 496995,
    "MSG_PK/JP/msgev.bin": 994731,
    PK_MSGGAME: 1806867,
    "MSG_PK/JP/msgire.bin": 23128,
    "MSG_PK/JP/msgstf.bin": 17341,
    "MSG_PK/JP/msgstf_ce.bin": 18767,
    "MSG_PK/JP/msgui.bin": 122733,
}
TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_MSGGAME: "4D6460F1B717FD8D424229ABD619DE4093C21929F6C42B061BAD62E163C5D3CB",
    PK_MSGGAME: "AD3F6DD64C0AD360C5A8C7A4747ABFCE9B2D72BFFDD3D44940781A68AC2DE8D1",
}
TARGET_SIZES = {**INPUT_SIZES, BASE_MSGGAME: 1504526, PK_MSGGAME: 1806647}
WAVE26_EVIDENCE = {
    "audit": {"path": PREDECESSOR_AUDIT, "size": 139560, "sha256": "E758558468CF222D2CC388A0F181443DB907511609D9F1092F458196273A12B1"},
    "manifest": {"path": PREDECESSOR_MANIFEST, "size": 5952, "sha256": "6F9AECA4B70DA33A8133319A052B224C3BD63B871D07FEE8028E8E82748094F2"},
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


class Wave27Error(RuntimeError):
    """A pinned source, structural guard, or private-output contract failed."""


@dataclass(frozen=True)
class Family:
    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    target_literals: tuple[str, ...]


FAMILIES = (
    Family("trade_port", (8, 1033), (8, 1045), ("교역항이 완공되어", "\n벌써 각지에서 배들이 모여들어\n크게 번성하고 있습니다.")),
    Family("gold_mine", (8, 1034), (8, 1046), ("금산정을 건설하여", "\n새로운 수입원을 얻은 덕에\n가문의 재정도 넉넉해졌습니다.")),
    Family("silver_mine", (8, 1035), (8, 1047), ("은산정을 건설하여", "\n가문의 새로운 수입원이 되었으니\n영지는 더욱 발전할 것입니다.")),
    Family("horse_pasture", (8, 1036), (8, 1048), ("말 목장을 건설하여", "\n이제 많은 준마를 기를 수 있으니\n기병도 크게 강해질 것입니다.")),
    Family("armory_village", (8, 1037), (8, 1049), ("대장간 마을을 건설하여", "\n철포를 충분히 갖추었으니\n전장에서도 마음껏 쓸 수 있습니다.")),
    Family("temple", (8, 1038), (8, 1050), ("사사를 건설하여", "\n백성들이 마음을 기댈 곳이 되었으니\n승려들도 매우 기뻐하는 듯합니다.")),
    Family("nanban_temple", (8, 1039), (8, 1051), ("남만사를 건설하여", "\n포교가 이루어짐에 따라\n새 문화가 뿌리내릴지도 모릅니다…")),
    Family("hot_spring", (8, 1040), (8, 1052), ("온천 마을을 건설하여", "\n상처에 효험이 있다고 하니\n병사들의 요양에도 도움이 될 것입니다.")),
    Family("large_farm", (8, 1041), (8, 1053), ("대농촌을 건설하여", "\n넓은 농지를 보고 백성도 의욕을 보이니\n수확은 물론 병력 증가도 기대됩니다.")),
    Family("large_market", (8, 1042), (8, 1054), ("대시장을 건설하여", "\n벌써 장사가 활발해진 듯하니\n큰 수입을 기대할 수 있습니다.")),
    Family("merchant_relocation", (8, 1044), (8, 1056), ("싸움에 휘말린 상인들을 위해\n새 터전을 마련하니", "\n상인들도 감사해하고 있습니다.")),
    Family("housing_recovery", (8, 1047), (8, 1059), ("피해를 입은 백성들을 위해\n살림집을 새로 마련하니", "\n예전의 활기를 되찾은 듯합니다.")),
    Family("road_repair", (8, 1048), (8, 1060), ("토사를 치우고 가도를 정비하여", "\n사람들의 왕래가 늘어나\n장사도 활기를 띠고 있습니다.")),
    Family("levee_repair", (8, 1049), (8, 1061), ("피해를 입은 마을을 복구하고\n제방도 수리했으니", "\n더 이상의 피해는 없을 것입니다.")),
    Family("settlement_recovery", (8, 1051), (8, 1063), ("파괴된 취락을\n다시 세웠으니", "\n백성들도 예전처럼 지낼 수 있습니다.")),
    Family("wall_repair", (8, 1053), (8, 1065), ("성벽을 수리하여", "\n작업에서 해방된 덕에\n백성의 불만도 줄어든 듯합니다.")),
    Family("village_relief", (8, 1055), (8, 1067), ("식량을 제공하고\n불태워진 마을을 지원하니", "\n백성들도 감사해하고 있습니다.")),
    Family("market_revival", (8, 1056), (8, 1068), ("시장을 재흥시켜", "\n사람들이 많이 모여들어\n장사도 활기를 띠고 있습니다.")),
    Family("food_relief", (8, 1057), (8, 1069), ("굶주린 백성의 불만을 달래기 위해\n식량을 나누어 주니", "\n백성의 불만도 누그러지고 있습니다.")),
    Family("food_distribution", (8, 1059), (8, 1071), ("굶주린 백성들을 위해\n식량을 배급하니", "\n모두 무척 감사해하고 있습니다.")),
)
if len({family.base_coordinate for family in FAMILIES}) != len(FAMILIES) or len({family.pk_coordinate for family in FAMILIES}) != len(FAMILIES):
    raise RuntimeError("duplicate Wave 27 coordinate")

# Independent per-record target pins.  Base and PK target records converge
# byte-for-byte after their platform-specific complete static 0143 commands
# are removed; each pin is therefore asserted for both members of the pair.
TARGET_RECORD_PINS = {
    "trade_port": ("AA6651ADBDA00D68CA0AFCAC51CBC59D543441CD30510E5D09C36AD8F28FE797", 95, (408, 696, 552)),
    "gold_mine": ("2C47253239D54C16DFA636C841E73EDB172F23497C774EAF057FBDFBA8A49FA5", 97, (408, 600, 696)),
    "silver_mine": ("A3322FCB31A783BAED62D76B7DBA3DAD8A6AB580423FE0AEE0AE69BE9011435D", 103, (408, 744, 672)),
    "horse_pasture": ("72D5FFCDEA6E5BB65D77E4D732067E22CF4CB268C498F28E8563DE08F8A1660B", 107, (432, 744, 672)),
    "armory_village": ("53823E72719BBE7C401CC37AA478179E59089430717352A3BEE32728576B9382", 107, (528, 576, 792)),
    "temple": ("0DAE9088C58D098445A031138CDF6FAAFB6203D6EA06A2142F44F0161864162E", 109, (360, 816, 768)),
    "nanban_temple": ("72E4CC9B05E95FF4985A95D346AC4546CE407853ECAFCA6B6ABEBFB5EEB29019", 97, (408, 528, 792)),
    "hot_spring": ("4DB32F7A0F63ABA0CF02398291318BCDDFF716364E6C8588580F222A7120E1AF", 111, (480, 600, 888)),
    "large_farm": ("E0B30DB97687A70449281FAF8611DE07D6A809C63C2C935C8387F1532B613E91", 119, (408, 888, 840)),
    "large_market": ("901251D84FE9DB353FE0535A264CE9765941291E252FE27A106C6864AD77A4F1", 101, (408, 648, 696)),
    "merchant_relocation": ("5C54195B7CEA0D221572110F9DD8F1AAB6AFB3AF140FD76E7E0E5D028582D825", 101, (648, 432, 696)),
    "housing_recovery": ("AEDD864F7F9863AAA2B66619D162D69B882A7AC96669D9F53A557E50FF1269C2", 105, (600, 528, 720)),
    "road_repair": ("89EE3284D7B5594340AA8D4F679C27EB96CAFD24D36E984159EF2AF76F06DFC0", 107, (696, 528, 672)),
    "levee_repair": ("A5B9E309C4FCDB0060BC88C0C868FEEAFCE6D731C8C3FA016BDDC61D07C53B2F", 103, (648, 408, 744)),
    "settlement_recovery": ("845783DA16A6464FF3FB499D338993C4DA0F83DECDD979DF4BF68B0FFF8CB5B0", 87, (312, 312, 840)),
    "wall_repair": ("6FA115CD6EE959894F1E9426EAD73EBD9124DB597E59B3D2B21D8D88A2A0B853", 91, (360, 480, 720)),
    "village_relief": ("D9A0F69F2EC52A46661BF9FCC5CF4AD6E013864DD48B85F0F7BF499E75F5432D", 93, (360, 576, 696)),
    "market_revival": ("1B718DCC36F6B5528F62B73C41E0D5BE29ED3387D94DEE8C62D2A37A00F2D559", 91, (360, 528, 672)),
    "food_relief": ("D51DF4374152DF1C5352D8D60BFD9257EC15907D24ED5AEABA524938479A8ECA", 113, (768, 432, 816)),
    "food_distribution": ("18D5328C6BE127ADA508B77AA41E5D928682284FDC0BFBEAA84DCDDD6F2ADCC3", 91, (480, 360, 720)),
}
if set(TARGET_RECORD_PINS) != {family.name for family in FAMILIES}:
    raise RuntimeError("incomplete Wave 27 target record pins")


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
                    raise Wave27Error("truncated 01 43 command")
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
                raise Wave27Error("truncated 01 43 command")
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
            raise Wave27Error(f"missing profile resource: {relative}")
        hashes[relative] = sha256_path(path)
        sizes[relative] = path.stat().st_size
    return hashes, sizes


def assert_profile(root: Path, expected_hashes: Mapping[str, str], expected_sizes: Mapping[str, int], label: str) -> None:
    actual_hashes, actual_sizes = profile(root)
    if actual_hashes != dict(expected_hashes) or actual_sizes != dict(expected_sizes):
        raise Wave27Error(f"{label} profile differs")


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave27Error(f"Switch input is forbidden: {label}")
    return resolved


def require_predecessor_root(root: Path) -> Path:
    expected = PREDECESSOR_ROOT.resolve(strict=True)
    checked = reject_switch_path(root, "Wave 26 private candidate")
    if checked != expected:
        raise Wave27Error("input must be the unique Wave 26 private candidate")
    return checked


def validate_wave26_evidence(root: Path) -> dict[str, Any]:
    for name, spec in WAVE26_EVIDENCE.items():
        path = Path(spec["path"])
        if not path.is_file() or path.stat().st_size != spec["size"] or sha256_path(path) != spec["sha256"]:
            raise Wave27Error(f"Wave 26 {name} evidence differs")
    try:
        audit = json.loads(PREDECESSOR_AUDIT.read_text(encoding="utf-8"))
        manifest = json.loads(PREDECESSOR_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Wave27Error("Wave 26 evidence JSON is invalid") from exc
    if (
        audit.get("target_sha256") != INPUT_SHA256
        or audit.get("target_sizes") != INPUT_SIZES
        or manifest.get("output_sha256") != INPUT_SHA256
        or manifest.get("output_sizes") != INPUT_SIZES
        or manifest.get("candidate_only") is not True
    ):
        raise Wave27Error("Wave 26 evidence contract differs")
    return {name: {"path": str(spec["path"]), "size": spec["size"], "sha256": spec["sha256"]} for name, spec in WAVE26_EVIDENCE.items()}


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    header, raw = decompress_wrapper(packed)
    if rebuild_raw_msggame(parse_packed_msggame(packed).archive) != raw:
        raise Wave27Error(f"{label} raw parse/rebuild differs")
    _header, restored = decompress_wrapper(recompress_wrapper(raw, header))
    if restored != raw:
        raise Wave27Error(f"{label} wrapper round-trip differs")


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
            raise Wave27Error(f"PC {language} reference profile differs")
        archives[language] = records_by_coordinate(checked.read_bytes())
        source_hashes[language] = expected_hash
    rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        base = archives["BASE_JP"].get(family.base_coordinate)
        pk = archives["PK_JP"].get(family.pk_coordinate)
        contexts = {language: archives[language].get(family.pk_coordinate) for language in ("EN", "SC", "TC")}
        if base is None or pk is None or any(value is None for value in contexts.values()):
            raise Wave27Error(f"PC anchor coordinate missing: {family.name}")
        if literal_texts(base) != literal_texts(pk):
            raise Wave27Error(f"PC Base/PK JP source differs: {family.name}")
        if not base.data.endswith(RECORD_TERMINATOR) or not pk.data.endswith(RECORD_TERMINATOR) or any(not value.data.endswith(RECORD_TERMINATOR) for value in contexts.values()):
            raise Wave27Error(f"PC anchor terminator differs: {family.name}")
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
        raise Wave27Error(f"invalid target literal: {label}")
    encoded = value.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave27Error(f"reserved marker in target: {label}")
    if any(unicodedata.category(char) == "Cc" and char not in "\n\r" for char in value):
        raise Wave27Error(f"control in target: {label}")


def load_font_advance() -> tuple[Callable[[str], tuple[int, bool]], dict[str, Any]]:
    path = reject_switch_path(DEFAULT_STEAM_ROOT / FONT_PATH, "active PC JP font")
    if sha256_path(path) != FONT_SHA256:
        raise Wave27Error("active PC JP font profile differs")
    archive = parse_link(path.read_bytes())
    _header, raw = decompress_wrapper(archive.entries[FONT_ENTRY].data)
    with tempfile.TemporaryDirectory(prefix="nobu16_wave27_font_") as directory:
        temp = Path(directory) / "font.g1n"
        temp.write_bytes(raw)
        parsed = g1n.parse_g1n(temp)
    if parsed.structural_errors or not parsed.tables:
        raise Wave27Error("active PC JP font cannot be parsed")
    table = parsed.tables[0]

    def advance(char: str) -> tuple[int, bool]:
        ordinal = table.mapping[ord(char)] if ord(char) < len(table.mapping) else 0
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(char):
                return 48, True
            raise Wave27Error(f"font lacks glyph U+{ord(char):04X}")
        glyph = table.records[ordinal]
        if glyph.width != glyph.advance or glyph.advance not in (24, 48):
            raise Wave27Error(f"font metric differs U+{ord(char):04X}")
        return glyph.advance, False

    return advance, {"resource": FONT_PATH, "entry": FONT_ENTRY, "packed_sha256": FONT_SHA256, "table_count": len(parsed.tables)}


def line_layout(values: tuple[str, ...], advance: Callable[[str], tuple[int, bool]]) -> dict[str, Any]:
    widths: list[int] = []
    fallback: set[str] = set()
    for line in "".join(values).split("\n"):
        width = 0
        for char in line:
            if unicodedata.category(char) == "Cc":
                raise Wave27Error(f"control in font layout U+{ord(char):04X}")
            glyph_width, used_fallback = advance(char)
            width += glyph_width
            if used_fallback:
                fallback.add(f"U+{ord(char):04X}")
        widths.append(width)
    return {"line_count": len(widths), "line_widths_px": widths, "max_width_px": max(widths, default=0), "wide_fallback_codepoints": sorted(fallback)}


def rebuild_static_record(source: MsgGameRecord, target_literals: tuple[str, ...]) -> bytes:
    source_spans = opaque_spans(source)
    if len(source_spans) != len(target_literals) + 1:
        raise Wave27Error("literal-marker count changes")
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
        raise Wave27Error(f"input static command/marker guard differs: {family.name} {resource}")
    if any(not command.startswith("0143") or len(command) != 12 for command in commands):
        raise Wave27Error(f"non-complete 0143 command: {family.name} {resource}")
    for index, value in enumerate(family.target_literals):
        validate_literal(value, f"{family.name}:{index}")
    current_text = "".join(current_values)
    target_text = "".join(family.target_literals)
    if current_text.count("\n") != target_text.count("\n") or target_text.count("\n") + 1 > 3:
        raise Wave27Error(f"manual line count differs: {family.name} {resource}")
    layout = line_layout(family.target_literals, advance)
    target_sha256, target_size, target_widths = TARGET_RECORD_PINS[family.name]
    if (
        tuple(layout["line_widths_px"]) != target_widths
        or layout["max_width_px"] > DIALOGUE_MAX_LINE_PX
        or layout["wide_fallback_codepoints"]
    ):
        raise Wave27Error(f"font layout differs: {family.name} {resource}")
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
        raise Wave27Error(f"target structural guard differs: {family.name} {resource}")
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
                raise Wave27Error(f"output record differs: {family.name} {resource}")


def prepare_candidate(input_root: Path = PREDECESSOR_ROOT) -> tuple[dict[str, bytes], dict[str, Any]]:
    input_root = require_predecessor_root(input_root)
    evidence = validate_wave26_evidence(input_root)
    assert_profile(input_root, INPUT_SHA256, INPUT_SIZES, "Wave 26 predecessor")
    before = {resource: (input_root / resource).read_bytes() for resource in CHANGED_PATHS}
    for resource, packed in before.items():
        validate_raw_roundtrip(packed, f"Wave 26 {resource}")
    anchors = validate_pc_anchors()
    advance, font = load_font_advance()
    current = {resource: records_by_coordinate(data) for resource, data in before.items()}
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in CHANGED_PATHS}
    rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        for resource, coordinate in ((BASE_MSGGAME, family.base_coordinate), (PK_MSGGAME, family.pk_coordinate)):
            record = current[resource].get(coordinate)
            if record is None or coordinate in replacements[resource]:
                raise Wave27Error(f"replacement coordinate differs: {family.name} {resource}")
            target, row = validate_change(family, resource, record, advance)
            replacements[resource][coordinate] = target
            rows.append(row)
    output: dict[str, bytes] = {}
    expected = expected_coordinate_sets()
    for resource in CHANGED_PATHS:
        candidate = rebuild_packed_msggame(before[resource], replacements[resource])
        if sha256_bytes(candidate) != TARGET_SHA256[resource] or len(candidate) != TARGET_SIZES[resource]:
            raise Wave27Error(f"target packed profile differs: {resource}")
        validate_raw_roundtrip(candidate, f"Wave 27 {resource}")
        old_records = current[resource]
        new_records = records_by_coordinate(candidate)
        changed = {coordinate for coordinate in old_records if old_records[coordinate].data != new_records[coordinate].data}
        if old_records.keys() != new_records.keys() or changed != expected[resource]:
            raise Wave27Error(f"unexpected changed record set: {resource}")
        output[resource] = candidate
    validate_output_records(output)
    target_hashes = {**INPUT_SHA256, **{resource: sha256_bytes(data) for resource, data in output.items()}}
    target_sizes = {**INPUT_SIZES, **{resource: len(data) for resource, data in output.items()}}
    if target_hashes != TARGET_SHA256 or target_sizes != TARGET_SIZES:
        raise Wave27Error("full output profile differs")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "predecessor": "exact Wave 26 eleven-file private candidate",
            "wave26_full_profile_required": True,
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
        raise Wave27Error(f"{label} must remain below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, TARGET_SIZES, "Wave 27 private candidate")
    expected, _audit = prepare_candidate(PREDECESSOR_ROOT)
    for resource in CHANGED_PATHS:
        actual = (candidate_root / resource).read_bytes()
        if actual != expected[resource]:
            raise Wave27Error(f"candidate bytes differ: {resource}")


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
        raise Wave27Error("candidate output, audit, or manifest already exists")
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
        assert_profile(stage, TARGET_SHA256, TARGET_SIZES, "Wave 27 staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave27-static-quality-v1",
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
    return {name: {"path": str(spec["path"]), "size": spec["size"], "sha256": spec["sha256"]} for name, spec in WAVE26_EVIDENCE.items()}


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
    except (OSError, ValueError, Wave27Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
