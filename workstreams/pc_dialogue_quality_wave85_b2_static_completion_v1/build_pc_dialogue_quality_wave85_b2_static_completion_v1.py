#!/usr/bin/env python3
"""Build a private Base B2 static-dialogue completion candidate.

Wave 85 accepts only the exact Wave 84 private candidate.  It completes six
Base B2 Korean literals that end before the terminal Japanese static 0143
inflection command.  The builder writes only beneath its own private tmp
directory and has no Steam, Git, network, or release operation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
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
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)

W84_CANDIDATE_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave84_b2_static_completion_v1" / "candidate"
W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave85-b2-static-completion.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave85-b2-static-completion-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave85-b2-static-completion-manifest.v1"

# static patch 007 verified runtime layout
MAX_LINES = 4
MAX_EFFECTIVE_LINE_PX = 912
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RUNTIME_FULL_WIDTH_ADVANCE = 30

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "exact_wave84_private_candidate",
        "path": W84_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_430,
        "sha256": "0D43F23F3943C7F360216734E1FD6B01FA37D9D194007FCD4DA41E642E4AF861",
        "raw_size": 1_498_528,
        "raw_sha256": "9EC87BE7C01521FC11A95BDD9201AC7D3957306B4B289DEAF7E54AA385F70001",
    },
    PK_RESOURCE: {
        "kind": "wave84_private_candidate_byte_identical_from_wave83",
        "path": W84_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_550,
        "sha256": "37782D6E96CC6E9C1D60AF50FA5A68AD7C7CC8BE724CEF85EE2E38F2D074B0A7",
        "raw_size": 1_799_468,
        "raw_sha256": "6089EA69FAF5F8730F665B4A82C79D5F0C1FE0B0993C963244BA578CD8D9C44C",
    },
}

W84_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W84_CANDIDATE_ROOT / "audit.v1.json",
        "size": 31_619,
        "sha256": "C883DC7E0EDF4D23FC41E8F802180CC7AEA1BFE3501443943D78FC67F3B1802A",
    },
    "build_manifest.v1.json": {
        "path": W84_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_619,
        "sha256": "6705FBCF63C69B61E45A95E21C8AD2A519B44F48425D302E578F700C1D827D6C",
    },
}

TARGET_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "size": 1_806_550,
        "sha256": "37782D6E96CC6E9C1D60AF50FA5A68AD7C7CC8BE724CEF85EE2E38F2D074B0A7",
        "raw_size": 1_799_468,
        "raw_sha256": "6089EA69FAF5F8730F665B4A82C79D5F0C1FE0B0993C963244BA578CD8D9C44C",
    },
}

# These six B2 source rows are Base-only.  SC/TC records are intentionally
# empty, and no exact literal is present in the original PK Japanese archive.
PC_SOURCE_PROFILES: Mapping[str, tuple[Path, str]] = {
    "BASE_JP": (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    "BASE_SC": (
        Path(r"F:\Games\NOBU16\MSG\SC\msggame.bin"),
        "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
    ),
    "BASE_TC": (
        Path(r"F:\Games\NOBU16\MSG\TC\msggame.bin"),
        "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
    ),
}


class Wave85Error(RuntimeError):
    """Raised if a source, predecessor, or surgical output contract drifts."""


@dataclass(frozen=True)
class Change:
    name: str
    coordinate: tuple[int, int]
    source_jp_literal: str
    target_literal: str
    current_record_sha256: str
    current_record_size: int
    target_record_sha256: str
    target_record_size: int
    target_raw_g1n_line_widths_px: tuple[int, ...]
    input_opaque_spans_hex: tuple[str, str]
    static_0143_commands: tuple[str, ...]
    source_record_sha256: Mapping[str, str]


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def source_hashes(base_jp: str) -> Mapping[str, str]:
    empty = "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"
    return {"BASE_JP": base_jp, "BASE_SC": empty, "BASE_TC": empty}


CHANGES = (
    Change(
        "construction_skill_315",
        (2, 315),
        "名手と謳われた普請の腕、\n存分に発揮",
        "명수로 이름난 공사 솜씨를\n마음껏 발휘하겠다.",
        "3911EA1D4515F75002716F11B53A027CB3B5ED6B758FD80DCBB577473434BA9A",
        57,
        "90C9FC73690E2D04F3C9FACC6457CE932E7F6774B460FB1664AE723BCB041B64",
        59,
        (600, 432),
        ("", "014394000000050505"),
        ("014394000000",),
        source_hashes("667B1BB1631C5D034865201E60EDDEA8646973081C92B60628ED78C5642E1F9E"),
    ),
    Change(
        "renowned_talent_331",
        (2, 331),
        "当代一と謳われた我が才、\nこの地で",
        "당대 제일이라 칭송받은 내 재주를,\n이 땅에서 펼쳐 보이겠다.",
        "5C85481C8299A8864FB205E6E6623E2BB3F6821B8CB38CB180B10893938CDF6F",
        71,
        "0665ED0B7F1D69E0F369453667CAA334E4E5A7F31DDE97BEA159ADE37EBA8B12",
        77,
        (792, 576),
        ("", "01437E01000001431E040000050505"),
        ("01437E010000", "01431E040000"),
        source_hashes("53146782130A3DD587721AC7F78AD138FB08E75DAB6B3245A046C52B2C950222"),
    ),
    Change(
        "banner_prosperity_335",
        (2, 335),
        "大一大万大吉の旗印のもと、\nこの地を豊かに",
        "대일대만대길의 기치 아래,\n이 땅을 풍요롭게 만들겠다.",
        "6001DBA8FD2D5C7E54DAE61D0EE64E2FFBAEBB00F9D563AD6AC2209BBB46D72C",
        63,
        "FA5136D5EA81A8F0C903B93E28A7510951E660CF49889B987B18AD368158E558",
        69,
        (600, 624),
        ("", "014394000000050505"),
        ("014394000000",),
        source_hashes("8DEBD2927C3EA9D79849A078A9E5DD1B28CFB587C6472DDF5DAFE8AF339349AA"),
    ),
    Change(
        "discipline_corps_340",
        (2, 340),
        "我が家の家訓にて、\n規律正しき軍団に",
        "우리 가문의 가훈에 따라,\n규율 바른 군단으로 만들겠다.",
        "35DDC893A7A97B7A2543F56EA19B9523D1C10C40BA8871E7C92C203418882785",
        65,
        "BBCFF60030B19EF7D146A08A02F5CAFAADF1EA7A12CFBF5FA4CD38ABF7B0D0F5",
        71,
        (576, 672),
        ("", "014394000000050505"),
        ("014394000000",),
        source_hashes("733988CEB895718AD1A72005C37FE63CB121D47914FC2283967BFEA897EF51D9"),
    ),
    Change(
        "musketeer_training_343",
        (2, 343),
        "この地の兵を、精悍なる鉄砲隊に\n訓練",
        "이 땅의 병사를 정예 철포대로\n훈련시키겠다.",
        "3FBDECBE097C61823F2343E34CD466BAB1D000A1A94615EBAC64E353B5A1D17B",
        53,
        "7227AC32FDC7445401822696770452AF700B17700211E0D1FDCB6ECEFFE21AE8",
        57,
        (672, 312),
        ("", "014394000000050505"),
        ("014394000000",),
        source_hashes("10995C208567AD0E217BFA2BD2C7396BC87FEE1298583A3B6FFF755FA904ADC2"),
    ),
    Change(
        "people_service_538",
        (2, 538),
        "この地を豊かにするため\n民たちに尽くして",
        "이 땅을 풍요롭게 하기 위해\n백성들을 위해 힘쓰겠다.",
        "EEEA173617CB3C236A031915A10ED00627A0D8C007312E3330F4E646C66FC92C",
        63,
        "CD2AF3D329782236AE8253140030E8B82720423399359E327383AB9C7FD504BE",
        67,
        (624, 552),
        ("", "01437C000000050505"),
        ("01437C000000",),
        source_hashes("1CF29B48DB8867128BE9FB78C87F62C48B818723A84A5564DC2694947C33D9B4"),
    ),
)


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave85Error(label)


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


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave85Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    root_resolved = root.resolve(strict=True)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise Wave85Error(f"{label} escapes required root: {resolved}") from exc
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave85Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "pinned Wave 27 helper differs")
    spec = importlib.util.spec_from_file_location("wave85_imported_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave85Error("cannot load pinned Wave 27 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def validate_w84_evidence() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, profile in W84_EVIDENCE.items():
        path = require_under(Path(profile["path"]), W84_CANDIDATE_ROOT, f"Wave 84 evidence {name}")
        require(path.stat().st_size == profile["size"], f"Wave 84 evidence size differs: {name}")
        actual_hash = sha256_path(path)
        require(actual_hash == profile["sha256"], f"Wave 84 evidence hash differs: {name}")
        result[name] = {"size": path.stat().st_size, "sha256": actual_hash}
    return result


def load_predecessors() -> tuple[dict[str, bytes], dict[str, Mapping[tuple[int, int], Any]], dict[str, Any]]:
    evidence = validate_w84_evidence()
    packed_by_resource: dict[str, bytes] = {}
    records_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    summary: dict[str, Any] = {}
    for resource in RESOURCE_ORDER:
        profile = INPUT_PROFILES[resource]
        path = require_under(Path(profile["path"]), W84_CANDIDATE_ROOT, f"Wave 84 predecessor {resource}")
        packed = path.read_bytes()
        require(len(packed) == profile["size"], f"predecessor size differs: {resource}")
        require(sha256_bytes(packed) == profile["sha256"], f"predecessor hash differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"Wave 85 predecessor {resource}")
        _header, raw = W27.decompress_wrapper(packed)
        require(len(raw) == profile["raw_size"], f"predecessor raw size differs: {resource}")
        require(sha256_bytes(raw) == profile["raw_sha256"], f"predecessor raw hash differs: {resource}")
        packed_by_resource[resource] = packed
        records_by_resource[resource] = W27.records_by_coordinate(packed)
        summary[resource] = {
            "kind": profile["kind"],
            "path": path.relative_to(REPO).as_posix(),
            "size": len(packed),
            "sha256": sha256_bytes(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256_bytes(raw),
        }
    return packed_by_resource, records_by_resource, {
        "resources": summary,
        "wave84_evidence": evidence,
    }


def load_source_records() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, str]]:
    records: dict[str, Mapping[tuple[int, int], Any]] = {}
    hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_SOURCE_PROFILES.items():
        checked = reject_switch(path, f"PC {language} source")
        actual_hash = sha256_path(checked)
        require(actual_hash == expected_hash, f"PC {language} source profile differs")
        records[language] = W27.records_by_coordinate(checked.read_bytes())
        hashes[language] = actual_hash
    return records, hashes


def opaque_02xx_prefixes(record: Any) -> tuple[str, ...]:
    found: list[str] = []
    for span in W27.opaque_spans(record):
        for index in range(len(span) - 1):
            if span[index] == 0x02:
                found.append(span[index:index + 2].hex().upper())
    return tuple(found)


def static_patch_007_layout(value: str, advance: Any) -> dict[str, Any]:
    """Measure visible text with raw G1N advances scaled to 30px runtime."""

    reports: list[dict[str, Any]] = []
    fallback: set[str] = set()
    for visible_line in value.split("\n"):
        raw_width = 0
        full_width_count = 0
        half_width_count = 0
        for char in visible_line:
            raw_advance, used_fallback = advance(char)
            if raw_advance == RAW_G1N_FULL_WIDTH_ADVANCE:
                full_width_count += 1
            elif raw_advance == RAW_G1N_FULL_WIDTH_ADVANCE // 2:
                half_width_count += 1
            else:
                raise Wave85Error(f"unexpected G1N advance U+{ord(char):04X}: {raw_advance}")
            raw_width += raw_advance
            if used_fallback:
                fallback.add(f"U+{ord(char):04X}")
        effective_width = (
            raw_width * RUNTIME_FULL_WIDTH_ADVANCE + RAW_G1N_FULL_WIDTH_ADVANCE - 1
        ) // RAW_G1N_FULL_WIDTH_ADVANCE
        reports.append(
            {
                "display_string": visible_line,
                "raw_g1n_width_px": raw_width,
                "effective_width_px": effective_width,
                "full_width_character_count": full_width_count,
                "half_width_character_count": half_width_count,
                "exceeds_912px": effective_width > MAX_EFFECTIVE_LINE_PX,
            }
        )
    return {
        "line_count": len(reports),
        "raw_g1n_line_widths_px": tuple(row["raw_g1n_width_px"] for row in reports),
        "effective_line_widths_px": tuple(row["effective_width_px"] for row in reports),
        "max_effective_line_width_px": max(
            (row["effective_width_px"] for row in reports),
            default=0,
        ),
        "any_effective_line_exceeds_912px": any(row["exceeds_912px"] for row in reports),
        "wide_fallback_codepoints": tuple(sorted(fallback)),
        "lines": tuple(reports),
    }


def validate_source_anchor(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    require(set(change.source_record_sha256) == set(PC_SOURCE_PROFILES), f"source hash scope differs: {change.name}")
    result: dict[str, Any] = {}
    for language in PC_SOURCE_PROFILES:
        record = sources[language].get(change.coordinate)
        require(record is not None, f"source coordinate is absent: {change.name} {language}")
        actual_hash = W27.sha256_bytes(record.data)
        require(actual_hash == change.source_record_sha256[language], f"source record differs: {change.name} {language}")
        literals = W27.literal_texts(record)
        if language == "BASE_JP":
            require(literals == (change.source_jp_literal,), f"Base JP literal differs: {change.name}")
        else:
            require(literals == ("",), f"Base {language[-2:]} source is not empty: {change.name}")
        result[language] = {
            "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
            "record_sha256": actual_hash,
            "visible_text_utf16le_sha256": sha256_bytes("".join(literals).encode("utf-16le")),
            "visible_literals": list(literals),
        }
    return result


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == change.current_record_sha256, f"current record hash differs: {change.name}")
    require(len(before.data) == change.current_record_size, f"current record size differs: {change.name}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"terminator differs: {change.name}")
    require(len(W27.literal_texts(before)) == 1, f"literal count differs: {change.name}")
    require(
        tuple(span.hex().upper() for span in W27.opaque_spans(before)) == change.input_opaque_spans_hex,
        f"input opaque spans differ: {change.name}",
    )
    commands = W27.complete_0143_commands(W27.opaque_spans(before))
    require(commands == change.static_0143_commands, f"static 0143 command set differs: {change.name}")
    require("014301000000" not in commands, f"runtime 0143 slot is forbidden: {change.name}")
    require(not opaque_02xx_prefixes(before), f"02xx opcode is forbidden: {change.name}")
    spans = W27.opaque_spans(before)
    require(
        W27.strip_complete_0143(spans[-1]) == W27.RECORD_TERMINATOR
        and all(not W27.complete_0143_commands((span,)) for span in spans[:-1]),
        f"static 0143 must be terminal-only: {change.name}",
    )

    before_text = W27.literal_texts(before)[0]
    require(before_text.count("\n") == change.target_literal.count("\n") == 1, f"two-line topology differs: {change.name}")
    layout = static_patch_007_layout(change.target_literal, advance)
    require(
        tuple(layout["raw_g1n_line_widths_px"]) == change.target_raw_g1n_line_widths_px,
        f"target raw G1N width differs: {change.name}",
    )
    require(
        layout["line_count"] == 2
        and layout["line_count"] <= MAX_LINES
        and not layout["any_effective_line_exceeds_912px"],
        f"target static-patch-007 layout differs: {change.name}",
    )
    require(not layout["wide_fallback_codepoints"], f"target fallback glyph differs: {change.name}")

    rebuilt = W27.rebuild_static_record(before, (change.target_literal,))
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == (change.target_literal,), f"target literal differs: {change.name}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"marker topology differs: {change.name}")
    require(W27.opaque_spans(after) == W27.stripped_opaque_spans(before), f"opaque topology differs: {change.name}")
    require(tuple(span.hex().upper() for span in W27.opaque_spans(after)) == ("", "050505"), f"target opaque spans differ: {change.name}")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), f"static 0143 remains: {change.name}")
    require(not opaque_02xx_prefixes(after), f"02xx opcode introduced: {change.name}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {change.name}")
    require(W27.sha256_bytes(after.data) == change.target_record_sha256, f"target record hash differs: {change.name}")
    require(len(after.data) == change.target_record_size, f"target record size differs: {change.name}")

    return rebuilt, {
        "name": change.name,
        "resource": BASE_RESOURCE,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "source_base_jp_literal": change.source_jp_literal,
        "display_literal": change.target_literal,
        "current_record_sha256": change.current_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "current_record_size": change.current_record_size,
        "target_record_size": change.target_record_size,
        "display_line_count": layout["line_count"],
        "manual_line_break_count": change.target_literal.count("\n"),
        "target_raw_g1n_line_widths_px": list(layout["raw_g1n_line_widths_px"]),
        "target_effective_line_widths_px": list(layout["effective_line_widths_px"]),
        "target_max_effective_line_width_px": layout["max_effective_line_width_px"],
        "target_any_effective_line_exceeds_912px": layout["any_effective_line_exceeds_912px"],
        "display_lines": list(layout["lines"]),
        "input_opaque_spans_hex": list(change.input_opaque_spans_hex),
        "target_opaque_spans_hex": ["", "050505"],
        "removed_static_0143_commands": list(change.static_0143_commands),
        "runtime_0143_slot_present": False,
        "input_02xx_opcodes": [],
        "target_02xx_opcodes": [],
    }


def prepare_candidate() -> CandidateBundle:
    packed_before, records_before, predecessor = load_predecessors()
    sources, source_file_hashes = load_source_records()
    advance, font = W27.load_font_advance()
    replacements: dict[tuple[int, int], bytes] = {}
    rows: list[dict[str, Any]] = []

    for change in CHANGES:
        before = records_before[BASE_RESOURCE].get(change.coordinate)
        require(before is not None, f"predecessor coordinate is absent: {change.name}")
        replacement, row = validate_change(change, before, advance)
        require(change.coordinate not in replacements, f"duplicate change coordinate: {change.name}")
        replacements[change.coordinate] = replacement
        row["pc_source_anchor"] = validate_source_anchor(change, sources)
        rows.append(row)

    packed_after: dict[str, bytes] = {}
    raw_after: dict[str, bytes] = {}
    non_target_counts: dict[str, int] = {}
    for resource in RESOURCE_ORDER:
        source = packed_before[resource]
        resource_replacements = replacements if resource == BASE_RESOURCE else {}
        candidate = W27.rebuild_packed_msggame(source, resource_replacements)
        profile = TARGET_PROFILES[resource]
        require(len(candidate) == profile["size"], f"target packed size differs: {resource}")
        require(sha256_bytes(candidate) == profile["sha256"], f"target packed hash differs: {resource}")
        W27.validate_raw_roundtrip(candidate, f"Wave 85 candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        require(len(raw) == profile["raw_size"], f"target raw size differs: {resource}")
        require(sha256_bytes(raw) == profile["raw_sha256"], f"target raw hash differs: {resource}")

        before_records = records_before[resource]
        after_records = W27.records_by_coordinate(candidate)
        require(set(before_records) == set(after_records), f"record coordinate set differs: {resource}")
        expected_changed = set(resource_replacements)
        actual_changed = {
            coordinate
            for coordinate, before in before_records.items()
            if before.data != after_records[coordinate].data
        }
        require(actual_changed == expected_changed, f"changed record scope differs: {resource}")
        for coordinate, before in before_records.items():
            if coordinate not in expected_changed:
                require(before.data == after_records[coordinate].data, f"non-target record changed: {resource} {coordinate}")
        if resource == BASE_RESOURCE:
            for change in CHANGES:
                require(
                    W27.sha256_bytes(after_records[change.coordinate].data) == change.target_record_sha256,
                    f"output record differs: {change.name}",
                )
        else:
            require(candidate == source, "PK must remain byte-identical from Wave 83")

        packed_after[resource] = candidate
        raw_after[resource] = raw
        non_target_counts[resource] = len(before_records) - len(expected_changed)

    audit: Mapping[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "predecessor": "exact Wave 84 private candidate",
            "pc_base_jp_sc_tc_only": True,
            "pk_exact_same_text_reference": "absent for all six Base-only B2 rows",
            "switch_korean_read": False,
            "sentence_shortening": "forbidden",
            "manual_line_break_topology": "semantic two-line layout preserved",
            "layout_baseline": {
                "runtime_full_width_advance_px": RUNTIME_FULL_WIDTH_ADVANCE,
                "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
                "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
                "max_effective_line_width_px": MAX_EFFECTIVE_LINE_PX,
                "max_lines": MAX_LINES,
            },
            "steam_game_resource_written": False,
            "steam_transaction_capability": "absent",
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor": predecessor,
        "pc_source_packed_sha256": source_file_hashes,
        "font": font,
        "records": rows,
        "changed_record_count": len(CHANGES),
        "non_target_record_counts": non_target_counts,
        "non_target_record_byte_identity": "PASS",
        "target": {
            resource: {
                "size": len(packed_after[resource]),
                "sha256": sha256_bytes(packed_after[resource]),
                "raw_size": len(raw_after[resource]),
                "raw_sha256": sha256_bytes(raw_after[resource]),
            }
            for resource in RESOURCE_ORDER
        },
    }
    manifest: Mapping[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "predecessor": predecessor,
        "resources": {
            resource: {
                "input": {
                    "size": INPUT_PROFILES[resource]["size"],
                    "sha256": INPUT_PROFILES[resource]["sha256"],
                },
                "output": {
                    "size": TARGET_PROFILES[resource]["size"],
                    "sha256": TARGET_PROFILES[resource]["sha256"],
                },
                "changed_coordinates": [
                    f"{change.coordinate[0]}:{change.coordinate[1]}"
                    for change in CHANGES
                    if resource == BASE_RESOURCE
                ],
            }
            for resource in RESOURCE_ORDER
        },
        "changed_record_count": len(CHANGES),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_after, raw_after, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, packed in bundle.packed.items():
            target = stage / resource
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(packed)
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
    for resource, packed in bundle.packed.items():
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "pk_byte_identical_from_wave83": True,
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
            "changed_record_count": len(CHANGES),
            "pk_byte_identical_from_wave83": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
