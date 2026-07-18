#!/usr/bin/env python3
"""Build the PC-only private Wave 25 static-consistency candidate.

The sole Korean preimage is the verified eleven-file Wave 24 candidate.  This
program changes exactly two literal slots in PK ``msggame`` and may write only
under its own tmp directory.  It has no Steam, Git, release, network, or
Switch-Korean input capability.
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
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / "pc_event_layout_wave24_v1" / "candidate"
PREDECESSOR_AUDIT = REPO / "tmp" / "pc_event_layout_wave24_v1" / "audit.v1.json"
PREDECESSOR_MANIFEST = REPO / "tmp" / "pc_event_layout_wave24_v1" / "build_manifest.v1.json"
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

for module_root in (TOOLS, MSGGAME_TOOLS):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402
from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
    rebuild_record_literals,
)


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave25-static-consistency.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave25-static-consistency-audit.v1"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
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
CHANGED_PATHS = (PK_MSGGAME,)
RECORD_TERMINATOR = b"\x05\x05\x05"
DIALOGUE_MAX_LINE_PX = 912
FONT_PATH = "RES_JP/res_lang.bin"
FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
FONT_ENTRY = 6
WIDE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]")

# Exact Wave 24 eleven-file private candidate profile.  Wave 24's PK msgev
# change is intentionally retained byte-for-byte.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    "MSG/JP/msggame.bin": "A5B688C4DF72F9796759A13FBEDB30C30C47873DF9228B9566127877AFD5F810",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "91F4C99B1C4D21CE9A3529CB174AA1EFD9E198E8FEB6F90F5AD507CEBB4B8C4F",
    PK_MSGGAME: "432B4F9D3DEF80DDF8288AE82AB1A245EE44585776FC368658A47CBBD826EB8B",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
INPUT_SIZES = {
    "MSG/JP/ev_strdata.bin": 928123,
    "MSG/JP/msggame.bin": 1504691,
    "MSG/JP/strdata.bin": 957204,
    "MSG_PK/JP/msgbre.bin": 484068,
    "MSG_PK/JP/msgdata.bin": 496995,
    "MSG_PK/JP/msgev.bin": 994731,
    PK_MSGGAME: 1806795,
    "MSG_PK/JP/msgire.bin": 23128,
    "MSG_PK/JP/msgstf.bin": 17341,
    "MSG_PK/JP/msgstf_ce.bin": 18767,
    "MSG_PK/JP/msgui.bin": 122733,
}
TARGET_SHA256 = {
    **INPUT_SHA256,
    PK_MSGGAME: "70FB0AB6EB2B07795CB37DEEB8941635184DC3C48246A6F45C25B59CD75559BC",
}
TARGET_SIZES = {**INPUT_SIZES, PK_MSGGAME: 1806811}
WAVE24_EVIDENCE = {
    "audit": {"path": PREDECESSOR_AUDIT, "size": 8246, "sha256": "4062A56D67EDB82FBBF7BD8E52BECCD84EDF8E6DD440E5F6D90E053EAD8EA536"},
    "manifest": {"path": PREDECESSOR_MANIFEST, "size": 3885, "sha256": "42C3A55AD6BA0EDA7463B5FA5FC88B4EF76AF13A656390A94E9033FD043BB25F"},
}

# All anchors are PC resources.  The JP original is the PC transaction
# backup; EN/SC/TC are PC-language resources.  No Switch resource is accepted.
PC_REFERENCE_PATHS = {
    "JP": (DEFAULT_STEAM_ROOT / "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin", "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"),
    "EN": (DEFAULT_STEAM_ROOT / "MSG_PK/EN/msggame.bin", "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916"),
    "SC": (DEFAULT_STEAM_ROOT / "MSG_PK/SC/msggame.bin", "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802"),
    "TC": (DEFAULT_STEAM_ROOT / "MSG_PK/TC/msggame.bin", "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23"),
}


class Wave25Error(RuntimeError):
    """A pinned input, source anchor, or candidate contract failed."""


@dataclass(frozen=True)
class RecordAnchor:
    sha256: str
    size: int


@dataclass(frozen=True)
class Change:
    coordinate: tuple[int, int]
    literal_id: int
    target_literal: str
    input_record_sha256: str
    input_record_size: int
    input_literal_sha256: str
    target_record_sha256: str
    target_record_size: int
    target_literal_sha256: str
    spans_hex: tuple[str, ...]
    current_widths_px: tuple[int, ...]
    target_widths_px: tuple[int, ...]
    rationale: str

    @property
    def text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


def _ko(value: str) -> str:
    return value.encode("ascii").decode("unicode_escape")


CHANGES = (
    Change(
        (2, 283), 0,
        _ko(r"\uc758 \uac15\ud568\uc740 \uc218\uc5d0 \uc788\uc9c0 \uc54a\ub2e4.\n\uc790, \uc801\uc9c4\uc744 \uaff0\ub6ab\uc5b4 \ubcf4\uc774\ub9ac\ub77c!"),
        "EEC788314E05255CDE37EA726A3D46473E7512A9A793944C2FEB6BC48E5C3588", 62,
        "6E984C1B79BB33AF5AF64E22EA6FF55E86A02A80DD26DBDAC2270AE15B4D5BED",
        "1F5AC0853BAD9D220F3A169E1421D80EE4DF1950E9282A25E4A63DD2A89AF01B", 76,
        "0B47DE0412EEEC125C517F3C6A5D8E60CCD487CF3A57C2F9A4BB48E71AC1DDA2",
        ("024634", "050505"), (600, 384), (600, 648),
        "PC JP/EN/SC/TC battle-context anchors support first-person battle wording.",
    ),
    Change(
        (13, 221), 0,
        _ko(r" > \uad70\uc0ac > \uc131 \uc5ed\ud560"),
        "649CB11C3FF724A3C99F460590EA208F821C88740D1CE0BC31E490B5F558B793", 35,
        "C2AD4CEE71EB9E45AA7F636370ACECE1E323D6D32C260BB5F33802BC575F49FA",
        "BE1EB28876AE68F4F106B08749C89E7B0FEE113CF14FDDC52866C970805F1704", 35,
        "D007AD434E994D8DA0580FE966F05FB0586E8FD17C3871876872EF5F64E9BF87",
        ("023C", "050505"), (408,), (408,),
        "PC JP/EN/SC/TC UI anchors identify the label as the castle-role category.",
    ),
)
CHANGE_BY_COORDINATE = {change.coordinate: change for change in CHANGES}
if len(CHANGE_BY_COORDINATE) != len(CHANGES):
    raise RuntimeError("duplicate Wave 25 coordinate")

# Exact whole-record PC anchor fingerprints at the two changed coordinates and
# their Korean duplicate counterparts.  This is intentionally a source-only
# check; it never reads an alternate Korean translation platform.
PC_ANCHORS: dict[tuple[int, int], dict[str, RecordAnchor]] = {
    (2, 283): {
        "JP": RecordAnchor("EAE6BD5751A085BCFA185C1C8100CE3DD15813572C665BE49E471759B984C129", 64),
        "EN": RecordAnchor("90560743D527D4C213A85D585BD4A6F7EAE9FC89A9E5C1C66EBACEB8386FC5DA", 174),
        "SC": RecordAnchor("5C613218ABD232CE926A73EE6A5248DCCC407C08496FD3C50A3B4252F78BDA27", 38),
        "TC": RecordAnchor("A90CDD6444A3C940963E6DBEAE1BE911A58208A7B1BE3FF43C150E39AAC0A1B0", 38),
    },
    (9, 3874): {
        "JP": RecordAnchor("EAE6BD5751A085BCFA185C1C8100CE3DD15813572C665BE49E471759B984C129", 64),
        "EN": RecordAnchor("90560743D527D4C213A85D585BD4A6F7EAE9FC89A9E5C1C66EBACEB8386FC5DA", 174),
        "SC": RecordAnchor("0150CBBC7B15B5D4F858773063977968FBDEF4653F6B626C86CF90BD4F24D29C", 52),
        "TC": RecordAnchor("FF83A0B737647683239408ACB416FBE15A12E3D0E711CD23DFF5A4802380E371", 44),
    },
    (13, 221): {
        "JP": RecordAnchor("20840C514BF94149423582587B50DFE09CD492652A20F5CA41C56C017465DC86", 33),
        "EN": RecordAnchor("FDEE85738123152328CF3F81AF46FE2425DF40A49C3EA378AAF61C1989ADD9C1", 61),
        "SC": RecordAnchor("ED6D37F811E234FF256A8A6068B15698B7A99B3F1B230B10B1A4ED52F81EAFCF", 33),
        "TC": RecordAnchor("8CE8EA646EA6462BB16EE22E8C900C2693EB2C42D7873DD99A5CCFB5BAAAD38F", 33),
    },
    (13, 274): {
        "JP": RecordAnchor("20840C514BF94149423582587B50DFE09CD492652A20F5CA41C56C017465DC86", 33),
        "EN": RecordAnchor("FDEE85738123152328CF3F81AF46FE2425DF40A49C3EA378AAF61C1989ADD9C1", 61),
        "SC": RecordAnchor("DA35F1EC5344A66C5EDC69309D38A1B9D2C11A71D5D9BD9B2FC08A68FF843590", 33),
        "TC": RecordAnchor("8CE8EA646EA6462BB16EE22E8C900C2693EB2C42D7873DD99A5CCFB5BAAAD38F", 33),
    },
}

# Seven screened consistency groups are expressly retained.  They are not
# rewrite permission: differing role/register, runtime concatenation, or
# punctuation requires contextual review outside this two-literal candidate.
RETAINED_CONSISTENCY_GROUPS = (
    {
        "jp_group_utf16le_sha256": "2F957DDF8FBAF32196C6809F35521A80C51DA37072536FCA1D1706589B2C97B1",
        "pc_coordinates": ["4:38:1", "4:48:1"],
        "reason": "punctuation_variation",
        "decision": "reviewed_and_retained",
    },
    {
        "jp_group_utf16le_sha256": "E35BF12C4140AB715A0E6924B1E277F15BC1EB9196694CDC0CBE7B2AD6298141",
        "pc_coordinates": ["6:1075:0", "9:2467:0"],
        "reason": "style_variation",
        "decision": "reviewed_and_retained",
    },
    {
        "jp_group_utf16le_sha256": "C00FE7859C114A673B04229B235EA13E5128CFC436E8150D3B1CE5A82C008FD2",
        "pc_coordinates": ["6:1089:0", "6:1095:0", "6:1105:0"],
        "reason": "style_variation",
        "decision": "reviewed_and_retained",
    },
    {
        "jp_group_utf16le_sha256": "7FE3C998A86A8EAEA784DB88F5F8D1E5DD948A23268AEC2D51620E8DEF5BEFE1",
        "pc_coordinates": ["2:194:1", "2:195:1", "2:196:1", "2:197:1", "6:3881:1"],
        "reason": "dynamic_fragment",
        "decision": "reviewed_and_retained",
    },
    {
        "jp_group_utf16le_sha256": "0EE3232398CF9F146BE5E84AE8CB74FAA1BEBB2124C4010744D0368F8874F446",
        "pc_coordinates": ["2:198:1", "2:200:1", "2:203:1", "2:205:1", "2:207:1", "6:2075:1", "6:2077:1", "6:2081:2", "6:2082:1"],
        "reason": "punctuation_variation",
        "decision": "reviewed_and_retained",
    },
    {
        "jp_group_utf16le_sha256": "11D6CB6698EA92B9016B4B9C6CE4D9C4B1CA93725177B86422D5F216BBC4F100",
        "pc_coordinates": ["6:4568:1", "6:4569:1", "6:4617:4", "9:833:0", "9:834:0", "9:859:0", "9:860:0", "9:3993:0", "9:3994:0"],
        "reason": "dynamic_fragment",
        "decision": "reviewed_and_retained",
    },
    {
        "jp_group_utf16le_sha256": "2C87D748729F3AE87A9828FD831A6FEFD0F5FC5C877BE9A45E68F8BEC87F0D16",
        "pc_coordinates": ["2:194:0", "2:197:0", "2:199:0", "2:201:0", "2:202:0", "2:204:0", "2:206:0", "2:662:0", "4:78:0", "6:3875:0", "6:3876:0", "6:3937:0", "6:4442:0", "15:1667:0", "15:1668:0", "15:1669:0"],
        "reason": "dynamic_fragment",
        "decision": "reviewed_and_retained",
    },
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    return {
        (record.block_id, record.record_id): record
        for block in parse_packed_msggame(packed).archive.blocks
        for record in block.records
    }


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in parse_record_literals(record))


def opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    cursor = 0
    spans: list[bytes] = []
    for literal in parse_record_literals(record):
        spans.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    spans.append(record.data[cursor:])
    return tuple(spans)


def marker_topology(record: MsgGameRecord) -> tuple[tuple[bytes, bytes], ...]:
    return tuple(
        (record.data[item.marker_offset : item.marker_offset + len(LITERAL_START)], record.data[item.marker_end - len(LITERAL_END) : item.marker_end])
        for item in parse_record_literals(record)
    )


def profile(root: Path) -> tuple[dict[str, str], dict[str, int]]:
    hashes: dict[str, str] = {}
    sizes: dict[str, int] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave25Error(f"missing profile resource: {relative}")
        hashes[relative] = sha256_path(path)
        sizes[relative] = path.stat().st_size
    return hashes, sizes


def assert_profile(root: Path, expected_hashes: Mapping[str, str], expected_sizes: Mapping[str, int], label: str) -> None:
    hashes, sizes = profile(root)
    if hashes != dict(expected_hashes) or sizes != dict(expected_sizes):
        raise Wave25Error(f"{label} profile differs")


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave25Error(f"Switch input is forbidden: {label}")
    return resolved


def validate_wave24_preimage(root: Path) -> Path:
    root = reject_switch_path(root, "Wave 24 private candidate")
    for name, expected in WAVE24_EVIDENCE.items():
        path = Path(expected["path"])
        if not path.is_file() or path.stat().st_size != expected["size"] or sha256_path(path) != expected["sha256"]:
            raise Wave25Error(f"Wave 24 {name} evidence differs")
    assert_profile(root, INPUT_SHA256, INPUT_SIZES, "Wave 24 predecessor")
    return root


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    header, raw = decompress_wrapper(packed)
    if rebuild_raw_msggame(parse_packed_msggame(packed).archive) != raw:
        raise Wave25Error(f"{label} raw parse/rebuild differs")
    _header, restored = decompress_wrapper(recompress_wrapper(raw, header))
    if restored != raw:
        raise Wave25Error(f"{label} wrapper round-trip differs")


def validate_pc_anchors() -> dict[str, Any]:
    source_records: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    resource_hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_REFERENCE_PATHS.items():
        checked = reject_switch_path(path, f"PC {language}")
        if sha256_path(checked) != expected_hash:
            raise Wave25Error(f"PC {language} source profile differs")
        source_records[language] = records_by_coordinate(checked.read_bytes())
        resource_hashes[language] = expected_hash
    report: dict[str, Any] = {}
    for coordinate, anchors in PC_ANCHORS.items():
        row: dict[str, Any] = {}
        for language, expected in anchors.items():
            record = source_records[language].get(coordinate)
            if record is None or sha256_bytes(record.data) != expected.sha256 or len(record.data) != expected.size:
                raise Wave25Error(f"PC {language} anchor differs at {coordinate}")
            row[language] = {"record_sha256": expected.sha256, "record_size": expected.size}
        report[f"{coordinate[0]}:{coordinate[1]}"] = row
    return {"reference_packed_sha256": resource_hashes, "records": report}


def validate_retained_consistency_groups() -> list[dict[str, Any]]:
    """Prove the seven hold groups against the pinned PC JP source only."""

    path, expected_hash = PC_REFERENCE_PATHS["JP"]
    checked = reject_switch_path(path, "PC JP retained consistency groups")
    if sha256_path(checked) != expected_hash:
        raise Wave25Error("PC JP retained-group source profile differs")
    records = records_by_coordinate(checked.read_bytes())
    report: list[dict[str, Any]] = []
    for group in RETAINED_CONSISTENCY_GROUPS:
        observed: list[str] = []
        for coordinate_text in group["pc_coordinates"]:
            block_id, record_id, literal_id = (int(value) for value in coordinate_text.split(":"))
            record = records.get((block_id, record_id))
            if record is None:
                raise Wave25Error(f"PC JP retained group lacks {coordinate_text}")
            literals = literal_texts(record)
            if literal_id >= len(literals):
                raise Wave25Error(f"PC JP retained group literal lacks {coordinate_text}")
            observed.append(text_sha256(literals[literal_id]))
        if set(observed) != {group["jp_group_utf16le_sha256"]}:
            raise Wave25Error("PC JP retained group source text differs")
        report.append({**group, "pc_jp_source_verified": True})
    return report


def validate_literal(value: str, label: str) -> None:
    if not value or "\0" in value or LITERAL_START in value.encode("utf-16-le") or LITERAL_END in value.encode("utf-16-le"):
        raise Wave25Error(f"invalid target literal: {label}")
    if any(unicodedata.category(char) == "Cc" and char not in "\n\r" for char in value):
        raise Wave25Error(f"target literal control character: {label}")


def validate_change(change: Change, record: MsgGameRecord) -> tuple[dict[str, Any], str]:
    values = literal_texts(record)
    if (
        sha256_bytes(record.data) != change.input_record_sha256
        or len(record.data) != change.input_record_size
        or len(values) <= change.literal_id
        or text_sha256(values[change.literal_id]) != change.input_literal_sha256
        or tuple(part.hex().upper() for part in opaque_spans(record)) != change.spans_hex
        or not record.data.endswith(RECORD_TERMINATOR)
    ):
        raise Wave25Error(f"input guard differs: {change.text}")
    validate_literal(change.target_literal, change.text)
    rebuilt_data = rebuild_record_literals(record, {change.literal_id: change.target_literal})
    rebuilt = MsgGameRecord(record.block_id, record.record_id, record.relative_offset, rebuilt_data)
    after = literal_texts(rebuilt)
    if (
        sha256_bytes(rebuilt.data) != change.target_record_sha256
        or len(rebuilt.data) != change.target_record_size
        or text_sha256(after[change.literal_id]) != change.target_literal_sha256
        or opaque_spans(rebuilt) != opaque_spans(record)
        or marker_topology(rebuilt) != marker_topology(record)
        or not rebuilt.data.endswith(RECORD_TERMINATOR)
        or any(after[index] != values[index] for index in range(len(values)) if index != change.literal_id)
    ):
        raise Wave25Error(f"literal rebuild differs: {change.text}")
    return {
        "coordinate": change.text,
        "literal_id": change.literal_id,
        "input_record_sha256": change.input_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "input_record_size": change.input_record_size,
        "target_record_size": change.target_record_size,
        "input_literal_utf16le_sha256": change.input_literal_sha256,
        "target_literal_utf16le_sha256": change.target_literal_sha256,
        "opaque_spans_hex": list(change.spans_hex),
        "rationale": change.rationale,
    }, after[change.literal_id]


def load_font_advance() -> tuple[Callable[[str], tuple[int, bool]], dict[str, Any]]:
    path = DEFAULT_STEAM_ROOT / FONT_PATH
    if not path.is_file() or sha256_path(path) != FONT_SHA256:
        raise Wave25Error("PC JP font profile differs")
    archive = parse_link(path.read_bytes())
    _header, raw = decompress_wrapper(archive.entries[FONT_ENTRY].data)
    with tempfile.TemporaryDirectory(prefix="nobu16_wave25_font_") as directory:
        temp = Path(directory) / "font.g1n"
        temp.write_bytes(raw)
        parsed = g1n.parse_g1n(temp)
    if parsed.structural_errors or not parsed.tables:
        raise Wave25Error("PC JP font cannot be parsed")
    table = parsed.tables[0]

    def advance(char: str) -> tuple[int, bool]:
        ordinal = table.mapping[ord(char)] if ord(char) < len(table.mapping) else 0
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(char):
                return 48, True
            raise Wave25Error(f"font lacks glyph U+{ord(char):04X}")
        glyph = table.records[ordinal]
        if glyph.width != glyph.advance or glyph.advance not in (24, 48):
            raise Wave25Error(f"bad font metric U+{ord(char):04X}")
        return glyph.advance, False

    return advance, {"resource": FONT_PATH, "entry": FONT_ENTRY, "packed_sha256": FONT_SHA256, "table_count": len(parsed.tables)}


def layout(values: tuple[str, ...], advance: Callable[[str], tuple[int, bool]]) -> dict[str, Any]:
    widths: list[int] = []
    fallback: set[str] = set()
    for line in "".join(values).split("\n"):
        width = 0
        for char in line:
            if unicodedata.category(char) == "Cc":
                raise Wave25Error(f"control in layout: U+{ord(char):04X}")
            glyph_width, used_fallback = advance(char)
            width += glyph_width
            if used_fallback:
                fallback.add(f"U+{ord(char):04X}")
        widths.append(width)
    return {"line_count": len(widths), "line_widths_px": widths, "max_width_px": max(widths, default=0), "wide_fallback_codepoints": sorted(fallback)}


def validate_font_layout(before: Mapping[tuple[int, int], MsgGameRecord], after: Mapping[tuple[int, int], MsgGameRecord]) -> dict[str, Any]:
    advance, font = load_font_advance()
    rows: dict[str, Any] = {}
    for change in CHANGES:
        current = layout(literal_texts(before[change.coordinate]), advance)
        target = layout(literal_texts(after[change.coordinate]), advance)
        if (
            tuple(current["line_widths_px"]) != change.current_widths_px
            or tuple(target["line_widths_px"]) != change.target_widths_px
            or current["wide_fallback_codepoints"]
            or target["wide_fallback_codepoints"]
            or target["max_width_px"] > DIALOGUE_MAX_LINE_PX
        ):
            raise Wave25Error(f"font layout differs: {change.text}")
        rows[change.text] = {"current": current, "target": target, "target_max_line_px": DIALOGUE_MAX_LINE_PX}
    return {"font": font, "records": rows}


def duplicate_report(before: Mapping[tuple[int, int], MsgGameRecord]) -> dict[str, Any]:
    battle = literal_texts(before[(9, 3874)])[0]
    role = literal_texts(before[(13, 274)])[0]
    expected_normalized = CHANGES[0].target_literal.replace("\uc54a\ub2e4.\n", "\uc54a\ub2e4\n")
    if battle != expected_normalized or role != CHANGES[1].target_literal:
        raise Wave25Error("known Korean duplicate guards differ")
    return {
        "battle_duplicate_coordinate": "9:3874",
        "battle_duplicate_literal_utf16le_sha256": text_sha256(battle),
        "battle_duplicate_is_not_modified": True,
        "battle_target_has_explicit_line1_period": True,
        "role_duplicate_coordinate": "13:274",
        "role_duplicate_literal_utf16le_sha256": text_sha256(role),
        "role_target_equals_duplicate": True,
    }


def prepare_candidate(predecessor_root: Path) -> tuple[bytes, dict[str, Any]]:
    predecessor_root = validate_wave24_preimage(predecessor_root)
    source = (predecessor_root / PK_MSGGAME).read_bytes()
    validate_raw_roundtrip(source, "Wave 24 PK msggame")
    anchors = validate_pc_anchors()
    retained_groups = validate_retained_consistency_groups()
    before = records_by_coordinate(source)
    replacements: dict[tuple[int, int, int], str] = {}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        record = before.get(change.coordinate)
        if record is None:
            raise Wave25Error(f"missing change coordinate: {change.text}")
        row, literal = validate_change(change, record)
        if literal != change.target_literal:
            raise Wave25Error(f"target literal differs: {change.text}")
        replacements[(*change.coordinate, change.literal_id)] = literal
        rows.append(row)
    output = rebuild_packed_with_literals(source, replacements)
    if len(output) != TARGET_SIZES[PK_MSGGAME] or sha256_bytes(output) != TARGET_SHA256[PK_MSGGAME]:
        raise Wave25Error("PK msggame target packed profile differs")
    validate_raw_roundtrip(output, "Wave 25 PK msggame")
    after = records_by_coordinate(output)
    changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
    if before.keys() != after.keys() or changed != set(CHANGE_BY_COORDINATE):
        raise Wave25Error("unexpected PK msggame record change")
    for change in CHANGES:
        result = after[change.coordinate]
        if sha256_bytes(result.data) != change.target_record_sha256 or literal_texts(result)[change.literal_id] != change.target_literal:
            raise Wave25Error(f"output record differs: {change.text}")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "predecessor": "exact Wave 24 eleven-file candidate",
            "wave24_full_profile_required": True,
            "pc_jp_en_sc_tc_anchors_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor_candidate_root": str(predecessor_root),
        "predecessor_evidence": {name: {"path": str(spec["path"]), "size": spec["size"], "sha256": spec["sha256"]} for name, spec in WAVE24_EVIDENCE.items()},
        "input_sha256": INPUT_SHA256,
        "input_sizes": INPUT_SIZES,
        "target_sha256": TARGET_SHA256,
        "target_sizes": TARGET_SIZES,
        "pc_anchors": anchors,
        "duplicate_evidence": duplicate_report(before),
        "retained_consistency_groups": retained_groups,
        "font_layout": validate_font_layout(before, after),
        "records": rows,
        "changed_record_count": len(changed),
        "changed_literal_count": len(replacements),
    }
    return output, audit


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave25Error(f"{label} must remain below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, TARGET_SIZES, "Wave 25 private candidate")
    packed = (candidate_root / PK_MSGGAME).read_bytes()
    validate_raw_roundtrip(packed, "Wave 25 private candidate")
    records = records_by_coordinate(packed)
    for change in CHANGES:
        record = records.get(change.coordinate)
        if record is None or sha256_bytes(record.data) != change.target_record_sha256 or literal_texts(record)[change.literal_id] != change.target_literal:
            raise Wave25Error(f"candidate verification differs: {change.text}")


def remove_stage(stage: Path) -> None:
    if stage.exists():
        require_tmp(stage, "candidate stage")
        shutil.rmtree(stage)


def build_candidate(predecessor_root: Path, output_root: Path, audit_path: Path, manifest_path: Path) -> dict[str, Any]:
    output_root, audit_path, manifest_path = (require_tmp(item, label) for item, label in ((output_root, "candidate output"), (audit_path, "audit output"), (manifest_path, "manifest output")))
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave25Error("candidate output, audit, or manifest already exists")
    output, audit = prepare_candidate(predecessor_root)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        predecessor_root = validate_wave24_preimage(predecessor_root)
        for relative in PROFILE_PATHS:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative == PK_MSGGAME:
                destination.write_bytes(output)
            else:
                shutil.copy2(predecessor_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, TARGET_SIZES, "Wave 25 staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave25-static-consistency-v1",
            "candidate_only": True,
            "predecessor_candidate_root": str(predecessor_root),
            "predecessor_evidence": {name: {"path": str(spec["path"]), "size": spec["size"], "sha256": spec["sha256"]} for name, spec in WAVE24_EVIDENCE.items()},
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "coordinates": [f"{PK_MSGGAME}:{item.text}:{item.literal_id}" for item in CHANGES],
            "input_sha256": INPUT_SHA256,
            "input_sizes": INPUT_SIZES,
            "output_sha256": TARGET_SHA256,
            "output_sizes": TARGET_SIZES,
            "audit_sha256": sha256_bytes(audit_bytes),
            "record_count": len(CHANGES),
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("hash", "build"):
        current = sub.add_parser(name)
        current.add_argument("--predecessor-root", type=Path, default=PREDECESSOR_CANDIDATE_ROOT)
        if name == "build":
            current.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
            current.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
            current.add_argument("--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    verify = sub.add_parser("verify-private")
    verify.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            _output, audit = prepare_candidate(args.predecessor_root)
            print(json.dumps({"status": "ok", "target_sha256": audit["target_sha256"], "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        elif args.command == "verify-private":
            verify_private_candidate(args.candidate_root)
            print(json.dumps({"status": "ok", "candidate_root": str(args.candidate_root), "steam_write_capability": "absent"}, ensure_ascii=False, sort_keys=True))
        else:
            manifest = build_candidate(args.predecessor_root, args.output_root, args.audit_path, args.manifest_path)
            print(json.dumps({"status": "ok", "manifest": manifest, "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, Wave25Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
