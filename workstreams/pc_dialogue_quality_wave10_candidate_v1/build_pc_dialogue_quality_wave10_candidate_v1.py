#!/usr/bin/env python3
"""Build the private PC-only Wave 10 static dialogue candidate.

Wave 10 deliberately has one narrow scope: twelve identical PK officer
dialogue records at block 6 IDs 1454 through 1465. It consumes the pinned
Wave 9 private candidate, never writes the Steam installation, and writes
only its candidate, audit, and manifest below this workstream's tmp root.

The target is independently pinned to the corresponding current PC Base
correction and to pristine PC Japanese. Nintendo Switch Korean assets are
not read.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
WAVE4_PATH = (
    REPO / "workstreams" / "pc_dialogue_quality_wave4_v1"
    / "build_pc_dialogue_quality_wave4_v1.py"
)
PRIVATE_TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
WAVE9_INPUT_ROOT = (
    REPO / "tmp" / "pc_dialogue_runtime_wave9_candidate_v1" / "candidate-build-1"
)
DEFAULT_FONT_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

RESOURCE = "MSG_PK/JP/msggame.bin"
SCHEMA = "nobu16.kr.pc-dialogue-quality-wave10-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave10-audit.v1"
RECORD_TERMINATOR = b"\x05\x05\x05"
LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"
MAX_LINES = 3
MAX_LINE_PX = 912
WIDE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]"
)

# This is the Wave 9 PK candidate, not an implicit read from Steam.
INPUT_SHA256 = "209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930"
TARGET_SHA256 = "51539ABBCF4C78F5B9D51CDE7D2ABB343CFF61FE8DB6ACBEF427253F9C86B463"
FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"

BASE_CURRENT_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin")
BASE_CURRENT_SHA256 = "7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492"
BASE_PRISTINE_JP_PATH = REPO.parent / "MSG" / "JP" / "msggame.bin"
BASE_PRISTINE_JP_SHA256 = "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"
PK_PRISTINE_JP_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
    r"\MSG_PK\JP\msggame.bin"
)
PK_PRISTINE_JP_SHA256 = "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"

PK_RECORD_IDS = tuple(range(1454, 1466))
BASE_DONOR_RECORD_IDS = tuple(range(1450, 1462))
CURRENT_LITERALS = ("승", "…\n가문을 위해서라면, 어쩔 수 없")
TARGET_LITERALS = ("알겠습니다", "…\n가문을 위한 일이라면, 어쩔 수 없지요.")
PRISTINE_JP_LITERALS = ("承", "…\n当家のためとあらば、致し方")
INPUT_RECORD_SHA256 = "42E93129E882897F9ED13716BB7E585D5A94997775A4363896BEAE864B27E3A4"
TARGET_RECORD_SHA256 = "D4B2F840C103BE180A535640CDC318746FE0C9D2A05125CD48FAACF429A6452D"
INPUT_OPAQUE_SPANS_HEX = ("", "014374020000", "0143E6020000050505")
OUTPUT_OPAQUE_SPANS_HEX = ("", "", "050505")
REMOVABLE_0143 = (
    (8, "014374020000"),
    (58, "0143E6020000"),
)


class Wave10Error(RuntimeError):
    """A Wave 10 source, preservation, or output contract was violated."""


for module_root in (TOOLS, MSGGAME_TOOLS):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from nobu16_lz4 import decompress_wrapper, parse_link  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402
from msggame_format import MsgGameRecord, parse_record_literals, rebuild_packed_msggame  # noqa: E402


def load_wave4() -> Any:
    spec = importlib.util.spec_from_file_location("wave10_wave4", WAVE4_PATH)
    if spec is None or spec.loader is None:
        raise Wave10Error(f"cannot load the Wave 4 record helper: {WAVE4_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE4 = load_wave4()


@dataclass(frozen=True)
class CandidateBundle:
    packed_msggame: bytes
    input_sha256: str
    output_sha256: str
    audit: dict[str, Any]


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


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave10Error(f"{label} escapes {resolved_root}: {resolved_path}") from exc
    return resolved_path


def require_private_output(path: Path, label: str) -> Path:
    return require_under(path, PRIVATE_TMP_ROOT, label)


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
        (
            record.data[literal.marker_offset : literal.marker_offset + len(LITERAL_START)],
            record.data[literal.marker_end - len(LITERAL_END) : literal.marker_end],
        )
        for literal in parse_record_literals(record)
    )


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    return WAVE4.records_by_coordinate(packed)


def coordinate_text(coordinate: tuple[int, int]) -> str:
    return f"{coordinate[0]}:{coordinate[1]}"


def load_font_advance(
    font_root: Path,
) -> tuple[Callable[[str], tuple[int, bool]], dict[str, Any]]:
    font_path = (font_root / "RES_JP" / "res_lang.bin").resolve()
    if not font_path.is_file():
        raise Wave10Error(f"PC JP font resource is absent: {font_path}")
    actual_font_sha256 = sha256_path(font_path)
    if actual_font_sha256 != FONT_SHA256:
        raise Wave10Error(
            f"PC JP font hash differs: expected {FONT_SHA256}, got {actual_font_sha256}"
        )
    try:
        archive = parse_link(font_path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[6].data)
    except (IndexError, ValueError) as exc:
        raise Wave10Error("PC JP font entry 6 cannot be unpacked") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_wave10_font_") as directory:
        g1n_path = Path(directory) / "font.g1n"
        g1n_path.write_bytes(raw)
        parsed = g1n.parse_g1n(g1n_path)
    if parsed.structural_errors or not parsed.tables:
        raise Wave10Error("PC JP font entry 6 is structurally invalid")
    table = parsed.tables[0]

    def advance(character: str) -> tuple[int, bool]:
        if len(character) != 1:
            raise Wave10Error("font width requests must contain exactly one character")
        codepoint = ord(character)
        ordinal = table.mapping[codepoint] if codepoint < len(table.mapping) else 0
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(character):
                return 48, True
            raise Wave10Error(f"PC JP font lacks glyph U+{codepoint:04X}")
        if ordinal >= len(table.records):
            raise Wave10Error(f"invalid PC JP glyph ordinal for U+{codepoint:04X}")
        glyph = table.records[ordinal]
        if glyph.width != glyph.advance or glyph.advance not in (24, 48):
            raise Wave10Error(f"invalid PC JP glyph metrics for U+{codepoint:04X}")
        return glyph.advance, False

    return advance, {
        "resource": "RES_JP/res_lang.bin",
        "entry": 6,
        "packed_sha256": actual_font_sha256,
        "table_count": len(parsed.tables),
    }


def merged_line_layout(
    literals: tuple[str, ...], advance: Callable[[str], tuple[int, bool]]
) -> dict[str, Any]:
    text = "".join(literals)
    widths: list[int] = []
    fallback_codepoints: set[str] = set()
    for line in text.split("\n"):
        width = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                raise Wave10Error(f"candidate contains control U+{ord(character):04X}")
            character_width, fallback = advance(character)
            width += character_width
            if fallback:
                fallback_codepoints.add(f"U+{ord(character):04X}")
        widths.append(width)
    layout = {
        "line_count": len(widths),
        "line_widths_px": widths,
        "max_width_px": max(widths, default=0),
        "wide_fallback_codepoints": sorted(fallback_codepoints),
    }
    if layout["line_count"] > MAX_LINES:
        raise Wave10Error(
            f"candidate exceeds {MAX_LINES} manual lines: {layout['line_count']}"
        )
    if layout["max_width_px"] > MAX_LINE_PX:
        raise Wave10Error(
            f"candidate exceeds {MAX_LINE_PX}px: {layout['max_width_px']}"
        )
    if layout["wide_fallback_codepoints"]:
        raise Wave10Error(
            "candidate relies on fallback glyph widths: "
            f"{layout['wide_fallback_codepoints']}"
        )
    return layout


def validate_wave9_input(input_root: Path) -> tuple[Path, bytes]:
    resolved = input_root.resolve()
    if not resolved.is_dir():
        raise Wave10Error(f"Wave 9 private candidate root is absent: {resolved}")
    if "switch" in "/".join(part.lower() for part in resolved.parts):
        raise Wave10Error("Nintendo Switch Korean input is forbidden")
    packed_path = resolved / Path(RESOURCE)
    if not packed_path.is_file():
        raise Wave10Error(f"Wave 9 PK msggame is absent: {packed_path}")
    packed = packed_path.read_bytes()
    actual = sha256_bytes(packed)
    if actual != INPUT_SHA256:
        raise Wave10Error(
            f"Wave 9 PK msggame hash differs: expected {INPUT_SHA256}, got {actual}"
        )
    return packed_path, packed


def validate_pc_direct_correction() -> dict[str, Any]:
    required = (
        (BASE_CURRENT_PATH, BASE_CURRENT_SHA256, "current PC Base correction"),
        (BASE_PRISTINE_JP_PATH, BASE_PRISTINE_JP_SHA256, "pristine PC Base Japanese"),
        (PK_PRISTINE_JP_PATH, PK_PRISTINE_JP_SHA256, "pristine PC PK Japanese"),
    )
    for path, expected, label in required:
        if not path.is_file():
            raise Wave10Error(f"{label} is absent: {path}")
        actual = sha256_path(path)
        if actual != expected:
            raise Wave10Error(
                f"{label} hash differs: expected {expected}, got {actual}"
            )

    base_current = records_by_coordinate(BASE_CURRENT_PATH.read_bytes())
    base_jp = records_by_coordinate(BASE_PRISTINE_JP_PATH.read_bytes())
    pk_jp = records_by_coordinate(PK_PRISTINE_JP_PATH.read_bytes())
    base_evidence: list[dict[str, str]] = []
    for base_record_id, pk_record_id in zip(BASE_DONOR_RECORD_IDS, PK_RECORD_IDS):
        base_coordinate = (6, base_record_id)
        pk_coordinate = (6, pk_record_id)
        base_ko_record = base_current.get(base_coordinate)
        base_jp_record = base_jp.get(base_coordinate)
        pk_jp_record = pk_jp.get(pk_coordinate)
        if base_ko_record is None or base_jp_record is None or pk_jp_record is None:
            raise Wave10Error(
                f"missing direct-correction source pair: "
                f"{coordinate_text(base_coordinate)} -> {coordinate_text(pk_coordinate)}"
            )
        if literal_texts(base_ko_record) != TARGET_LITERALS:
            raise Wave10Error(
                f"Base direct correction literals differ at {coordinate_text(base_coordinate)}"
            )
        if literal_texts(base_jp_record) != PRISTINE_JP_LITERALS:
            raise Wave10Error(
                f"Base pristine Japanese differs at {coordinate_text(base_coordinate)}"
            )
        if literal_texts(pk_jp_record) != PRISTINE_JP_LITERALS:
            raise Wave10Error(
                f"PK pristine Japanese differs at {coordinate_text(pk_coordinate)}"
            )
        if sha256_bytes(base_ko_record.data) != TARGET_RECORD_SHA256:
            raise Wave10Error(
                f"Base direct correction record hash differs at {coordinate_text(base_coordinate)}"
            )
        if opaque_spans(base_ko_record) != (b"", b"", RECORD_TERMINATOR):
            raise Wave10Error(
                f"Base direct correction opaque topology differs at {coordinate_text(base_coordinate)}"
            )
        if marker_topology(base_ko_record) != (
            (LITERAL_START, LITERAL_END),
            (LITERAL_START, LITERAL_END),
        ):
            raise Wave10Error(
                f"Base direct correction marker topology differs at {coordinate_text(base_coordinate)}"
            )
        base_evidence.append(
            {
                "base_coordinate": coordinate_text(base_coordinate),
                "pk_coordinate": coordinate_text(pk_coordinate),
                "base_output_record_sha256": sha256_bytes(base_ko_record.data),
                "base_pristine_jp_record_sha256": sha256_bytes(base_jp_record.data),
                "pk_pristine_jp_record_sha256": sha256_bytes(pk_jp_record.data),
            }
        )

    return {
        "base_current_sha256": BASE_CURRENT_SHA256,
        "base_pristine_jp_sha256": BASE_PRISTINE_JP_SHA256,
        "pk_pristine_jp_sha256": PK_PRISTINE_JP_SHA256,
        "one_to_one_pairs": base_evidence,
    }


def validate_input_record(record: MsgGameRecord, coordinate: tuple[int, int]) -> None:
    if sha256_bytes(record.data) != INPUT_RECORD_SHA256:
        raise Wave10Error(f"{coordinate_text(coordinate)} input record hash differs")
    if literal_texts(record) != CURRENT_LITERALS:
        raise Wave10Error(f"{coordinate_text(coordinate)} input literals differ")
    if tuple(value.hex().upper() for value in opaque_spans(record)) != INPUT_OPAQUE_SPANS_HEX:
        raise Wave10Error(f"{coordinate_text(coordinate)} input opaque spans differ")
    if marker_topology(record) != (
        (LITERAL_START, LITERAL_END),
        (LITERAL_START, LITERAL_END),
    ):
        raise Wave10Error(f"{coordinate_text(coordinate)} input marker topology differs")
    if not record.data.endswith(RECORD_TERMINATOR):
        raise Wave10Error(f"{coordinate_text(coordinate)} input record lacks terminator")
    actual_commands = tuple(
        (offset, command.hex().upper()) for offset, command in WAVE4.opaque_commands(record)
    )
    if actual_commands != REMOVABLE_0143:
        raise Wave10Error(
            f"{coordinate_text(coordinate)} removable JP-only 0143 commands differ"
        )


def rebuild_static_record(record: MsgGameRecord, coordinate: tuple[int, int]) -> MsgGameRecord:
    changes = tuple(
        WAVE4.change(index, before, after)
        for index, (before, after) in enumerate(zip(CURRENT_LITERALS, TARGET_LITERALS))
    )
    removals = tuple(
        WAVE4.remove_command(offset, command_hex)
        for offset, command_hex in REMOVABLE_0143
    )
    plan = WAVE4.plan(
        coordinate[0],
        coordinate[1],
        INPUT_RECORD_SHA256,
        changes,
        remove_commands=removals,
    )
    output_data = WAVE4.rebuild_quality_record(
        record,
        plan,
        {0: TARGET_LITERALS[0], 1: TARGET_LITERALS[1]},
    )
    output = MsgGameRecord(
        block_id=record.block_id,
        record_id=record.record_id,
        relative_offset=record.relative_offset,
        data=output_data,
    )
    if literal_texts(output) != TARGET_LITERALS:
        raise Wave10Error(f"{coordinate_text(coordinate)} output literals differ")
    if sha256_bytes(output.data) != TARGET_RECORD_SHA256:
        raise Wave10Error(f"{coordinate_text(coordinate)} output record hash differs")
    if tuple(value.hex().upper() for value in opaque_spans(output)) != OUTPUT_OPAQUE_SPANS_HEX:
        raise Wave10Error(f"{coordinate_text(coordinate)} output opaque spans differ")
    if marker_topology(output) != marker_topology(record):
        raise Wave10Error(f"{coordinate_text(coordinate)} output marker topology changed")
    if not output.data.endswith(RECORD_TERMINATOR):
        raise Wave10Error(f"{coordinate_text(coordinate)} output terminator changed")
    if WAVE4.opaque_commands(output):
        raise Wave10Error(f"{coordinate_text(coordinate)} output retained a JP-only 0143 command")
    return output


def validate_full_output(
    input_packed: bytes,
    output_packed: bytes,
    expected_records: Mapping[tuple[int, int], MsgGameRecord],
) -> None:
    before = records_by_coordinate(input_packed)
    after = records_by_coordinate(output_packed)
    if before.keys() != after.keys():
        raise Wave10Error("candidate changed msggame record topology")
    changed = {
        coordinate
        for coordinate in before
        if before[coordinate].data != after[coordinate].data
    }
    expected = set(expected_records)
    if changed != expected:
        raise Wave10Error(
            f"candidate changed records outside the 12-row contract: "
            f"expected={sorted(expected)} actual={sorted(changed)}"
        )
    for coordinate, expected_record in expected_records.items():
        if after[coordinate].data != expected_record.data:
            raise Wave10Error(f"{coordinate_text(coordinate)} candidate payload differs")


def source_free_audit_row(
    coordinate: tuple[int, int],
    input_record: MsgGameRecord,
    output_record: MsgGameRecord,
    input_layout: dict[str, Any],
    output_layout: dict[str, Any],
) -> dict[str, Any]:
    return {
        "coordinate": coordinate_text(coordinate),
        "input_record_sha256": sha256_bytes(input_record.data),
        "output_record_sha256": sha256_bytes(output_record.data),
        "literal_slot_count": len(CURRENT_LITERALS),
        "input_literal_utf16le_sha256": [text_sha256(value) for value in CURRENT_LITERALS],
        "output_literal_utf16le_sha256": [text_sha256(value) for value in TARGET_LITERALS],
        "input_opaque_span_sha256": [
            sha256_bytes(value) for value in opaque_spans(input_record)
        ],
        "output_opaque_span_sha256": [
            sha256_bytes(value) for value in opaque_spans(output_record)
        ],
        "input_opaque_spans_hex": list(INPUT_OPAQUE_SPANS_HEX),
        "output_opaque_spans_hex": list(OUTPUT_OPAQUE_SPANS_HEX),
        "removed_jp_only_0143": [
            {"offset": offset, "hex": command_hex}
            for offset, command_hex in REMOVABLE_0143
        ],
        "literal_marker_topology": [
            {"start": start.hex().upper(), "end": end.hex().upper()}
            for start, end in marker_topology(input_record)
        ],
        "terminator_hex": RECORD_TERMINATOR.hex().upper(),
        "input_layout": input_layout,
        "output_layout": output_layout,
        "missing_static_glyphs": [],
        "real_game_qa_required_before_release": True,
    }


def prepare_candidate(input_root: Path, font_root: Path) -> CandidateBundle:
    _packed_path, input_packed = validate_wave9_input(input_root)
    direct_correction_evidence = validate_pc_direct_correction()
    advance, font_evidence = load_font_advance(font_root)
    input_layout = merged_line_layout(CURRENT_LITERALS, advance)
    output_layout = merged_line_layout(TARGET_LITERALS, advance)
    if input_layout["line_count"] != 2 or output_layout["line_count"] != 2:
        raise Wave10Error("Wave 10 must preserve the intentional two-line layout")
    if output_layout["line_widths_px"] != [288, 888]:
        raise Wave10Error(
            f"Wave 10 target font widths differ: {output_layout['line_widths_px']}"
        )

    before = records_by_coordinate(input_packed)
    replacements: dict[tuple[int, int], bytes] = {}
    expected_records: dict[tuple[int, int], MsgGameRecord] = {}
    audit_rows: list[dict[str, Any]] = []
    for record_id in PK_RECORD_IDS:
        coordinate = (6, record_id)
        input_record = before.get(coordinate)
        if input_record is None:
            raise Wave10Error(f"Wave 9 input lacks {coordinate_text(coordinate)}")
        validate_input_record(input_record, coordinate)
        output_record = rebuild_static_record(input_record, coordinate)
        replacements[coordinate] = output_record.data
        expected_records[coordinate] = output_record
        audit_rows.append(
            source_free_audit_row(
                coordinate,
                input_record,
                output_record,
                input_layout,
                output_layout,
            )
        )

    output_packed = rebuild_packed_msggame(input_packed, replacements)
    validate_full_output(input_packed, output_packed, expected_records)
    output_sha256 = sha256_bytes(output_packed)
    if output_sha256 != TARGET_SHA256:
        raise Wave10Error(
            f"Wave 10 target hash differs: expected {TARGET_SHA256}, got {output_sha256}"
        )

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_free": True,
        "literal_source_text_embedded": False,
        "source_policy": {
            "platform": "Steam PC",
            "input_text_profile": "private Wave 9 candidate",
            "semantic_anchor": "current PC Base direct correction + pristine PC Japanese",
            "switch_korean_used": False,
            "excluded": ["Nintendo Switch Korean"],
        },
        "steam_write_capability": "absent",
        "input_sha256": INPUT_SHA256,
        "output_sha256": output_sha256,
        "font_evidence": font_evidence,
        "pc_direct_correction_evidence": direct_correction_evidence,
        "summary": {
            "changed_resource": RESOURCE,
            "physical_records": len(PK_RECORD_IDS),
            "logical_sentences": 1,
            "coordinates": [coordinate_text((6, record_id)) for record_id in PK_RECORD_IDS],
            "manual_lines": 2,
            "max_line_px": MAX_LINE_PX,
            "target_line_widths_px": output_layout["line_widths_px"],
            "real_game_qa_required_before_release": True,
        },
        "records": audit_rows,
    }
    return CandidateBundle(
        packed_msggame=output_packed,
        input_sha256=INPUT_SHA256,
        output_sha256=output_sha256,
        audit=audit,
    )


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def write_json(path: Path, value: Mapping[str, Any]) -> str:
    payload = canonical_json(value)
    atomic_write(path, payload)
    return sha256_bytes(payload)


def write_candidate(bundle: CandidateBundle, output_root: Path) -> None:
    output_root = require_private_output(output_root, "candidate output")
    if output_root.exists():
        raise Wave10Error(f"refusing to overwrite candidate output: {output_root}")
    destination = output_root / Path(RESOURCE)
    atomic_write(destination, bundle.packed_msggame)
    actual = sha256_path(destination)
    if actual != bundle.output_sha256:
        raise Wave10Error("written candidate hash differs")


def build_manifest(bundle: CandidateBundle, audit_sha256: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "source_free_audit": True,
        "source_free_audit_sha256": audit_sha256,
        "steam_write_capability": "absent",
        "steam_apply_command": None,
        "input_sha256": bundle.input_sha256,
        "output_sha256": bundle.output_sha256,
        "changed_paths": [RESOURCE],
        "coordinates": [coordinate_text((6, record_id)) for record_id in PK_RECORD_IDS],
        "real_game_qa_required_before_release": True,
    }


def print_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def command_hash(args: argparse.Namespace) -> int:
    bundle = prepare_candidate(args.input_root, args.font_root)
    print_json(
        {
            "status": "ok",
            "candidate_records": len(PK_RECORD_IDS),
            "output_sha256": bundle.output_sha256,
            "steam_write_capability": "absent",
        }
    )
    return 0


def command_audit(args: argparse.Namespace) -> int:
    audit_path = require_private_output(args.audit_path, "audit output")
    bundle = prepare_candidate(args.input_root, args.font_root)
    audit_sha256 = write_json(audit_path, bundle.audit)
    print_json(
        {
            "status": "ok",
            "audit": audit_path.relative_to(REPO).as_posix(),
            "audit_sha256": audit_sha256,
            "output_sha256": bundle.output_sha256,
            "steam_write_capability": "absent",
        }
    )
    return 0


def command_build(args: argparse.Namespace) -> int:
    output_root = require_private_output(args.output_root, "candidate output")
    audit_path = require_private_output(args.audit_path, "audit output")
    manifest_path = require_private_output(args.manifest, "manifest output")
    bundle = prepare_candidate(args.input_root, args.font_root)
    write_candidate(bundle, output_root)
    audit_sha256 = write_json(audit_path, bundle.audit)
    manifest_sha256 = write_json(manifest_path, build_manifest(bundle, audit_sha256))
    print_json(
        {
            "status": "ok",
            "candidate": output_root.relative_to(REPO).as_posix(),
            "audit": audit_path.relative_to(REPO).as_posix(),
            "manifest": manifest_path.relative_to(REPO).as_posix(),
            "audit_sha256": audit_sha256,
            "manifest_sha256": manifest_sha256,
            "output_sha256": bundle.output_sha256,
            "steam_write_capability": "absent",
        }
    )
    return 0


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input-root", type=Path, default=WAVE9_INPUT_ROOT)
    parser.add_argument("--font-root", type=Path, default=DEFAULT_FONT_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    hash_parser = subparsers.add_parser("hash", help="validate and print the private target hash")
    add_input_arguments(hash_parser)
    hash_parser.set_defaults(func=command_hash)

    audit_parser = subparsers.add_parser("audit", help="write a source-free private audit")
    add_input_arguments(audit_parser)
    audit_parser.add_argument(
        "--audit-path",
        type=Path,
        default=PRIVATE_TMP_ROOT / "audit_pc_dialogue_quality_wave10.v1.json",
    )
    audit_parser.set_defaults(func=command_audit)

    candidate_parser = subparsers.add_parser(
        "build", help="write the private candidate, audit, and manifest"
    )
    add_input_arguments(candidate_parser)
    candidate_parser.add_argument(
        "--output-root", type=Path, default=PRIVATE_TMP_ROOT / "candidate-build-1"
    )
    candidate_parser.add_argument(
        "--audit-path",
        type=Path,
        default=PRIVATE_TMP_ROOT / "audit_pc_dialogue_quality_wave10.v1.json",
    )
    candidate_parser.add_argument(
        "--manifest",
        type=Path,
        default=PRIVATE_TMP_ROOT / "build_manifest.v1.json",
    )
    candidate_parser.set_defaults(func=command_build)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Wave10Error as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
