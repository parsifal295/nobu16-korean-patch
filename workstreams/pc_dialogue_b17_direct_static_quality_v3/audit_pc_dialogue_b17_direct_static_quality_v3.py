#!/usr/bin/env python3
"""Read-only coverage audit for B17's already-inherited static repairs.

The exact Wave 97 private candidate is the only Korean input.  It already
contains every high-confidence B17 v2 static repair, so this tool must never
create a replacement candidate or rewrite either MSGGAME binary.  Instead it
pins that fact, the direct-PC evidence, and the structural/layout guards into
the checked-in review artifacts for a later commit.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)
BLOCK_ID = 17

STRICT_INPUT_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave97_pk_security_development_static_v1" / "candidate"
)
STRICT_INPUT_AUDIT = STRICT_INPUT_ROOT / "audit.v1.json"
STRICT_INPUT_MANIFEST = STRICT_INPUT_ROOT / "build_manifest.v1.json"

B17_DIRECT_AUDIT_README = REPO / "workstreams" / "pc_dialogue_b17_direct_pc_audit_v2" / "README_KO.md"
B17_STATIC_V2_BUILDER = (
    REPO / "workstreams" / "pc_b17_direct_static_candidate_v2" / "build_pc_b17_direct_static_candidate_v2.py"
)
MSGGAME_FORMAT = REPO / "workstreams" / "msggame" / "msggame_format.py"
LZ4_HELPER = REPO / "tools" / "nobu16_lz4.py"
W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)

B17_DIRECT_AUDIT_README_SHA256 = "6879589130F2E6B0982D802FC940A4CA3CCB8E3AA5ECA04B097D34DCFF7343D7"
B17_STATIC_V2_BUILDER_SHA256 = "123BF810B7B4ECE606F77CEFD11216442C612BBE215470AC446B4243B093EC7D"
MSGGAME_FORMAT_SHA256 = "5F2D8076335822BE49A4F84EC334254527F3766F046165C56B1BFB7E4DAE8458"
LZ4_HELPER_SHA256 = "96E7E934355F1B7B1764FAFA1B2809BA7D165E4ADA1DE16EA15C089790E77CFB"
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

STRICT_INPUT_EVIDENCE = {
    "audit.v1.json": {
        "size": 18_710,
        "sha256": "54BF4C8A0BC63C91CEEE91652D33D680E56717C5E05D1748A6F1C2E2BC12E5A2",
        "schema": "nobu16.kr.pc-dialogue-quality-wave97-pk-security-development-static-audit.v1",
    },
    "build_manifest.v1.json": {
        "size": 2_733,
        "sha256": "AA242F0EBFCB3E5BEB1F046D87BB3F0C6DD274380A901550367A7A0DCC824AEB",
        "schema": "nobu16.kr.pc-dialogue-quality-wave97-pk-security-development-static-manifest.v1",
    },
}


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class DirectSource:
    key: str
    language: str
    resource: str
    path: Path
    profile: Profile


STRICT_INPUT_PROFILES: Mapping[str, Profile] = {
    BASE_RESOURCE: Profile(
        1_504_458,
        "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        1_498_556,
        "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    ),
    PK_RESOURCE: Profile(
        1_806_687,
        "E507D55F2FECE844FA3AF1FBA213DE2DB7D0F4113082190615DA9C15D3906540",
        1_799_604,
        "599C1415FA511E934303FFF7B15BB92834DAB90C54365A7FD62E6BB12C850F67",
    ),
}

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DIRECT_SOURCES: Mapping[str, DirectSource] = {
    "BASE_JP": DirectSource(
        "BASE_JP",
        "JP",
        BASE_RESOURCE,
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        Profile(
            610_163,
            "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
            1_337_548,
            "353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38",
        ),
    ),
    "BASE_SC": DirectSource(
        "BASE_SC",
        "SC",
        "MSG/SC/msggame.bin",
        STEAM_ROOT / "MSG/SC/msggame.bin",
        Profile(
            430_720,
            "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
            878_860,
            "A42DF025567DB627274454F97E57AC7B77D593401DEAF4CC6476D81A614CF020",
        ),
    ),
    "BASE_TC": DirectSource(
        "BASE_TC",
        "TC",
        "MSG/TC/msggame.bin",
        STEAM_ROOT / "MSG/TC/msggame.bin",
        Profile(
            433_170,
            "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
            916_148,
            "754EAE338FA15594ADA28604C98E40CF2CB1C10EC829CDCCF8FB0F10D01CC0CF",
        ),
    ),
    "PK_JP": DirectSource(
        "PK_JP",
        "JP",
        PK_RESOURCE,
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin",
        Profile(
            721_304,
            "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
            1_599_324,
            "F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8",
        ),
    ),
    "PK_EN": DirectSource(
        "PK_EN",
        "EN",
        "MSG_PK/EN/msggame.bin",
        STEAM_ROOT / "MSG_PK/EN/msggame.bin",
        Profile(
            737_377,
            "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
            2_237_648,
            "6B26D22B419A95498BCF8BF3019CA6D6DCD157C81628F73D5C658A605D00A463",
        ),
    ),
    "PK_SC": DirectSource(
        "PK_SC",
        "SC",
        "MSG_PK/SC/msggame.bin",
        STEAM_ROOT / "MSG_PK/SC/msggame.bin",
        Profile(
            540_757,
            "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
            1_099_712,
            "07D0EFD997CB1C49CE6298AD1A1684F87CE50DA05E9430C018F09D926F97D704",
        ),
    ),
    "PK_TC": DirectSource(
        "PK_TC",
        "TC",
        "MSG_PK/TC/msggame.bin",
        STEAM_ROOT / "MSG_PK/TC/msggame.bin",
        Profile(
            546_853,
            "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
            1_142_788,
            "2C3AF2396EA32C203B0D529078CB33576CC803E159F9EDE053527399179BDEC3",
        ),
    ),
}

SOURCE_KEYS_BY_RESOURCE: Mapping[str, Mapping[str, str | None]] = {
    BASE_RESOURCE: {"JP": "BASE_JP", "EN": None, "SC": "BASE_SC", "TC": "BASE_TC"},
    PK_RESOURCE: {"JP": "PK_JP", "EN": "PK_EN", "SC": "PK_SC", "TC": "PK_TC"},
}

EXPECTED_B17_TOPOLOGY = {
    BASE_RESOURCE: {"records": 33, "literals": 66},
    PK_RESOURCE: {"records": 1_159, "literals": 2_256},
}

MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-b17-direct-static-quality-preapplied-audit.v3"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-b17-direct-static-quality-preapplied-manifest.v3"


class B17AuditError(RuntimeError):
    """Raised if any strict source, evidence, or no-op audit guard drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise B17AuditError(label)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(profile: Profile) -> dict[str, Any]:
    return {
        "size": profile.size,
        "sha256": profile.sha256,
        "raw_size": profile.raw_size,
        "raw_sha256": profile.raw_sha256,
    }


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def path_is_pc(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    require(not any("switch" in part.casefold() for part in resolved.parts), f"Switch path is forbidden: {label}")
    return resolved


def load_module(path: Path, expected_sha256: str, name: str) -> Any:
    require(path.is_file(), f"required helper is absent: {path}")
    require(sha256_path(path) == expected_sha256, f"pinned helper differs: {path.name}")
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load helper: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def initialize_helpers() -> tuple[Any, Any, Any]:
    require(sha256_path(B17_DIRECT_AUDIT_README) == B17_DIRECT_AUDIT_README_SHA256, "B17 direct-audit README differs")
    require(sha256_path(MSGGAME_FORMAT) == MSGGAME_FORMAT_SHA256, "MS GGame parser differs")
    require(sha256_path(LZ4_HELPER) == LZ4_HELPER_SHA256, "LZ4 helper differs")
    for root in (REPO / "tools", REPO / "workstreams" / "msggame"):
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
    old = load_module(B17_STATIC_V2_BUILDER, B17_STATIC_V2_BUILDER_SHA256, "b17_v3_pinned_static_v2")
    w27 = load_module(W27_HELPER, W27_HELPER_SHA256, "b17_v3_pinned_w27")
    from nobu16_lz4 import decompress_wrapper  # noqa: PLC0415
    from msggame_format import parse_raw_msggame, parse_record_literals, rebuild_raw_msggame  # noqa: PLC0415

    return old, w27, (decompress_wrapper, parse_raw_msggame, parse_record_literals, rebuild_raw_msggame)


def literal_signature(value: str) -> dict[str, Any]:
    controls = [f"U+{ord(char):04X}" for char in value if char not in ("\r", "\n") and ord(char) < 0x20]
    return {"lf": value.count("\n"), "cr": value.count("\r"), "controls": controls}


def opaque_skeleton(record: Any, parse_record_literals: Any) -> bytes:
    literal_start = b"\x07\x07\x01"
    literal_end = b"\x07\x07\x02"
    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        output.extend(record.data[cursor : literal.marker_offset + len(literal_start)])
        output.extend(b"<UTF16_LITERAL>")
        output.extend(record.data[literal.marker_end - len(literal_end) : literal.marker_end])
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return bytes(output)


def marker_topology(record: Any, parse_record_literals: Any) -> list[dict[str, str]]:
    literal_start = b"\x07\x07\x01"
    literal_end = b"\x07\x07\x02"
    return [
        {
            "start": record.data[literal.marker_offset : literal.marker_offset + len(literal_start)].hex().upper(),
            "end": record.data[literal.marker_end - len(literal_end) : literal.marker_end].hex().upper(),
        }
        for literal in parse_record_literals(record)
    ]


def record_tail_after_last_literal(record: Any, parse_record_literals: Any) -> bytes:
    literals = parse_record_literals(record)
    return record.data[literals[-1].marker_end :] if literals else record.data


def literal_vector_hash(values: tuple[str, ...]) -> str:
    payload = bytearray()
    for value in values:
        encoded = value.encode("utf-16-le")
        payload.extend(len(encoded).to_bytes(4, "little"))
        payload.extend(encoded)
    return sha256_bytes(bytes(payload))


def complete_0143_commands(record: Any, parse_record_literals: Any) -> list[str]:
    commands: list[str] = []
    spans: list[bytes] = []
    cursor = 0
    for literal in parse_record_literals(record):
        spans.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    spans.append(record.data[cursor:])
    for span in spans:
        index = 0
        while index + 6 <= len(span):
            if span[index : index + 2] == b"\x01\x43":
                commands.append(span[index : index + 6].hex().upper())
                index += 6
            else:
                index += 1
    return commands


def compact_record_report(record: Any, parse_record_literals: Any, literal_id: int) -> dict[str, Any]:
    literals = parse_record_literals(record)
    selected = literals[literal_id].text if literal_id < len(literals) else None
    skeleton = opaque_skeleton(record, parse_record_literals)
    tail = record_tail_after_last_literal(record, parse_record_literals)
    return {
        "record_sha256": sha256_bytes(record.data),
        "record_size": len(record.data),
        "literal_count": len(literals),
        "literal_vector_utf16le_sha256": literal_vector_hash(tuple(item.text for item in literals)),
        "literal_index_available": selected is not None,
        "literal_index_text": selected,
        "literal_index_utf16le_sha256": text_hash(selected) if selected is not None else None,
        "opaque_skeleton_sha256": sha256_bytes(skeleton),
        "marker_topology": marker_topology(record, parse_record_literals),
        "tail_after_last_literal_size": len(tail),
        "tail_after_last_literal_sha256": sha256_bytes(tail),
        "record_terminator_hex": tail[-3:].hex().upper() if len(tail) >= 3 else tail.hex().upper(),
        "complete_0143_commands_hex": complete_0143_commands(record, parse_record_literals),
    }


def static_person_dialogue_layout(value: str, advance: Any) -> dict[str, Any]:
    lines: list[dict[str, Any]] = []
    fallback_codepoints: set[str] = set()
    for display in value.split("\n"):
        raw_width = 0
        full_width = 0
        half_width = 0
        for char in display:
            measured, used_fallback = advance(char)
            require(measured in (RAW_G1N_FULL_WIDTH_ADVANCE, RAW_G1N_HALF_WIDTH_ADVANCE), f"unexpected G1N advance U+{ord(char):04X}: {measured}")
            raw_width += measured
            if measured == RAW_G1N_FULL_WIDTH_ADVANCE:
                full_width += 1
            else:
                half_width += 1
            if used_fallback:
                fallback_codepoints.add(f"U+{ord(char):04X}")
        lines.append(
            {
                "display_string": display,
                "raw_g1n_width_px": raw_width,
                "static_person_dialogue_width_px": raw_width,
                "full_width_character_count": full_width,
                "half_width_character_count": half_width,
                "exceeds_static_person_dialogue_width": raw_width > MAX_PERSON_DIALOGUE_RAW_LINE_PX,
            }
        )
    return {
        "line_count": len(lines),
        "manual_line_break_count": value.count("\n"),
        "raw_g1n_line_widths_px": [item["raw_g1n_width_px"] for item in lines],
        "max_static_person_dialogue_width_px": max((item["raw_g1n_width_px"] for item in lines), default=0),
        "any_static_person_dialogue_line_exceeds_888px": any(item["exceeds_static_person_dialogue_width"] for item in lines),
        "wide_fallback_codepoints": sorted(fallback_codepoints),
        "lines": lines,
    }


def require_profile(packed: bytes, raw: bytes, profile: Profile, label: str) -> None:
    actual = Profile(len(packed), sha256_bytes(packed), len(raw), sha256_bytes(raw))
    require(actual == profile, f"profile differs: {label}")


def strict_file_set() -> set[str]:
    return {path.relative_to(STRICT_INPUT_ROOT).as_posix() for path in STRICT_INPUT_ROOT.rglob("*") if path.is_file()}


def load_strict_input(parse_raw_msggame: Any, rebuild_raw_msggame: Any, decompress_wrapper: Any) -> tuple[dict[str, tuple[bytes, bytes, Any]], dict[str, Any]]:
    require(STRICT_INPUT_ROOT.is_dir(), "Wave 97 strict input is absent")
    expected_files = {BASE_RESOURCE, PK_RESOURCE, "audit.v1.json", "build_manifest.v1.json"}
    require(strict_file_set() == expected_files, "Wave 97 strict input file set differs")
    evidence: dict[str, Any] = {}
    for filename, spec in STRICT_INPUT_EVIDENCE.items():
        path = STRICT_INPUT_ROOT / filename
        require(path.stat().st_size == spec["size"], f"Wave 97 evidence size differs: {filename}")
        require(sha256_path(path) == spec["sha256"], f"Wave 97 evidence hash differs: {filename}")
        parsed = json.loads(path.read_text(encoding="utf-8"))
        require(parsed.get("schema") == spec["schema"], f"Wave 97 evidence schema differs: {filename}")
        evidence[filename] = {"size": spec["size"], "sha256": spec["sha256"], "schema": spec["schema"]}

    audit_json = json.loads(STRICT_INPUT_AUDIT.read_text(encoding="utf-8"))
    manifest_json = json.loads(STRICT_INPUT_MANIFEST.read_text(encoding="utf-8"))
    require(manifest_json.get("candidate_only") is True, "Wave 97 predecessor is not private")

    loaded: dict[str, tuple[bytes, bytes, Any]] = {}
    for resource in RESOURCE_ORDER:
        packed = (STRICT_INPUT_ROOT / resource).read_bytes()
        _header, raw = decompress_wrapper(packed)
        require_profile(packed, raw, STRICT_INPUT_PROFILES[resource], f"Wave 97 strict input {resource}")
        require(audit_json.get("target", {}).get(resource) == profile_dict(STRICT_INPUT_PROFILES[resource]), f"Wave 97 audit target differs: {resource}")
        require(manifest_json.get("resources", {}).get(resource, {}).get("output", {}) == {"size": STRICT_INPUT_PROFILES[resource].size, "sha256": STRICT_INPUT_PROFILES[resource].sha256}, f"Wave 97 manifest target differs: {resource}")
        archive = parse_raw_msggame(raw)
        require(rebuild_raw_msggame(archive) == raw, f"strict raw parser round trip differs: {resource}")
        loaded[resource] = (packed, raw, archive)
    return loaded, evidence


def load_direct_sources(parse_raw_msggame: Any, decompress_wrapper: Any) -> tuple[dict[str, tuple[bytes, bytes, Any]], dict[str, Any]]:
    loaded: dict[str, tuple[bytes, bytes, Any]] = {}
    reports: dict[str, Any] = {}
    for key, source in DIRECT_SOURCES.items():
        path = path_is_pc(source.path, f"direct PC {key}")
        packed = path.read_bytes()
        _header, raw = decompress_wrapper(packed)
        require_profile(packed, raw, source.profile, f"direct PC {key}")
        archive = parse_raw_msggame(raw)
        loaded[key] = (packed, raw, archive)
        reports[key] = {
            "language": source.language,
            "resource": source.resource,
            "path": str(path),
            **profile_dict(source.profile),
        }
    return loaded, reports


def record_at(archive: Any, record_id: int, label: str) -> Any:
    require(len(archive.blocks) > BLOCK_ID, f"B17 absent: {label}")
    block = archive.blocks[BLOCK_ID]
    require(record_id < len(block.records), f"B17 record absent: {label}:{record_id}")
    record = block.records[record_id]
    require(record.block_id == BLOCK_ID and record.record_id == record_id, f"B17 coordinate differs: {label}:{record_id}")
    return record


def validate_complete_b17_topology(resource: str, strict_archive: Any, jp_archive: Any, parse_record_literals: Any) -> dict[str, Any]:
    strict_block = strict_archive.blocks[BLOCK_ID]
    jp_block = jp_archive.blocks[BLOCK_ID]
    expected = EXPECTED_B17_TOPOLOGY[resource]
    require(len(strict_block.records) == len(jp_block.records) == expected["records"], f"B17 record count differs: {resource}")
    literal_total = 0
    literal_with_lf = 0
    lf_total = 0
    for strict_record, jp_record in zip(strict_block.records, jp_block.records):
        require(strict_record.record_id == jp_record.record_id, f"B17 record topology differs: {resource}")
        strict_literals = parse_record_literals(strict_record)
        jp_literals = parse_record_literals(jp_record)
        require(len(strict_literals) == len(jp_literals), f"B17 literal topology differs: {resource}:{strict_record.record_id}")
        require(opaque_skeleton(strict_record, parse_record_literals) == opaque_skeleton(jp_record, parse_record_literals), f"B17 opaque skeleton differs: {resource}:{strict_record.record_id}")
        require(marker_topology(strict_record, parse_record_literals) == marker_topology(jp_record, parse_record_literals), f"B17 marker topology differs: {resource}:{strict_record.record_id}")
        require(record_tail_after_last_literal(strict_record, parse_record_literals) == record_tail_after_last_literal(jp_record, parse_record_literals), f"B17 record terminator tail differs: {resource}:{strict_record.record_id}")
        for strict_literal, jp_literal in zip(strict_literals, jp_literals):
            require(strict_literal.text.count("\n") == jp_literal.text.count("\n"), f"B17 LF topology differs: {resource}:{strict_record.record_id}:{strict_literal.literal_id}")
            literal_total += 1
            if strict_literal.text.count("\n"):
                literal_with_lf += 1
                lf_total += strict_literal.text.count("\n")
    require(literal_total == expected["literals"], f"B17 literal count differs: {resource}")
    return {
        "record_count": len(strict_block.records),
        "literal_count": literal_total,
        "literal_with_manual_lf_count": literal_with_lf,
        "manual_lf_total": lf_total,
        "opaque_skeleton_all_records_match_direct_pc_jp": True,
        "marker_topology_all_records_match_direct_pc_jp": True,
        "terminator_tail_all_records_match_direct_pc_jp": True,
        "manual_lf_topology_all_literals_match_direct_pc_jp": True,
    }


def source_evidence_for_row(
    resource: str,
    record_id: int,
    literal_id: int,
    direct_archives: Mapping[str, tuple[bytes, bytes, Any]],
    parse_record_literals: Any,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for language in ("JP", "EN", "SC", "TC"):
        source_key = SOURCE_KEYS_BY_RESOURCE[resource][language]
        if source_key is None:
            result[language] = {
                "available": False,
                "reason": "The installed PC Base resource has no MSG/EN/msggame.bin; MSG_PK/EN is not substituted as same-resource evidence.",
            }
            continue
        source = DIRECT_SOURCES[source_key]
        record = record_at(direct_archives[source_key][2], record_id, source_key)
        result[language] = {
            "available": True,
            "source_key": source_key,
            "source_resource": source.resource,
            **compact_record_report(record, parse_record_literals, literal_id),
        }
    return result


def prepare_artifacts() -> tuple[dict[str, Any], dict[str, Any]]:
    old, w27, helpers = initialize_helpers()
    decompress_wrapper, parse_raw_msggame, parse_record_literals, rebuild_raw_msggame = helpers
    require(old.BLOCK_ID == BLOCK_ID, "pinned B17 block differs")
    targets = tuple(old.TARGETS)
    observed_scope = tuple((target.resource, *target.slot) for target in targets)
    require(observed_scope == old.EXPECTED_SCOPE, "pinned B17 static target scope differs")
    require(len(targets) == 44, "B17 static high-confidence target count differs")
    require(set(observed_scope).isdisjoint(old.EXCLUDED_HOLD_SLOTS), "B17 static scope overlaps a HOLD")

    strict, strict_evidence = load_strict_input(parse_raw_msggame, rebuild_raw_msggame, decompress_wrapper)
    direct, direct_source_reports = load_direct_sources(parse_raw_msggame, decompress_wrapper)
    advance, font = w27.load_font_advance()
    require(font.get("packed_sha256") == "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7", "G1N font profile differs")

    complete_topology: dict[str, Any] = {}
    for resource, jp_key in ((BASE_RESOURCE, "BASE_JP"), (PK_RESOURCE, "PK_JP")):
        complete_topology[resource] = validate_complete_b17_topology(resource, strict[resource][2], direct[jp_key][2], parse_record_literals)

    rows: list[dict[str, Any]] = []
    missing_slots: list[str] = []
    for target in targets:
        resource = target.resource
        strict_record = record_at(strict[resource][2], target.record_id, f"strict {resource}")
        jp_record = record_at(direct["BASE_JP" if resource == BASE_RESOURCE else "PK_JP"][2], target.record_id, f"direct JP {resource}")
        strict_literals = parse_record_literals(strict_record)
        jp_literals = parse_record_literals(jp_record)
        require(target.literal_id < len(strict_literals) == len(jp_literals), f"B17 target literal topology differs: {target.slot_text}")
        strict_value = strict_literals[target.literal_id].text
        jp_value = jp_literals[target.literal_id].text
        expected_target = target.target_ko
        is_preapplied = strict_value == expected_target
        if not is_preapplied:
            missing_slots.append(f"{resource}:{target.slot_text}")
        require(is_preapplied, f"B17 static repair is missing from strict Wave 97 input: {target.slot_text}")
        require(jp_value == target.pc_jp, f"direct PC Japanese evidence differs: {target.slot_text}")
        require(strict_value != target.current_ko, f"strict input is unexpectedly the old B17 preimage: {target.slot_text}")
        require(literal_signature(target.current_ko) == literal_signature(expected_target), f"historical LF/control signature differs: {target.slot_text}")
        require(literal_signature(strict_value) == literal_signature(expected_target), f"strict LF/control signature differs: {target.slot_text}")
        require(opaque_skeleton(strict_record, parse_record_literals) == opaque_skeleton(jp_record, parse_record_literals), f"strict opaque skeleton differs: {target.slot_text}")
        require(marker_topology(strict_record, parse_record_literals) == marker_topology(jp_record, parse_record_literals), f"strict token topology differs: {target.slot_text}")
        require(record_tail_after_last_literal(strict_record, parse_record_literals) == record_tail_after_last_literal(jp_record, parse_record_literals), f"strict record terminator differs: {target.slot_text}")

        historical_layout = static_person_dialogue_layout(target.current_ko, advance)
        strict_layout = static_person_dialogue_layout(strict_value, advance)
        require(
            historical_layout["line_count"] == strict_layout["line_count"]
            and historical_layout["manual_line_break_count"] == strict_layout["manual_line_break_count"],
            f"manual line topology differs: {target.slot_text}",
        )
        # This is an inheritance audit, not an LF reflow.  A pre-existing
        # over-width line is recorded below but is deliberately not shortened
        # or re-broken here; the static target itself must remain byte/text
        # identical to Wave 97.  The 3-line route and G1N glyph coverage are
        # still hard guards.
        require(
            strict_layout["line_count"] <= MAX_PERSON_DIALOGUE_LINES
            and not strict_layout["wide_fallback_codepoints"],
            f"strict fixed-person dialogue layout topology differs: {target.slot_text}",
        )

        evidence = source_evidence_for_row(resource, target.record_id, target.literal_id, direct, parse_record_literals)
        require(evidence["JP"]["literal_index_text"] == target.pc_jp, f"JP source row differs: {target.slot_text}")
        rows.append(
            {
                "resource": resource,
                "slot": target.slot_text,
                "rationale": target.rationale,
                "historical_preimage_ko": target.current_ko,
                "historical_preimage_ko_utf16le_sha256": text_hash(target.current_ko),
                "expected_static_target_ko": expected_target,
                "expected_static_target_ko_utf16le_sha256": text_hash(expected_target),
                "strict_wave97_ko": strict_value,
                "strict_wave97_ko_utf16le_sha256": text_hash(strict_value),
                "pre_applied": True,
                "direct_pc_jp": jp_value,
                "direct_pc_jp_utf16le_sha256": text_hash(jp_value),
                "literal_signature": literal_signature(strict_value),
                "historical_preimage_layout": historical_layout,
                "strict_wave97_layout": strict_layout,
                "line_count_preserved_from_historical_preimage": True,
                "strict_width_preserved_exactly_as_expected_target": True,
                "strict_width_within_static_person_dialogue_limit": not strict_layout[
                    "any_static_person_dialogue_line_exceeds_888px"
                ],
                "opaque_skeleton_preserved": True,
                "token_marker_topology_preserved": True,
                "terminator_tail_preserved": True,
                "strict_record": compact_record_report(strict_record, parse_record_literals, target.literal_id),
                "direct_pc_evidence": evidence,
            }
        )

    require(not missing_slots, "one or more B17 static rows are missing from strict Wave 97 input")
    by_resource = {resource: sum(row["resource"] == resource for row in rows) for resource in RESOURCE_ORDER}
    require(by_resource == {BASE_RESOURCE: 4, PK_RESOURCE: 40}, "B17 static resource split differs")
    total_lf = sum(item["manual_lf_total"] for item in complete_topology.values())
    total_lf_literals = sum(item["literal_with_manual_lf_count"] for item in complete_topology.values())
    require(total_lf == 849 and total_lf_literals == 839, "B17 complete LF census differs")
    preexisting_overwidth = [
        {
            "resource": row["resource"],
            "slot": row["slot"],
            "raw_g1n_line_widths_px": row["strict_wave97_layout"]["raw_g1n_line_widths_px"],
        }
        for row in rows
        if not row["strict_width_within_static_person_dialogue_limit"]
    ]

    audit: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "artifact_kind": "read-only pre-applied static-quality coverage audit",
        "candidate_binary_created": False,
        "steam_game_resource_written": False,
        "source_policy": {
            "strict_korean_input": "exact Wave 97 private candidate only",
            "direct_pc_jp_en_sc_tc_evidence_opened": True,
            "base_en_same_resource": "unavailable on the installed PC; no MSG_PK/EN substitution is used",
            "switch_korean_read": False,
            "sentence_shortening": "forbidden",
            "manual_line_break_global_edit": "forbidden",
            "runtime_token_particle_holds": "excluded",
            "color_blue_hold": "excluded",
            "steam_apply": "absent",
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "review_sources": {
            "b17_direct_audit_readme": {
                "path": B17_DIRECT_AUDIT_README.relative_to(REPO).as_posix(),
                "sha256": B17_DIRECT_AUDIT_README_SHA256,
            },
            "pinned_b17_static_v2_target_table": {
                "path": B17_STATIC_V2_BUILDER.relative_to(REPO).as_posix(),
                "sha256": B17_STATIC_V2_BUILDER_SHA256,
                "high_confidence_static_target_count": len(targets),
            },
        },
        "strict_input": {
            "root": STRICT_INPUT_ROOT.relative_to(REPO).as_posix(),
            "evidence": strict_evidence,
            "resources": {resource: profile_dict(STRICT_INPUT_PROFILES[resource]) for resource in RESOURCE_ORDER},
        },
        "direct_pc_sources": direct_source_reports,
        "font": font,
        "layout_baseline": {
            "widget": "fixed MSGGAME person dialogue",
            "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
            "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
            "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
            "max_lines": MAX_PERSON_DIALOGUE_LINES,
            "event_msgev_static_patch_007_rule": "not applied",
        },
        "layout_review": {
            "strict_input_widths_preserved_without_reflow": True,
            "preexisting_overwidth_rows": preexisting_overwidth,
            "preexisting_overwidth_row_count": len(preexisting_overwidth),
            "disposition": "recorded only; this no-op audit does not shorten text or alter manual line breaks",
        },
        "scope": {
            "block_id": BLOCK_ID,
            "static_high_confidence_literal_count": len(rows),
            "static_high_confidence_count_by_resource": by_resource,
            "expected_static_slots": [f"{target.resource}:{target.slot_text}" for target in targets],
            "pre_applied_verified_slots": [f"{row['resource']}:{row['slot']}" for row in rows],
            "missing_static_slots": missing_slots,
            "binary_replacement_slots_required": [],
        },
        "excluded_holds": {
            "all_slots": [f"{resource}:{block}:{record}:{literal}" for resource, block, record, literal in old.EXCLUDED_HOLD_SLOTS],
            "runtime_name_or_particle": [
                f"{BASE_RESOURCE}:17:5:3",
                f"{PK_RESOURCE}:17:226:0",
                f"{PK_RESOURCE}:17:226:1",
                f"{PK_RESOURCE}:17:226:2",
                f"{PK_RESOURCE}:17:226:3",
                f"{PK_RESOURCE}:17:510:0",
                f"{PK_RESOURCE}:17:510:1",
                f"{PK_RESOURCE}:17:510:2",
                f"{PK_RESOURCE}:17:920:0",
                f"{PK_RESOURCE}:17:920:1",
                f"{PK_RESOURCE}:17:991:0",
                f"{PK_RESOURCE}:17:991:1",
            ],
            "color_blue": [f"{PK_RESOURCE}:17:282:0"],
            "global_manual_lf": {
                "excluded": True,
                "b17_literal_with_lf_count": total_lf_literals,
                "b17_total_lf_count": total_lf,
                "direct_pc_jp_topology_match": True,
            },
            "preexisting_layout_warning_holds": {
                "slots": preexisting_overwidth,
                "reason": "The strict Wave 97 text is already over the fixed-person 888px raw-G1N guide at these rows. This no-op coverage audit must not shorten text or alter semantic manual line breaks.",
                "binary_change_allowed_in_this_artifact": False,
            },
        },
        "complete_b17_topology": complete_topology,
        "records": rows,
        "pre_applied_verified_literal_count": len(rows),
        "pre_applied_verified_record_count": len(rows),
        "missing_static_literal_count": 0,
        "binary_replacement_count": 0,
    }
    manifest: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "artifact_kind": "read-only coverage evidence; no candidate output",
        "candidate_binary_created": False,
        "candidate_output": "absent by design because all 44 approved static targets are already present in the strict Wave 97 input",
        "strict_input": audit["strict_input"],
        "resources": {
            resource: {
                "input_and_retained_output": profile_dict(STRICT_INPUT_PROFILES[resource]),
                "pre_applied_static_literal_count": by_resource[resource],
                "binary_replacement_count": 0,
            }
            for resource in RESOURCE_ORDER
        },
        "pre_applied_verified_literal_count": len(rows),
        "missing_static_literal_count": 0,
        "binary_replacement_count": 0,
        "excluded_hold_count": len(old.EXCLUDED_HOLD_SLOTS),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return audit, manifest


def verify_artifacts() -> dict[str, Any]:
    audit, manifest = prepare_artifacts()
    audit_path = WORKSTREAM / "audit.v3.json"
    manifest_path = WORKSTREAM / "manifest.v3.json"
    require(audit_path.is_file() and audit_path.read_bytes() == canonical_json(audit), "checked-in audit artifact differs")
    require(manifest_path.is_file() and manifest_path.read_bytes() == canonical_json(manifest), "checked-in manifest artifact differs")
    return {
        "artifact_root": WORKSTREAM.relative_to(REPO).as_posix(),
        "pre_applied_verified_literal_count": audit["pre_applied_verified_literal_count"],
        "missing_static_literal_count": audit["missing_static_literal_count"],
        "binary_replacement_count": audit["binary_replacement_count"],
        "candidate_binary_created": False,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("report", "verify-artifacts"))
    args = parser.parse_args(argv)
    if args.command == "report":
        audit, manifest = prepare_artifacts()
        result: Mapping[str, Any] = {"audit": audit, "manifest": manifest}
    else:
        result = verify_artifacts()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
