#!/usr/bin/env python3
"""Build source-redacted PK B022 segment 1083 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch021_segment1082.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B022_S1083.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B021_S1080.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B021_S1081.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B021_S1082.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B022_S1084.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B022_S1085.private.v1.jsonl",
)

SEGMENT = 1083
QUEUE_BATCH_ID = "pk_msggame-B022"
QUEUE_START = 0
QUEUE_STOP = 67
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
        "pc_dialogue_full_retranslation_v0150_pk_s1083_common",
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
    *(f"6:{record_id}:0" for record_id in range(1454, 1466)),
    "6:1466:1",
    "6:1470:0",
    "6:1473:0",
    "6:1474:0",
    "6:1474:1",
    "6:1475:0",
    "6:1476:0",
    "6:1476:1",
    "6:1477:0",
    "6:1478:0",
    "6:1479:0",
    "6:1479:1",
    "6:1480:0",
    "6:1480:1",
    "6:1481:0",
    "6:1481:1",
    "6:1482:0",
    "6:1483:0",
    "6:1483:1",
    "6:1484:0",
)
TRANSLATIONS = {
    **{
        f"6:{record_id}:0": "알겠습니다"
        for record_id in range(1454, 1466)
    },
    "6:1466:1": "」 LV",
    "6:1470:0": "합계",
    "6:1473:0": "의 새로운 군단장으로\n임명할 무장을 선택하십시오",
    "6:1474:0": "군단장을 임명하지 않으면\n",
    "6:1474:1": "은(는) 해산됩니다.\n계속하시겠습니까?",
    "6:1475:0": "이(가)",
    "6:1476:0": "이(가) ",
    "6:1476:1": "에게 신종",
    "6:1477:0": "와(과)",
    "6:1478:0": "와(과)",
    "6:1479:0": "와(과)",
    "6:1479:1": " 이(가) 절연",
    "6:1480:0": "와(과)",
    "6:1480:1": " 이(가) 절연",
    "6:1481:0": "와(과)",
    "6:1481:1": " 이(가) 절연",
    "6:1482:0": "이(가)",
    "6:1483:0": "와(과)",
    "6:1483:1": "이(가)",
    "6:1484:0": "와(과)",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = tuple(
    dict.fromkeys(
        coordinate_key(coordinate)[1]
        for coordinate in TARGET_COORDINATES
    )
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
SLICE_RECORD_IDS = tuple(range(1450, 1485))
BOUNDARY_RECORD_IDS = (1449, 1485)
DIRECT_CALL_SLICE_RECORD_IDS = tuple(range(1450, 1466))
DIRECT_CALL_TARGET_RECORD_IDS = tuple(range(1454, 1466))
MANUAL_PK_ONLY_COORDINATES = {
    "6:1473:0",
    "6:1474:0",
    "6:1474:1",
}

BASE_CONTEXT_REFERENCES = {
    **{
        f"6:{record_id}:0": f"6:{record_id - 4}:0"
        for record_id in range(1454, 1466)
    },
    "6:1466:1": "6:1462:1",
    "6:1470:0": "6:1466:0",
    "6:1475:0": "6:1469:0",
    "6:1476:0": "6:1470:0",
    "6:1476:1": "6:1470:1",
    "6:1477:0": "6:1471:0",
    "6:1478:0": "6:1472:0",
    "6:1479:0": "6:1473:0",
    "6:1479:1": "6:1473:1",
    "6:1480:0": "6:1474:0",
    "6:1480:1": "6:1474:1",
    "6:1481:0": "6:1475:0",
    "6:1481:1": "6:1475:1",
    "6:1482:0": "6:1476:0",
    "6:1483:0": "6:1477:0",
    "6:1483:1": "6:1477:1",
    "6:1484:0": "6:1478:0",
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "AF9A606FF7DC5525E8C9F022C8B3DA12186A898C2D92DE99C38C541910542BCD"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "F907CB5A92EFD8FCB43272E0C6B3132064AAA4124769DC21B10EC76A7CF79635"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "A6E42663ECF5DAE89A9AD834CD83310AC784C2697D512504A8B50AACBEB83986"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "CC0909D66F61B6C1EECC3FE2A88670ACBC3D5C2CC87112965DF2CD128235E7D7"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "F8468D952B86885BD492EE29A503E05469D48F67C9D94CFC3E2A5D7D8ABCDF6E"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "C68A5BE7FC1B09897C3C755A8BF59C25549E70D0A7CC96B856BC515D316992BB"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "266BCB504F78F2368DDA69C9154A49CD887306B6A398BDBDEC29CAB0C01F21FA"
)
EXPECTED_BOUNDARY_SHA256 = (
    "4147136AF49058DC12B0F8626E9248C0FCA9E53D16341588E1ACD96B1FF4C322"
)
EXPECTED_DIRECT_CALL_SHA256 = (
    "FC96D31D515626CA596796FE3211A1F15E73D1E31114572873A21D1408A4A525"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "C903FA3E5E2D40A14AD90010B6F371B4F6D1116AE4692D358B234DF5372A7603"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "8B63449A7D65851671FD4845EFB384AFC4835FE2F14F2AAAF40F115607AEEBD5"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "04BB11E6C4B3349D690B02A38E9311DD5034994AC6427E86204915A7564A98D2"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "089F9DA28F5191612E2431F3D4B5CC8AA334B58D90F6B5F3FD8BC4DFA8D8F719"
)
EXPECTED_CANDIDATE_SHA256 = (
    "51FF8357EADEFFBA4316325AACB6E90E2FAF86E55EB0AB1A2B0A26211E36BB17"
)
EXPECTED_CHANGED_LITERAL_COUNT = 17

DIRECT_CALL_FIRST_GAPS = (
    "",
    "0143D2010000",
    "014366040000050505",
)
DIRECT_CALL_FIRST_OPERANDS = (466, 1126)
DIRECT_CALL_SECOND_GAPS = (
    "",
    "014374020000",
    "0143E6020000050505",
)
DIRECT_CALL_SECOND_OPERANDS = (628, 742)
DIRECT_CALL_CURRENT_FLATTENED_GAPS = ("", "", "050505")

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; all thirty-five exact-reuse "
    "prefill rows in the queue slice and completed Base runtime-verified "
    "semantic donors are pinned; twelve PK direct-call response variants "
    "retain their polite response and full continuation; the PK-only "
    "corps selection and disband messages are independently reviewed; "
    "single-name possessive and mid-sentence subject structures retain "
    "their particles, while two-force vassalage, submission, marriage, "
    "severance and truce notices use the completed Base particle policy; "
    "the B019 dash rule is inapplicable to every structure here; corps, "
    "castle-lord, policy, officer and diplomatic terminology, UI register, "
    "historical setting, protected signatures, line counts, bytecode gaps, "
    "complete assembly ownership, reverse overlay, two-run reproduction, "
    "tamper rejection and read-only inputs are guarded; Base runtime state "
    "is not inherited and every residual PK fragment remains runtime pending"
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
        len(queue_rows) != 117
        or len(visible) != 200
        or visible[0] != "6:1450:0"
        or visible[-1] != "6:1566:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B022 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:1450:0"
        or queue_slice[-1] != "6:1484:2"
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
    if len(prefilled) != 35:
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
    if residual != TARGET_COORDINATES or len(residual) != 32:
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


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()):]
    return leading + donor.strip() + trailing


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
    context_ids = tuple(range(1449, 1486))
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
        for record_id in DIRECT_CALL_SLICE_RECORD_IDS
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

    if any(
        source != current
        and not (
            record_id in DIRECT_CALL_TARGET_RECORD_IDS
            and current == DIRECT_CALL_CURRENT_FLATTENED_GAPS
        )
        for record_id, source, current in gaps
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source/current gap policy drifted"
        )
    for (
        record_id,
        source_gap_hex,
        source_operands,
        current_gap_hex,
        current_operands,
    ) in direct_calls:
        expected_gaps = (
            DIRECT_CALL_FIRST_GAPS
            if record_id <= 1453
            else DIRECT_CALL_SECOND_GAPS
        )
        expected_operands = (
            DIRECT_CALL_FIRST_OPERANDS
            if record_id <= 1453
            else DIRECT_CALL_SECOND_OPERANDS
        )
        expected_current_gaps = (
            expected_gaps
            if record_id <= 1453
            else DIRECT_CALL_CURRENT_FLATTENED_GAPS
        )
        expected_current_operands = (
            expected_operands if record_id <= 1453 else ()
        )
        if (
            source_gap_hex != expected_gaps
            or source_operands != expected_operands
            or current_gap_hex != expected_current_gaps
            or current_operands != expected_current_operands
        ):
            raise RuntimeError(
                f"segment {SEGMENT} direct call drifted: "
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
    if actual_direct_records != DIRECT_CALL_SLICE_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} direct call universe drifted"
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
    base_evidence: list[tuple[Any, ...]] = []
    for coordinate, base_coordinate in (
        BASE_CONTEXT_REFERENCES.items()
    ):
        pk_key = coordinate_key(coordinate)
        base_key = coordinate_key(base_coordinate)
        pk_source = literal_texts(
            records_by_label["jp"],
            pk_key[:2],
        )[pk_key[2]]
        base_source = literal_texts(
            base_source_records,
            base_key[:2],
        )[base_key[2]]
        base_row = base_rows[base_coordinate]
        current_text = literal_texts(
            records_by_label["current"],
            pk_key[:2],
        )[pk_key[2]]
        adapted_translation = adapt_outer_whitespace(
            str(base_row.get("translation")),
            current_text,
        )
        pk_record = records_by_label["jp"][pk_key[:2]]
        base_record = base_source_records[base_key[:2]]
        exact_gaps = gap_bytes(pk_record) == gap_bytes(base_record)
        masked_gaps = (
            masked_gap_tuple(pk_record)
            == masked_gap_tuple(base_record)
        )
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                pk_source,
                base_source,
                base_row.get("translation"),
                adapted_translation,
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
                exact_gaps,
                masked_gaps,
            )
        )
        if (
            pk_source != base_source
            or TRANSLATIONS[coordinate]
            != adapted_translation
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
            or (
                not exact_gaps
                and not (
                    coordinate_key(coordinate)[1]
                    in DIRECT_CALL_TARGET_RECORD_IDS
                    and masked_gaps
                )
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base semantic donor drifted: "
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
        len(prefill_coordinates) != 35
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
    assembly_map: dict[int, tuple[str, ...]] = {}
    for record_id in SLICE_RECORD_IDS:
        translations: list[str] = []
        owners: list[str] = []
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                translations.append(TRANSLATIONS[coordinate])
                owners.append("segment")
            elif coordinate in prefill_rows:
                translations.append(
                    str(prefill_rows[coordinate]["translation"])
                )
                owners.append("prefill")
            else:
                translations.append(current_text)
                owners.append("current")
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
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                source_gaps,
                current_gaps,
            )
        )
        if (
            "current" in owners
            or (
                source_gaps != current_gaps
                and not (
                    record_id in DIRECT_CALL_SLICE_RECORD_IDS
                    and current_gaps
                    == DIRECT_CALL_CURRENT_FLATTENED_GAPS
                )
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} complete assembly drifted: "
                f"{record_id}"
            )

    expected_assemblies = {
        **{
            record_id: (
                "알겠습니다",
                "…\n우리 가문을 위한 일이라면 어쩔 수 없지요",
            )
            for record_id in DIRECT_CALL_TARGET_RECORD_IDS
        },
        1466: (
            "성주 이동은 정책「",
            "」 LV",
            "에서 해금됩니다",
        ),
        1470: (
            "합계",
            "개 성이 통치 범위를 벗어나\n"
            "다이묘 군단 소속이 됩니다. 계속하시겠습니까?",
        ),
        1473: (
            "의 새로운 군단장으로\n"
            "임명할 무장을 선택하십시오",
        ),
        1474: (
            "군단장을 임명하지 않으면\n",
            "은(는) 해산됩니다.\n계속하시겠습니까?",
        ),
        1475: ("이(가)", "을(를) 종속시킴"),
        1476: ("이(가) ", "에게 신종"),
        1477: ("와(과)", "이(가) 혼인 동맹"),
        1478: ("와(과)", "이(가) 혼인 동맹"),
        1479: ("와(과)", " 이(가) 절연"),
        1480: ("와(과)", " 이(가) 절연"),
        1481: ("와(과)", " 이(가) 절연"),
        1482: ("이(가)", "을(를) 종속시킴"),
        1483: ("와(과)", "이(가)", "개월간 정전"),
        1484: ("와(과)", "의 정전이", "개월 연장"),
    }
    for record_id, expected in expected_assemblies.items():
        if assembly_map[record_id] != expected:
            raise RuntimeError(
                f"segment {SEGMENT} semantic assembly drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
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
        or len(TARGET_COORDINATES) != 32
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
        any(
            TRANSLATIONS[f"6:{record_id}:0"] != "알겠습니다"
            for record_id in DIRECT_CALL_TARGET_RECORD_IDS
        )
        or TRANSLATIONS["6:1473:0"]
        != "의 새로운 군단장으로\n임명할 무장을 선택하십시오"
        or TRANSLATIONS["6:1474:1"]
        != "은(는) 해산됩니다.\n계속하시겠습니까?"
        or any("—" in value for value in TRANSLATIONS.values())
        or any(": " in value for value in TRANSLATIONS.values())
        or any(
            TRANSLATIONS[f"6:{record_id}:0"] != "와(과)"
            or TRANSLATIONS[f"6:{record_id}:1"]
            != " 이(가) 절연"
            for record_id in range(1479, 1482)
        )
        or TRANSLATIONS["6:1484:0"] != "와(과)"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} wording or relation drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def record_variant(record_id: int) -> str:
    if record_id in DIRECT_CALL_TARGET_RECORD_IDS:
        return "corps_response_direct_call"
    if record_id == 1466:
        return "policy_level_ui"
    if record_id == 1470:
        return "out_of_range_castle_count_ui"
    if record_id == 1473:
        return "single_corps_name_possessive"
    if record_id == 1474:
        return "single_corps_name_mid_sentence_subject"
    if record_id in (1475, 1482):
        return "two_force_vassalage"
    if record_id == 1476:
        return "two_force_submission"
    if record_id in (1477, 1478):
        return "two_force_marriage_alliance"
    if record_id in (1479, 1480, 1481):
        return "two_force_severance"
    return "two_force_truce"


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
    source_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(source_record)
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(current_record)
    )
    expected_gap_relation = (
        source_gap_hex == DIRECT_CALL_SECOND_GAPS
        and current_gap_hex
        == DIRECT_CALL_CURRENT_FLATTENED_GAPS
        if record_id in DIRECT_CALL_TARGET_RECORD_IDS
        else source_gap_hex == current_gap_hex
    )
    if not expected_gap_relation:
        raise RuntimeError(
            f"segment {SEGMENT} runtime controls drifted: "
            f"{record_id}"
        )
    operands = direct_call_operands(source_record)
    variant = record_variant(record_id)
    if (
        record_id in DIRECT_CALL_TARGET_RECORD_IDS
        and (
            source_gap_hex != DIRECT_CALL_SECOND_GAPS
            or operands != DIRECT_CALL_SECOND_OPERANDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} response call drifted: "
            f"{record_id}"
        )
    return {
        "source_record_gap_sha256": canonical_sha256(
            source_gap_hex
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gap_hex
        ),
        "source_runtime_gap_hex": source_gap_hex,
        "current_runtime_gap_hex": current_gap_hex,
        "source_current_runtime_gap_equal":
        source_gap_hex == current_gap_hex,
        "source_direct_call_operands": operands,
        "current_direct_call_operands":
        direct_call_operands(current_record),
        "korean_direct_call_flattening_preserved":
        record_id in DIRECT_CALL_TARGET_RECORD_IDS,
        "record_variant": variant,
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_prefill_companions_reviewed": True,
        "single_target_dash_rule_applicable": False,
        "single_target_dash_rule_applied": False,
        "single_name_possessive_preserved":
        record_id in (1473, 1484),
        "single_name_mid_sentence_subject_preserved":
        record_id == 1474,
        "two_name_particle_relation_preserved":
        record_id in range(1475, 1485),
        "polite_response_register_reviewed":
        record_id in DIRECT_CALL_TARGET_RECORD_IDS,
        "ui_and_diplomatic_terminology_reviewed": True,
        "historical_setting_reviewed": True,
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
    rows: list[dict[str, Any]] = []
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
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
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "base_context_reference_coordinate":
            BASE_CONTEXT_REFERENCES.get(coordinate),
            "base_semantic_translation_reused":
            coordinate in BASE_CONTEXT_REFERENCES,
            "manual_pk_only_translation":
            coordinate in MANUAL_PK_ONLY_COORDINATES,
            "base_runtime_state_inherited": False,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "protected_signature_review": True,
            "same_record_prefill_companion_coordinates":
            companion_coordinates,
            "record_variant": record_variant(record_id),
            "single_target_dash_rule_applicable": False,
            "single_target_dash_rule_applied": False,
            "runtime_assembly_evidence":
            runtime_control_evidence(
                records_by_label,
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
        len(rows) != 32
        or len(validated) != 32
        or counts != Counter({"runtime_fragment_pending": 32})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["base_runtime_state_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["protected_signature_review"] is not True
            or row["single_target_dash_rule_applicable"] is not False
            or row["single_target_dash_rule_applied"] is not False
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
                "segment": "pk_msggame_B022_S1083",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 35,
                "residual_count": 32,
                "reviewed_slice_record_count":
                len(SLICE_RECORD_IDS),
                "reviewed_target_record_count":
                len(TARGET_RECORD_IDS),
                "direct_call_slice_record_count":
                len(DIRECT_CALL_SLICE_RECORD_IDS),
                "direct_call_target_record_count":
                len(DIRECT_CALL_TARGET_RECORD_IDS),
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
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "complete_slice_assembly_guarded": True,
                "direct_call_operands_guarded": True,
                "single_name_possessive_preserved": True,
                "single_name_subject_relation_preserved": True,
                "two_name_particle_relations_preserved": True,
                "single_target_dash_rule_applied": False,
                "polite_response_register_reviewed": True,
                "ui_and_diplomatic_terms_reviewed": True,
                "historical_context_reviewed": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "outside_scope_records_exact": True,
                "runtime_gap_contracts_exact": True,
                "korean_direct_call_flattening_preserved": True,
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
