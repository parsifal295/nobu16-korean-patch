#!/usr/bin/env python3
"""Build source-redacted PK B026 segment 1093 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch014_segment1063.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B026_S1093.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B026_S1092.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B026_S1094.private.v1.jsonl",
)

SEGMENT = 1093
QUEUE_BATCH_ID = "pk_msggame-B026"
QUEUE_START = 66
QUEUE_STOP = 132
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

GUIDELINE_TARGET_COORDINATES = (
    "6:2077:0",
    "6:2077:1",
    "6:2078:1",
    "6:2079:0",
    "6:2079:1",
    "6:2080:0",
    "6:2081:1",
    "6:2081:2",
    "6:2082:0",
    "6:2082:1",
    "6:2083:0",
    "6:2083:1",
    "6:2084:0",
    "6:2084:1",
    "6:2085:0",
    "6:2085:1",
    "6:2086:0",
    "6:2087:0",
    "6:2087:1",
)
CAPTURE_TARGET_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in range(2089, 2101)
    for literal_id in (0, 2)
)
TRANSFER_TARGET_COORDINATES = (
    "6:2101:1",
    "6:2102:1",
)
TARGET_COORDINATES = (
    *GUIDELINE_TARGET_COORDINATES,
    *CAPTURE_TARGET_COORDINATES,
    *TRANSFER_TARGET_COORDINATES,
)
TRANSLATIONS: dict[str, str] = {
    "6:2077:0": "의 「",
    "6:2077:1": "」 등",
    "6:2078:1": "의",
    "6:2079:0": "의 지침 「",
    "6:2079:1": "」 등\n",
    "6:2080:0": "의 「",
    "6:2081:1": "의 지침\n「",
    "6:2081:2": "」 등",
    "6:2082:0": "「",
    "6:2082:1": "」 등",
    "6:2083:0": "의 지침 「",
    "6:2083:1": "」 등\n",
    "6:2084:0": "의 지침 「",
    "6:2084:1": "」 등\n",
    "6:2085:0": "의 「",
    "6:2085:1": "」 등\n",
    "6:2086:0": "의 「",
    "6:2087:0": "의 「",
    "6:2087:1": "」 등\n",
}
for capture_record_id in range(2089, 2101):
    TRANSLATIONS[f"6:{capture_record_id}:0"] = (
        " 함락에 성공했군…"
    )
    TRANSLATIONS[f"6:{capture_record_id}:2"] = (
        "의 원군에 감사하오"
    )
TRANSLATIONS["6:2101:1"] = "에"
TRANSLATIONS["6:2102:1"] = "에"

DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
GUIDELINE_RECORD_IDS = tuple(range(2077, 2088))
CAPTURE_RECORD_IDS = tuple(range(2089, 2101))
TRANSFER_RECORD_IDS = (2101, 2102)
TARGET_RECORD_IDS = (
    *GUIDELINE_RECORD_IDS,
    *CAPTURE_RECORD_IDS,
    *TRANSFER_RECORD_IDS,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (2076, 2088, 2103)
BASE_RECORD_MAPPING = {
    record_id: record_id - 6
    for record_id in TARGET_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{coordinate_key_record - 6}:{literal_id}"
    )
    for coordinate in TARGET_COORDINATES
    for _, coordinate_key_record, literal_id in (
        tuple(int(value) for value in coordinate.split(":")),
    )
}
PREFILL_COMPANION_COORDINATES = (
    "6:2077:2",
    "6:2078:0",
    "6:2078:2",
    "6:2078:3",
    "6:2079:2",
    "6:2080:1",
    "6:2080:2",
    "6:2081:0",
    "6:2081:3",
    "6:2082:2",
    "6:2083:2",
    "6:2084:2",
    "6:2085:2",
    "6:2086:1",
    "6:2086:2",
    "6:2087:2",
    "6:2088:0",
    "6:2101:0",
    "6:2101:2",
    "6:2102:0",
    "6:2102:2",
)
EXPECTED_GAPS_BY_RECORD = {
    2077: ("025A32", "023C", "0232", "050505"),
    2078: ("", "025A32", "0232", "023C", "050505"),
    2079: ("025A32", "023C", "0232", "050505"),
    2080: ("025A32", "023C", "0232", "050505"),
    2081: ("", "025A32", "023C", "0232", "050505"),
    2082: ("", "023C", "0232", "050505"),
    2083: ("025A32", "023C", "0232", "050505"),
    2084: ("025A32", "023C", "0232", "050505"),
    2085: ("025A32", "023C", "0232", "050505"),
    2086: ("025A32", "023C", "0232", "050505"),
    2087: ("025A32", "023C", "0232", "050505"),
    **{
        record_id: (
            "026432",
            "01431A020000",
            "025032",
            "0143F0010000050505",
        )
        for record_id in CAPTURE_RECORD_IDS
    },
    2101: (
        "",
        "025032",
        "026432",
        "01431A020000",
        "0143FC010000050505",
    ),
    2102: (
        "",
        "025032",
        "026432",
        "01431A020000",
        "0143FC010000050505",
    ),
}
EXPECTED_BASE_GAPS_BY_RECORD = {
    **{
        record_id: EXPECTED_GAPS_BY_RECORD[record_id]
        for record_id in GUIDELINE_RECORD_IDS
    },
    **{
        record_id: (
            "026432",
            "014314020000",
            "025032",
            "0143EA010000050505",
        )
        for record_id in CAPTURE_RECORD_IDS
    },
    2101: (
        "",
        "025032",
        "026432",
        "014314020000",
        "0143F6010000050505",
    ),
    2102: (
        "",
        "025032",
        "026432",
        "014314020000",
        "0143F6010000050505",
    ),
}
EXPECTED_CURRENT_GAPS_BY_RECORD = {
    **{
        record_id: EXPECTED_GAPS_BY_RECORD[record_id]
        for record_id in GUIDELINE_RECORD_IDS
    },
    **{
        record_id: (
            "026432",
            "",
            "025032",
            "050505",
        )
        for record_id in CAPTURE_RECORD_IDS
    },
    **{
        record_id: EXPECTED_GAPS_BY_RECORD[record_id]
        for record_id in TRANSFER_RECORD_IDS
    },
}
EXPECTED_BASE_CURRENT_GAPS_BY_RECORD = {
    **{
        record_id: EXPECTED_BASE_GAPS_BY_RECORD[record_id]
        for record_id in GUIDELINE_RECORD_IDS
    },
    **{
        record_id: (
            "026432",
            "",
            "025032",
            "050505",
        )
        for record_id in CAPTURE_RECORD_IDS
    },
    **{
        record_id: EXPECTED_BASE_GAPS_BY_RECORD[record_id]
        for record_id in TRANSFER_RECORD_IDS
    },
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
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "11A05AB1BEC3030596040330811B091BC14BAB49237B0BE447A6E3C769B2BDB1"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "8CAF1DC8E1A0B55402F6188EEFC2F3E88ADFEECE2A52F8AE6875FC0C43815C08"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "AD0C16F6E2FD2F4478845D41D706B919EC26A0EDB5F64843B22E02E5ADEECB0E"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "46A6CA760909EB9DB7E1841AA396C14E81B5491EEE21EECF9B731CA56526B2D6"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "4CF2CD4A304E356AC436DBACEDF9208D0A37E8F03FE94115E9F003C19E2B9998"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "48DE02E3F995B881F8763968C12DFB064A88C1DE96301123644C1E1179C0E06A"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "33BDC205DE5CB9FBD066B269F0EAAF8E4BB643208076173EB5563659EA3160EB"
)
EXPECTED_BOUNDARY_SHA256 = (
    "8A95483C94C2B137CA248356F11C79D72F4D30B0A9EE29403E0197483E8493EE"
)
EXPECTED_RUNTIME_OPERAND_SHA256 = (
    "7245B0F56378322BE9E9CAA563687F24031B0C5B1ED5C21BDEF67C422C518D88"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "520AF8E20FF5441845AC69180B5C306396C710A92D5A06233E87622197420497"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "7DA3005C3E6DD0A6A88E4A765CEE978179170686347C9B0669AD4037979C8638"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "4B2CC340F2A5359D5FDB339D83016B46878CFAA4E0A3641DEDA6A6DC6751CBE8"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "78BE47F07BBF2044B2F40C1141EE14435CDE2795C41B48D95C30015622871EDF"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "BFB695BC8FF710E0BDE16AFEC62C4456152B666071598673123BF5E9CE731D21"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "D28003FCB793CAF0FC4575844BAB358FA1FEA13654DAF842DE443711DD9766E2"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "86FBACB3BCBC6FCDEE4EE0255C32FF4B2A2F2534A22CAFE7AE1B8574FD6DADEC"
)
EXPECTED_CANDIDATE_SHA256 = (
    "B6A3A0096FF8EEE6548E2A0BC1C5C73F640B471E3047A9EA14457F1878207A25"
)
EXPECTED_CHANGED_LITERAL_COUNT = 28

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base full-record "
    "donors pin every guideline fragment, castle-capture result, "
    "reinforcement acknowledgement and transfer particle while Base "
    "runtime state is not inherited; exact-gap Base records and PK records "
    "are identical for the guideline group, while the capture and transfer "
    "groups retain PK-specific source direct-call operands under an "
    "operand-masked template match; the current Korean capture records "
    "intentionally absorb both calls into their literals exactly as the "
    "completed Base Korean does; all available predecessors are validated "
    "and excluded; "
    "inline force, guideline, count, castle and clan tokens, direct calls, "
    "hidden glue fragments, exact-reuse companions, full-record assembly, "
    "historical terminology, speaker register, adjacent records, protected "
    "signatures, line counts, bytecode gaps, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are guarded; all "
    "targets remain PK runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1093_common",
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
    if actual != expected:
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
    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if (
        len(queue_slice) != 66
        or len(prefilled) != 21
        or prefilled != PREFILL_COMPANION_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice drifted"
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
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: "
            f"{len(residual)} rows"
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


def direct_call_operands(record: Any) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(value[2:6], "little")
        for value in gap_bytes(record)
        if value.startswith(b"\x01\x43")
    )


def inline_token_hex(record: Any) -> tuple[str, ...]:
    return tuple(
        value.hex().upper()
        for value in gap_bytes(record)
        if value.startswith(b"\x02")
    )


def masked_gap_hex(record: Any) -> tuple[str, ...]:
    result: list[str] = []
    for value in gap_bytes(record):
        if value.startswith(b"\x01\x43") and len(value) >= 6:
            value = value[:2] + (b"\x00" * 4) + value[6:]
        result.append(value.hex().upper())
    return tuple(result)


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
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
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
        for record_id in TARGET_RECORD_IDS
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
    operand_evidence = tuple(
        (
            label,
            record_id,
            direct_call_operands(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ]
            ),
            inline_token_hex(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if (
            direct_call_operands(
                records_by_label["jp"][(BLOCK_ID, record_id)]
            )
            or inline_token_hex(
                records_by_label["jp"][(BLOCK_ID, record_id)]
            )
        )
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
            "runtime operand",
            operand_evidence,
            EXPECTED_RUNTIME_OPERAND_SHA256,
        ),
        (
            "dynamic record",
            actual_dynamic,
            EXPECTED_DYNAMIC_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        actual_dynamic != DYNAMIC_RECORD_IDS
        or any(
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current
            != EXPECTED_CURRENT_GAPS_BY_RECORD[record_id]
            for record_id, source, current in gaps
        )
        or any(
            direct_call_operands(
                records_by_label["jp"][(BLOCK_ID, record_id)]
            )
            for record_id in GUIDELINE_RECORD_IDS
        )
        or any(
            direct_call_operands(
                records_by_label["jp"][(BLOCK_ID, record_id)]
            )
            != (538, 496)
            for record_id in CAPTURE_RECORD_IDS
        )
        or any(
            direct_call_operands(
                records_by_label["current"][
                    (BLOCK_ID, record_id)
                ]
            )
            for record_id in CAPTURE_RECORD_IDS
        )
        or any(
            direct_call_operands(
                records_by_label["jp"][(BLOCK_ID, record_id)]
            )
            != (538, 508)
            for record_id in TRANSFER_RECORD_IDS
        )
        or any(
            direct_call_operands(
                records_by_label["current"][
                    (BLOCK_ID, record_id)
                ]
            )
            != (538, 508)
            for record_id in TRANSFER_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def assert_base_prefill_and_assembly(
    prepared: Any,
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
    base_current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    for coordinate in TARGET_COORDINATES:
        base_coordinate = BASE_CONTEXT_REFERENCES[coordinate]
        pk_key = coordinate_key(coordinate)
        base_key = coordinate_key(base_coordinate)
        base_row = base_rows[base_coordinate]
        pk_record = records_by_label["jp"][pk_key[:2]]
        base_record = base_source_records[base_key[:2]]
        base_current_record = base_current_records[
            base_key[:2]
        ]
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                literal_texts(
                    records_by_label["jp"],
                    pk_key[:2],
                )[pk_key[2]],
                literal_texts(
                    base_source_records,
                    base_key[:2],
                )[base_key[2]],
                base_row.get("translation"),
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_record)
                ),
                masked_gap_hex(pk_record),
                masked_gap_hex(base_record),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_current_record)
                ),
            )
        )
        if (
            base_evidence[-1][2] != base_evidence[-1][3]
            or base_row.get("translation")
            != TRANSLATIONS[coordinate]
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
            or (
                pk_key[1] in GUIDELINE_RECORD_IDS
                and base_evidence[-1][7]
                != base_evidence[-1][8]
            )
            or (
                pk_key[1] not in GUIDELINE_RECORD_IDS
                and base_evidence[-1][9]
                != base_evidence[-1][10]
            )
            or base_evidence[-1][11]
            != EXPECTED_BASE_CURRENT_GAPS_BY_RECORD[pk_key[1]]
            or (
                pk_key[1] in CAPTURE_RECORD_IDS
                and base_evidence[-1][11]
                != EXPECTED_CURRENT_GAPS_BY_RECORD[pk_key[1]]
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: "
                f"{coordinate}"
            )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    companion_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get("layout_review"),
            prefill_rows[coordinate].get(
                "scope_classification"
            ),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
        )
        for coordinate in PREFILL_COMPANION_COORDINATES
    )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    if any(
        semantic != "approved"
        or runtime != "pending"
        or scope != "runtime_fragment_pending"
        for (
            _,
            _,
            semantic,
            runtime,
            _,
            scope,
            _,
            _,
        ) in companion_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill companion drifted"
        )

    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        owners: list[str] = []
        translations: list[str] = []
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                owners.append("segment")
                translations.append(TRANSLATIONS[coordinate])
            elif coordinate in prefill_rows:
                owners.append("prefill")
                translations.append(
                    str(prefill_rows[coordinate]["translation"])
                )
            else:
                owners.append("current_hidden")
                translations.append(current_text)
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                source_literals,
                current_literals,
                tuple(translations),
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
                inline_token_hex(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                ),
            )
        )
        if (
            record_id in GUIDELINE_RECORD_IDS
            and (
                "지침" not in "\u241f".join(translations)
                or "current_hidden" in owners
            )
        ) or (
            record_id in CAPTURE_RECORD_IDS
            and (
                tuple(owners)
                != ("segment", "current_hidden", "segment")
                or translations[0] != " 함락에 성공했군…"
                or translations[2] != "의 원군에 감사하오"
            )
        ) or (
            record_id in TRANSFER_RECORD_IDS
            and (
                tuple(owners)
                != (
                    "prefill",
                    "segment",
                    "prefill",
                    "current_hidden",
                )
                or translations[1] != "에"
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly semantics drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def runtime_category(record_id: int) -> str:
    if record_id in GUIDELINE_RECORD_IDS:
        return "inline_force_guideline_count"
    if record_id in CAPTURE_RECORD_IDS:
        return "inline_castle_clan_dual_direct_call"
    return "inline_clan_castle_dual_direct_call_transfer"


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    terminology_policy = (
        ("land_grant_command", "지행"),
        ("loyalty", "충성"),
        ("retainer_band", "가신단"),
        ("guideline", "지침"),
        ("reinforcement", "원군"),
        ("castle_capture", "함락"),
        ("uprising", "잇키"),
    )
    guarded_digest(
        "terminology policy",
        terminology_policy,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    runtime_categories = tuple(
        (
            record_id,
            runtime_category(record_id),
            "runtime_fragment_pending",
            "pending",
            "runtime_pending",
            False,
        )
        for record_id in TARGET_RECORD_IDS
    )
    guarded_digest(
        "runtime category",
        runtime_categories,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
        or len(TRANSLATIONS) != 45
        or any(
            TRANSLATIONS[f"6:{record_id}:0"]
            != " 함락에 성공했군…"
            or TRANSLATIONS[f"6:{record_id}:2"]
            != "의 원군에 감사하오"
            for record_id in CAPTURE_RECORD_IDS
        )
        or any(
            TRANSLATIONS[f"6:{record_id}:1"] != "에"
            for record_id in TRANSFER_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
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


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    return {
        "runtime_category": runtime_category(record_id),
        "source_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(source_record)
            )
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(current_record)
            )
        ),
        "source_direct_call_operands":
        direct_call_operands(source_record),
        "current_direct_call_operands":
        direct_call_operands(current_record),
        "source_inline_token_hex":
        inline_token_hex(source_record),
        "current_inline_token_hex":
        inline_token_hex(current_record),
        "source_current_runtime_gap_equal":
        gap_bytes(source_record) == gap_bytes(current_record),
        "source_direct_calls_absorbed_by_current_korean":
        record_id in CAPTURE_RECORD_IDS,
        "base_operand_masked_template_match": True,
        "complete_record_assembly_reviewed": True,
        "prefill_companions_reviewed": True,
        "hidden_glue_fragments_reviewed": True,
        "historical_terminology_reviewed": True,
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
    assert_base_prefill_and_assembly(prepared, records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
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
                "scope_classification":
                "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_s1092_s1094_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "hidden_glue_fragments_reviewed": True,
                "historical_terminology_reviewed": True,
                "speaker_register_reviewed": True,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
                    records_by_label,
                    record_id,
                ),
            }
        )
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
        len(rows) != 45
        or len(validated) != 45
        or counts != Counter({"runtime_fragment_pending": 45})
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
                "segment": "pk_msggame_B026_S1093",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 21,
                "base_semantic_reference_count": len(rows),
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "hidden_glue_fragments_guarded": True,
                "direct_call_operands_guarded": True,
                "localized_direct_call_absorption_guarded": True,
                "inline_tokens_guarded": True,
                "historical_terminology_guarded": True,
                "speaker_register_guarded": True,
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
