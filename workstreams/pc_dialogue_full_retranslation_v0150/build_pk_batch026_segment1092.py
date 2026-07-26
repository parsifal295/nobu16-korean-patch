#!/usr/bin/env python3
"""Build source-redacted PK B026 segment 1092 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch024_segment1089.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B026_S1092.private.v1.jsonl"
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
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B024_S1089.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B024_S1090.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B025_S1091.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B026_S1093.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B026_S1094.private.v1.jsonl",
)

SEGMENT = 1092
QUEUE_BATCH_ID = "pk_msggame-B026"
QUEUE_START = 0
QUEUE_STOP = 66
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

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


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1092_common",
        COMMON_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {COMMON_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = load_common()
ENGINE = COMMON.ENGINE
sha256_bytes = COMMON.sha256_bytes
canonical_sha256 = COMMON.canonical_sha256
coordinate_key = COMMON.coordinate_key
literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
read_jsonl = COMMON.read_jsonl
context_records = COMMON.context_records

TARGET_COORDINATES = (
    "6:2061:0",
    "6:2063:0",
    "6:2064:1",
    "6:2065:0",
    "6:2066:0",
    "6:2067:1",
    "6:2068:0",
    "6:2069:0",
    "6:2070:0",
    "6:2071:0",
    "6:2072:0",
    "6:2073:0",
    "6:2074:0",
    "6:2074:3",
    "6:2075:0",
    "6:2075:1",
)
TRANSLATIONS = {
    "6:2061:0": "의 지침 「",
    "6:2063:0": "의 「",
    "6:2064:1": "의 지침\n「",
    "6:2065:0": "의 지침 「",
    "6:2066:0": "의 「",
    "6:2067:1": "의 지침\n「",
    "6:2068:0": "「",
    "6:2069:0": "의 지침 「",
    "6:2070:0": "의 지침 「",
    "6:2071:0": "의 「",
    "6:2072:0": "의 「",
    "6:2073:0": "의 지침 「",
    "6:2074:0": "의 지침 「",
    "6:2074:3": "인가",
    "6:2075:0": "의 「",
    "6:2075:1": "」 등",
}
TARGET_RECORD_IDS = tuple(
    dict.fromkeys(coordinate_key(value)[1] for value in TARGET_COORDINATES)
)
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
SLICE_RECORD_IDS = tuple(range(2032, 2077))
BOUNDARY_RECORD_IDS = (2031, 2077)
ALLOTMENT_RECORD_IDS = (2059, 2060)
POLICY_RECORD_IDS = tuple(range(2061, 2077))
RUNTIME_RECORD_IDS = (*ALLOTMENT_RECORD_IDS, *POLICY_RECORD_IDS)
DIRECT_CALL_RECORD_IDS = (2074,)
BASE_RECORD_MAPPING = {
    record_id: record_id - 6 for record_id in SLICE_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[coordinate_key(coordinate)[1]]}:"
        f"{coordinate_key(coordinate)[2]}"
    )
    for coordinate in TARGET_COORDINATES
}

EXPECTED_GAPS_BY_RECORD = {
    **{
        record_id: ("", "050505")
        for record_id in range(2032, 2059)
    },
    2059: ("024633", "0232050505"),
    2060: ("024633", "0232050505"),
    2061: ("025A32", "023C", "050505"),
    2062: ("025A32", "023C", "050505"),
    2063: ("025A32", "023C", "050505"),
    2064: ("", "025A32", "023C", "050505"),
    2065: ("025A32", "023C", "050505"),
    2066: ("025A32", "023C", "050505"),
    2067: ("", "025A32", "023C", "050505"),
    2068: ("", "023C", "050505"),
    2069: ("025A32", "023C", "050505"),
    2070: ("025A32", "023C", "050505"),
    2071: ("025A32", "023C", "050505"),
    2072: ("025A32", "023C", "050505"),
    2073: ("025A32", "023C", "050505"),
    2074: (
        "025A32",
        "023C",
        "014374020000",
        "0143BC020000014362020000",
        "050505",
    ),
    2075: ("025A32", "023C", "0232", "050505"),
    2076: ("025A32", "0232", "050505"),
}
EXPECTED_BASE_2074_GAPS = (
    "025A32",
    "023C",
    "014368020000",
    "0143B0020000014356020000",
    "050505",
)
EXPECTED_2074_MASKED_GAPS = (
    "025A32",
    "023C",
    "014300000000",
    "014300000000014300000000",
    "050505",
)
EXPECTED_DIRECT_CALL_OPERANDS = {2074: (628, 700, 610)}
EXPECTED_BASE_DIRECT_CALL_OPERANDS = {2068: (616, 688, 598)}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "BF4973D05BCB25A2C936DB49BB9AFE163466866D562BC521176F2C8D40B661DC"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "288CAC7623D9A12844B9BFAAAC2DF724A35E40A1F835BE3AADC874EFA1BBAB92"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "0809201D404E5836CBC1779D9B1FB8C1F3CEF4B742D7608BA59256E16D0804CC"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "619E787F5B3E5982967A85EE97C61C50946F9D922D28FD3BD4A2061666EB56F8"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "B630B0262DA9B26AE0FAE4D65F799D37A7F8B685B43C6DA33EB53F445A6F5B14"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "E29640F6C9A82096E59808C7EC3ADB4A9BBDFEE6D30837EAB9219BAB045A7D71"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "4C0CA0850064211ED959327CEF0A98B400363E128F19A6F0789FB7E84CDE5670"
)
EXPECTED_BOUNDARY_SHA256 = (
    "9FAB422970A46FEC5BAA0BF70CB0AB1BB2BDB9834CAD564CAA8965C69DE8D9E5"
)
EXPECTED_DIRECT_CALL_SHA256 = (
    "0B603D1285EA082B1255B21523464593680027F0F93E85626DE833D67A4F3119"
)
EXPECTED_BASE_EXACT_RECORD_SHA256 = (
    "108A7C6C37D09D9777B4F57DF8F6D15ABD183C8E73A3B72C9E855B873CBA3CA8"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "49DEDFCF5B7F72BF44C42B69CEEF26CDEE151066F43553BD7A3D41F55F8F3793"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "9FBC099539BAB8F01512E13EA32AB17240EDAB1F1239CE76E2F86A611F593719"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "D14C2AFD033AA57E9C207EBA1283668A2310A6543FC811F2B7D94158449F34EC"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "90F8C538619FC072AD7D92646134E53C416248BCCDC4CA278C1BA590BE680575"
)
EXPECTED_CANDIDATE_SHA256 = (
    "8F751799F88F97261E16B62E1DA32E2E655755D5441ABFC2C1EE53F8D5FEFC20"
)
EXPECTED_CHANGED_LITERAL_COUNT = 8

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; all fifty exact-reuse prefill "
    "rows and all sixteen residual fragments in the sixty-six-literal "
    "queue slice are pinned to completed Base semantic donors; all "
    "forty-five slice records are reconstructed without current-text "
    "fallback; retainer allegiance, new-lord, stipend allotment, loyalty "
    "and policy terminology and twelve speaker registers are reviewed; "
    "the PK-only three-direct-call policy question keeps operands 628, "
    "700 and 610 while the exact Base semantic donor uses 616, 688 and "
    "598; source/current opcode gaps, protected signatures, line counts, "
    "complete multi-literal assembly, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are guarded; "
    "Base runtime state is never inherited and every residual PK "
    "fragment remains runtime pending"
)


def patch_common_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(COMMON, name, value)
    COMMON.patch_common_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def decision_map(
    resource: str,
    exclude_output: bool,
) -> dict[str, dict[str, Any]]:
    paths = (
        (BASE_PROMOTED,)
        if resource == "base_msggame"
        else tuple(
            sorted(
                DECISIONS_ROOT.glob(
                    "pk_msggame_*.private.v1.jsonl"
                )
            )
        )
    )
    result: dict[str, dict[str, Any]] = {}
    for path in paths:
        if (
            exclude_output
            and path.resolve(strict=False)
            == OUTPUT.resolve(strict=False)
        ):
            continue
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") == resource
                and isinstance(coordinate, str)
            ):
                previous = result.setdefault(coordinate, row)
                if previous is not row:
                    raise RuntimeError(
                        f"segment {SEGMENT} duplicate decision: "
                        f"{coordinate}"
                    )
    return result


def direct_call_operands(record: Any) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gap_bytes(record)
        for match in re.finditer(b"\x01\x43(.{4})", gap, re.DOTALL)
    )


def masked_gap_tuple(record: Any) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01\x43.{4}",
            b"\x01\x43\x00\x00\x00\x00",
            gap,
            flags=re.DOTALL,
        ).hex().upper()
        for gap in gap_bytes(record)
    )


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pinned source input drifted"
        )
    ENGINE.validate_decisions(
        prepared,
        PREFILL,
        require_complete=False,
    )
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 97
        or len(visible) != 198
        or visible[0] != "6:2032:0"
        or visible[-1] != "6:2128:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B026 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:2032:0"
        or queue_slice[-1] != "6:2076:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue slice boundary drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if len(prefilled) != 50:
        raise RuntimeError(
            f"segment {SEGMENT} prefill count drifted: "
            f"{len(prefilled)}"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )

    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
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
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES or len(residual) != 16:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: "
            f"{len(residual)} rows"
        )
    guarded_digest(
        "target coordinate",
        residual,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )

    optional_present: list[str] = []
    for path in OPTIONAL_PREDECESSORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_context_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    context_ids = tuple(range(2031, 2078))
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in context_ids
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for record_id in SLICE_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    direct_calls = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            direct_call_operands(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            direct_call_operands(
                records_by_label["current"][
                    (BLOCK_ID, record_id)
                ]
            ),
        )
        for record_id in DIRECT_CALL_RECORD_IDS
    )
    for label, value, expected in (
        (
            "source target",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "current target",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "multilingual context",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "gap contract",
            gaps,
            EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "boundary",
            boundary,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "direct call",
            direct_calls,
            EXPECTED_DIRECT_CALL_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)

    if any(source != current for _, source, current in gaps):
        raise RuntimeError(
            f"segment {SEGMENT} source/current gap drifted"
        )
    for record_id, source, current in gaps:
        if (
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current != source
        ):
            raise RuntimeError(
                f"segment {SEGMENT} runtime gap drifted: "
                f"{record_id}"
            )
    actual_direct_records = tuple(
        record_id
        for record_id in SLICE_RECORD_IDS
        if direct_call_operands(
            records_by_label["jp"][
                (BLOCK_ID, record_id)
            ]
        )
    )
    if actual_direct_records != DIRECT_CALL_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} direct call universe drifted"
        )
    if (
        direct_calls[0][2]
        != EXPECTED_DIRECT_CALL_OPERANDS[2074]
        or direct_calls[0][4] != direct_calls[0][2]
        or masked_gap_tuple(
            records_by_label["jp"][(BLOCK_ID, 2074)]
        )
        != EXPECTED_2074_MASKED_GAPS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} direct call operands drifted"
        )


def assert_base_prefill_and_assembly_context(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame", False)
    base_source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }

    exact_records: list[tuple[Any, ...]] = []
    for pk_record_id in SLICE_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[pk_record_id]
        pk_record = records_by_label["jp"][
            (BLOCK_ID, pk_record_id)
        ]
        base_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        pk_sha = sha256_bytes(pk_record.data)
        base_sha = sha256_bytes(base_record.data)
        source_literals_equal = (
            literal_texts(
                records_by_label["jp"],
                (BLOCK_ID, pk_record_id),
            )
            == literal_texts(
                base_source_records,
                (BLOCK_ID, base_record_id),
            )
        )
        raw_equal = pk_sha == base_sha
        exact_records.append(
            (
                pk_record_id,
                base_record_id,
                pk_sha,
                base_sha,
                source_literals_equal,
                raw_equal,
            )
        )
        if (
            not source_literals_equal
            or raw_equal is (pk_record_id == 2074)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base record mapping drifted: "
                f"{pk_record_id}"
            )
    guarded_digest(
        "Base exact record",
        tuple(exact_records),
        EXPECTED_BASE_EXACT_RECORD_SHA256,
    )

    slice_coordinates = tuple(
        f"6:{record_id}:{literal_id}"
        for record_id in SLICE_RECORD_IDS
        for literal_id in range(
            len(
                literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )
            )
        )
    )
    prefill_coordinates = tuple(
        coordinate
        for coordinate in slice_coordinates
        if coordinate in prefill_rows
    )
    prefill_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
        )
        for coordinate in prefill_coordinates
    )
    if (
        len(prefill_coordinates) != 50
        or any(
            semantic != "approved"
            or runtime not in ("pending", "not_required")
            for _, _, semantic, runtime, _, _ in prefill_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill context drifted"
        )
    guarded_digest(
        "prefill context",
        prefill_evidence,
        EXPECTED_PREFILL_CONTEXT_SHA256,
    )

    assembly_evidence: list[tuple[Any, ...]] = []
    base_evidence: list[tuple[Any, ...]] = []
    assembly_map: dict[int, tuple[str, ...]] = {}
    owner_map: dict[int, tuple[str, ...]] = {}
    for record_id in SLICE_RECORD_IDS:
        translations: list[str] = []
        owners: list[str] = []
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        for literal_id, _current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = (
                f"6:{BASE_RECORD_MAPPING[record_id]}:{literal_id}"
            )
            if coordinate in TRANSLATIONS:
                translation = TRANSLATIONS[coordinate]
                owner = "segment"
            elif coordinate in prefill_rows:
                translation = str(
                    prefill_rows[coordinate]["translation"]
                )
                owner = "prefill"
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} current fallback forbidden: "
                    f"{coordinate}"
                )
            base_row = base_rows[base_coordinate]
            expected_base_runtime = (
                "verified"
                if record_id in RUNTIME_RECORD_IDS
                else "not_required"
            )
            if (
                base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review")
                != expected_base_runtime
                or translation != base_row.get("translation")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base donor drifted: "
                    f"{coordinate}"
                )
            translations.append(translation)
            owners.append(owner)
            base_evidence.append(
                (
                    coordinate,
                    base_coordinate,
                    translation,
                    base_row.get("translation"),
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                )
            )
        source_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
        current_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["current"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
        assembly_map[record_id] = tuple(translations)
        owner_map[record_id] = tuple(owners)
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                source_gaps,
                current_gaps,
            )
        )
        if source_gaps != current_gaps:
            raise RuntimeError(
                f"segment {SEGMENT} assembly controls drifted: "
                f"{record_id}"
            )
    if (
        sum(
            owner == "segment"
            for owners in owner_map.values()
            for owner in owners
        )
        != 16
        or sum(
            owner == "prefill"
            for owners in owner_map.values()
            for owner in owners
        )
        != 50
    ):
        raise RuntimeError(
            f"segment {SEGMENT} assembly ownership drifted"
        )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )

    pk_2074 = records_by_label["jp"][(BLOCK_ID, 2074)]
    base_2068 = base_source_records[(BLOCK_ID, 2068)]
    if (
        tuple(
            value.hex().upper()
            for value in gap_bytes(base_2068)
        )
        != EXPECTED_BASE_2074_GAPS
        or masked_gap_tuple(pk_2074)
        != EXPECTED_2074_MASKED_GAPS
        or masked_gap_tuple(base_2068)
        != EXPECTED_2074_MASKED_GAPS
        or direct_call_operands(pk_2074)
        != EXPECTED_DIRECT_CALL_OPERANDS[2074]
        or direct_call_operands(base_2068)
        != EXPECTED_BASE_DIRECT_CALL_OPERANDS[2068]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base direct-call variant drifted"
        )

    if (
        assembly_map[2037]
        != ("대상 세력을 새 주군으로 삼겠다고 청합니다",)
        or assembly_map[2059]
        != ("이(가) 지급받은 지행 수에 불만  충성-",)
        or assembly_map[2060]
        != ("이(가) 지급받은 지행 수에 만족  충성+",)
        or assembly_map[2075]
        != ("의 「", "」 등", "개 지침은 지속 불가")
        or any(
            "방침" in text
            for record_id in POLICY_RECORD_IDS
            for text in assembly_map[record_id]
        )
        or "Gd1.GdName "
        not in assembly_map[2068][1]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} historical terminology drifted"
        )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or len(TARGET_COORDINATES) != 16
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )

    current = records_by_label["current"]
    changed = 0
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            current,
            (block_id, record_id),
        )[literal_id]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )
        changed += translation != current_text
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed policy drifted: {changed}"
        )
    if (
        tuple(
            coordinate
            for coordinate, translation in TRANSLATIONS.items()
            if translation
            != literal_texts(
                current,
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]]
        )
        != (
            "6:2061:0",
            "6:2065:0",
            "6:2067:1",
            "6:2069:0",
            "6:2070:0",
            "6:2073:0",
            "6:2074:0",
            "6:2075:1",
        )
        or any(
            text not in ("의 지침 「", "의 지침\n「")
            for coordinate, text in TRANSLATIONS.items()
            if coordinate
            in {
                "6:2061:0",
                "6:2065:0",
                "6:2067:1",
                "6:2069:0",
                "6:2070:0",
                "6:2073:0",
                "6:2074:0",
            }
        )
        or TRANSLATIONS["6:2075:1"] != "」 등"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} wording policy drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def speaker_register_variant(record_id: int) -> str:
    return {
        2061: "system_policy_status",
        2063: "warrior_formal_o_register",
        2064: "senior_formal_o_register",
        2065: "polite_request_register",
        2066: "old_warrior_o_register",
        2067: "formal_attendant_register",
        2068: "court_attendant_high_register",
        2069: "elder_plain_register",
        2070: "polite_request_register",
        2071: "court_attendant_archaic_register",
        2072: "polite_consultative_register",
        2073: "formal_advisory_register",
        2074: "direct_call_inflected_advisory_register",
        2075: "system_multi_policy_status",
    }[record_id]


def runtime_order(record_id: int) -> tuple[str, ...]:
    if record_id in (2064, 2067):
        return (
            "speaker_intro",
            "policy_owner_025A32",
            "policy_prefix",
            "policy_name_023C",
            "policy_failure_suffix",
        )
    if record_id == 2068:
        return (
            "opening_quote",
            "policy_name_023C",
            "gd1_name_and_court_report_suffix",
        )
    if record_id == 2074:
        return (
            "policy_owner_025A32",
            "policy_prefix",
            "policy_name_023C",
            "failure_stem",
            "direct_call_628",
            "advice_stem",
            "direct_call_700",
            "direct_call_610",
            "question_ending",
        )
    if record_id == 2075:
        return (
            "policy_owner_025A32",
            "opening_quote",
            "policy_name_023C",
            "etc_suffix",
            "policy_count_0232",
            "multi_policy_failure_suffix",
        )
    return (
        "policy_owner_025A32",
        "policy_prefix",
        "policy_name_023C",
        "policy_failure_suffix",
    )


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    base_source_records: dict[tuple[int, int], Any],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    base_record_id = BASE_RECORD_MAPPING[record_id]
    base_record = base_source_records[(BLOCK_ID, base_record_id)]
    source_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(source_record)
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(current_record)
    )
    base_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(base_record)
    )
    source_operands = direct_call_operands(source_record)
    current_operands = direct_call_operands(current_record)
    base_operands = direct_call_operands(base_record)
    if (
        source_gap_hex != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gap_hex != source_gap_hex
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime controls drifted: "
            f"{record_id}"
        )
    if record_id == 2074:
        if (
            source_operands != (628, 700, 610)
            or current_operands != source_operands
            or base_operands != (616, 688, 598)
            or masked_gap_tuple(source_record)
            != masked_gap_tuple(base_record)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} direct-call evidence drifted"
            )
    elif source_operands or current_operands or base_operands:
        raise RuntimeError(
            f"segment {SEGMENT} unexpected direct-call evidence"
        )
    return {
        "source_record_gap_sha256":
        canonical_sha256(source_gap_hex),
        "current_record_gap_sha256":
        canonical_sha256(current_gap_hex),
        "base_record_gap_sha256":
        canonical_sha256(base_gap_hex),
        "source_runtime_gap_hex": source_gap_hex,
        "current_runtime_gap_hex": current_gap_hex,
        "base_runtime_gap_hex": base_gap_hex,
        "source_current_runtime_gap_equal": True,
        "source_direct_call_operands": source_operands,
        "current_direct_call_operands": current_operands,
        "base_direct_call_operands": base_operands,
        "runtime_order": runtime_order(record_id),
        "record_variant": "policy_discontinuation",
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_prefill_companions_reviewed": True,
        "direct_call_positions_reviewed":
        record_id == 2074,
        "retainer_allegiance_terminology_reviewed": True,
        "stipend_and_loyalty_terminology_reviewed": True,
        "policy_terminology_reviewed": True,
        "speaker_register_reviewed": True,
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
    tuple[str, ...],
]:
    patch_common_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_prefill_and_assembly_context(records_by_label)
    assert_semantics(records_by_label)
    if DISCOVERED_PINS:
        return prepared, [], b"", "", -1, optional_present

    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    base_source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        companion_coordinates = tuple(
            f"6:{record_id}:{other_id}"
            for other_id in range(
                len(
                    literal_texts(
                        records_by_label["current"],
                        (block_id, record_id),
                    )
                )
            )
            if other_id != literal_id
            and f"6:{record_id}:{other_id}" in prefill_rows
        )
        row: dict[str, Any] = {
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
            "historical_term_review": True,
            "speaker_register_review": True,
            "retainer_allegiance_term_review": True,
            "stipend_term_review": True,
            "loyalty_term_review": True,
            "policy_term_review": True,
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "base_context_reference_coordinate":
            BASE_CONTEXT_REFERENCES[coordinate],
            "base_semantic_translation_reused": True,
            "base_source_literal_exact": True,
            "base_record_opcode_variant":
            record_id == 2074,
            "base_runtime_state_inherited": False,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "protected_signature_review": True,
            "same_record_prefill_companion_coordinates":
            companion_coordinates,
            "record_variant": "policy_discontinuation",
            "speaker_register_variant":
            speaker_register_variant(record_id),
            "runtime_assembly_evidence":
            runtime_control_evidence(
                records_by_label,
                base_source_records,
                record_id,
            ),
        }
        rows.append(row)
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_common_globals()
    COMMON.assert_tamper_rejection(
        prepared,
        rows,
        candidate,
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
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
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
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 16
        or len(validated) != 16
        or counts != Counter({"runtime_fragment_pending": 16})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["base_runtime_state_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["protected_signature_review"] is not True
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
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(steam_path.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B026_S1092",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 50,
                "residual_count": 16,
                "reviewed_slice_record_count":
                len(SLICE_RECORD_IDS),
                "runtime_record_count":
                len(RUNTIME_RECORD_IDS),
                "direct_call_record_count":
                len(DIRECT_CALL_RECORD_IDS),
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "base_exact_records_guarded": True,
                "base_semantics_pinned": True,
                "base_direct_call_variant_guarded": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "complete_slice_assembly_guarded": True,
                "retainer_allegiance_terms_reviewed": True,
                "stipend_and_loyalty_terms_reviewed": True,
                "policy_terms_reviewed": True,
                "speaker_registers_reviewed": True,
                "direct_call_operands_guarded": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
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
