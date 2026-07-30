#!/usr/bin/env python3
"""Build the source-free PK record 3887 complete runtime-gap repair."""

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
S1131 = DECISIONS_ROOT / "pk_msggame_B040_S1131.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
CONTROL_REPAIRS = (
    WORKSTREAM / "runtime_control_repairs.source_free.v1.json"
)
OUTPUT_ROOT = TMP_ROOT / "runtime_gap_repairs"
CANDIDATE_OUTPUT = (
    OUTPUT_ROOT
    / "pk_msggame_3887_runtime_gap_repair.candidate.bin"
)
EVIDENCE_OUTPUT = (
    OUTPUT_ROOT
    / "pk_msggame_3887_runtime_gap_repair.private.v1.json"
)

RESOURCE = "pk_msggame"
BLOCK_ID = 6
RECORD_ID = 3887
RECORD_KEY = (BLOCK_ID, RECORD_ID)
TARGET_COORDINATE = "6:3887:0"
COMPANION_COORDINATE = "6:3887:1"
RECORD_COORDINATE = "6:3887"
PK_RECORD_COUNT = 21_751

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_S1131_SHA256 = (
    "4423DE02F2CDB4499F9C88557DDBF1CB1BB83198DE70702C227E39CC0D0E6C30"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_CONTROL_REPAIRS_SHA256 = (
    "240D504BDA7D92021E37A6E2387B84BBD7249C6ED2362F57CE61177EFC51F8AB"
)
EXPECTED_CONTROL_REPAIR_ENTRY_SHA256 = (
    "DF4C6874651D962B877AD3019FA5EBC4515917726C05E0FE721AD3BC77701A11"
)
EXPECTED_SOURCE_RECORD_SHA256 = (
    "04459780AE6FCCEB6E2E792B3317A12E88D67563573B51FD0E325E7BF5D9300C"
)
EXPECTED_CURRENT_RECORD_SHA256 = (
    "BA9CB401D2C4425D0BEB55F75221D5931C57F4275ADB7948CB7174C7F81723B4"
)
EXPECTED_CANDIDATE_RECORD_SHA256 = (
    "290E5692BD4B6DBD047F83745D07E4AEFDB3C194C98E0A351CB93822BE4E058D"
)
EXPECTED_SOURCE_GAPS = (
    "023C",
    "0143D0030000",
    "0143F0010000050505",
)
EXPECTED_CURRENT_GAPS = ("023C", "", "050505")
EXPECTED_SOURCE_CALLS = (976, 496)
EXPECTED_CURRENT_CALLS: tuple[int, ...] = ()
EXPECTED_CURRENT_PACKED_SIZE = 1_806_586
EXPECTED_TARGET_ROW_SHA256 = (
    "9657D420BBA47D0DECCEAC22F3F0F7B89A642F9C2B972EC5325249A027729D14"
)
EXPECTED_COMPANION_ROW_SHA256 = (
    "8927FE8D6033B2D97131243D7AFB1CF716078FD5A73BCC595F23D7844192625F"
)
EXPECTED_LITERAL_OVERLAY_SHA256 = (
    "7F2C237FA00545F33CC84144B24CB675C3145819B2091574EA9C7DFC1059FF8E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "5438FA8699FCCDA9279AE06113E1130324E212C592D4C309FD6EE0F243CD9A55"
)
EXPECTED_CANDIDATE_PACKED_SIZE = 1_806_590
EXPECTED_EVIDENCE_SHA256 = (
    "2DF75358016EEF9A0DC0A6150A4EEDAD4F62AC8E419C98462531D45C99A34178"
)

EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-msggame-runtime-gap-repair.v1.private-evidence"
)
CONTROL_REPAIRS_SCHEMA = (
    "nobu16.kr.pc-dialogue-full-retranslation-runtime-"
    "control-repairs.v1"
)
DISCOVERED_PINS: dict[str, str | int] = {}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module(
    "pc_dialogue_full_retranslation_v0150_gap3887_engine",
    ENGINE_PATH,
)
FORMAT = load_module(
    "pc_dialogue_full_retranslation_v0150_gap3887_format",
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


def guard_pin(
    label: str, actual: str | int, expected: str | int
) -> None:
    if expected in {"TO_PIN", -1}:
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"{label} drifted: {actual!r} != {expected!r}"
        )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line:
            value = json.loads(line)
            if not isinstance(value, dict):
                raise RuntimeError(f"non-object JSONL row in {path}")
            rows.append(value)
    return rows


def find_row(path: Path, coordinate: str) -> dict[str, Any]:
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


def archive_records(packed: bytes) -> dict[tuple[int, int], Any]:
    return ENGINE.archive_records(
        FORMAT.parse_packed_msggame(packed).archive
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return ENGINE.record_gap_bytes(record)


def gap_hex(record: Any) -> tuple[str, ...]:
    return tuple(value.hex().upper() for value in gap_bytes(record))


def direct_calls(record: Any) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gap_bytes(record)
        for match in re.finditer(
            b"\x01\x43(.{4})", gap, re.DOTALL
        )
    )


def load_control_repair_entry() -> dict[str, Any]:
    if (
        sha256_bytes(CONTROL_REPAIRS.read_bytes())
        != EXPECTED_CONTROL_REPAIRS_SHA256
    ):
        raise RuntimeError("record 3887 control repair ledger drifted")
    document = json.loads(
        CONTROL_REPAIRS.read_text(encoding="utf-8")
    )
    if (
        document.get("schema") != CONTROL_REPAIRS_SCHEMA
        or document.get("release_target") != "0.15.0"
        or document.get("source_text_present") is not False
        or document.get("semantic_decision_count_delta") != 0
        or len(document.get("entries", [])) != 2
    ):
        raise RuntimeError("record 3887 control repair ledger invalid")
    matches = [
        entry
        for entry in document["entries"]
        if entry.get("resource") == RESOURCE
        and entry.get("coordinate") == TARGET_COORDINATE
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "record 3887 control repair entry binding drifted"
        )
    entry = matches[0]
    expected = {
        "resource": RESOURCE,
        "coordinate": TARGET_COORDINATE,
        "record_coordinate": RECORD_COORDINATE,
        "source_decision_segment_id": "pk_msggame_B040_S1131",
        "source_decision_file_sha256": EXPECTED_S1131_SHA256,
        "source_decision_row_canonical_sha256":
        EXPECTED_TARGET_ROW_SHA256,
        "original_scope_classification":
        "runtime_fragment_pending",
        "original_runtime_review": "pending",
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
    if (
        entry != expected
        or canonical_row_sha256(entry)
        != EXPECTED_CONTROL_REPAIR_ENTRY_SHA256
    ):
        raise RuntimeError("record 3887 control repair entry drifted")
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
        or len(resource.current_blob)
        != EXPECTED_CURRENT_PACKED_SIZE
        or sha256_bytes(S1131.read_bytes())
        != EXPECTED_S1131_SHA256
        or sha256_bytes(PREFILL.read_bytes())
        != EXPECTED_PREFILL_SHA256
    ):
        raise RuntimeError("record 3887 repair input drifted")
    ENGINE.validate_decisions(
        prepared, S1131, require_complete=False
    )
    current_records = archive_records(resource.current_blob)
    source_records = archive_records(resource.pristine_blob)
    if (
        len(current_records) != PK_RECORD_COUNT
        or len(source_records) != PK_RECORD_COUNT
        or set(current_records) != set(source_records)
    ):
        raise RuntimeError("record 3887 universe drifted")
    current_record = current_records[RECORD_KEY]
    source_record = source_records[RECORD_KEY]
    current_literals = FORMAT.parse_record_literals(current_record)
    source_literals = FORMAT.parse_record_literals(source_record)
    target_row = find_row(S1131, TARGET_COORDINATE)
    companion_row = find_row(PREFILL, COMPANION_COORDINATE)
    guard_pin(
        "EXPECTED_TARGET_ROW_SHA256",
        canonical_row_sha256(target_row),
        EXPECTED_TARGET_ROW_SHA256,
    )
    guard_pin(
        "EXPECTED_COMPANION_ROW_SHA256",
        canonical_row_sha256(companion_row),
        EXPECTED_COMPANION_ROW_SHA256,
    )
    evidence = target_row.get("runtime_assembly_evidence")
    if (
        len(current_literals) != 2
        or len(source_literals) != 2
        or sha256_bytes(current_record.data)
        != EXPECTED_CURRENT_RECORD_SHA256
        or sha256_bytes(source_record.data)
        != EXPECTED_SOURCE_RECORD_SHA256
        or gap_hex(current_record) != EXPECTED_CURRENT_GAPS
        or gap_hex(source_record) != EXPECTED_SOURCE_GAPS
        or direct_calls(current_record) != EXPECTED_CURRENT_CALLS
        or direct_calls(source_record) != EXPECTED_SOURCE_CALLS
        or target_row.get("resource") != RESOURCE
        or target_row.get("scope_classification")
        != "runtime_fragment_pending"
        or target_row.get("runtime_review") != "pending"
        or target_row.get("semantic_review") != "approved"
        or target_row.get("source_outer_whitespace_restored")
        is not True
        or companion_row.get("resource") != RESOURCE
        or companion_row.get("scope_classification")
        != "runtime_fragment_pending"
        or companion_row.get("runtime_review") != "pending"
        or companion_row.get("semantic_review") != "approved"
        or not isinstance(target_row.get("translation"), str)
        or not isinstance(companion_row.get("translation"), str)
        or target_row.get("source_record_raw_sha256")
        != EXPECTED_SOURCE_RECORD_SHA256
        or companion_row.get("source_record_raw_sha256")
        != EXPECTED_SOURCE_RECORD_SHA256
        or ENGINE.protected_signature(
            str(target_row["translation"])
        )
        != ENGINE.protected_signature(source_literals[0].text)
        or not isinstance(evidence, dict)
        or evidence.get(
            "source_runtime_gap_repair_evidence_schema"
        )
        != EVIDENCE_SCHEMA
        or evidence.get("source_runtime_gap_repair_builder")
        != SCRIPT.name
        or evidence.get(
            "source_runtime_gap_repair_record_coordinate"
        )
        != RECORD_COORDINATE
        or evidence.get(
            "source_runtime_gap_repair_candidate_record_sha256"
        )
        != EXPECTED_CANDIDATE_RECORD_SHA256
        or evidence.get("runtime_promotion_authorized") is not False
    ):
        raise RuntimeError("record 3887 decision evidence drifted")
    control_entry = load_control_repair_entry()
    return {
        "prepared": prepared,
        "resource": resource,
        "current_records": current_records,
        "source_records": source_records,
        "current_record": current_record,
        "source_record": source_record,
        "current_literals": current_literals,
        "source_literals": source_literals,
        "target_row": target_row,
        "companion_row": companion_row,
        "control_entry": control_entry,
    }


def build_candidate(
    inputs: dict[str, Any],
) -> tuple[bytes, bytes, Any, Any]:
    resource = inputs["resource"]
    replacements = {
        (BLOCK_ID, RECORD_ID, 0):
        str(inputs["target_row"]["translation"]),
        (BLOCK_ID, RECORD_ID, 1):
        str(inputs["companion_row"]["translation"]),
    }
    literal_overlay = ENGINE.rebuild_packed_with_literals(
        resource.current_blob, replacements
    )
    literal_records = archive_records(literal_overlay)
    assembled_record_data = FORMAT.rebuild_record_literals(
        inputs["source_record"],
        {
            0: replacements[(BLOCK_ID, RECORD_ID, 0)],
            1: replacements[(BLOCK_ID, RECORD_ID, 1)],
        },
    )
    candidate = FORMAT.rebuild_packed_msggame(
        literal_overlay, {RECORD_KEY: assembled_record_data}
    )
    candidate_records = archive_records(candidate)
    candidate_record = candidate_records[RECORD_KEY]
    candidate_literals = FORMAT.parse_record_literals(
        candidate_record
    )
    guard_pin(
        "EXPECTED_LITERAL_OVERLAY_SHA256",
        sha256_bytes(literal_overlay),
        EXPECTED_LITERAL_OVERLAY_SHA256,
    )
    guard_pin(
        "EXPECTED_CANDIDATE_SHA256",
        sha256_bytes(candidate),
        EXPECTED_CANDIDATE_SHA256,
    )
    guard_pin(
        "EXPECTED_CANDIDATE_PACKED_SIZE",
        len(candidate),
        EXPECTED_CANDIDATE_PACKED_SIZE,
    )
    if (
        sha256_bytes(candidate_record.data)
        != EXPECTED_CANDIDATE_RECORD_SHA256
        or candidate_record.data != assembled_record_data
        or gap_hex(candidate_record) != EXPECTED_SOURCE_GAPS
        or direct_calls(candidate_record) != EXPECTED_SOURCE_CALLS
        or len(candidate_literals) != 2
        or candidate_literals[0].text
        != inputs["target_row"]["translation"]
        or candidate_literals[1].text
        != inputs["companion_row"]["translation"]
    ):
        raise RuntimeError("record 3887 candidate drifted")
    for key, current_record in inputs["current_records"].items():
        if (
            key != RECORD_KEY
            and candidate_records[key].data != current_record.data
        ):
            raise RuntimeError(
                f"record 3887 repair changed outside target: {key}"
            )
    reverse_gap = FORMAT.rebuild_packed_msggame(
        candidate,
        {RECORD_KEY: literal_records[RECORD_KEY].data},
    )
    if reverse_gap != literal_overlay:
        raise RuntimeError("record 3887 gap reverse drifted")
    reverse_literals = {
        (BLOCK_ID, RECORD_ID, literal.literal_id): literal.text
        for literal in inputs["current_literals"]
    }
    if (
        ENGINE.rebuild_packed_with_literals(
            literal_overlay, reverse_literals
        )
        != resource.current_blob
    ):
        raise RuntimeError("record 3887 literal reverse drifted")
    return (
        candidate,
        literal_overlay,
        candidate_record,
        literal_records[RECORD_KEY],
    )


def build_evidence(
    inputs: dict[str, Any],
    candidate: bytes,
    literal_overlay: bytes,
    candidate_record: Any,
) -> dict[str, Any]:
    target_row = inputs["target_row"]
    companion_row = inputs["companion_row"]
    return {
        "schema": EVIDENCE_SCHEMA,
        "release_target": "0.15.0",
        "resource": RESOURCE,
        "coordinate": TARGET_COORDINATE,
        "companion_coordinate": COMPANION_COORDINATE,
        "record_coordinate": RECORD_COORDINATE,
        "repair_builder": SCRIPT.name,
        "source_text_present": False,
        "current_packed_sha256": EXPECTED_STEAM_PK_SHA256,
        "pristine_pk_packed_sha256":
        EXPECTED_PRISTINE_PK_SHA256,
        "current_record_sha256":
        EXPECTED_CURRENT_RECORD_SHA256,
        "pristine_pk_record_sha256":
        EXPECTED_SOURCE_RECORD_SHA256,
        "source_decision_file": S1131.name,
        "source_decision_file_sha256":
        EXPECTED_S1131_SHA256,
        "source_decision_row_canonical_sha256":
        canonical_row_sha256(target_row),
        "companion_decision_file": PREFILL.name,
        "companion_decision_file_sha256":
        EXPECTED_PREFILL_SHA256,
        "companion_decision_row_canonical_sha256":
        canonical_row_sha256(companion_row),
        "current_runtime_gap_hex":
        list(gap_hex(inputs["current_record"])),
        "pristine_pk_runtime_gap_hex":
        list(gap_hex(inputs["source_record"])),
        "repair_candidate_runtime_gap_hex":
        list(gap_hex(candidate_record)),
        "current_direct_call_operands":
        list(direct_calls(inputs["current_record"])),
        "pristine_pk_direct_call_operands":
        list(direct_calls(inputs["source_record"])),
        "repair_candidate_direct_call_operands":
        list(direct_calls(candidate_record)),
        "missing_current_call_operands":
        list(EXPECTED_SOURCE_CALLS),
        "source_outer_whitespace_restored": True,
        "source_record_controls_authoritative": True,
        "current_record_gap_anomaly": True,
        "all_record_literals_reviewed": True,
        "prefill_companion_reviewed": True,
        "semantic_decision_duplicate_added": False,
        "semantic_decision_count_delta": 0,
        "progress_control_repair_ledger":
        CONTROL_REPAIRS.name,
        "progress_control_repair_ledger_sha256":
        EXPECTED_CONTROL_REPAIRS_SHA256,
        "progress_control_repair_entry_canonical_sha256":
        EXPECTED_CONTROL_REPAIR_ENTRY_SHA256,
        "original_scope_classification":
        "runtime_fragment_pending",
        "original_runtime_review": "pending",
        "effective_scope_classification":
        "runtime_fragment_pending",
        "effective_runtime_review": "pending",
        "literal_overlay_sha256":
        sha256_bytes(literal_overlay),
        "repair_candidate_sha256": sha256_bytes(candidate),
        "repair_candidate_record_sha256":
        sha256_bytes(candidate_record.data),
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


def evidence_sha256(evidence: dict[str, Any]) -> str:
    return sha256_bytes(
        ENGINE.canonical_json(evidence).encode("utf-8")
    )


def validate_evidence(evidence: dict[str, Any]) -> None:
    if (
        evidence.get("schema") != EVIDENCE_SCHEMA
        or evidence.get("record_coordinate") != RECORD_COORDINATE
        or evidence.get("repair_builder") != SCRIPT.name
        or evidence.get("source_text_present") is not False
        or evidence.get("source_decision_file_sha256")
        != EXPECTED_S1131_SHA256
        or evidence.get("companion_decision_file_sha256")
        != EXPECTED_PREFILL_SHA256
        or evidence.get("source_decision_row_canonical_sha256")
        != canonical_row_sha256(
            find_row(S1131, TARGET_COORDINATE)
        )
        or evidence.get(
            "companion_decision_row_canonical_sha256"
        )
        != canonical_row_sha256(
            find_row(PREFILL, COMPANION_COORDINATE)
        )
        or evidence.get("current_record_gap_anomaly") is not True
        or evidence.get("progress_control_repair_ledger")
        != CONTROL_REPAIRS.name
        or evidence.get(
            "progress_control_repair_ledger_sha256"
        )
        != EXPECTED_CONTROL_REPAIRS_SHA256
        or evidence.get(
            "progress_control_repair_entry_canonical_sha256"
        )
        != EXPECTED_CONTROL_REPAIR_ENTRY_SHA256
        or evidence.get("original_scope_classification")
        != "runtime_fragment_pending"
        or evidence.get("original_runtime_review") != "pending"
        or evidence.get("effective_scope_classification")
        != "runtime_fragment_pending"
        or evidence.get("effective_runtime_review") != "pending"
        or evidence.get("missing_current_call_operands")
        != list(EXPECTED_SOURCE_CALLS)
        or evidence.get("source_outer_whitespace_restored")
        is not True
        or evidence.get("repair_candidate_record_sha256")
        != EXPECTED_CANDIDATE_RECORD_SHA256
        or (
            EXPECTED_CANDIDATE_SHA256 != "TO_PIN"
            and evidence.get("repair_candidate_sha256")
            != EXPECTED_CANDIDATE_SHA256
        )
        or evidence.get("outside_scope_record_count")
        != PK_RECORD_COUNT - 1
        or evidence.get("outside_scope_records_exact") is not True
        or evidence.get("runtime_validation_state") != "pending"
        or evidence.get("runtime_promotion_authorized") is not False
        or evidence.get("steam_write_performed") is not False
    ):
        raise RuntimeError("record 3887 repair evidence invalid")


def assert_tamper_rejection(
    inputs: dict[str, Any],
    candidate: bytes,
    evidence: dict[str, Any],
) -> None:
    assembled = bytearray(
        FORMAT.rebuild_record_literals(
            inputs["source_record"],
            {
                0: str(inputs["target_row"]["translation"]),
                1: str(inputs["companion_row"]["translation"]),
            },
        )
    )
    call_offset = assembled.find(bytes.fromhex("0143D0030000"))
    if call_offset < 0:
        raise RuntimeError("record 3887 source call absent")
    assembled[call_offset + 2] ^= 0x01
    wrong_candidate = FORMAT.rebuild_packed_msggame(
        inputs["resource"].current_blob,
        {RECORD_KEY: bytes(assembled)},
    )
    if (
        wrong_candidate == candidate
        or sha256_bytes(
            archive_records(wrong_candidate)[RECORD_KEY].data
        )
        == EXPECTED_CANDIDATE_RECORD_SHA256
    ):
        raise RuntimeError("record 3887 operand tamper accepted")

    tampered_target = copy.deepcopy(inputs["target_row"])
    tampered_target["translation"] += "X"
    if (
        canonical_row_sha256(tampered_target)
        == canonical_row_sha256(inputs["target_row"])
    ):
        raise RuntimeError("record 3887 decision tamper accepted")

    tampered_evidence = copy.deepcopy(evidence)
    tampered_evidence["repair_candidate_record_sha256"] = "0" * 64
    try:
        validate_evidence(tampered_evidence)
    except RuntimeError:
        pass
    else:
        raise RuntimeError("record 3887 evidence tamper accepted")


def build_once() -> tuple[dict[str, Any], bytes, dict[str, Any]]:
    inputs = prepare_inputs()
    (
        candidate,
        literal_overlay,
        candidate_record,
        _literal_record,
    ) = build_candidate(inputs)
    evidence = build_evidence(
        inputs, candidate, literal_overlay, candidate_record
    )
    validate_evidence(evidence)
    assert_tamper_rejection(inputs, candidate, evidence)
    return inputs, candidate, evidence


def main() -> int:
    first = build_once()
    if DISCOVERED_PINS:
        evidence_digest = evidence_sha256(first[2])
        guard_pin(
            "EXPECTED_EVIDENCE_SHA256",
            evidence_digest,
            EXPECTED_EVIDENCE_SHA256,
        )
        print(
            json.dumps(
                DISCOVERED_PINS,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    second = build_once()
    if (
        first[1] != second[1]
        or ENGINE.canonical_json(first[2])
        != ENGINE.canonical_json(second[2])
    ):
        raise RuntimeError(
            "record 3887 second-run reproduction drifted"
        )
    digest = evidence_sha256(first[2])
    if digest != EXPECTED_EVIDENCE_SHA256:
        raise RuntimeError(
            f"record 3887 evidence digest drifted: {digest}"
        )
    steam_path = first[0]["resource"].current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError("record 3887 Steam input drifted")
    ENGINE.atomic_write(CANDIDATE_OUTPUT, first[1])
    ENGINE.atomic_write(
        EVIDENCE_OUTPUT, ENGINE.canonical_json(first[2])
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
        raise RuntimeError("record 3887 written output drifted")
    validate_evidence(
        json.loads(EVIDENCE_OUTPUT.read_text(encoding="utf-8"))
    )
    if sha256_bytes(steam_path.read_bytes()) != steam_before:
        raise RuntimeError("record 3887 repair wrote to Steam")
    print(
        json.dumps(
            {
                "status": "ok",
                "resource": RESOURCE,
                "record_coordinate": RECORD_COORDINATE,
                "target_coordinate": TARGET_COORDINATE,
                "companion_coordinate": COMPANION_COORDINATE,
                "repair_candidate_sha256":
                EXPECTED_CANDIDATE_SHA256,
                "repair_candidate_record_sha256":
                EXPECTED_CANDIDATE_RECORD_SHA256,
                "evidence_sha256": EXPECTED_EVIDENCE_SHA256,
                "source_call_operands":
                list(EXPECTED_SOURCE_CALLS),
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
