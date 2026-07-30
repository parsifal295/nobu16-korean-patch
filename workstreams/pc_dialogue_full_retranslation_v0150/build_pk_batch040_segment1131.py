#!/usr/bin/env python3
"""Build source-redacted PK B040 segment 1131 residual decisions."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch039_segment1129.py"
FORMAT_PATH = REPO / "workstreams" / "msggame" / "msggame_format.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B040_S1131.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B039_S1130.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B040_S1132.private.v1.jsonl",
)

SEGMENT = 1131
QUEUE_BATCH_ID = "pk_msggame-B040"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 3867
QUEUE_LAST_RECORD = 3979

TARGET_COORDINATES = (
    "6:3867:0",
    "6:3870:0",
    "6:3872:0",
    "6:3872:1",
    "6:3873:0",
    "6:3875:0",
    "6:3876:0",
    "6:3880:0",
    "6:3880:1",
    "6:3881:0",
    "6:3881:1",
    "6:3883:1",
    "6:3886:0",
    "6:3887:0",
    "6:3888:1",
)
TRANSLATIONS = {
    "6:3867:0": "께서는",
    "6:3870:0": "이럴 수가,",
    "6:3872:0": "이(가)",
    "6:3872:1": "에 대한",
    "6:3873:0": "에서 온",
    "6:3875:0": "정책「",
    "6:3876:0": "정책「",
    "6:3880:0": "봉행 변경으로 정책「",
    "6:3880:1": "」의 발전을 중단",
    "6:3881:0": "봉행 변경으로 정책「",
    "6:3881:1": "」을(를) 철회",
    "6:3883:1": "\n이번에",
    "6:3886:0": "을(를) 건설하",
    "6:3887:0": "의 건설에 착수하",
    "6:3888:1": "을(를) 건설하",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3867,
    3870,
    3872,
    3873,
    3875,
    3876,
    3880,
    3881,
    3883,
    3886,
    3887,
    3888,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXACT_BASE_RECORD_MAPPING = {
    3867: 3860,
    3870: 3863,
    3872: 3865,
    3873: 3866,
    3875: 3868,
    3876: 3869,
    3883: 3874,
    3886: 3877,
    3887: 3878,
    3888: 3879,
}
MANUAL_CONTEXT_RECORD_IDS = (3880, 3881)
BASE_CONTEXT_REFERENCES = {
    "6:3867:0": "6:3860:0",
    "6:3870:0": "6:3863:0",
    "6:3872:0": "6:3865:0",
    "6:3872:1": "6:3865:1",
    "6:3873:0": "6:3866:0",
    "6:3875:0": "6:3868:0",
    "6:3876:0": "6:3869:0",
    "6:3880:0": "6:3869:0",
    "6:3880:1": "6:3869:1",
    "6:3881:0": "6:3869:0",
    "6:3881:1": "2:187:0",
    "6:3883:1": "6:3874:1",
    "6:3886:0": "6:3877:0",
    "6:3887:0": "6:3878:0",
    "6:3888:1": "6:3879:1",
}
PREFILL_COMPANION_COORDINATES = (
    "6:3867:1",
    "6:3867:2",
    "6:3870:1",
    "6:3872:2",
    "6:3873:1",
    "6:3875:1",
    "6:3876:1",
    "6:3883:0",
    "6:3883:2",
    "6:3886:1",
    "6:3886:2",
    "6:3887:1",
    "6:3888:0",
    "6:3888:2",
)
BOUNDARY_RECORD_IDS = tuple(range(3866, 3912))
RUNTIME_GAP_ANOMALY_RECORD_ID = 3887

EXPECTED_SOURCE_GAPS_BY_RECORD = {
    3867: (
        "01431D000000",
        "025032",
        "023C",
        "014308020000050505",
    ),
    3870: ("", "023C", "050505"),
    3872: ("025032", "026432", "023C", "050505"),
    3873: ("025032", "023C", "050505"),
    3875: ("", "023C", "050505"),
    3876: ("", "023C", "050505"),
    3880: ("", "023C", "050505"),
    3881: ("", "023C", "050505"),
    3883: (
        "",
        "01431A020000",
        "023C",
        "014366040000050505",
    ),
    3886: (
        "023C",
        "0143F6010000",
        "0143480400000143FC010000",
        "0143B8030000050505",
    ),
    3887: (
        "023C",
        "0143D0030000",
        "0143F0010000050505",
    ),
    3888: (
        "",
        "023C",
        "0143D2010000",
        "0143F6010000050505",
    ),
}
EXPECTED_CURRENT_GAPS_BY_RECORD = {
    **EXPECTED_SOURCE_GAPS_BY_RECORD,
    3887: ("023C", "", "050505"),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = {
    3867: ((29, 520), ("025032", "023C")),
    3870: ((), ("023C",)),
    3872: ((), ("025032", "026432", "023C")),
    3873: ((), ("025032", "023C")),
    3875: ((), ("023C",)),
    3876: ((), ("023C",)),
    3880: ((), ("023C",)),
    3881: ((), ("023C",)),
    3883: ((538, 1126), ("023C",)),
    3886: ((502, 1096, 508, 952), ("023C",)),
    3887: ((976, 496), ("023C",)),
    3888: ((466, 502), ("023C",)),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_SOURCE_CONTROLS_BY_RECORD,
    3887: ((), ("023C",)),
}
EXPECTED_MANUAL_COMPLETED_RECORDS = {
    3880: (
        "봉행 변경으로 정책「",
        "」의 발전을 중단",
    ),
    3881: (
        "봉행 변경으로 정책「",
        "」을(를) 철회",
    ),
}

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "F93A4F340DD30519D26AB0C2F507A3753DAAF7D9D762ED8C4E080FCE5106B248"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "4C4BFFE0C5D82916758F501C5CC8099AE44A91D1C87DC25878634486EAAAD247"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "F1CC3C20A8F50D915F988701371798AA6B069E677A4B22C84B33B2010361A602"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "F314F937926194899E3BD133B29D37B8C05577DF5A55849AD829B1E1106E01D9"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "081DAFAEBEAE04DF50C8D0676C83F23EAD0BCF35397871F6F3946691CFD7E1DE"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "EC93C434BC590D761C8E72EE81C3A33E5AF8AFFD1F3D6999C8EFBD6F96F88AA2"
)
EXPECTED_BOUNDARY_SHA256 = (
    "C29E9E1B8A584AB874F692DF4D94A571045C8064BEA02C72DEF72A77F90E72F6"
)
EXPECTED_RUNTIME_CONTRACT_SHA256 = (
    "6336B90626E9AC5FCFDE69D8FC46E753B5F26D294EA22AB36D43EFBDCEF5F726"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "C9A1B5B5D2DA7764005D37FFBF9132113DAED8457511CC1100647F7F05B0BAAB"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "44E528FF8369C20465AC9DC39136E32DB9ACAFAD06A81841547579AAECE84829"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "9114A445D184B3F97BD99EB511C898805E690267A130743A782D9EA55D97E8A4"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "2508C64615BE908F005CF117145F3367558502E63FA56688D900D70B50A991C4"
)
EXPECTED_REGISTER_POLICY_SHA256 = (
    "D74D8844722F22EA4A582BA9E5B7EE8706A4B250895E3791EECA9CC1E7E76C36"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "879AA6081D9B91C7B6D7C8A98F7545A392E4AA2A5AD2D4A37C201FF35A7E2E0D"
)
EXPECTED_CANDIDATE_SHA256 = (
    "49B2CE37B31F4152DE5D8913A49AD523539EE7D81795D1224B5527101FDCDD5D"
)
EXPECTED_COMPLETE_RUNTIME_ASSEMBLY_SHA256 = (
    "098E21F0513D1D94662A49B8CC0B903948E277C710A9294578B7F8744C13F0CA"
)
EXPECTED_COMPLETE_RUNTIME_RECORD_SHA256 = (
    "290E5692BD4B6DBD047F83745D07E4AEFDB3C194C98E0A351CB93822BE4E058D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 13

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; fifty-two Base exact-reuse "
    "prefill rows and fifteen residual rows cover the assigned sixty-"
    "seven visible literals; twelve complete multi-literal records are "
    "assembled with fourteen prefill companions; ten record-specific "
    "Base semantic donors are exact under reviewed PK/Base call-operand "
    "remapping, while two PK-only policy records use completed Base policy "
    "syntax plus the project withdrawal glossary; Base runtime state is "
    "not inherited; court appointment, request acceptance, policy, "
    "overseer, construction, reward, castle-town and posterity terminology "
    "and formal, surprised, administrative, assertive and civic registers "
    "are reviewed; source-style corner quotes replace broken current smart "
    "quotes; pristine PK direct calls, dynamic person, request, policy and "
    "construction tokens, protected whitespace, line counts, boundaries, "
    "reverse overlay, two-run reproduction, tamper rejection, outside-"
    "scope records and read-only inputs are guarded; current Korean record "
    "3887 is explicitly anomalous because it lost pristine PK calls 976 "
    "and 496, so a source-gap in-memory complete assembly is verified but "
    "runtime promotion remains forbidden until that record repair is "
    "integrated; all fifteen dynamic fragments remain runtime pending"
)
DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = load_module(
    "pc_dialogue_full_retranslation_v0150_pk_s1131_common",
    COMMON_PATH,
)
FORMAT = load_module(
    "pc_dialogue_full_retranslation_v0150_pk_s1131_format",
    FORMAT_PATH,
)
ENGINE = COMMON.ENGINE
sha256_bytes = COMMON.sha256_bytes
canonical_sha256 = COMMON.canonical_sha256
coordinate_key = COMMON.coordinate_key
literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
read_jsonl = COMMON.read_jsonl
context_records = COMMON.context_records


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def guarded_raw_digest(label: str, value: bytes, expected: str) -> str:
    actual = sha256_bytes(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
    paths = (
        (BASE_PROMOTED,)
        if resource == "base_msggame"
        else tuple(
            sorted(
                DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
            )
        )
    )
    result: dict[str, dict[str, Any]] = {}
    for path in paths:
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if row.get("resource") == resource and isinstance(coordinate, str):
                result[coordinate] = row
    return result


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 113
        or len(visible) != 199
        or visible[0] != f"6:{QUEUE_FIRST_RECORD}:0"
        or visible[-1] != f"6:{QUEUE_LAST_RECORD}:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B040 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3867:0"
        or queue_slice[-1] != "6:3910:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "EXPECTED_QUEUE_SLICE_SHA256",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 52:
        raise RuntimeError(f"segment {SEGMENT} prefill count drifted")
    guarded_digest(
        "EXPECTED_PREFILLED_COORDINATE_SHA256",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def runtime_controls(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    calls = tuple(
        int.from_bytes(match.group(1), "little")
        for value in gaps
        for match in DIRECT_CALL_RE.finditer(value)
    )
    inline = tuple(
        value.hex().upper() for value in gaps if value.startswith(b"\x02")
    )
    return calls, inline


def masked_gaps(record: Any) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01\x43.{4}",
            b"\x01\x43\xFF\xFF\xFF\xFF",
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gap_bytes(record)
    )


def assert_expected_runtime_record(
    record: Any,
    record_id: int,
    source: bool,
) -> None:
    expected_gaps = (
        EXPECTED_SOURCE_GAPS_BY_RECORD
        if source
        else EXPECTED_CURRENT_GAPS_BY_RECORD
    )[record_id]
    expected_controls = (
        EXPECTED_SOURCE_CONTROLS_BY_RECORD
        if source
        else EXPECTED_CURRENT_CONTROLS_BY_RECORD
    )[record_id]
    if (
        tuple(value.hex().upper() for value in gap_bytes(record))
        != expected_gaps
        or runtime_controls(record) != expected_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime record drifted: "
            f"{record_id}:{source}"
        )


def assert_context_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"], coordinate_key(coordinate)[:2]
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"], coordinate_key(coordinate)[:2]
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in TARGET_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records_by_label[label], (BLOCK_ID, record_id)
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    runtime_contract = tuple(
        (
            label,
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
            masked_gaps(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        (
            "EXPECTED_SOURCE_TARGET_SHA256",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "EXPECTED_CURRENT_TARGET_SHA256",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "EXPECTED_CONTEXT_CORPUS_SHA256",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "EXPECTED_BOUNDARY_SHA256",
            boundary,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "EXPECTED_RUNTIME_CONTRACT_SHA256",
            runtime_contract,
            EXPECTED_RUNTIME_CONTRACT_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    for record_id in TARGET_RECORD_IDS:
        assert_expected_runtime_record(
            records_by_label["jp"][(BLOCK_ID, record_id)],
            record_id,
            True,
        )
        assert_expected_runtime_record(
            records_by_label["current"][(BLOCK_ID, record_id)],
            record_id,
            False,
        )
    unequal = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if gap_bytes(records_by_label["jp"][(BLOCK_ID, record_id)])
        != gap_bytes(records_by_label["current"][(BLOCK_ID, record_id)])
    )
    if unequal != (RUNTIME_GAP_ANOMALY_RECORD_ID,):
        raise RuntimeError(
            f"segment {SEGMENT} runtime anomaly set drifted: {unequal}"
        )


def base_translation_tuple(
    base_rows: dict[str, dict[str, Any]],
    base_record_id: int,
    arity: int,
) -> tuple[str, ...]:
    values: list[str] = []
    for literal_id in range(arity):
        coordinate = f"6:{base_record_id}:{literal_id}"
        row = base_rows.get(coordinate)
        if row is None:
            raise RuntimeError(
                f"segment {SEGMENT} missing Base decision: {coordinate}"
            )
        values.append(str(row["translation"]))
    return tuple(values)


def assert_base_companions_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[tuple[int, int, int], str]:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_rows = decision_map("base_msggame")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    companion_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    complete_replacements: dict[tuple[int, int, int], str] = {}
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        pk_literals = literal_texts(
            records_by_label["jp"], (BLOCK_ID, record_id)
        )
        if record_id in EXACT_BASE_RECORD_MAPPING:
            base_record_id = EXACT_BASE_RECORD_MAPPING[record_id]
            base_record = base_source[(BLOCK_ID, base_record_id)]
            base_literals = literal_texts(
                base_source, (BLOCK_ID, base_record_id)
            )
            base_translations = base_translation_tuple(
                base_rows, base_record_id, len(base_literals)
            )
            if (
                pk_literals != base_literals
                or masked_gaps(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
                != masked_gaps(base_record)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base donor drifted: {record_id}"
                )
            base_evidence.append(
                (
                    record_id,
                    base_record_id,
                    sha256_bytes(
                        records_by_label["jp"][(BLOCK_ID, record_id)].data
                    ),
                    sha256_bytes(base_record.data),
                    pk_literals,
                    base_literals,
                    base_translations,
                    runtime_controls(
                        records_by_label["jp"][(BLOCK_ID, record_id)]
                    ),
                    runtime_controls(base_record),
                )
            )
        else:
            base_record_id = None
            base_translations = EXPECTED_MANUAL_COMPLETED_RECORDS[record_id]
            base_evidence.append(
                (
                    record_id,
                    None,
                    sha256_bytes(
                        records_by_label["jp"][(BLOCK_ID, record_id)].data
                    ),
                    pk_literals,
                    base_translations,
                    tuple(
                        BASE_CONTEXT_REFERENCES[
                            f"6:{record_id}:{literal_id}"
                        ]
                        for literal_id in range(len(pk_literals))
                    ),
                )
            )

        owners: list[str] = []
        completed: list[str] = []
        for literal_id in range(len(pk_literals)):
            coordinate = f"6:{record_id}:{literal_id}"
            key = (BLOCK_ID, record_id, literal_id)
            if coordinate in TRANSLATIONS:
                translation = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                if row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                translation = str(row["translation"])
                owner = "prefill"
                seen_prefill.add(coordinate)
                companion_evidence.append(
                    (
                        coordinate,
                        translation,
                        str(row["source_record_raw_sha256"]),
                        str(row["current_ko_utf16le_sha256"]),
                    )
                )
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: {coordinate}"
                )
            owners.append(owner)
            completed.append(translation)
            complete_replacements[key] = translation
        if tuple(completed) != tuple(base_translations):
            raise RuntimeError(
                f"segment {SEGMENT} complete wording drifted: {record_id}"
            )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(completed),
                runtime_controls(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                ),
                runtime_controls(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                ),
                record_id == RUNTIME_GAP_ANOMALY_RECORD_ID,
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "EXPECTED_BASE_CONTEXT_SHA256",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "EXPECTED_PREFILL_COMPANION_SHA256",
        tuple(companion_evidence),
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    guarded_digest(
        "EXPECTED_ASSEMBLY_POLICY_SHA256",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )
    return complete_replacements


def runtime_category(record_id: int) -> str:
    return {
        3867: "court_appointment_honor",
        3870: "appointment_refusal_surprise",
        3872: "request_acceptance_target",
        3873: "request_acceptance_origin",
        3875: "policy_development_complete",
        3876: "policy_development_stop",
        3880: "overseer_change_development_stop",
        3881: "overseer_change_policy_withdrawal",
        3883: "construction_acceptance_civic",
        3886: "construction_reward_exhortation",
        3887: "construction_castle_town_anomalous_gap",
        3888: "construction_posterity",
    }[record_id]


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "EXPECTED_TARGET_COORDINATE_SHA256",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TRANSLATION_POLICY_SHA256",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    terminology = (
        ("court_order", "분부"),
        ("great_duty", "대임"),
        ("request", "요청"),
        ("policy", "정책"),
        ("overseer", "봉행"),
        ("development_stop", "발전을 중단"),
        ("policy_withdrawal", "정책을 철회"),
        ("construction", "건설"),
        ("castle_town", "성하"),
        ("posterity", "후세"),
    )
    guarded_digest(
        "EXPECTED_TERMINOLOGY_POLICY_SHA256",
        terminology,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    register_policy = tuple(
        (
            record_id,
            runtime_category(record_id),
            "runtime_fragment_pending",
            "pending",
            "runtime_pending",
            record_id in MANUAL_CONTEXT_RECORD_IDS,
            record_id == RUNTIME_GAP_ANOMALY_RECORD_ID,
            False,
        )
        for record_id in TARGET_RECORD_IDS
    )
    guarded_digest(
        "EXPECTED_REGISTER_POLICY_SHA256",
        register_policy,
        EXPECTED_REGISTER_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"], (block_id, record_id)
        )[literal_id]
        shape_baseline = (
            literal_texts(
                records_by_label["jp"], (block_id, record_id)
            )[literal_id]
            if record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            else current_text
        )
        ENGINE.validate_translation_shape(
            shape_baseline,
            translation,
            "runtime_pending",
            coordinate,
        )
        if translation.count("\n") != current_text.count("\n"):
            raise RuntimeError(
                f"segment {SEGMENT} line count drifted: {coordinate}"
            )
        if (
            record_id != RUNTIME_GAP_ANOMALY_RECORD_ID
            and ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected shape drifted: {coordinate}"
            )
        if (
            record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            and (
                translation.startswith((" ", "\n", "\t"))
                or not current_text.startswith(" ")
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} anomaly spacing policy drifted"
            )


def assert_candidate_records(
    current_records: dict[tuple[int, int], Any],
    candidate_records: dict[tuple[int, int], Any],
    repaired_runtime: bool,
) -> None:
    target_keys = {
        (BLOCK_ID, record_id) for record_id in TARGET_RECORD_IDS
    }
    if (
        len(current_records) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(f"segment {SEGMENT} candidate universe drifted")
    for key, record in current_records.items():
        if (
            key not in target_keys
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed outside scope: {key}"
            )
    for key in target_keys:
        record_id = key[1]
        expected = (
            EXPECTED_SOURCE_GAPS_BY_RECORD[record_id]
            if repaired_runtime
            and record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            else EXPECTED_CURRENT_GAPS_BY_RECORD[record_id]
        )
        if (
            tuple(
                value.hex().upper()
                for value in gap_bytes(candidate_records[key])
            )
            != expected
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate gap drifted: {key}"
            )


def build_candidates(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    complete_replacements: dict[tuple[int, int, int], str],
) -> tuple[bytes, str, int, bytes, Any]:
    resource = prepared.resources["pk_msggame"]
    current_records = records_by_label["current"]
    replacements = {
        coordinate_key(coordinate): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: literal_texts(current_records, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob, replacements
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    assert_candidate_records(current_records, candidate_records, False)
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        if (
            literal_texts(candidate_records, key[:2])[key[2]]
            != translation
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate literal drifted: {coordinate}"
            )
    if (
        ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != resource.current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} reverse overlay drifted")
    changed = sum(
        translation != reverse[key]
        for key, translation in replacements.items()
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed literal count drifted: {changed}"
        )
    candidate_sha256 = guarded_raw_digest(
        "EXPECTED_CANDIDATE_SHA256",
        candidate,
        EXPECTED_CANDIDATE_SHA256,
    )

    complete_reverse = {
        key: literal_texts(current_records, key[:2])[key[2]]
        for key in complete_replacements
    }
    literal_complete_candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob, complete_replacements
    )
    literal_complete_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(literal_complete_candidate).archive
    )
    assert_candidate_records(
        current_records, literal_complete_records, False
    )
    anomaly_keys = {
        key: translation
        for key, translation in complete_replacements.items()
        if key[:2] == (BLOCK_ID, RUNTIME_GAP_ANOMALY_RECORD_ID)
    }
    source_assembled = ENGINE.rebuild_packed_with_literals(
        resource.pristine_blob, anomaly_keys
    )
    source_assembled_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(source_assembled).archive
    )
    source_assembled_record = source_assembled_records[
        (BLOCK_ID, RUNTIME_GAP_ANOMALY_RECORD_ID)
    ]
    complete_runtime_candidate = FORMAT.rebuild_packed_msggame(
        literal_complete_candidate,
        {
            (
                BLOCK_ID,
                RUNTIME_GAP_ANOMALY_RECORD_ID,
            ): source_assembled_record.data
        },
    )
    complete_runtime_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(complete_runtime_candidate).archive
    )
    assert_candidate_records(
        current_records, complete_runtime_records, True
    )
    for key, translation in complete_replacements.items():
        if (
            literal_texts(complete_runtime_records, key[:2])[key[2]]
            != translation
        ):
            raise RuntimeError(
                f"segment {SEGMENT} complete assembly drifted: {key}"
            )
    anomaly_record = complete_runtime_records[
        (BLOCK_ID, RUNTIME_GAP_ANOMALY_RECORD_ID)
    ]
    assert_expected_runtime_record(
        anomaly_record,
        RUNTIME_GAP_ANOMALY_RECORD_ID,
        True,
    )
    reverse_runtime_repair = FORMAT.rebuild_packed_msggame(
        complete_runtime_candidate,
        {
            (
                BLOCK_ID,
                RUNTIME_GAP_ANOMALY_RECORD_ID,
            ): literal_complete_records[
                (BLOCK_ID, RUNTIME_GAP_ANOMALY_RECORD_ID)
            ].data
        },
    )
    if reverse_runtime_repair != literal_complete_candidate:
        raise RuntimeError(
            f"segment {SEGMENT} runtime repair reverse drifted"
        )
    if (
        ENGINE.rebuild_packed_with_literals(
            literal_complete_candidate, complete_reverse
        )
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} complete literal reverse drifted"
        )
    guarded_raw_digest(
        "EXPECTED_COMPLETE_RUNTIME_ASSEMBLY_SHA256",
        complete_runtime_candidate,
        EXPECTED_COMPLETE_RUNTIME_ASSEMBLY_SHA256,
    )
    guarded_raw_digest(
        "EXPECTED_COMPLETE_RUNTIME_RECORD_SHA256",
        anomaly_record.data,
        EXPECTED_COMPLETE_RUNTIME_RECORD_SHA256,
    )
    return (
        candidate,
        candidate_sha256,
        changed,
        complete_runtime_candidate,
        anomaly_record,
    )


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    assert_expected_runtime_record(source, record_id, True)
    assert_expected_runtime_record(current, record_id, False)
    return {
        "runtime_category": runtime_category(record_id),
        "source_record_gap_sha256": canonical_sha256(
            EXPECTED_SOURCE_GAPS_BY_RECORD[record_id]
        ),
        "current_record_gap_sha256": canonical_sha256(
            EXPECTED_CURRENT_GAPS_BY_RECORD[record_id]
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "current_runtime_gap_anomaly":
        record_id == RUNTIME_GAP_ANOMALY_RECORD_ID,
        "missing_current_call_operands":
        (
            source_controls[0]
            if record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            else ()
        ),
        "source_runtime_gap_repair_required":
        record_id == RUNTIME_GAP_ANOMALY_RECORD_ID,
        "source_runtime_gap_repair_integrated_for_evidence_only":
        record_id == RUNTIME_GAP_ANOMALY_RECORD_ID,
        "source_runtime_gap_repair_evidence_schema":
        (
            ENGINE.SOURCE_OUTER_WHITESPACE_REPAIR_EVIDENCE_SCHEMA
            if record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            else None
        ),
        "source_runtime_gap_repair_builder":
        (
            "build_pk_runtime_gap_repair_3887.py"
            if record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            else None
        ),
        "source_runtime_gap_repair_record_coordinate":
        (
            f"{BLOCK_ID}:{record_id}"
            if record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            else None
        ),
        "source_runtime_gap_repair_source_record_sha256":
        (
            sha256_bytes(source.data)
            if record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            else None
        ),
        "source_runtime_gap_repair_current_record_sha256":
        (
            sha256_bytes(current.data)
            if record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            else None
        ),
        "source_runtime_gap_repair_candidate_record_sha256":
        (
            EXPECTED_COMPLETE_RUNTIME_RECORD_SHA256
            if record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
            else None
        ),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companions_reviewed": True,
        "protected_outer_whitespace_preserved":
        record_id != RUNTIME_GAP_ANOMALY_RECORD_ID,
        "source_outer_whitespace_restored":
        record_id == RUNTIME_GAP_ANOMALY_RECORD_ID,
        "source_style_corner_quotes_restored":
        record_id in MANUAL_CONTEXT_RECORD_IDS,
        "base_wording_contextually_adapted":
        record_id in MANUAL_CONTEXT_RECORD_IDS,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    bytes,
    Any,
    tuple[str, ...],
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    complete_replacements = assert_base_companions_and_assembly(
        prepared, records_by_label
    )
    assert_semantics(records_by_label)
    (
        candidate,
        candidate_sha256,
        changed,
        complete_runtime_candidate,
        complete_runtime_record,
    ) = build_candidates(
        prepared, records_by_label, complete_replacements
    )
    if DISCOVERED_PINS:
        return (
            prepared,
            [],
            candidate,
            candidate_sha256,
            changed,
            complete_runtime_candidate,
            complete_runtime_record,
            optional_present,
        )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"], (block_id, record_id)
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_record_literals_reviewed": True,
                "prefill_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved":
                record_id != RUNTIME_GAP_ANOMALY_RECORD_ID,
                **(
                    {"source_outer_whitespace_restored": True}
                    if record_id == RUNTIME_GAP_ANOMALY_RECORD_ID
                    else {}
                ),
                "source_style_corner_quotes_restored":
                record_id in MANUAL_CONTEXT_RECORD_IDS,
                "base_wording_contextually_adapted":
                record_id in MANUAL_CONTEXT_RECORD_IDS,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(records_by_label, record_id),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        complete_runtime_candidate,
        complete_runtime_record,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
    complete_runtime_record: Any,
) -> None:
    def expect_decision_rejection(
        name: str, tampered: list[dict[str, Any]]
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix=f"pk-s1131-{name}-", dir=DECISIONS_ROOT
        ) as directory:
            tampered_path = (
                Path(directory) / "tampered.private.v1.jsonl"
            )
            ENGINE.atomic_write(
                tampered_path, ENGINE.jsonl(tampered)
            )
            try:
                ENGINE.validate_decisions(
                    prepared, tampered_path, require_complete=False
                )
            except ENGINE.RetranslationError:
                return
        raise RuntimeError(
            f"segment {SEGMENT} {name} tamper was accepted"
        )

    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    expect_decision_rejection("source", tampered_rows)
    anomaly_index = next(
        index
        for index, row in enumerate(rows)
        if row["coordinate"] == "6:3887:0"
    )

    false_flag_rows = copy.deepcopy(rows)
    false_flag_rows[anomaly_index][
        "source_outer_whitespace_restored"
    ] = False
    expect_decision_rejection("false-flag", false_flag_rows)

    other_coordinate_rows = copy.deepcopy(rows)
    other_coordinate_rows[0][
        "source_outer_whitespace_restored"
    ] = True
    other_coordinate_rows[0][
        "runtime_assembly_evidence"
    ] = copy.deepcopy(
        rows[anomaly_index]["runtime_assembly_evidence"]
    )
    expect_decision_rejection(
        "other-coordinate-flag", other_coordinate_rows
    )

    missing_evidence_rows = copy.deepcopy(rows)
    del missing_evidence_rows[anomaly_index][
        "runtime_assembly_evidence"
    ]["source_runtime_gap_repair_candidate_record_sha256"]
    expect_decision_rejection(
        "missing-repair-evidence", missing_evidence_rows
    )

    whitespace_rows = copy.deepcopy(rows)
    whitespace_rows[anomaly_index]["translation"] = (
        " " + whitespace_rows[anomaly_index]["translation"]
    )
    expect_decision_rejection(
        "arbitrary-whitespace", whitespace_rows
    )

    tampered_policy = dict(TRANSLATIONS)
    tampered_policy[TARGET_COORDINATES[0]] += "X"
    if (
        canonical_sha256(tuple(tampered_policy.items()))
        == EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} policy tamper was accepted"
        )
    tampered_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        {
            coordinate_key(coordinate): translation
            for coordinate, translation in tampered_policy.items()
        },
    )
    if (
        tampered_candidate == candidate
        or sha256_bytes(tampered_candidate)
        == EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate tamper was accepted"
        )
    current_record = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )[(BLOCK_ID, RUNTIME_GAP_ANOMALY_RECORD_ID)]
    try:
        assert_expected_runtime_record(
            current_record,
            RUNTIME_GAP_ANOMALY_RECORD_ID,
            True,
        )
    except RuntimeError:
        pass
    else:
        raise RuntimeError(
            f"segment {SEGMENT} missing-call tamper was accepted"
        )
    tampered_runtime = bytearray(complete_runtime_record.data)
    call = bytes.fromhex("0143D0030000")
    offset = tampered_runtime.find(call)
    if offset < 0:
        raise RuntimeError(f"segment {SEGMENT} repaired call is absent")
    tampered_runtime[offset + 2] ^= 0x01
    tampered_record = type(complete_runtime_record)(
        block_id=complete_runtime_record.block_id,
        record_id=complete_runtime_record.record_id,
        relative_offset=complete_runtime_record.relative_offset,
        data=bytes(tampered_runtime),
    )
    try:
        assert_expected_runtime_record(
            tampered_record,
            RUNTIME_GAP_ANOMALY_RECORD_ID,
            True,
        )
    except RuntimeError:
        pass
    else:
        raise RuntimeError(
            f"segment {SEGMENT} repaired-call tamper was accepted"
        )


def main() -> int:
    first = build_rows()
    if DISCOVERED_PINS:
        print(
            json.dumps(
                DISCOVERED_PINS,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        complete_runtime_candidate,
        complete_runtime_record,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or complete_runtime_candidate != second[5]
        or complete_runtime_record.data != second[6].data
        or optional_present != second[7]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    steam_path = prepared.resources["pk_msggame"].current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    anomaly_rows = [
        row
        for row in rows
        if row["runtime_assembly_evidence"][
            "current_runtime_gap_anomaly"
        ]
    ]
    if (
        len(rows) != 15
        or len(validated) != 15
        or counts != Counter({"runtime_fragment_pending": 15})
        or len(anomaly_rows) != 1
        or anomaly_rows[0]["coordinate"] != "6:3887:0"
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(
        prepared, rows, candidate, complete_runtime_record
    )
    if sha256_bytes(steam_path.read_bytes()) != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B040_S1131",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 52,
                "base_semantic_reference_count": len(rows),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "complete_runtime_assembly_sha256":
                EXPECTED_COMPLETE_RUNTIME_ASSEMBLY_SHA256,
                "complete_runtime_record_sha256":
                EXPECTED_COMPLETE_RUNTIME_RECORD_SHA256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "runtime_gap_anomaly_coordinate": "6:3887:0",
                "runtime_gap_anomaly_record": "6:3887",
                "missing_current_call_operands": [976, 496],
                "source_runtime_gap_repair_required": True,
                "source_runtime_gap_repair_integrated_for_evidence_only":
                True,
                "runtime_repair_release_integrated": False,
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_only": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "prefill_companions_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "direct_calls_and_tokens_guarded": True,
                "source_outer_whitespace_restored_for_anomaly": True,
                "source_style_corner_quotes_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact_or_anomaly_repaired_for_evidence":
                True,
                "protected_signatures_exact_except_source_restoration":
                True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "runtime_repair_reverse_exact": True,
                "complete_assembly_reverse_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "runtime_promotion_authorized": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
