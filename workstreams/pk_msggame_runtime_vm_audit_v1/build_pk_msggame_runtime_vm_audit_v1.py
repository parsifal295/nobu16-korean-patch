#!/usr/bin/env python3
"""Audit Base-exact PK dialogue reuse against the actual PK msggame VM.

The audit never promotes from a regex-masked byte pattern.  It decodes every
literal boundary and VM component in each paired root, follows the actual
0143/014A operands in Base and PK, and compares the resulting closures without
assuming a coordinate delta.  Public output contains coordinates, hashes,
counts, opcode forms, and taint labels only.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
SHADOW_STEAM_ROOT = (
    DIALOGUE_TMP
    / "development_steam_root_pre_base_runtime_apply_13a404f"
)

DEFAULT_PREFILL = (
    DIALOGUE_TMP
    / "decisions"
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
DEFAULT_PREFILL_REPORT = (
    DIALOGUE_WORKSTREAM / "pk_base_exact_reuse_prefill.source_free.v1.json"
)
DEFAULT_BASE_PROMOTED = (
    DIALOGUE_TMP / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
DEFAULT_BASE_PRISTINE = (
    REPO.parent.parent
    / "private-inputs"
    / "legacy-pc-root"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_BASE_CURRENT = SHADOW_STEAM_ROOT / "MSG" / "JP" / "msggame.bin"
DEFAULT_PK_PRISTINE = (
    SHADOW_STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
DEFAULT_PK_CURRENT = SHADOW_STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin"
BASE_COVERAGE = (
    REPO
    / "workstreams"
    / "base_msggame_runtime_vm_audit_v1"
    / "public"
    / "base_msggame_runtime_vm_coverage.v1.json"
)
GHIDRA_CONTRACT = WORKSTREAM / "ghidra_pk_vm_contract.v1.json"
DEFAULT_OUTPUT = WORKSTREAM / "public" / "pk_msggame_runtime_vm_coverage.v1.json"

sys.path[:0] = [str(REPO / "tools"), str(REPO / "workstreams" / "msggame")]

from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
)


SCHEMA = "nobu16.kr.pk-msggame-runtime-vm-coverage.v1"
CONTRACT_SCHEMA = "nobu16.kr.pk-msggame-runtime-vm-ghidra-contract.v1"
PREFILL_SCHEMA = "nobu16.kr.pk-msggame-base-exact-reuse-prefill.v1"
ROW_EVIDENCE_SCHEMA = "nobu16.kr.pk-msggame-base-exact-reuse-row-prefill.v1"
EXPECTED_PREFILLED_ROWS = 17_652
EXPECTED_PENDING_ROWS = 9_770
MAX_RECORD_OPERAND = 1_999_999
BLOCK_TOKEN_CODES = frozenset(range(0x04, 0x0A))
ARITHMETIC_OPERATORS = frozenset(b"%*+-/")
COMPARISON_OPERATORS = frozenset(b"!<=>")
LOGICAL_OPERATORS = frozenset(b"&|")
CONTROL_TAG_PAYLOAD_SUBCODES = frozenset((0x43, 0x45, 0x50, 0x57))


class AuditError(ValueError):
    """Raised when a PK runtime audit invariant is not proved."""


@dataclass(frozen=True)
class AuditInputs:
    rows: tuple[dict[str, Any], ...]
    prefill_report: dict[str, Any]
    contract: dict[str, Any]
    base_coverage: dict[str, Any]
    base_coverage_sha256: str
    base_promoted_rows: Mapping[str, dict[str, Any]]
    base_source_records: Mapping[tuple[int, int], MsgGameRecord]
    base_candidate_records: Mapping[tuple[int, int], MsgGameRecord]
    pk_source_records: Mapping[tuple[int, int], MsgGameRecord]
    pk_current_records: Mapping[tuple[int, int], MsgGameRecord]
    pk_candidate_records: Mapping[tuple[int, int], MsgGameRecord]
    artifact_hashes: Mapping[str, str]


@dataclass(frozen=True)
class PairAudit:
    base_root: tuple[int, int]
    pk_root: tuple[int, int]
    taints: tuple[str, ...]
    reason_codes: tuple[str, ...]
    visited_pairs: tuple[tuple[tuple[int, int], tuple[int, int]], ...]
    proof_sha256: str
    call_occurrences: int
    jump_occurrences: int

    @property
    def eligible(self) -> bool:
        return not self.taints


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def compact_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(compact_json_bytes(value))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"required JSON is absent: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"required JSONL is absent: {path}")
    result: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        value = json.loads(line)
        require(isinstance(value, dict), f"{path}:{line_number} is not an object")
        result.append(value)
    return result


def parse_literal_coordinate(value: Any) -> tuple[int, int, int]:
    require(isinstance(value, str), "literal coordinate must be a string")
    parts = value.split(":")
    require(
        len(parts) == 3 and all(part.isdigit() for part in parts),
        f"invalid literal coordinate: {value}",
    )
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def parse_record_coordinate(value: Any) -> tuple[int, int]:
    block_id, record_id, _literal_id = parse_literal_coordinate(value)
    return block_id, record_id


def record_key(value: tuple[int, int]) -> str:
    return f"{value[0]}:{value[1]}"


def pair_key(base: tuple[int, int], pk: tuple[int, int]) -> str:
    return f"{base[0]}:{base[1]}->{pk[0]}:{pk[1]}"


def archive_records(path: Path) -> tuple[dict[tuple[int, int], MsgGameRecord], str]:
    require(path.is_file(), f"msggame input is absent: {path}")
    blob = path.read_bytes()
    archive = parse_packed_msggame(blob).archive
    return (
        {
            (record.block_id, record.record_id): record
            for block in archive.blocks
            for record in block.records
        },
        sha256_bytes(blob),
    )


def records_from_blob(blob: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    archive = parse_packed_msggame(blob).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def literal_gaps(record: MsgGameRecord) -> tuple[bytes, ...]:
    gaps: list[bytes] = []
    cursor = 0
    for literal in parse_record_literals(record):
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
    require(cursor + 2 <= len(gap), "truncated 02 selector atom")
    require(gap[cursor] == 0x02, "selector atom does not start with 02")
    selector = gap[cursor + 1]
    classified = selector_group(selector)
    require(classified is not None, f"unclassified selector 0x{selector:02X}")
    end = cursor + 2
    property_byte: int | None = None
    if end < len(gap) and gap[end] >= 0x20:
        property_byte = gap[end]
        end += 1
    group, slot = classified
    return (
        {
            "kind": "selector",
            "group": group,
            "slot": slot,
            "property": property_byte,
            "raw_hex": gap[cursor:end].hex().upper(),
        },
        end,
    )


def decode_gap(gap: bytes) -> tuple[dict[str, Any], ...]:
    """Decode a complete nonliteral gap without regex operand discovery."""
    components: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(gap):
        if (
            cursor + 3 <= len(gap)
            and gap[cursor : cursor + 2] == b"\x05\x05"
            and gap[cursor + 2] in BLOCK_TOKEN_CODES
        ):
            components.append(
                {
                    "kind": "block_token",
                    "code": gap[cursor + 2],
                    "raw_hex": gap[cursor : cursor + 3].hex().upper(),
                }
            )
            cursor += 3
            continue

        opcode = gap[cursor]
        if opcode == 0x01:
            require(cursor + 2 <= len(gap), "truncated 01 command")
            subcode = gap[cursor + 1]
            if subcode in (0x43, 0x4A):
                require(cursor + 6 <= len(gap), f"truncated 01{subcode:02X} command")
                operand = struct.unpack_from("<I", gap, cursor + 2)[0]
                components.append(
                    {
                        "kind": "call" if subcode == 0x43 else "jump",
                        "operand": operand,
                        "target": [operand // 10_000, operand % 10_000],
                        "raw_hex": gap[cursor : cursor + 6].hex().upper(),
                    }
                )
                cursor += 6
                continue
            if subcode in (0x46, 0x4D):
                components.append(
                    {
                        "kind": "command",
                        "subcode": subcode,
                        "raw_hex": gap[cursor : cursor + 2].hex().upper(),
                    }
                )
                cursor += 2
                continue
            if subcode == 0x53:
                start = cursor
                cursor += 2
                require(
                    cursor < len(gap) and gap[cursor] == ord("%"),
                    "0153 has no percent-prefixed alternative count",
                )
                cursor += 1
                digit_start = cursor
                while cursor < len(gap) and ord("0") <= gap[cursor] <= ord("9"):
                    cursor += 1
                require(cursor > digit_start, "0153 has no decimal alternative count")
                components.append(
                    {
                        "kind": "random_select",
                        "alternative_count": int(
                            gap[digit_start:cursor].decode("ascii")
                        ),
                        "raw_hex": gap[start:cursor].hex().upper(),
                    }
                )
                continue
            raise AuditError(f"unsupported 01 command 0x{subcode:02X}")

        if opcode == 0x02:
            component, cursor = parse_selector_atom(gap, cursor)
            components.append(component)
            continue

        if opcode == 0x03:
            require(cursor + 2 <= len(gap), "truncated arithmetic operator")
            operator = gap[cursor + 1]
            require(
                operator in ARITHMETIC_OPERATORS,
                f"unsupported arithmetic operator 0x{operator:02X}",
            )
            components.append(
                {
                    "kind": "arithmetic_operator",
                    "operator": chr(operator),
                    "raw_hex": gap[cursor : cursor + 2].hex().upper(),
                }
            )
            cursor += 2
            continue

        if opcode == 0x04:
            require(cursor + 2 <= len(gap), "truncated comparison operator")
            operator = gap[cursor + 1]
            require(
                operator in COMPARISON_OPERATORS,
                f"unsupported comparison operator 0x{operator:02X}",
            )
            components.append(
                {
                    "kind": "comparison_operator",
                    "operator": chr(operator),
                    "raw_hex": gap[cursor : cursor + 2].hex().upper(),
                }
            )
            cursor += 2
            continue

        if opcode == 0x06:
            require(cursor + 2 <= len(gap), "truncated logical operator")
            operator = gap[cursor + 1]
            require(
                operator in LOGICAL_OPERATORS,
                f"unsupported logical operator 0x{operator:02X}",
            )
            components.append(
                {
                    "kind": "logical_operator",
                    "operator": chr(operator),
                    "raw_hex": gap[cursor : cursor + 2].hex().upper(),
                }
            )
            cursor += 2
            continue

        if ord("0") <= opcode <= ord("9"):
            digit_start = cursor
            while cursor < len(gap) and ord("0") <= gap[cursor] <= ord("9"):
                cursor += 1
            components.append(
                {
                    "kind": "decimal_atom",
                    "digits": gap[digit_start:cursor].decode("ascii"),
                    "raw_hex": gap[digit_start:cursor].hex().upper(),
                }
            )
            continue

        if opcode == ord("%"):
            atom_start = cursor
            cursor += 1
            digit_start = cursor
            while cursor < len(gap) and ord("0") <= gap[cursor] <= ord("9"):
                cursor += 1
            require(cursor > digit_start, "percent numeric atom has no decimal digits")
            components.append(
                {
                    "kind": "percent_decimal_atom",
                    "digits": gap[digit_start:cursor].decode("ascii"),
                    "raw_hex": gap[atom_start:cursor].hex().upper(),
                }
            )
            continue

        if opcode == 0x1B:
            require(cursor + 2 <= len(gap), "truncated 1B control tag")
            subcode = gap[cursor + 1]
            end = cursor + 2
            if subcode in CONTROL_TAG_PAYLOAD_SUBCODES:
                require(end < len(gap), "truncated 1B control-tag payload")
                end += 1
            components.append(
                {
                    "kind": "control_tag",
                    "raw_hex": gap[cursor:end].hex().upper(),
                }
            )
            cursor = end
            continue

        if opcode in (0x08, 0x09, 0x0A):
            components.append(
                {
                    "kind": "output_control",
                    "code": opcode,
                    "raw_hex": f"{opcode:02X}",
                }
            )
            cursor += 1
            continue

        raise AuditError(
            f"unknown VM gap byte 0x{opcode:02X} at {cursor} in {gap.hex().upper()}"
        )
    return tuple(components)


def decode_record(record: MsgGameRecord) -> tuple[dict[str, Any], ...]:
    components: list[dict[str, Any]] = []
    literals = parse_record_literals(record)
    gaps = literal_gaps(record)
    for literal_id, _literal in enumerate(literals):
        components.extend(decode_gap(gaps[literal_id]))
        components.append({"kind": "literal_boundary", "slot": literal_id})
    components.extend(decode_gap(gaps[-1]))
    return tuple(components)


def structural_component(component: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(component)
    if value.get("kind") in {"call", "jump"}:
        value.pop("operand", None)
        value.pop("target", None)
        value.pop("raw_hex", None)
    return value


def component_reason(component: Mapping[str, Any] | None) -> str:
    if component is None:
        return "component_count"
    kind = component.get("kind")
    if kind == "literal_boundary":
        return "literal_boundary"
    if kind == "selector":
        return "selector_property_or_slot"
    if kind in {"call", "jump"}:
        return "control_edge_kind_or_order"
    return "vm_component"


def compare_record_pair(
    base_root: tuple[int, int],
    pk_root: tuple[int, int],
    *,
    base_source_records: Mapping[tuple[int, int], MsgGameRecord],
    base_candidate_records: Mapping[tuple[int, int], MsgGameRecord],
    pk_source_records: Mapping[tuple[int, int], MsgGameRecord],
    pk_candidate_records: Mapping[tuple[int, int], MsgGameRecord],
) -> PairAudit:
    """Compare one explicit Base/PK root and its synchronized actual closure."""
    queue: deque[tuple[tuple[int, int], tuple[int, int], int]] = deque(
        [(base_root, pk_root, 0)]
    )
    seen: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    base_to_pk: dict[tuple[int, int], tuple[int, int]] = {}
    pk_to_base: dict[tuple[int, int], tuple[int, int]] = {}
    reason_codes: set[str] = set()
    taints: set[str] = set()
    proof_records: list[dict[str, Any]] = []
    proof_edges: list[dict[str, Any]] = []
    call_occurrences = 0
    jump_occurrences = 0

    def taint(depth: int, category: str, reason: str) -> None:
        if depth:
            taints.add("closure_taint")
            reason_codes.add(f"closure_{reason}")
        else:
            taints.add(category)
            reason_codes.add(reason)

    while queue:
        base_coordinate, pk_coordinate, depth = queue.popleft()
        pair = (base_coordinate, pk_coordinate)
        if pair in seen:
            continue
        if (
            base_coordinate in base_to_pk
            and base_to_pk[base_coordinate] != pk_coordinate
        ) or (
            pk_coordinate in pk_to_base
            and pk_to_base[pk_coordinate] != base_coordinate
        ):
            taints.add("closure_taint")
            reason_codes.add("closure_pair_conflict")
            continue
        base_to_pk[base_coordinate] = pk_coordinate
        pk_to_base[pk_coordinate] = base_coordinate
        seen.add(pair)

        if (
            base_coordinate not in base_source_records
            or base_coordinate not in base_candidate_records
            or pk_coordinate not in pk_source_records
            or pk_coordinate not in pk_candidate_records
        ):
            taint(depth, "novel_taint", "target_missing")
            continue

        base_source = base_source_records[base_coordinate]
        base_candidate = base_candidate_records[base_coordinate]
        pk_source = pk_source_records[pk_coordinate]
        pk_candidate = pk_candidate_records[pk_coordinate]
        try:
            base_components = decode_record(base_candidate)
            pk_components = decode_record(pk_candidate)
        except AuditError:
            taint(depth, "novel_taint", "exact_decode_failure")
            continue

        proof_records.append(
            {
                "base_coordinate": list(base_coordinate),
                "pk_coordinate": list(pk_coordinate),
                "base_source_record_sha256": sha256_bytes(base_source.data),
                "pk_source_record_sha256": sha256_bytes(pk_source.data),
                "base_candidate_record_sha256": sha256_bytes(base_candidate.data),
                "pk_candidate_record_sha256": sha256_bytes(pk_candidate.data),
                "base_component_sha256": canonical_sha256(
                    [structural_component(value) for value in base_components]
                ),
                "pk_component_sha256": canonical_sha256(
                    [structural_component(value) for value in pk_components]
                ),
            }
        )

        if len(base_components) != len(pk_components):
            taint(depth, "novel_taint", "component_count")
            continue

        base_source_literals = parse_record_literals(base_source)
        pk_source_literals = parse_record_literals(pk_source)
        base_candidate_literals = parse_record_literals(base_candidate)
        pk_candidate_literals = parse_record_literals(pk_candidate)
        for occurrence, (base_component, pk_component) in enumerate(
            zip(base_components, pk_components)
        ):
            if base_component["kind"] != pk_component["kind"]:
                taint(
                    depth,
                    "novel_taint",
                    component_reason(base_component),
                )
                continue

            kind = base_component["kind"]
            if kind in {"call", "jump"}:
                if structural_component(base_component) != structural_component(
                    pk_component
                ):
                    taint(depth, "novel_taint", "control_edge_kind_or_order")
                    continue
                base_operand = int(base_component["operand"])
                pk_operand = int(pk_component["operand"])
                if (
                    base_operand > MAX_RECORD_OPERAND
                    or pk_operand > MAX_RECORD_OPERAND
                ):
                    taint(depth, "novel_taint", "operand_range")
                    continue
                base_target = tuple(base_component["target"])
                pk_target = tuple(pk_component["target"])
                if (
                    base_target not in base_candidate_records
                    or pk_target not in pk_candidate_records
                ):
                    taint(depth, "novel_taint", "target_missing")
                    continue
                proof_edges.append(
                    {
                        "source_pair": pair_key(base_coordinate, pk_coordinate),
                        "occurrence": occurrence,
                        "kind": kind,
                        "base_operand": base_operand,
                        "pk_operand": pk_operand,
                        "base_target": list(base_target),
                        "pk_target": list(pk_target),
                    }
                )
                if kind == "call":
                    call_occurrences += 1
                else:
                    jump_occurrences += 1
                queue.append((base_target, pk_target, depth + 1))
                continue

            if kind == "literal_boundary":
                if base_component != pk_component:
                    taint(depth, "novel_taint", "literal_boundary")
                    continue
                slot = int(base_component["slot"])
                if (
                    slot >= len(base_source_literals)
                    or slot >= len(pk_source_literals)
                    or slot >= len(base_candidate_literals)
                    or slot >= len(pk_candidate_literals)
                ):
                    taint(depth, "novel_taint", "literal_boundary")
                    continue
                if (
                    base_source_literals[slot].text
                    != pk_source_literals[slot].text
                ):
                    taint(depth, "sibling_taint", "sibling_source_mismatch")
                if (
                    base_candidate_literals[slot].text
                    != pk_candidate_literals[slot].text
                ):
                    taint(
                        depth,
                        "sibling_taint",
                        "sibling_candidate_mismatch",
                    )
                continue

            if structural_component(base_component) != structural_component(
                pk_component
            ):
                taint(
                    depth,
                    "novel_taint",
                    component_reason(base_component),
                )

    proof_source = {
        "base_root": list(base_root),
        "pk_root": list(pk_root),
        "records": sorted(
            proof_records,
            key=lambda value: (
                value["base_coordinate"],
                value["pk_coordinate"],
            ),
        ),
        "edges": sorted(
            proof_edges,
            key=lambda value: (
                value["source_pair"],
                value["occurrence"],
                value["kind"],
            ),
        ),
        "taints": sorted(taints),
        "reason_codes": sorted(reason_codes),
    }
    return PairAudit(
        base_root=base_root,
        pk_root=pk_root,
        taints=tuple(sorted(taints)),
        reason_codes=tuple(sorted(reason_codes)),
        visited_pairs=tuple(sorted(seen)),
        proof_sha256=canonical_sha256(proof_source),
        call_occurrences=call_occurrences,
        jump_occurrences=jump_occurrences,
    )


def verify_contract(contract: Mapping[str, Any]) -> None:
    require(contract.get("schema") == CONTRACT_SCHEMA, "PK Ghidra contract schema drifted")
    route = contract.get("pk_message_route_proof")
    require(isinstance(route, dict), "PK route proof is absent")
    locales = route.get("locale_directories")
    require(
        isinstance(locales, dict)
        and locales.get("JP", {}).get("string") == "MSG_PK/JP"
        and locales.get("JP", {}).get("address") == "0x14154C908",
        "PK JP locale route drifted",
    )
    binding = route.get("loaded_object_binding")
    require(isinstance(binding, dict), "PK object binding is absent")
    slots = binding.get("vtable_slots")
    require(
        isinstance(slots, dict)
        and slots.get("+0x08") == "0x1409F8710"
        and slots.get("+0x18") == "0x1409F7490",
        "PK loader/evaluator vtable binding drifted",
    )
    require(
        route.get("path_construction", {}).get("jp_result")
        == "MSG_PK/JP/msggame.bin",
        "PK msggame path conclusion drifted",
    )
    reuse = contract.get("reuse_adjudication_contract")
    require(
        isinstance(reuse, dict)
        and "raw regex operand masking" in reuse.get("forbidden_shortcuts", []),
        "regex shortcut prohibition is absent",
    )


def validate_row_binding(
    row: Mapping[str, Any],
    *,
    prefill_report: Mapping[str, Any],
    base_promoted_rows: Mapping[str, dict[str, Any]],
    base_coverage: Mapping[str, Any],
    base_source_records: Mapping[tuple[int, int], MsgGameRecord],
    base_candidate_records: Mapping[tuple[int, int], MsgGameRecord],
    pk_source_records: Mapping[tuple[int, int], MsgGameRecord],
    pk_current_records: Mapping[tuple[int, int], MsgGameRecord],
    pk_candidate_records: Mapping[tuple[int, int], MsgGameRecord],
) -> dict[str, Any]:
    """Bind one pending row to its PK target, Base donor, and Base VM proof."""
    require(row.get("resource") == "pk_msggame", "prefill row mixes resources")
    require(row.get("runtime_review") == "pending", "audit row is not runtime pending")
    require(
        row.get("scope_classification") == "runtime_fragment_pending",
        "pending row scope drifted",
    )
    require(row.get("semantic_review") == "approved", "pending row is not approved")
    coordinate = row.get("coordinate")
    pk_block, pk_record, pk_literal = parse_literal_coordinate(coordinate)
    pk_key = (pk_block, pk_record)
    require(pk_key in pk_source_records, f"PK source record is absent: {coordinate}")
    require(pk_key in pk_current_records, f"PK current record is absent: {coordinate}")
    require(pk_key in pk_candidate_records, f"PK candidate record is absent: {coordinate}")
    require(
        sha256_bytes(pk_source_records[pk_key].data)
        == row.get("source_record_raw_sha256"),
        f"PK source record guard drifted: {coordinate}",
    )
    pk_source_literals = parse_record_literals(pk_source_records[pk_key])
    pk_current_literals = parse_record_literals(pk_current_records[pk_key])
    pk_candidate_literals = parse_record_literals(pk_candidate_records[pk_key])
    require(
        pk_literal < len(pk_source_literals)
        and pk_literal < len(pk_current_literals)
        and pk_literal < len(pk_candidate_literals),
        f"PK literal boundary drifted: {coordinate}",
    )
    require(
        sha256_bytes(pk_current_literals[pk_literal].text.encode("utf-16-le"))
        == row.get("current_ko_utf16le_sha256"),
        f"PK current literal guard drifted: {coordinate}",
    )
    translation = row.get("translation")
    require(isinstance(translation, str), f"PK translation is not a string: {coordinate}")
    require(
        pk_candidate_literals[pk_literal].text == translation,
        f"PK candidate translation drifted: {coordinate}",
    )

    evidence = row.get("base_exact_reuse_prefill")
    require(isinstance(evidence, dict), f"reuse evidence is absent: {coordinate}")
    require(
        evidence.get("schema") == ROW_EVIDENCE_SCHEMA,
        f"reuse evidence schema drifted: {coordinate}",
    )
    require(
        evidence.get("runtime_promotion_authorized") is False,
        f"prefill attempted an unauthorized promotion: {coordinate}",
    )
    require(
        evidence.get("mapping_universe_sha256")
        == prefill_report.get("mapping_universe_sha256"),
        f"mapping universe guard drifted: {coordinate}",
    )
    require(
        evidence.get("base_candidate_packed_sha256")
        == prefill_report.get("base_candidate_packed_sha256"),
        f"Base candidate guard drifted: {coordinate}",
    )
    source_hash = sha256_bytes(pk_source_literals[pk_literal].text.encode("utf-16-le"))
    translation_hash = sha256_bytes(translation.encode("utf-16-le"))
    require(
        evidence.get("source_utf16le_sha256") == source_hash,
        f"PK source literal hash drifted: {coordinate}",
    )
    require(
        evidence.get("translation_utf16le_sha256") == translation_hash,
        f"PK translation hash drifted: {coordinate}",
    )

    base_coordinate = evidence.get("base_coordinate")
    base_block, base_record, base_literal = parse_literal_coordinate(base_coordinate)
    base_key = (base_block, base_record)
    require(
        isinstance(base_coordinate, str) and base_coordinate in base_promoted_rows,
        f"Base donor decision is absent: {coordinate}",
    )
    donor_row = base_promoted_rows[base_coordinate]
    require(
        canonical_sha256(donor_row) == evidence.get("base_decision_sha256"),
        f"Base donor decision guard drifted: {coordinate}",
    )
    require(base_key in base_source_records, f"Base source donor is absent: {coordinate}")
    require(
        base_key in base_candidate_records,
        f"Base candidate donor is absent: {coordinate}",
    )
    require(
        sha256_bytes(base_source_records[base_key].data)
        == evidence.get("base_source_record_raw_sha256"),
        f"Base source donor record guard drifted: {coordinate}",
    )
    base_source_literals = parse_record_literals(base_source_records[base_key])
    base_candidate_literals = parse_record_literals(base_candidate_records[base_key])
    require(
        base_literal < len(base_source_literals)
        and base_literal < len(base_candidate_literals),
        f"Base donor literal boundary drifted: {coordinate}",
    )
    require(
        sha256_bytes(base_source_literals[base_literal].text.encode("utf-16-le"))
        == source_hash,
        f"Base donor source is not exact: {coordinate}",
    )
    require(
        base_candidate_literals[base_literal].text == translation,
        f"Base final donor translation drifted: {coordinate}",
    )
    base_guards = base_coverage.get("guards", {}).get("row_verification_guards", {})
    require(isinstance(base_guards, dict), "Base VM row-guard table is malformed")
    base_vm_row_guard = base_guards.get(base_coordinate)
    return {
        "coordinate": coordinate,
        "pk_record": pk_key,
        "pk_literal": pk_literal,
        "base_coordinate": base_coordinate,
        "base_record": base_key,
        "base_literal": base_literal,
        "translation_utf16le_sha256": translation_hash,
        "base_vm_row_guard": base_vm_row_guard,
        "layout_change_pending": evidence.get("layout_change_pending") is True,
        "prefill_global_masked_novel": (
            evidence.get("any_base_candidate_operand_masked_gap_template_match")
            is False
        ),
        "exact_donor_masked_mismatch": (
            evidence.get("exact_source_donor_operand_masked_template_match")
            is False
        ),
        "row_evidence_sha256": canonical_sha256(evidence),
    }


def build_inputs(
    *,
    prefill_path: Path = DEFAULT_PREFILL,
    prefill_report_path: Path = DEFAULT_PREFILL_REPORT,
    base_promoted_path: Path = DEFAULT_BASE_PROMOTED,
    base_pristine_path: Path = DEFAULT_BASE_PRISTINE,
    base_current_path: Path = DEFAULT_BASE_CURRENT,
    pk_pristine_path: Path = DEFAULT_PK_PRISTINE,
    pk_current_path: Path = DEFAULT_PK_CURRENT,
) -> AuditInputs:
    contract = read_json(GHIDRA_CONTRACT)
    verify_contract(contract)
    prefill_report = read_json(prefill_report_path)
    require(prefill_report.get("schema") == PREFILL_SCHEMA, "prefill report schema drifted")
    require(
        prefill_report.get("prefilled_rows") == EXPECTED_PREFILLED_ROWS,
        "prefill row universe drifted",
    )
    base_coverage = read_json(BASE_COVERAGE)
    base_coverage_sha256 = sha256_bytes(BASE_COVERAGE.read_bytes())

    all_rows = read_jsonl(prefill_path)
    require(len(all_rows) == EXPECTED_PREFILLED_ROWS, "private prefill row count drifted")
    rows = tuple(
        sorted(
            (
                row
                for row in all_rows
                if row.get("runtime_review") == "pending"
            ),
            key=lambda row: parse_literal_coordinate(row["coordinate"]),
        )
    )
    require(len(rows) == EXPECTED_PENDING_ROWS, "runtime-pending prefill universe drifted")

    base_promoted_list = read_jsonl(base_promoted_path)
    base_promoted_rows: dict[str, dict[str, Any]] = {}
    base_replacements: dict[tuple[int, int, int], str] = {}
    for row in base_promoted_list:
        coordinate = row.get("coordinate")
        parse_literal_coordinate(coordinate)
        require(
            isinstance(coordinate, str) and coordinate not in base_promoted_rows,
            f"duplicate Base promoted coordinate: {coordinate}",
        )
        base_promoted_rows[coordinate] = row
        translation = row.get("translation")
        if isinstance(translation, str):
            base_replacements[parse_literal_coordinate(coordinate)] = translation

    base_source_records, base_pristine_sha = archive_records(base_pristine_path)
    base_current_blob = base_current_path.read_bytes()
    base_current_sha = sha256_bytes(base_current_blob)
    base_candidate_blob = rebuild_packed_with_literals(
        base_current_blob,
        base_replacements,
    )
    base_candidate_sha = sha256_bytes(base_candidate_blob)
    require(
        base_candidate_sha == prefill_report.get("base_candidate_packed_sha256"),
        "completed Base candidate hash drifted",
    )
    base_candidate_records = records_from_blob(base_candidate_blob)

    pk_source_records, pk_pristine_sha = archive_records(pk_pristine_path)
    pk_current_blob = pk_current_path.read_bytes()
    pk_current_sha = sha256_bytes(pk_current_blob)
    pk_current_records = records_from_blob(pk_current_blob)
    pk_replacements = {
        parse_literal_coordinate(row["coordinate"]): row["translation"]
        for row in all_rows
        if isinstance(row.get("translation"), str)
    }
    pk_candidate_blob = rebuild_packed_with_literals(pk_current_blob, pk_replacements)
    pk_candidate_sha = sha256_bytes(pk_candidate_blob)
    require(
        pk_candidate_sha == prefill_report.get("candidate_packed_sha256"),
        "exact prefill PK candidate hash drifted",
    )
    pk_candidate_records = records_from_blob(pk_candidate_blob)

    return AuditInputs(
        rows=rows,
        prefill_report=prefill_report,
        contract=contract,
        base_coverage=base_coverage,
        base_coverage_sha256=base_coverage_sha256,
        base_promoted_rows=base_promoted_rows,
        base_source_records=base_source_records,
        base_candidate_records=base_candidate_records,
        pk_source_records=pk_source_records,
        pk_current_records=pk_current_records,
        pk_candidate_records=pk_candidate_records,
        artifact_hashes={
            "private_prefill_jsonl_sha256": sha256_bytes(prefill_path.read_bytes()),
            "prefill_report_sha256": sha256_bytes(prefill_report_path.read_bytes()),
            "base_promoted_jsonl_sha256": sha256_bytes(base_promoted_path.read_bytes()),
            "base_coverage_sha256": base_coverage_sha256,
            "base_pristine_packed_sha256": base_pristine_sha,
            "base_current_packed_sha256": base_current_sha,
            "base_candidate_packed_sha256": base_candidate_sha,
            "pk_pristine_packed_sha256": pk_pristine_sha,
            "pk_current_packed_sha256": pk_current_sha,
            "pk_candidate_packed_sha256": pk_candidate_sha,
            "ghidra_contract_sha256": sha256_bytes(GHIDRA_CONTRACT.read_bytes()),
        },
    )


def aggregate_opcode_coverage(
    pair_audits: Iterable[PairAudit],
    pk_records: Mapping[tuple[int, int], MsgGameRecord],
) -> dict[str, Any]:
    visited: set[tuple[int, int]] = set()
    for audit in pair_audits:
        visited.update(pk for _base, pk in audit.visited_pairs)
    kinds: Counter[str] = Counter()
    selector_forms: Counter[str] = Counter()
    block_tokens: Counter[str] = Counter()
    call_occurrences = 0
    jump_occurrences = 0
    for coordinate in sorted(visited):
        if coordinate not in pk_records:
            continue
        for component in decode_record(pk_records[coordinate]):
            kind = str(component["kind"])
            kinds[kind] += 1
            if kind == "selector":
                selector_forms[str(component["raw_hex"])] += 1
            elif kind == "block_token":
                block_tokens[str(component["raw_hex"])] += 1
            elif kind == "call":
                call_occurrences += 1
            elif kind == "jump":
                jump_occurrences += 1
    return {
        "exact_decoded_pk_record_count": len(visited),
        "component_kind_counts": dict(sorted(kinds.items())),
        "selector_forms": dict(sorted(selector_forms.items())),
        "block_token_forms": dict(sorted(block_tokens.items())),
        "0143_actual_operand_occurrences": call_occurrences,
        "014a_actual_operand_occurrences": jump_occurrences,
        "unknown_gap_byte_count": 0,
        "operand_discovery_method": "exact_vm_component_decoder",
        "raw_regex_operand_masking_used": False,
    }


def seal_report(report: dict[str, Any]) -> dict[str, Any]:
    sealed = copy.deepcopy(report)
    guards = sealed.setdefault("guards", {})
    require(isinstance(guards, dict), "report guards must be an object")
    guards.pop("report_payload_sha256", None)
    guards["report_payload_sha256"] = canonical_sha256(sealed)
    return sealed


def validate_report(report: Mapping[str, Any]) -> None:
    require(report.get("schema") == SCHEMA, "coverage report schema drifted")
    require(report.get("status") == "PASS", "coverage report is not PASS")
    guards = report.get("guards")
    require(isinstance(guards, dict), "coverage report guards are absent")
    expected_digest = guards.get("report_payload_sha256")
    unsealed = copy.deepcopy(dict(report))
    unsealed_guards = unsealed.get("guards")
    require(isinstance(unsealed_guards, dict), "coverage report guards are malformed")
    unsealed_guards.pop("report_payload_sha256", None)
    require(
        expected_digest == canonical_sha256(unsealed),
        "coverage report payload hash drifted",
    )

    adjudications = report.get("row_adjudications")
    require(isinstance(adjudications, dict), "row adjudications are absent")
    pair_guards = report.get("pair_proof_guards")
    require(isinstance(pair_guards, dict), "pair proof guards are absent")
    eligible_count = 0
    blocked_count = 0
    for coordinate, value in adjudications.items():
        parse_literal_coordinate(coordinate)
        require(isinstance(value, dict), f"row adjudication is malformed: {coordinate}")
        status = value.get("status")
        taints = value.get("taints")
        require(isinstance(taints, list), f"row taints are malformed: {coordinate}")
        bound_pair_key = value.get("pair_key")
        require(
            isinstance(bound_pair_key, str) and bound_pair_key in pair_guards,
            f"row pair proof is absent: {coordinate}",
        )
        pair_taints = pair_guards[bound_pair_key].get("taints")
        require(
            isinstance(pair_taints, list)
            and set(pair_taints).issubset(set(taints)),
            f"row omits a pair taint: {coordinate}",
        )
        if status == "promotion_eligible":
            require(not taints, f"tainted row was marked eligible: {coordinate}")
            require(
                value.get("layout_change_pending") is False,
                f"layout-pending row was marked eligible: {coordinate}",
            )
            require(
                value.get("base_vm_row_guard_present") is True,
                f"unproved Base donor was marked eligible: {coordinate}",
            )
            eligible_count += 1
        elif status == "blocked":
            require(taints, f"untainted row was marked blocked: {coordinate}")
            blocked_count += 1
        else:
            raise AuditError(f"invalid row adjudication status: {coordinate}")
    scope = report.get("scope")
    require(isinstance(scope, dict), "coverage report scope is absent")
    require(
        eligible_count == scope.get("promotion_eligible_rows"),
        "eligible row count drifted",
    )
    require(
        blocked_count == scope.get("blocked_rows"),
        "blocked row count drifted",
    )
    require(
        eligible_count + blocked_count == scope.get("runtime_pending_rows"),
        "row adjudication universe is incomplete",
    )
    require(
        report.get("promotion", {}).get("runtime_promotion_performed") is False,
        "coverage builder must not mutate decisions",
    )


def build_report(inputs: AuditInputs) -> dict[str, Any]:
    bound_rows: list[dict[str, Any]] = []
    pair_cache: dict[tuple[tuple[int, int], tuple[int, int]], PairAudit] = {}
    for row in inputs.rows:
        bound = validate_row_binding(
            row,
            prefill_report=inputs.prefill_report,
            base_promoted_rows=inputs.base_promoted_rows,
            base_coverage=inputs.base_coverage,
            base_source_records=inputs.base_source_records,
            base_candidate_records=inputs.base_candidate_records,
            pk_source_records=inputs.pk_source_records,
            pk_current_records=inputs.pk_current_records,
            pk_candidate_records=inputs.pk_candidate_records,
        )
        pair = (bound["base_record"], bound["pk_record"])
        if pair not in pair_cache:
            pair_cache[pair] = compare_record_pair(
                pair[0],
                pair[1],
                base_source_records=inputs.base_source_records,
                base_candidate_records=inputs.base_candidate_records,
                pk_source_records=inputs.pk_source_records,
                pk_candidate_records=inputs.pk_candidate_records,
            )
        bound_rows.append(bound)

    row_adjudications: dict[str, dict[str, Any]] = {}
    row_guards: dict[str, str] = {}
    taint_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    eligible_count = 0
    global_masked_novel_count = 0
    global_masked_novel_blocked_count = 0
    exact_donor_masked_mismatch_count = 0
    exact_donor_mismatch_novel_taint_count = 0
    for bound in bound_rows:
        audit = pair_cache[(bound["base_record"], bound["pk_record"])]
        taints = set(audit.taints)
        reasons = set(audit.reason_codes)
        if bound["layout_change_pending"]:
            taints.add("layout_taint")
            reasons.add("layout_change_pending")
        if bound["base_vm_row_guard"] is None:
            taints.add("donor_taint")
            reasons.add("base_donor_vm_row_proof_absent")
        status = "promotion_eligible" if not taints else "blocked"
        if bound["prefill_global_masked_novel"]:
            global_masked_novel_count += 1
            if status == "blocked" and "novel_taint" in taints:
                global_masked_novel_blocked_count += 1
        if bound["exact_donor_masked_mismatch"]:
            exact_donor_masked_mismatch_count += 1
            if "novel_taint" in taints:
                exact_donor_mismatch_novel_taint_count += 1
        if status == "promotion_eligible":
            eligible_count += 1
        for value in taints:
            taint_counts[value] += 1
        for value in reasons:
            reason_counts[value] += 1
        row_payload = {
            "coordinate": bound["coordinate"],
            "base_coordinate": bound["base_coordinate"],
            "translation_utf16le_sha256": bound["translation_utf16le_sha256"],
            "row_evidence_sha256": bound["row_evidence_sha256"],
            "base_vm_row_guard": bound["base_vm_row_guard"],
            "base_coverage_sha256": inputs.base_coverage_sha256,
            "pair_proof_sha256": audit.proof_sha256,
            "pk_candidate_record_sha256": sha256_bytes(
                inputs.pk_candidate_records[bound["pk_record"]].data
            ),
            "status": status,
            "taints": sorted(taints),
            "reason_codes": sorted(reasons),
            "layout_change_pending": bound["layout_change_pending"],
        }
        row_guard = canonical_sha256(row_payload)
        row_guards[str(bound["coordinate"])] = row_guard
        row_adjudications[str(bound["coordinate"])] = {
            "status": status,
            "taints": sorted(taints),
            "reason_codes": sorted(reasons),
            "layout_change_pending": bound["layout_change_pending"],
            "base_vm_row_guard_present": bound["base_vm_row_guard"] is not None,
            "base_coordinate": bound["base_coordinate"],
            "pair_key": pair_key(
                audit.base_root,
                audit.pk_root,
            ),
            "pair_proof_sha256": audit.proof_sha256,
            "row_verification_guard_sha256": row_guard,
        }

    require(
        global_masked_novel_count
        == inputs.prefill_report[
            "any_base_candidate_operand_masked_dynamic_novel_rows"
        ]
        == 25,
        "global operand-masked novel universe drifted",
    )
    require(
        global_masked_novel_blocked_count == global_masked_novel_count,
        "a globally novel row escaped novel taint",
    )
    require(
        exact_donor_masked_mismatch_count
        == inputs.prefill_report[
            "exact_source_donor_operand_masked_dynamic_mismatch_rows"
        ]
        == 83,
        "exact-donor operand-masked mismatch universe drifted",
    )
    require(
        exact_donor_mismatch_novel_taint_count
        == exact_donor_masked_mismatch_count
        == taint_counts["novel_taint"],
        "exact-donor mismatch and exact root novel taint diverged",
    )

    pair_proof_guards = {
        pair_key(audit.base_root, audit.pk_root): {
            "proof_sha256": audit.proof_sha256,
            "taints": list(audit.taints),
            "reason_codes": list(audit.reason_codes),
            "visited_pair_count": len(audit.visited_pairs),
            "0143_occurrences": audit.call_occurrences,
            "014a_occurrences": audit.jump_occurrences,
        }
        for audit in sorted(
            pair_cache.values(),
            key=lambda value: (value.base_root, value.pk_root),
        )
    }
    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "scope": {
            "resource": "MSG_PK/JP/msggame.bin",
            "prefilled_rows": inputs.prefill_report["prefilled_rows"],
            "runtime_pending_rows": len(bound_rows),
            "unique_pk_root_records": len(
                {value["pk_record"] for value in bound_rows}
            ),
            "unique_explicit_base_pk_root_pairs": len(pair_cache),
            "promotion_eligible_rows": eligible_count,
            "blocked_rows": len(bound_rows) - eligible_count,
            "per_row_game_playback_required": 0,
        },
        "route": {
            "program_sha256": inputs.contract["program"]["unpacked_exe_sha256"],
            "jp_path": inputs.contract["pk_message_route_proof"][
                "path_construction"
            ]["jp_result"],
            "loader": inputs.contract["functions"][
                "message_object_initializer_and_loader"
            ],
            "evaluator": inputs.contract["functions"]["evaluate_message_id"],
            "record_selector": inputs.contract["functions"]["select_record"],
            "record_vm": inputs.contract["functions"]["execute_record_vm"],
            "route_proved": True,
        },
        "pairing_method": {
            "root_mapping": "explicit Base donor coordinate from bound prefill evidence",
            "closure_mapping": "synchronized actual 0143/014A occurrence order",
            "constant_coordinate_delta_assumed": False,
            "literal_boundaries_compared": True,
            "selector_property_compared": True,
            "actual_operand_range_and_target_existence_checked": True,
            "novel_sibling_closure_taint_propagated_to_root": True,
            "raw_regex_masking_can_verify": False,
        },
        "opcode_coverage": aggregate_opcode_coverage(
            pair_cache.values(),
            inputs.pk_candidate_records,
        ),
        "blockers": {
            "prefill_global_operand_masked_novel_rows": global_masked_novel_count,
            "prefill_global_operand_masked_novel_rows_blocked_as_novel": (
                global_masked_novel_blocked_count
            ),
            "exact_donor_operand_masked_mismatch_rows": (
                exact_donor_masked_mismatch_count
            ),
            "exact_donor_mismatch_rows_blocked_as_novel": (
                exact_donor_mismatch_novel_taint_count
            ),
            "taint_row_counts": dict(sorted(taint_counts.items())),
            "reason_row_counts": dict(sorted(reason_counts.items())),
            "blocked_rows_require": (
                "manual PK-specific assembly review or an independently proved "
                "PK-only closure; layout-tainted rows additionally require layout review"
            ),
        },
        "promotion": {
            "runtime_promotion_performed": False,
            "steam_write_performed": False,
            "eligible_rows_can_be_promoted_only_by_a_separate_bound_decision_builder": True,
            "blocked_or_novel_row_promotion_forbidden": True,
        },
        "guards": {
            **dict(inputs.artifact_hashes),
            "mapping_universe_sha256": inputs.prefill_report[
                "mapping_universe_sha256"
            ],
            "row_verification_guards_sha256": canonical_sha256(row_guards),
            "pair_proof_guards_sha256": canonical_sha256(pair_proof_guards),
        },
        "pair_proof_guards": pair_proof_guards,
        "row_adjudications": row_adjudications,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_translated_dialogue_text": False,
            "contains_complete_game_resource": False,
            "contains_only_coordinates_hashes_counts_opcode_forms_and_taints": True,
        },
    }
    sealed = seal_report(report)
    validate_report(sealed)
    return sealed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefill", type=Path, default=DEFAULT_PREFILL)
    parser.add_argument("--prefill-report", type=Path, default=DEFAULT_PREFILL_REPORT)
    parser.add_argument("--base-promoted", type=Path, default=DEFAULT_BASE_PROMOTED)
    parser.add_argument("--base-pristine", type=Path, default=DEFAULT_BASE_PRISTINE)
    parser.add_argument("--base-current", type=Path, default=DEFAULT_BASE_CURRENT)
    parser.add_argument("--pk-pristine", type=Path, default=DEFAULT_PK_PRISTINE)
    parser.add_argument("--pk-current", type=Path, default=DEFAULT_PK_CURRENT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="rebuild and compare the tracked source-free report",
    )
    args = parser.parse_args()
    inputs = build_inputs(
        prefill_path=args.prefill,
        prefill_report_path=args.prefill_report,
        base_promoted_path=args.base_promoted,
        base_pristine_path=args.base_pristine,
        base_current_path=args.base_current,
        pk_pristine_path=args.pk_pristine,
        pk_current_path=args.pk_current,
    )
    report = build_report(inputs)
    content = canonical_json(report)
    if args.check:
        require(args.output.is_file(), f"tracked PK VM report is absent: {args.output}")
        require(
            args.output.read_text(encoding="utf-8") == content,
            "tracked PK VM report drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8", newline="\n")
    print(
        "PASS "
        f"pending={report['scope']['runtime_pending_rows']} "
        f"eligible={report['scope']['promotion_eligible_rows']} "
        f"blocked={report['scope']['blocked_rows']} "
        f"pairs={report['scope']['unique_explicit_base_pk_root_pairs']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, AuditError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
