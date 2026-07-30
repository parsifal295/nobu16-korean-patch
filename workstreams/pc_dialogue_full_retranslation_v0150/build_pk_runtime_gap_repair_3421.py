#!/usr/bin/env python3
"""Build the source-free PK record 3421 control-gap repair candidate."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
FORMAT_PATH = REPO / "workstreams" / "msggame" / "msggame_format.py"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
DECISIONS_ROOT = TMP_ROOT / "decisions"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    TMP_ROOT / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
CONTROL_REPAIRS = (
    WORKSTREAM / "runtime_control_repairs.source_free.v1.json"
)
OUTPUT_ROOT = TMP_ROOT / "runtime_gap_repairs"
CANDIDATE_OUTPUT = (
    OUTPUT_ROOT
    / "pk_msggame_3421_control_gap_repair.candidate.bin"
)
EVIDENCE_OUTPUT = (
    OUTPUT_ROOT
    / "pk_msggame_3421_control_gap_repair.private.v1.json"
)

RESOURCE = "pk_msggame"
BLOCK_ID = 6
RECORD_ID = 3421
LITERAL_ID = 0
RECORD_KEY = (BLOCK_ID, RECORD_ID)
COORDINATE = "6:3421:0"
RECORD_COORDINATE = "6:3421"
BASE_RECORD_ID = 3414
BASE_RECORD_KEY = (BLOCK_ID, BASE_RECORD_ID)
BASE_COORDINATE = "6:3414:0"
PK_RECORD_COUNT = 21_751

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_BASE_PRISTINE_SHA256 = (
    "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"
)
EXPECTED_CURRENT_RECORD_SHA256 = (
    "4EE00E2439FBCCB33C3020749AA7C4DF208C42F6688026DF7BAC4808ED8E5B2A"
)
EXPECTED_SOURCE_RECORD_SHA256 = (
    "063FE464ADFF1B684E6A20AC54EBAC04AF75513CF8AE92B54176ABB356F853D8"
)
EXPECTED_BASE_RECORD_SHA256 = (
    "D51ED5805E3656D083C4919EA34536077CA760771AAD286BD003612B0AA0F5EE"
)
EXPECTED_CURRENT_LITERAL_SHA256 = (
    "4199077CDE9E45540B0CD27408F3BCF20BFC3FCA4F2E27E69EDF195DBEDE1C62"
)
EXPECTED_PREFILL_TRANSLATION_SHA256 = (
    "7E712B54A6EDC74E154EE7A34EF4DD49151D6A5F8E43DB89082D1B0CB4485CCA"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_PREFILL_ROW_SHA256 = (
    "487B06C7B2F2A04594545382241D3598B3E3B667CBA3A70B97FD8AC428594DBC"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_BASE_ROW_SHA256 = (
    "F02BFA28E42DD5EF9AB9B98751BC04C09B8C33E5B7840289AB0DFB6F4D4C6B93"
)
EXPECTED_CONTROL_REPAIRS_SHA256 = (
    "240D504BDA7D92021E37A6E2387B84BBD7249C6ED2362F57CE61177EFC51F8AB"
)
EXPECTED_CURRENT_GAPS = ("", "050505")
EXPECTED_SOURCE_GAPS = ("", "01432A040000050505")
EXPECTED_BASE_GAPS = ("", "01431E040000050505")
EXPECTED_CURRENT_CALLS: tuple[int, ...] = ()
EXPECTED_SOURCE_CALLS = (1066,)
EXPECTED_BASE_CALLS = (1054,)
EXPECTED_CANDIDATE_SHA256 = (
    "E1D6E1C4133473382CD629BEF3705787B146B39D984AE6EF8106243D191B933F"
)
EXPECTED_CANDIDATE_RECORD_SHA256 = (
    "FDB2C242C327F75DC6CCF510D130EE50F4A09271F28A0AE1ABAE976DA68AD872"
)
EXPECTED_ASSEMBLED_CANDIDATE_SHA256 = (
    "5C4B2251C5706D3CB1B018E9A49F2E0545ACB8BABBB579DEF2C35D19095DD803"
)
EXPECTED_ASSEMBLED_RECORD_SHA256 = (
    "640BE59047587DBA06A2E983E07DC9CA1639A72CB75304F38CA18F2FD2FAEF11"
)
EXPECTED_EVIDENCE_SHA256 = (
    "1A91B942E3EDD0EF0B4421CC96766F2BF0934D2C407090DA5D074C3C4305C185"
)
EXPECTED_CURRENT_PACKED_SIZE = 1_806_586
EXPECTED_CANDIDATE_PACKED_SIZE = 1_806_594
EXPECTED_CURRENT_RECORD_SIZE = 81
EXPECTED_CANDIDATE_RECORD_SIZE = 87

EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-msggame-runtime-gap-repair.v1.private-evidence"
)
CONTROL_REPAIR_SCHEMA = (
    "nobu16.kr.pc-dialogue-full-retranslation-runtime-"
    "control-repairs.v1"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module(
    "pc_dialogue_full_retranslation_v0150_gap_repair_engine",
    ENGINE_PATH,
)
FORMAT = load_module(
    "pc_dialogue_full_retranslation_v0150_gap_repair_format",
    FORMAT_PATH,
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_row_sha256(row: dict[str, Any]) -> str:
    encoded = json.dumps(
        row,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(encoded)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise RuntimeError(f"non-object JSONL row in {path}")
        rows.append(value)
    return rows


def archive_records(
    packed: bytes,
) -> dict[tuple[int, int], Any]:
    return ENGINE.archive_records(
        FORMAT.parse_packed_msggame(packed).archive
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    literals = FORMAT.parse_record_literals(record)
    if not literals:
        return (record.data,)
    gaps: list[bytes] = [
        record.data[: literals[0].marker_offset]
    ]
    for left, right in zip(literals, literals[1:]):
        gaps.append(
            record.data[left.marker_end : right.marker_offset]
        )
    gaps.append(record.data[literals[-1].marker_end :])
    return tuple(gaps)


def gap_hex(record: Any) -> tuple[str, ...]:
    return tuple(value.hex().upper() for value in gap_bytes(record))


def direct_calls(record: Any) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gap_bytes(record)
        for match in re.finditer(
            b"\x01\x43(.{4})",
            gap,
            re.DOTALL,
        )
    )


def find_row(
    path: Path,
    coordinate: str,
) -> dict[str, Any]:
    matches = [
        row
        for row in read_jsonl(path)
        if row.get("coordinate") == coordinate
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one {coordinate} row in {path}, got "
            f"{len(matches)}"
        )
    return matches[0]


def load_control_repair_entry() -> dict[str, Any]:
    if (
        sha256_bytes(CONTROL_REPAIRS.read_bytes())
        != EXPECTED_CONTROL_REPAIRS_SHA256
    ):
        raise RuntimeError("source-free control repair ledger drifted")
    document = json.loads(
        CONTROL_REPAIRS.read_text(encoding="utf-8")
    )
    if (
        document.get("schema") != CONTROL_REPAIR_SCHEMA
        or document.get("release_target") != "0.15.0"
        or document.get("source_text_present") is not False
        or document.get("semantic_decision_count_delta") != 0
        or len(document.get("entries", [])) != 2
    ):
        raise RuntimeError("source-free control repair ledger invalid")
    matches = [
        entry
        for entry in document["entries"]
        if entry.get("resource") == RESOURCE
        and entry.get("coordinate") == COORDINATE
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "source-free control repair entry binding drifted"
        )
    entry = matches[0]
    expected = {
        "resource": RESOURCE,
        "coordinate": COORDINATE,
        "record_coordinate": RECORD_COORDINATE,
        "source_decision_segment_id":
        "pk_msggame_base_exact_reuse_prefill",
        "source_decision_file_sha256": EXPECTED_PREFILL_SHA256,
        "source_decision_row_canonical_sha256":
        EXPECTED_PREFILL_ROW_SHA256,
        "original_scope_classification": "retranslated",
        "original_runtime_review": "not_required",
        "effective_scope_classification":
        "runtime_fragment_pending",
        "effective_runtime_review": "pending",
        "override_reason":
        "control_gap_repair_pending_runtime_validation",
        "repair_builder": SCRIPT.name,
        "repair_evidence_schema": EVIDENCE_SCHEMA,
        "repair_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
        "repair_candidate_required_for_release": True,
        "repair_status": "prepared_pending_runtime_validation",
        "semantic_decision_duplicate_added": False,
        "steam_write_performed": False,
    }
    if entry != expected:
        raise RuntimeError("source-free control repair entry drifted")
    return entry


def prepare_inputs() -> dict[str, Any]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    resource = prepared.resources[RESOURCE]
    if (
        sha256_bytes(resource.current_blob)
        != EXPECTED_STEAM_PK_SHA256
        or sha256_bytes(resource.pristine_blob)
        != EXPECTED_PRISTINE_PK_SHA256
        or sha256_bytes(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        )
        != EXPECTED_BASE_PRISTINE_SHA256
        or len(resource.current_blob)
        != EXPECTED_CURRENT_PACKED_SIZE
    ):
        raise RuntimeError("repair input packed resource drifted")
    current_records = archive_records(resource.current_blob)
    source_records = archive_records(resource.pristine_blob)
    base_blob = ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
    base_records = archive_records(base_blob)
    if (
        len(current_records) != PK_RECORD_COUNT
        or len(source_records) != PK_RECORD_COUNT
        or set(current_records) != set(source_records)
    ):
        raise RuntimeError("repair record universe drifted")
    current_record = current_records[RECORD_KEY]
    source_record = source_records[RECORD_KEY]
    base_record = base_records[BASE_RECORD_KEY]
    current_literals = FORMAT.parse_record_literals(current_record)
    source_literals = FORMAT.parse_record_literals(source_record)
    base_literals = FORMAT.parse_record_literals(base_record)
    if (
        len(current_literals) != 1
        or len(source_literals) != 1
        or len(base_literals) != 1
        or current_literals[0].literal_id != LITERAL_ID
        or source_literals[0].literal_id != LITERAL_ID
        or base_literals[0].literal_id != LITERAL_ID
        or sha256_bytes(current_record.data)
        != EXPECTED_CURRENT_RECORD_SHA256
        or sha256_bytes(source_record.data)
        != EXPECTED_SOURCE_RECORD_SHA256
        or sha256_bytes(base_record.data)
        != EXPECTED_BASE_RECORD_SHA256
        or sha256_bytes(
            current_literals[0].text.encode("utf-16le")
        )
        != EXPECTED_CURRENT_LITERAL_SHA256
        or gap_hex(current_record) != EXPECTED_CURRENT_GAPS
        or gap_hex(source_record) != EXPECTED_SOURCE_GAPS
        or gap_hex(base_record) != EXPECTED_BASE_GAPS
        or direct_calls(current_record) != EXPECTED_CURRENT_CALLS
        or direct_calls(source_record) != EXPECTED_SOURCE_CALLS
        or direct_calls(base_record) != EXPECTED_BASE_CALLS
        or len(current_record.data) != EXPECTED_CURRENT_RECORD_SIZE
    ):
        raise RuntimeError("repair record or control-gap input drifted")

    if (
        sha256_bytes(PREFILL.read_bytes())
        != EXPECTED_PREFILL_SHA256
        or sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("repair decision input drifted")
    prefill_row = find_row(PREFILL, COORDINATE)
    base_row = find_row(BASE_PROMOTED, BASE_COORDINATE)
    if (
        canonical_row_sha256(prefill_row)
        != EXPECTED_PREFILL_ROW_SHA256
        or canonical_row_sha256(base_row)
        != EXPECTED_BASE_ROW_SHA256
        or prefill_row.get("resource") != RESOURCE
        or prefill_row.get("runtime_review") != "not_required"
        or prefill_row.get("scope_classification") != "retranslated"
        or prefill_row.get("semantic_review") != "approved"
        or prefill_row.get("source_record_raw_sha256")
        != EXPECTED_SOURCE_RECORD_SHA256
        or prefill_row.get("current_ko_utf16le_sha256")
        != EXPECTED_CURRENT_LITERAL_SHA256
        or sha256_bytes(
            str(prefill_row.get("translation")).encode("utf-16le")
        )
        != EXPECTED_PREFILL_TRANSLATION_SHA256
        or base_row.get("resource") != "base_msggame"
        or base_row.get("runtime_review") != "verified"
        or base_row.get("semantic_review") != "approved"
        or sha256_bytes(
            str(base_row.get("translation")).encode("utf-16le")
        )
        != EXPECTED_PREFILL_TRANSLATION_SHA256
        or prefill_row.get("translation")
        != base_row.get("translation")
    ):
        raise RuntimeError("repair semantic donor state drifted")
    control_entry = load_control_repair_entry()
    return {
        "prepared": prepared,
        "resource": resource,
        "current_records": current_records,
        "source_records": source_records,
        "base_records": base_records,
        "current_record": current_record,
        "source_record": source_record,
        "base_record": base_record,
        "current_literal": current_literals[0],
        "source_literal": source_literals[0],
        "prefill_row": prefill_row,
        "base_row": base_row,
        "control_entry": control_entry,
    }


def candidate_record(inputs: dict[str, Any]) -> bytes:
    current_record = inputs["current_record"]
    source_record = inputs["source_record"]
    current_literal = inputs["current_literal"]
    source_literal = inputs["source_literal"]
    current_prefix = current_record.data[: current_literal.marker_end]
    source_terminal_gap = source_record.data[
        source_literal.marker_end :
    ]
    if (
        current_prefix
        != current_record.data[: -len(bytes.fromhex("050505"))]
        or source_terminal_gap
        != bytes.fromhex("01432A040000050505")
    ):
        raise RuntimeError("repair splice boundary drifted")
    result = current_prefix + source_terminal_gap
    if (
        len(result) != EXPECTED_CANDIDATE_RECORD_SIZE
        or sha256_bytes(result)
        != EXPECTED_CANDIDATE_RECORD_SHA256
    ):
        raise RuntimeError("repair record candidate drifted")
    return result


def build_candidate(
    inputs: dict[str, Any],
) -> tuple[bytes, dict[tuple[int, int], Any]]:
    resource = inputs["resource"]
    repaired_record = candidate_record(inputs)
    candidate = FORMAT.rebuild_packed_msggame(
        resource.current_blob,
        {RECORD_KEY: repaired_record},
    )
    candidate_records = archive_records(candidate)
    if (
        sha256_bytes(candidate) != EXPECTED_CANDIDATE_SHA256
        or len(candidate) != EXPECTED_CANDIDATE_PACKED_SIZE
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError("repair packed candidate drifted")
    target_record = candidate_records[RECORD_KEY]
    target_literals = FORMAT.parse_record_literals(target_record)
    current_literal = inputs["current_literal"]
    if (
        sha256_bytes(target_record.data)
        != EXPECTED_CANDIDATE_RECORD_SHA256
        or gap_hex(target_record) != EXPECTED_SOURCE_GAPS
        or direct_calls(target_record) != EXPECTED_SOURCE_CALLS
        or len(target_literals) != 1
        or target_literals[0].text != current_literal.text
        or sha256_bytes(
            target_literals[0].text.encode("utf-16le")
        )
        != EXPECTED_CURRENT_LITERAL_SHA256
        or target_record.data[: target_literals[0].marker_end]
        != inputs["current_record"].data[
            : inputs["current_literal"].marker_end
        ]
    ):
        raise RuntimeError("repair target record invariant drifted")
    for key, record in inputs["current_records"].items():
        if key != RECORD_KEY and candidate_records[key].data != record.data:
            raise RuntimeError(
                f"repair changed outside target record: {key}"
            )
    reverse = FORMAT.rebuild_packed_msggame(
        candidate,
        {RECORD_KEY: inputs["current_record"].data},
    )
    if reverse != resource.current_blob:
        raise RuntimeError("repair reverse record overlay drifted")
    if (
        FORMAT.rebuild_packed_msggame(resource.current_blob)
        != resource.current_blob
    ):
        raise RuntimeError("repair current packed repack drifted")
    return candidate, candidate_records


def assert_complete_runtime_assembly(
    inputs: dict[str, Any],
    repair_candidate: bytes,
) -> tuple[bytes, Any]:
    translation = str(inputs["prefill_row"]["translation"])
    assembled = ENGINE.rebuild_packed_with_literals(
        repair_candidate,
        {(BLOCK_ID, RECORD_ID, LITERAL_ID): translation},
    )
    assembled_records = archive_records(assembled)
    assembled_record = assembled_records[RECORD_KEY]
    assembled_literals = FORMAT.parse_record_literals(assembled_record)
    if (
        sha256_bytes(assembled)
        != EXPECTED_ASSEMBLED_CANDIDATE_SHA256
        or sha256_bytes(assembled_record.data)
        != EXPECTED_ASSEMBLED_RECORD_SHA256
        or len(assembled_literals) != 1
        or sha256_bytes(
            assembled_literals[0].text.encode("utf-16le")
        )
        != EXPECTED_PREFILL_TRANSLATION_SHA256
        or gap_hex(assembled_record) != EXPECTED_SOURCE_GAPS
        or direct_calls(assembled_record) != EXPECTED_SOURCE_CALLS
    ):
        raise RuntimeError("repair complete runtime assembly drifted")
    reverse = ENGINE.rebuild_packed_with_literals(
        assembled,
        {
            (
                BLOCK_ID,
                RECORD_ID,
                LITERAL_ID,
            ): inputs["current_literal"].text
        },
    )
    if reverse != repair_candidate:
        raise RuntimeError(
            "repair semantic overlay reverse drifted"
        )
    for key, record in inputs["current_records"].items():
        if key == RECORD_KEY:
            continue
        if assembled_records[key].data != record.data:
            raise RuntimeError(
                f"assembled repair changed outside target: {key}"
            )
    return assembled, assembled_record


def build_evidence(
    inputs: dict[str, Any],
    candidate: bytes,
    candidate_records: dict[tuple[int, int], Any],
    assembled: bytes,
    assembled_record: Any,
) -> dict[str, Any]:
    current_record = inputs["current_record"]
    source_record = inputs["source_record"]
    base_record = inputs["base_record"]
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "release_target": "0.15.0",
        "resource": RESOURCE,
        "coordinate": COORDINATE,
        "record_coordinate": RECORD_COORDINATE,
        "base_reference_coordinate": BASE_COORDINATE,
        "source_text_present": False,
        "current_packed_sha256": EXPECTED_STEAM_PK_SHA256,
        "pristine_pk_packed_sha256":
        EXPECTED_PRISTINE_PK_SHA256,
        "current_record_sha256":
        EXPECTED_CURRENT_RECORD_SHA256,
        "pristine_pk_record_sha256":
        EXPECTED_SOURCE_RECORD_SHA256,
        "base_reference_record_sha256":
        EXPECTED_BASE_RECORD_SHA256,
        "current_literal_utf16le_sha256":
        EXPECTED_CURRENT_LITERAL_SHA256,
        "prefill_translation_utf16le_sha256":
        EXPECTED_PREFILL_TRANSLATION_SHA256,
        "current_runtime_gap_hex": list(gap_hex(current_record)),
        "pristine_pk_runtime_gap_hex":
        list(gap_hex(source_record)),
        "base_reference_runtime_gap_hex":
        list(gap_hex(base_record)),
        "repair_candidate_runtime_gap_hex":
        list(gap_hex(candidate_records[RECORD_KEY])),
        "current_direct_call_operands":
        list(direct_calls(current_record)),
        "pristine_pk_direct_call_operands":
        list(direct_calls(source_record)),
        "base_reference_direct_call_operands":
        list(direct_calls(base_record)),
        "repair_candidate_direct_call_operands":
        list(direct_calls(candidate_records[RECORD_KEY])),
        "pk_operand_1066_authoritative": True,
        "base_operand_1054_reference_only": True,
        "base_operand_copied_to_pk": False,
        "current_literal_bytes_preserved": True,
        "prefill_translation_unchanged": True,
        "semantic_decision_duplicate_added": False,
        "semantic_decision_count_delta": 0,
        "prefill_original_runtime_review": "not_required",
        "prefill_original_scope_classification":
        "retranslated",
        "effective_runtime_review": "pending",
        "effective_scope_classification":
        "runtime_fragment_pending",
        "progress_override_reason":
        "control_gap_repair_pending_runtime_validation",
        "progress_override_ledger":
        CONTROL_REPAIRS.name,
        "progress_override_ledger_sha256":
        EXPECTED_CONTROL_REPAIRS_SHA256,
        "repair_candidate_sha256": sha256_bytes(candidate),
        "repair_candidate_record_sha256":
        sha256_bytes(candidate_records[RECORD_KEY].data),
        "prefill_assembled_candidate_sha256":
        sha256_bytes(assembled),
        "prefill_assembled_record_sha256":
        sha256_bytes(assembled_record.data),
        "complete_record_runtime_assembly_reviewed": True,
        "outside_scope_record_count": PK_RECORD_COUNT - 1,
        "outside_scope_records_exact": True,
        "reverse_record_overlay_exact": True,
        "reverse_semantic_overlay_exact": True,
        "two_run_reproduction_exact": True,
        "tamper_tests_passed": True,
        "runtime_validation_state": "pending",
        "runtime_promotion_authorized": False,
        "repair_candidate_required_for_release": True,
        "repair_status": "prepared_pending_runtime_validation",
        "steam_write_performed": False,
        "candidate_deployed_to_steam": False,
    }
    return evidence


def evidence_sha256(evidence: dict[str, Any]) -> str:
    return sha256_bytes(
        ENGINE.canonical_json(evidence).encode("utf-8")
    )


def validate_evidence(evidence: dict[str, Any]) -> None:
    if (
        evidence.get("schema") != EVIDENCE_SCHEMA
        or evidence.get("coordinate") != COORDINATE
        or evidence.get("source_text_present") is not False
        or evidence.get("pk_operand_1066_authoritative")
        is not True
        or evidence.get("base_operand_1054_reference_only")
        is not True
        or evidence.get("base_operand_copied_to_pk") is not False
        or evidence.get("current_literal_bytes_preserved")
        is not True
        or evidence.get("semantic_decision_duplicate_added")
        is not False
        or evidence.get("semantic_decision_count_delta") != 0
        or evidence.get("effective_runtime_review") != "pending"
        or evidence.get("effective_scope_classification")
        != "runtime_fragment_pending"
        or evidence.get("repair_candidate_sha256")
        != EXPECTED_CANDIDATE_SHA256
        or evidence.get("repair_candidate_record_sha256")
        != EXPECTED_CANDIDATE_RECORD_SHA256
        or evidence.get("runtime_validation_state") != "pending"
        or evidence.get("runtime_promotion_authorized") is not False
        or evidence.get("steam_write_performed") is not False
    ):
        raise RuntimeError("repair evidence validation failed")


def assert_tamper_rejection(
    inputs: dict[str, Any],
    candidate: bytes,
    evidence: dict[str, Any],
) -> None:
    current_record = inputs["current_record"]
    current_literal = inputs["current_literal"]
    base_gap = bytes.fromhex("01431E040000050505")
    wrong_record = (
        current_record.data[: current_literal.marker_end]
        + base_gap
    )
    wrong_candidate = FORMAT.rebuild_packed_msggame(
        inputs["resource"].current_blob,
        {RECORD_KEY: wrong_record},
    )
    wrong_records = archive_records(wrong_candidate)
    if (
        wrong_candidate == candidate
        or sha256_bytes(wrong_candidate)
        == EXPECTED_CANDIDATE_SHA256
        or direct_calls(wrong_records[RECORD_KEY])
        != EXPECTED_BASE_CALLS
    ):
        raise RuntimeError("Base operand tamper was not rejected")

    tampered_record = bytearray(candidate_record(inputs))
    call_offset = tampered_record.rfind(bytes.fromhex("01432A040000"))
    if call_offset < 0:
        raise RuntimeError("repair call opcode is absent")
    tampered_record[call_offset + 2] ^= 0x01
    tampered_candidate = FORMAT.rebuild_packed_msggame(
        inputs["resource"].current_blob,
        {RECORD_KEY: bytes(tampered_record)},
    )
    if (
        tampered_candidate == candidate
        or sha256_bytes(tampered_candidate)
        == EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError("repair operand tamper was not rejected")

    tampered_evidence = copy.deepcopy(evidence)
    tampered_evidence["repair_candidate_sha256"] = "0" * 64
    try:
        validate_evidence(tampered_evidence)
    except RuntimeError:
        pass
    else:
        raise RuntimeError("repair evidence tamper was not rejected")


def build_once() -> tuple[
    dict[str, Any],
    bytes,
    dict[str, Any],
]:
    inputs = prepare_inputs()
    candidate, candidate_records = build_candidate(inputs)
    assembled, assembled_record = (
        assert_complete_runtime_assembly(inputs, candidate)
    )
    evidence = build_evidence(
        inputs,
        candidate,
        candidate_records,
        assembled,
        assembled_record,
    )
    validate_evidence(evidence)
    assert_tamper_rejection(inputs, candidate, evidence)
    return inputs, candidate, evidence


def main() -> int:
    first = build_once()
    second = build_once()
    if (
        first[1] != second[1]
        or ENGINE.canonical_json(first[2])
        != ENGINE.canonical_json(second[2])
    ):
        raise RuntimeError(
            "repair second-run reproduction drifted"
        )
    evidence_digest = evidence_sha256(first[2])
    if EXPECTED_EVIDENCE_SHA256 == "TO_PIN":
        print(
            json.dumps(
                {"evidence": evidence_digest},
                ensure_ascii=True,
                separators=(",", ":"),
            )
        )
        return 2
    if evidence_digest != EXPECTED_EVIDENCE_SHA256:
        raise RuntimeError(
            f"repair evidence digest drifted: {evidence_digest}"
        )

    steam_path = first[0]["resource"].current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"repair Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(CANDIDATE_OUTPUT, first[1])
    ENGINE.atomic_write(
        EVIDENCE_OUTPUT,
        ENGINE.canonical_json(first[2]),
    )
    if (
        sha256_bytes(CANDIDATE_OUTPUT.read_bytes())
        != EXPECTED_CANDIDATE_SHA256
        or sha256_bytes(EVIDENCE_OUTPUT.read_bytes())
        != EXPECTED_EVIDENCE_SHA256
        or json.loads(
            EVIDENCE_OUTPUT.read_text(encoding="utf-8")
        )
        != first[2]
    ):
        raise RuntimeError("repair written output drifted")
    validate_evidence(
        json.loads(EVIDENCE_OUTPUT.read_text(encoding="utf-8"))
    )
    steam_after = sha256_bytes(steam_path.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError("repair wrote to Steam input")

    print(
        json.dumps(
            {
                "status": "ok",
                "resource": RESOURCE,
                "record_coordinate": RECORD_COORDINATE,
                "coordinate": COORDINATE,
                "repair_candidate_sha256":
                EXPECTED_CANDIDATE_SHA256,
                "repair_candidate_record_sha256":
                EXPECTED_CANDIDATE_RECORD_SHA256,
                "prefill_assembled_candidate_sha256":
                EXPECTED_ASSEMBLED_CANDIDATE_SHA256,
                "prefill_assembled_record_sha256":
                EXPECTED_ASSEMBLED_RECORD_SHA256,
                "evidence_sha256":
                EXPECTED_EVIDENCE_SHA256,
                "source_pk_call_operand": 1066,
                "base_reference_call_operand": 1054,
                "current_literal_bytes_preserved": True,
                "prefill_translation_unchanged": True,
                "semantic_decision_duplicate_added": False,
                "semantic_decision_count_delta": 0,
                "effective_runtime_review": "pending",
                "effective_scope_classification":
                "runtime_fragment_pending",
                "complete_record_runtime_assembly_reviewed":
                True,
                "outside_scope_records_exact": True,
                "reverse_record_overlay_exact": True,
                "reverse_semantic_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "runtime_promotion_authorized": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "candidate_output": str(CANDIDATE_OUTPUT),
                "evidence_output": str(EVIDENCE_OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
