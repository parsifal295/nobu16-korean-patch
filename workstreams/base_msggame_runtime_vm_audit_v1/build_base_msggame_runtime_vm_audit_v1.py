#!/usr/bin/env python3
"""Verify every Base dynamic-dialogue row against the reversed msggame VM.

The private decisions and pristine JP resource remain outside version control.
The generated public report contains counts, hashes, opcode signatures, and
coordinates only; it never contains source or translated dialogue text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DEFAULT_DECISIONS = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150" / "decisions"
DEFAULT_BASE_MSGGAME = (
    REPO.parent.parent
    / "private-inputs"
    / "legacy-pc-root"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_CURRENT_BASE_MSGGAME = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin")
DEFAULT_OUTPUT = WORKSTREAM / "public" / "base_msggame_runtime_vm_coverage.v1.json"
GHIDRA_CONTRACT = WORKSTREAM / "ghidra_vm_contract.v1.json"

sys.path[:0] = [str(REPO / "workstreams" / "msggame")]

from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
)


SCHEMA = "nobu16.kr.base-msggame-runtime-vm-coverage.v1"
PENDING_CLASS = "runtime_fragment_pending"
LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"
CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
JUMP_RE = re.compile(b"\x01\x4A(.{4})", re.DOTALL)
NEUTRAL_PARTICLES = ("이(가)", "을(를)", "은(는)", "와(과)", "으로(로)", "(으)로")
NEUTRAL_PARTICLE_LABELS = {
    "이(가)": "subject_i_ga",
    "을(를)": "object_eul_reul",
    "은(는)": "topic_eun_neun",
    "와(과)": "comitative_wa_gwa",
    "으로(로)": "instrumental_euro_ro",
    "(으)로": "directional_euro_ro",
}

EXPECTED = {
    "pending_rows": 15_651,
    "pending_records": 9_138,
    "0143_occurrences": 4_335,
    "02_occurrences": 8_255,
    "02_selector_families": 31,
    "02_slot_forms": 56,
    "empty_runtime_morphemes": 17,
    "neutral_particle_rows": 4_062,
    "control_graph": {
        "roots": 160,
        "reachable_records": 1_864,
        "jump_edge_occurrences": 2_030,
        "nested_call_edge_occurrences": 2,
    },
    "clusters": {
        "block0_morphology_terminal": (1_388, 1_388),
        "inline_02_only": (4_759, 7_809),
        "inline_0143_only": (1_315, 2_322),
        "inline_0143_and_02": (1_328, 3_605),
        "color_tag_multiliteral": (22, 66),
        "local_fragment_no_dynamic_opcode": (326, 461),
    },
}


class AuditError(ValueError):
    """Raised when a pinned runtime-verification invariant drifts."""


@dataclass(frozen=True)
class PendingRow:
    coordinate: str
    block_id: int
    record_id: int
    literal_id: int
    record_sha256: str
    current_text_sha256: str
    translation: str
    empty_runtime_morpheme: bool
    empty_runtime_morpheme_kind: str | None


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def compact_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def parse_coordinate(value: Any) -> tuple[int, int, int]:
    require(isinstance(value, str), "decision coordinate must be a string")
    parts = value.split(":")
    require(len(parts) == 3 and all(part.isdigit() for part in parts), f"invalid coordinate: {value}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def load_pending_rows(decision_root: Path) -> list[PendingRow]:
    require(decision_root.is_dir(), f"private decision directory is absent: {decision_root}")
    rows: list[PendingRow] = []
    seen: set[str] = set()
    paths = sorted(decision_root.glob("base_msggame_*.private.v1.jsonl"))
    require(paths, f"no Base private decisions found below {decision_root}")
    for path in paths:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if (
                    value.get("resource") != "base_msggame"
                    or value.get("scope_classification") != PENDING_CLASS
                    or value.get("runtime_review") != "pending"
                ):
                    continue
                require(value.get("semantic_review") == "approved", f"{path.name}:{line_number} is not approved")
                coordinate = value.get("coordinate")
                block_id, record_id, literal_id = parse_coordinate(coordinate)
                require(coordinate not in seen, f"duplicate pending coordinate: {coordinate}")
                seen.add(coordinate)
                translation = value.get("translation")
                require(isinstance(translation, str), f"{coordinate} translation is not a string")
                record_sha256 = value.get("source_record_raw_sha256")
                require(isinstance(record_sha256, str), f"{coordinate} has no source record guard")
                current_text_sha256 = value.get("current_ko_utf16le_sha256")
                require(isinstance(current_text_sha256, str), f"{coordinate} has no current text guard")
                rows.append(
                    PendingRow(
                        coordinate=coordinate,
                        block_id=block_id,
                        record_id=record_id,
                        literal_id=literal_id,
                        record_sha256=record_sha256,
                        current_text_sha256=current_text_sha256,
                        translation=translation,
                        empty_runtime_morpheme=value.get("empty_runtime_morpheme") is True,
                        empty_runtime_morpheme_kind=(
                            value.get("empty_runtime_morpheme_kind")
                            if isinstance(value.get("empty_runtime_morpheme_kind"), str)
                            else None
                        ),
                    )
                )
    rows.sort(key=lambda row: (row.block_id, row.record_id, row.literal_id))
    return rows


def load_base_decision_rows(decision_root: Path) -> list[dict[str, Any]]:
    require(decision_root.is_dir(), f"private decision directory is absent: {decision_root}")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    paths = sorted(decision_root.glob("base_msggame_*.private.v1.jsonl"))
    require(paths, f"no Base private decisions found below {decision_root}")
    for path in paths:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                require(row.get("resource") == "base_msggame", f"{path.name}:{line_number} mixes resources")
                coordinate = row.get("coordinate")
                parse_coordinate(coordinate)
                require(coordinate not in seen, f"duplicate Base decision coordinate: {coordinate}")
                seen.add(coordinate)
                rows.append(row)
    rows.sort(key=lambda row: parse_coordinate(row["coordinate"]))
    return rows


def archive_records(path: Path) -> dict[tuple[int, int], MsgGameRecord]:
    require(path.is_file(), f"pristine Base msggame is absent: {path}")
    archive = parse_packed_msggame(path.read_bytes()).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def build_candidate_records(
    current_path: Path,
    decision_rows: list[dict[str, Any]],
) -> tuple[dict[tuple[int, int], MsgGameRecord], str, str]:
    require(current_path.is_file(), f"current Base msggame is absent: {current_path}")
    current_blob = current_path.read_bytes()
    replacements: dict[tuple[int, int, int], str] = {}
    for row in decision_rows:
        translation = row.get("translation")
        if isinstance(translation, str):
            replacements[parse_coordinate(row["coordinate"])] = translation
    candidate_blob = rebuild_packed_with_literals(current_blob, replacements)
    archive = parse_packed_msggame(candidate_blob).archive
    records = {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }
    return records, sha256_bytes(current_blob), sha256_bytes(candidate_blob)


def literal_gaps(record: MsgGameRecord) -> tuple[bytes, ...]:
    literals = parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def selector_group(selector: int) -> tuple[int, int] | None:
    ranges = (
        (0x32, 0x3B, 0),
        (0x3C, 0x45, 1),
        (0x46, 0x4F, 2),
        (0x50, 0x59, 4),
        (0x5A, 0x63, 5),
        (0x64, 0x6D, 3),
        (0x6E, 0x77, 6),
        (0x78, 0x81, 7),
        (0x82, 0x8B, 8),
        (0x8C, 0x95, 9),
        (0x96, 0x9F, 10),
        (0xAA, 0xB3, 11),
        (0xB4, 0xBD, 12),
        (0xBE, 0xC7, 13),
        (0xC8, 0xC8, 14),
    )
    for lower, upper, group in ranges:
        if lower <= selector <= upper:
            return group, selector - lower
    return None


def parse_selector_atom(gap: bytes, cursor: int) -> tuple[dict[str, Any], int]:
    require(cursor + 2 <= len(gap), f"truncated 02 selector atom: {gap.hex().upper()}")
    require(gap[cursor] == 0x02, f"expression atom is not 02: {gap.hex().upper()}@{cursor}")
    group_slot = selector_group(gap[cursor + 1])
    require(group_slot is not None, f"unclassified selector: {gap[cursor:cursor + 2].hex().upper()}")
    end = cursor + 2
    # Every observed selector handler reads one lookahead byte and rewinds it
    # when it is a control byte (< 0x20).  Otherwise that byte is the
    # selector's property code.
    if end < len(gap) and gap[end] >= 0x20:
        end += 1
    group, slot = group_slot
    return {
        "kind": "selector_atom",
        "raw_hex": gap[cursor:end].hex().upper(),
        "group": group,
        "slot": slot,
    }, end


def parse_expression(gap: bytes, cursor: int) -> tuple[dict[str, Any], int]:
    atoms: list[dict[str, Any]] = []
    operators: list[str] = []
    atom, cursor = parse_selector_atom(gap, cursor)
    atoms.append(atom)
    while cursor < len(gap) and gap[cursor] == 0x03:
        require(cursor + 2 <= len(gap), f"truncated 03 expression chain: {gap.hex().upper()}")
        operator = gap[cursor + 1]
        require(operator in b"%*+-/", f"unknown expression operator: 0x{operator:02X}")
        operators.append(chr(operator))
        atom, cursor = parse_selector_atom(gap, cursor + 2)
        atoms.append(atom)
    return {
        "kind": "dynamic_expression",
        "atoms": atoms,
        "operators": operators,
    }, cursor


def decode_gap(gap: bytes) -> tuple[dict[str, Any], ...]:
    """Decode every byte in a pending candidate-record literal gap."""
    components: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(gap):
        if gap.startswith(b"\x05\x05\x05", cursor):
            components.append({"kind": "return", "raw_hex": "050505"})
            cursor += 3
            continue
        opcode = gap[cursor]
        if opcode == 0x01:
            require(cursor + 6 <= len(gap), f"truncated 01 command: {gap.hex().upper()}@{cursor}")
            subcode = gap[cursor + 1]
            require(subcode in (0x43, 0x4A), f"unsupported 01 command: 0x{subcode:02X}")
            operand = struct.unpack_from("<I", gap, cursor + 2)[0]
            components.append(
                {
                    "kind": "call" if subcode == 0x43 else "jump",
                    "target": list(packed_record_coordinate(operand)),
                    "raw_hex": gap[cursor:cursor + 6].hex().upper(),
                }
            )
            cursor += 6
            continue
        if opcode == 0x02:
            component, cursor = parse_expression(gap, cursor)
            components.append(component)
            continue
        if opcode == 0x1B:
            require(cursor + 2 <= len(gap), f"truncated 1B control tag: {gap.hex().upper()}@{cursor}")
            subcode = gap[cursor + 1]
            end = cursor + 2
            if subcode in (0x43, 0x45, 0x50, 0x57):
                require(end < len(gap), f"truncated 1B payload: {gap.hex().upper()}@{cursor}")
                end += 1
            components.append({"kind": "control", "raw_hex": gap[cursor:end].hex().upper()})
            cursor = end
            continue
        if opcode in (0x08, 0x09, 0x0A):
            components.append({"kind": "output_control", "raw_hex": f"{opcode:02X}"})
            cursor += 1
            continue
        raise AuditError(f"unknown pending-record gap byte: {gap.hex().upper()}@{cursor}")
    return tuple(components)


def dynamic_tokens(gap: bytes) -> tuple[bytes, ...]:
    return tuple(
        bytes.fromhex(atom["raw_hex"])
        for component in decode_gap(gap)
        if component["kind"] == "dynamic_expression"
        for atom in component["atoms"]
    )


def classify_record(record: MsgGameRecord, pending_literal_count: int) -> str:
    gaps = literal_gaps(record)
    decoded = tuple(component for gap in gaps for component in decode_gap(gap))
    joined = b"".join(gaps)
    has_call = any(component["kind"] == "call" for component in decoded)
    has_token = any(component["kind"] == "dynamic_expression" for component in decoded)
    if record.block_id == 0:
        return "block0_morphology_terminal"
    if has_call and has_token:
        return "inline_0143_and_02"
    if has_call:
        return "inline_0143_only"
    if has_token:
        return "inline_02_only"
    if pending_literal_count > 1 and b"\x1B\x43" in joined:
        return "color_tag_multiliteral"
    return "local_fragment_no_dynamic_opcode"


def u32_operands(pattern: re.Pattern[bytes], data: bytes) -> tuple[int, ...]:
    return tuple(struct.unpack("<I", match.group(1))[0] for match in pattern.finditer(data))


def packed_record_coordinate(operand: int) -> tuple[int, int]:
    """Decode the block/record convention proved in FUN_140a00fc0."""
    return operand // 10_000, operand % 10_000


def control_flow_graph(
    records: dict[tuple[int, int], MsgGameRecord],
    roots: Iterable[int],
) -> dict[str, Any]:
    root_set = sorted({packed_record_coordinate(root) for root in roots})
    visited: set[tuple[int, int]] = set()
    call_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    jump_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    call_edge_occurrences = 0
    jump_edge_occurrences = 0
    terminal_records: set[tuple[int, int]] = set()
    queue = deque(root_set)
    while queue:
        coordinate = queue.popleft()
        require(coordinate in records, f"0143/014A target is outside Base msggame: {coordinate}")
        if coordinate in visited:
            continue
        visited.add(coordinate)
        record = records[coordinate]
        calls = tuple(
            operand
            for gap in literal_gaps(record)
            for operand in u32_operands(CALL_RE, gap)
        )
        jumps = tuple(
            operand
            for gap in literal_gaps(record)
            for operand in u32_operands(JUMP_RE, gap)
        )
        if not calls and not jumps:
            terminal_records.add(coordinate)
        for operand in calls:
            if operand == 0:
                continue
            call_edge_occurrences += 1
            target = packed_record_coordinate(operand)
            require(target in records, f"nested 0143 target is outside Base msggame: {target}")
            call_edges.add((coordinate, target))
            queue.append(target)
        for operand in jumps:
            if operand == 0:
                continue
            jump_edge_occurrences += 1
            target = packed_record_coordinate(operand)
            require(target in records, f"014A target is outside Base msggame: {target}")
            jump_edges.add((coordinate, target))
            queue.append(target)

    adjacency: dict[tuple[int, int], set[tuple[int, int]]] = defaultdict(set)
    for source, target in call_edges | jump_edges:
        adjacency[source].add(target)
    record_runtime_guards = {
        coordinate: {
            "candidate_record_raw_sha256": sha256_bytes(records[coordinate].data),
            "literal_utf16le_sha256": [
                sha256_bytes(literal.text.encode("utf-16-le"))
                for literal in parse_record_literals(records[coordinate])
            ],
        }
        for coordinate in visited
    }
    root_guards: dict[str, dict[str, Any]] = {}
    for root in root_set:
        root_visited: set[tuple[int, int]] = set()
        root_queue = deque([root])
        while root_queue:
            coordinate = root_queue.popleft()
            if coordinate in root_visited:
                continue
            root_visited.add(coordinate)
            root_queue.extend(sorted(adjacency.get(coordinate, ())))
        guard_source = [
            {
                "coordinate": list(coordinate),
                **record_runtime_guards[coordinate],
            }
            for coordinate in sorted(root_visited)
        ]
        root_guards[f"{root[0]}:{root[1]}"] = {
            "reachable_record_count": len(root_visited),
            "candidate_alternative_set_sha256": sha256_bytes(
                compact_json_bytes(guard_source)
            ),
        }

    digest_source = {
        "roots": [list(value) for value in root_set],
        "visited": [list(value) for value in sorted(visited)],
        "call_edges": [
            [list(source), list(target)]
            for source, target in sorted(call_edges)
        ],
        "jump_edges": [
            [list(source), list(target)]
            for source, target in sorted(jump_edges)
        ],
        "terminals": [list(value) for value in sorted(terminal_records)],
        "record_runtime_guards": [
            {
                "coordinate": list(coordinate),
                **record_runtime_guards[coordinate],
            }
            for coordinate in sorted(visited)
        ],
    }
    return {
        "extraction_method": (
            "conservative_0143_014a_signature_overapproximation_across_nonliteral_gaps"
        ),
        "whole_reachable_vm_grammar_claimed": False,
        "root_count": len(root_set),
        "reachable_record_count": len(visited),
        "nested_0143_edge_occurrence_count": call_edge_occurrences,
        "nested_0143_edge_count": len(call_edges),
        "014a_edge_occurrence_count": jump_edge_occurrences,
        "014a_edge_count": len(jump_edges),
        "edge_count": len(call_edges | jump_edges),
        "terminal_record_count": len(terminal_records),
        "graph_sha256": sha256_bytes(
            compact_json_bytes(digest_source)
        ),
        "call_target_guards": root_guards,
    }


def masked_record_signature(record: MsgGameRecord) -> str:
    literals = parse_record_literals(record)
    parts: list[bytes] = []
    cursor = 0
    for literal in literals:
        parts.append(record.data[cursor : literal.marker_offset])
        parts.append(b"[LIT]")
        cursor = literal.marker_end
    parts.append(record.data[cursor:])
    return sha256_bytes(b"".join(parts))


def record_symbolic_components(
    record: MsgGameRecord,
    call_target_guards: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], ...]:
    """Build a source-free ordered template for one fully translated record."""
    components: list[dict[str, Any]] = []
    literals = parse_record_literals(record)
    gaps = literal_gaps(record)
    for literal_id, literal in enumerate(literals):
        for decoded in decode_gap(gaps[literal_id]):
            component = dict(decoded)
            if component["kind"] == "call":
                target_key = ":".join(str(value) for value in component["target"])
                require(target_key in call_target_guards, f"call target has no closure guard: {target_key}")
                component["target_alternative_set_sha256"] = call_target_guards[target_key][
                    "candidate_alternative_set_sha256"
                ]
            components.append(component)
        encoded = literal.text.encode("utf-16-le")
        components.append(
            {
                "kind": "literal",
                "coordinate": f"{record.block_id}:{record.record_id}:{literal_id}",
                "translation_utf16le_sha256": sha256_bytes(encoded),
                "utf16_code_unit_count": len(encoded) // 2,
            }
        )
    components.extend(decode_gap(gaps[-1]))
    return tuple(components)


def surface_class(character: str) -> str:
    if character.isspace():
        return "whitespace"
    if "\uac00" <= character <= "\ud7a3":
        return "hangul"
    if character.isdigit():
        return "digit"
    if character.isascii() and character.isalpha():
        return "latin"
    if not character.isalnum():
        return "punctuation"
    return "other"


def symbolic_boundary_counts(
    record: MsgGameRecord,
    components: tuple[dict[str, Any], ...],
) -> Counter[str]:
    literal_text = {
        f"{record.block_id}:{record.record_id}:{literal.literal_id}": literal.text
        for literal in parse_record_literals(record)
    }
    visible: list[tuple[str, str | None, str | None]] = []
    for component in components:
        kind = component["kind"]
        if kind == "literal":
            text = literal_text[component["coordinate"]]
            if text:
                visible.append(("literal", text[0], text[-1]))
        elif kind in {"dynamic_expression", "call"}:
            visible.append(("dynamic" if kind == "dynamic_expression" else "call", None, None))
    counts: Counter[str] = Counter()
    for left, right in zip(visible, visible[1:]):
        left_kind, _left_first, left_last = left
        right_kind, right_first, _right_last = right
        boundary_character = left_last if left_last is not None else right_first
        boundary_class = surface_class(boundary_character) if boundary_character else "runtime_value"
        counts[f"{left_kind}>{right_kind}:{boundary_class}"] += 1
    return counts


def row_verification_payload(
    row: PendingRow,
    record_template_sha256: str,
    candidate_record_raw_sha256: str,
) -> dict[str, str]:
    return {
        "coordinate": row.coordinate,
        "source_record_raw_sha256": row.record_sha256,
        "current_ko_utf16le_sha256": row.current_text_sha256,
        "translation_utf16le_sha256": sha256_bytes(row.translation.encode("utf-16-le")),
        "record_template_sha256": record_template_sha256,
        "candidate_record_raw_sha256": candidate_record_raw_sha256,
    }


def build_report(
    rows: list[PendingRow],
    source_records: dict[tuple[int, int], MsgGameRecord],
    current_records: dict[tuple[int, int], MsgGameRecord],
    candidate_records: dict[tuple[int, int], MsgGameRecord],
    contract: dict[str, Any],
    *,
    source_blob_sha256: str,
    current_blob_sha256: str,
    candidate_blob_sha256: str,
) -> dict[str, Any]:
    require(len(rows) == EXPECTED["pending_rows"], "Base pending row universe drifted")
    rows_by_record: dict[tuple[int, int], list[PendingRow]] = defaultdict(list)
    for row in rows:
        key = (row.block_id, row.record_id)
        require(key in source_records, f"pending source record is absent: {row.coordinate}")
        require(key in current_records, f"pending current record is absent: {row.coordinate}")
        require(key in candidate_records, f"pending candidate record is absent: {row.coordinate}")
        source_record = source_records[key]
        require(
            sha256_bytes(source_record.data) == row.record_sha256,
            f"pristine record guard drifted: {row.coordinate}",
        )
        source_literals = parse_record_literals(source_record)
        current_literals = parse_record_literals(current_records[key])
        candidate_literals = parse_record_literals(candidate_records[key])
        require(row.literal_id < len(source_literals), f"source literal index is outside: {row.coordinate}")
        require(row.literal_id < len(current_literals), f"current literal index is outside: {row.coordinate}")
        require(row.literal_id < len(candidate_literals), f"candidate literal index is outside: {row.coordinate}")
        require(
            sha256_bytes(current_literals[row.literal_id].text.encode("utf-16-le"))
            == row.current_text_sha256,
            f"current Korean literal guard drifted: {row.coordinate}",
        )
        require(
            candidate_literals[row.literal_id].text == row.translation,
            f"candidate translation was not applied exactly: {row.coordinate}",
        )
        rows_by_record[key].append(row)
    require(len(rows_by_record) == EXPECTED["pending_records"], "Base pending record universe drifted")

    cluster_records: Counter[str] = Counter()
    cluster_literals: Counter[str] = Counter()
    token_forms: Counter[str] = Counter()
    selector_families: Counter[str] = Counter()
    call_count = 0
    jump_count = 0
    call_roots: list[int] = []
    expression_chain_count = 0
    decoded_gap_count = 0
    decoded_component_count = 0
    signature_counts: Counter[str] = Counter()
    representative_coordinate: dict[str, str] = {}

    for key, record_rows in sorted(rows_by_record.items()):
        record = candidate_records[key]
        cluster = classify_record(record, len(record_rows))
        cluster_records[cluster] += 1
        cluster_literals[cluster] += len(record_rows)
        representative_coordinate.setdefault(cluster, record_rows[0].coordinate)
        signature_counts[masked_record_signature(record)] += 1
        for gap in literal_gaps(record):
            decoded_gap_count += 1
            decoded = decode_gap(gap)
            decoded_component_count += len(decoded)
            for component in decoded:
                if component["kind"] == "call":
                    call_count += 1
                    block_id, record_id = component["target"]
                    call_roots.append(block_id * 10_000 + record_id)
                elif component["kind"] == "jump":
                    jump_count += 1
                elif component["kind"] == "dynamic_expression":
                    expression_chain_count += bool(component["operators"])
                    for atom in component["atoms"]:
                        token = bytes.fromhex(atom["raw_hex"])
                        token_forms[atom["raw_hex"]] += 1
                        group_slot = selector_group(token[1])
                        require(group_slot is not None, f"unclassified selector: {token.hex()}")
                        group, slot = group_slot
                        selector_families[f"group_{group:02d}_slot_{slot:02d}"] += 1

    actual_clusters = {
        name: (cluster_records[name], cluster_literals[name])
        for name in EXPECTED["clusters"]
    }
    require(actual_clusters == EXPECTED["clusters"], f"record clusters drifted: {actual_clusters}")
    require(call_count == EXPECTED["0143_occurrences"], f"0143 count drifted: {call_count}")
    require(sum(token_forms.values()) == EXPECTED["02_occurrences"], "02 token count drifted")
    require(len(selector_families) == EXPECTED["02_selector_families"], "02 selector family count drifted")
    require(len(token_forms) == EXPECTED["02_slot_forms"], "02 slot form count drifted")

    empty_rows = [row for row in rows if row.empty_runtime_morpheme]
    require(len(empty_rows) == EXPECTED["empty_runtime_morphemes"], "empty runtime morpheme universe drifted")
    neutral_counts = Counter(
        NEUTRAL_PARTICLE_LABELS[particle]
        for row in rows
        for particle in NEUTRAL_PARTICLES
        if particle in row.translation
    )
    neutral_union = sum(any(particle in row.translation for particle in NEUTRAL_PARTICLES) for row in rows)
    require(neutral_union == EXPECTED["neutral_particle_rows"], "neutral-particle row universe drifted")

    graph = control_flow_graph(candidate_records, call_roots)
    expected_graph = EXPECTED["control_graph"]
    require(graph["root_count"] == expected_graph["roots"], "0143 root universe drifted")
    require(
        graph["reachable_record_count"] == expected_graph["reachable_records"],
        "reachable record universe drifted",
    )
    require(
        graph["014a_edge_occurrence_count"] == expected_graph["jump_edge_occurrences"],
        "014A graph edge universe drifted",
    )
    require(
        graph["nested_0143_edge_occurrence_count"]
        == expected_graph["nested_call_edge_occurrences"],
        "nested 0143 graph edge universe drifted",
    )

    template_guards: dict[str, dict[str, str]] = {}
    row_guards: dict[str, str] = {}
    template_digest_source: list[dict[str, str]] = []
    boundary_counts: Counter[str] = Counter()
    for key, record_rows in sorted(rows_by_record.items()):
        record = candidate_records[key]
        components = record_symbolic_components(record, graph["call_target_guards"])
        template_sha256 = sha256_bytes(compact_json_bytes(components))
        candidate_record_sha256 = sha256_bytes(record.data)
        record_key = f"{key[0]}:{key[1]}"
        template_guards[record_key] = {
            "template_sha256": template_sha256,
            "candidate_record_raw_sha256": candidate_record_sha256,
        }
        template_digest_source.append(
            {
                "record": record_key,
                "template_sha256": template_sha256,
                "candidate_record_raw_sha256": candidate_record_sha256,
            }
        )
        boundary_counts.update(symbolic_boundary_counts(record, components))
        literal_coordinates = {
            component["coordinate"]
            for component in components
            if component["kind"] == "literal"
        }
        for row in record_rows:
            require(row.coordinate in literal_coordinates, f"row is absent from template: {row.coordinate}")
            payload = row_verification_payload(row, template_sha256, candidate_record_sha256)
            row_guards[row.coordinate] = sha256_bytes(compact_json_bytes(payload))
    require(len(template_guards) == len(rows_by_record), "record template guard coverage drifted")
    require(len(row_guards) == len(rows), "row verification guard coverage drifted")

    contract_sha256 = sha256_bytes(canonical_json(contract).encode("utf-8"))
    rows_digest = sha256_bytes(
        "\n".join(
            f"{coordinate}:{row_guards[coordinate]}"
            for coordinate in sorted(row_guards, key=lambda value: tuple(map(int, value.split(":"))))
        ).encode("ascii")
    )
    template_digest = sha256_bytes(compact_json_bytes(template_digest_source))

    return {
        "schema": SCHEMA,
        "status": "PASS",
        "scope": {
            "resource": "MSG/JP/msggame.bin",
            "runtime_pending_rows": len(rows),
            "runtime_pending_records": len(rows_by_record),
            "semantic_review_approved_rows": len(rows),
            "symbolic_candidate_template_covered_rows": len(rows),
            "runtime_structurally_verified_rows": len(rows),
            "runtime_automatically_verified_rows": len(rows),
            "per_row_game_playback_required": 0,
        },
        "candidate_build": {
            "pristine_jp_packed_sha256": source_blob_sha256,
            "current_ko_packed_sha256": current_blob_sha256,
            "fully_decided_candidate_packed_sha256": candidate_blob_sha256,
            "runtime_structure_source": "current_ko_msggame_bytecode_with_all_decision_literals_overlaid",
            "pristine_jp_use": "source_record_guard_and_semantic_reference_only",
        },
        "ghidra_contract": {
            "path": "workstreams/base_msggame_runtime_vm_audit_v1/ghidra_vm_contract.v1.json",
            "sha256": contract_sha256,
            "base_msggame_route_proved": (
                contract["message_route_proof"]["base_msggame"]["loader"] == "0x1409F8710"
                and contract["message_route_proof"]["base_msggame"]["vtable_evaluator"]
                == "0x1409F7490"
            ),
            "no_implicit_space_proved": contract["opcode_contract"]["02"]["automatic_space_inserted"] is False,
            "no_implicit_punctuation_proved": (
                contract["opcode_contract"]["02"]["automatic_punctuation_inserted"] is False
            ),
        },
        "record_clusters": {
            name: {
                "record_count": cluster_records[name],
                "literal_count": cluster_literals[name],
                "representative_coordinate": representative_coordinate[name],
            }
            for name in EXPECTED["clusters"]
        },
        "opcode_coverage": {
            "0143_call_occurrences": call_count,
            "014a_jump_occurrences_in_pending_records": jump_count,
            "02_dynamic_value_occurrences": sum(token_forms.values()),
            "02_selector_family_count": len(selector_families),
            "02_slot_form_count": len(token_forms),
            "02_expression_chain_occurrences": expression_chain_count,
            "exact_decoded_pending_record_count": len(rows_by_record),
            "exact_decoded_literal_gap_count": decoded_gap_count,
            "exact_decoded_component_count": decoded_component_count,
            "unknown_pending_gap_byte_count": 0,
            "masked_record_signature_count": len(signature_counts),
            "all_02_selectors_in_reversed_dispatch_table": (
                len(selector_families) == EXPECTED["02_selector_families"]
            ),
            "all_0143_targets_valid": graph["root_count"] == EXPECTED["control_graph"]["roots"],
            "all_reachable_014a_targets_valid": (
                graph["014a_edge_occurrence_count"]
                == EXPECTED["control_graph"]["jump_edge_occurrences"]
            ),
            "all_nested_0143_targets_valid": (
                graph["nested_0143_edge_occurrence_count"]
                == EXPECTED["control_graph"]["nested_call_edge_occurrences"]
            ),
        },
        "reachable_control_flow_graph": graph,
        "selector_families": dict(sorted(selector_families.items())),
        "selector_forms": dict(sorted(token_forms.items())),
        "symbolic_boundaries": {
            "ordered_output_boundary_counts": dict(sorted(boundary_counts.items())),
            "all_candidate_records_have_template_guards": len(template_guards) == len(rows_by_record),
            "all_pending_rows_have_exact_translation_bound_guards": len(row_guards) == len(rows),
        },
        "korean_boundary_risks": {
            "neutral_particle_row_count": neutral_union,
            "neutral_particle_occurrences": dict(sorted(neutral_counts.items())),
            "empty_runtime_morpheme_count": len(empty_rows),
            "empty_runtime_morpheme_kind_counts": dict(
                sorted(Counter(row.empty_runtime_morpheme_kind for row in empty_rows).items())
            ),
            "automatic_separator_absence_makes_boundaries_literal_owned": True,
        },
        "adjudication": {
            "runtime_review_result": "verified_by_reversed_vm_and_symbolic_candidate_template",
            "semantic_translation_review_reused": "approved",
            "layout_review_reused": "unchanged_from_current",
            "manual_game_qa_scope": "representative_smoke_tests_only",
            "manual_game_qa_not_per_row": True,
        },
        "guards": {
            "pending_universe_digest_sha256": rows_digest,
            "pending_coordinate_and_translation_digest_sha256": rows_digest,
            "candidate_record_template_universe_sha256": template_digest,
            "record_template_guards": template_guards,
            "row_verification_guards": row_guards,
            "record_hash_guards_all_match": True,
            "current_literal_hash_guards_all_match": True,
            "candidate_translations_all_match": True,
            "cluster_counts_pinned": True,
            "selector_counts_pinned": True,
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_translated_dialogue_text": False,
            "contains_complete_game_resource": False,
            "contains_only_counts_hashes_coordinates_and_opcode_forms": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--base-msggame", type=Path, default=DEFAULT_BASE_MSGGAME)
    parser.add_argument("--current-base-msggame", type=Path, default=DEFAULT_CURRENT_BASE_MSGGAME)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="verify the tracked report without rewriting it")
    args = parser.parse_args()

    contract = load_json(GHIDRA_CONTRACT)
    require(contract.get("schema") == "nobu16.kr.base-msggame-runtime-vm-ghidra-contract.v1", "contract schema drifted")
    rows = load_pending_rows(args.decisions)
    decision_rows = load_base_decision_rows(args.decisions)
    source_records = archive_records(args.base_msggame)
    current_records = archive_records(args.current_base_msggame)
    candidate_records, current_blob_sha256, candidate_blob_sha256 = build_candidate_records(
        args.current_base_msggame,
        decision_rows,
    )
    report = build_report(
        rows,
        source_records,
        current_records,
        candidate_records,
        contract,
        source_blob_sha256=sha256_bytes(args.base_msggame.read_bytes()),
        current_blob_sha256=current_blob_sha256,
        candidate_blob_sha256=candidate_blob_sha256,
    )
    content = canonical_json(report)
    if args.check:
        require(args.output.is_file(), f"tracked report is absent: {args.output}")
        require(args.output.read_text(encoding="utf-8") == content, "tracked runtime coverage report drifted")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8", newline="\n")
    print(
        f"PASS rows={report['scope']['runtime_automatically_verified_rows']} "
        f"records={report['scope']['runtime_pending_records']} "
        f"selectors={report['opcode_coverage']['02_selector_family_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
