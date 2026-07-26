#!/usr/bin/env python3
"""Build source-redacted PK B038 segment 1125 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch037_segment1122.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B038_S1125.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B037_S1124.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B038_S1126.private.v1.jsonl",
)

SEGMENT = 1125
QUEUE_BATCH_ID = "pk_msggame-B038"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 3644
QUEUE_LAST_RECORD = 3751

TARGET_COORDINATES = (
    "6:3644:0",
    "6:3645:0",
    "6:3645:1",
    "6:3646:0",
    "6:3646:1",
    "6:3646:2",
    "6:3648:0",
    "6:3652:0",
    "6:3652:2",
    "6:3655:0",
    "6:3655:2",
    "6:3656:0",
    "6:3657:1",
    "6:3657:2",
    "6:3658:1",
    "6:3659:0",
    "6:3659:1",
    "6:3661:0",
    "6:3665:0",
    "6:3670:0",
    "6:3672:0",
    "6:3673:0",
    "6:3674:0",
    "6:3675:0",
    "6:3676:0",
    "6:3677:0",
    "6:3677:2",
    "6:3678:0",
    "6:3678:3",
    "6:3680:1",
)
TRANSLATIONS = {
    "6:3644:0": "이것이",
    "6:3645:0": ", 이것은",
    "6:3645:1": "입니까?\n",
    "6:3646:0": ",",
    "6:3646:1": "의 취향에 맞는\n물건이 아니",
    "6:3646:2": "까",
    "6:3648:0": "혹시,",
    "6:3652:0": ", 이",
    "6:3652:2": "의 취향",
    "6:3655:0": ",",
    "6:3655:2": "까",
    "6:3656:0": ", 이것은",
    "6:3657:1": "을(를)\n이렇게 내려 주시",
    "6:3657:2": "다니…\n감사의 말씀도",
    "6:3658:1": "인가",
    "6:3659:0": "이럴 수가,",
    "6:3659:1": "을(를)…!\n",
    "6:3661:0": "이것이",
    "6:3665:0": "을(를)",
    "6:3670:0": "이것이",
    "6:3672:0": "의",
    "6:3673:0": "의",
    "6:3674:0": "의",
    "6:3675:0": "의",
    "6:3676:0": "의",
    "6:3677:0": "의",
    "6:3677:2": "군",
    "6:3678:0": "\n어찌하여",
    "6:3678:3": "습니까",
    "6:3680:1": "의",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3644,
    3645,
    3646,
    3648,
    3652,
    3655,
    3656,
    3657,
    3658,
    3659,
    3661,
    3665,
    3670,
    3672,
    3673,
    3674,
    3675,
    3676,
    3677,
    3678,
    3680,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BASE_RECORD_MAPPING = {
    record_id: record_id - 7 for record_id in TARGET_RECORD_IDS
}
SPLIT_ADAPTED_RECORD_IDS = (3646, 3657)
EXACT_BASE_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in SPLIT_ADAPTED_RECORD_IDS
)
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        "6:3650:1"
        if coordinate in {"6:3657:1", "6:3657:2"}
        else (
            f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
            f"{coordinate.split(':')[2]}"
        )
    )
    for coordinate in TARGET_COORDINATES
}
PREFILL_COMPANION_COORDINATES = (
    "6:3644:1",
    "6:3645:2",
    "6:3648:1",
    "6:3652:1",
    "6:3655:1",
    "6:3656:1",
    "6:3657:0",
    "6:3658:0",
    "6:3659:2",
    "6:3661:1",
    "6:3665:1",
    "6:3670:1",
    "6:3672:1",
    "6:3673:1",
    "6:3674:1",
    "6:3675:1",
    "6:3676:1",
    "6:3677:1",
    "6:3678:1",
    "6:3678:2",
    "6:3680:2",
)
INVISIBLE_CURRENT_COORDINATES = ("6:3680:0",)
BOUNDARY_RECORD_IDS = tuple(range(3643, 3682))

EXPECTED_GAPS_BY_RECORD = {
    3644: ("", "023C", "014332020000050505"),
    3645: (
        "0143D6000000",
        "023C",
        "014301000000",
        "014332020000050505",
    ),
    3646: (
        "0143D6000000",
        "014301000000",
        "0143F2020000",
        "050505",
    ),
    3648: ("", "014301000000", "014324010000050505"),
    3652: (
        "0143D6000000",
        "023C",
        "014301000000",
        "014332020000050505",
    ),
    3655: (
        "0143D6000000",
        "014301000000",
        "0143E6020000",
        "050505",
    ),
    3656: (
        "0143D6000000",
        "023C",
        "014332020000050505",
    ),
    3657: (
        "",
        "023C",
        "0143AE040000",
        "0143E6020000050505",
    ),
    3658: ("014301000000", "014366040000", "050505"),
    3659: (
        "",
        "023C",
        "014301000000",
        "0143EC020000050505",
    ),
    3661: ("", "023C", "014318010000050505"),
    3665: ("023C", "014301000000", "014352000000050505"),
    3670: ("", "023C", "0143E6020000050505"),
    3672: ("014301000000", "023C", "014326020000050505"),
    3673: ("014301000000", "023C", "050505"),
    3674: ("014301000000", "023C", "050505"),
    3675: ("014301000000", "023C", "014356020000050505"),
    3676: ("014301000000", "023C", "0143EC020000050505"),
    3677: (
        "014301000000",
        "023C",
        "0143EC020000",
        "050505",
    ),
    3678: (
        "01438E030000",
        "023C",
        "014301000000",
        "014346000000",
        "050505",
    ),
    3680: (
        "01438E030000",
        "014301000000",
        "023C",
        "014342010000050505",
    ),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3644: ((562,), ("023C",)),
    3645: ((214, 1, 562), ("023C",)),
    3646: ((214, 1, 754), ()),
    3648: ((1, 292), ()),
    3652: ((214, 1, 562), ("023C",)),
    3655: ((214, 1, 742), ()),
    3656: ((214, 562), ("023C",)),
    3657: ((1198, 742), ("023C",)),
    3658: ((1, 1126), ()),
    3659: ((1, 748), ("023C",)),
    3661: ((280,), ("023C",)),
    3665: ((1, 82), ("023C",)),
    3670: ((742,), ("023C",)),
    3672: ((1, 550), ("023C",)),
    3673: ((1,), ("023C",)),
    3674: ((1,), ("023C",)),
    3675: ((1, 598), ("023C",)),
    3676: ((1, 748), ("023C",)),
    3677: ((1, 748), ("023C",)),
    3678: ((910, 1, 70), ("023C",)),
    3680: ((910, 1, 322), ("023C",)),
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
    "3079022839D47F7DFA3F71A0AAC2020BEC3D4580846E7F252E289F2A3C030CF5"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "C2C73C32EEE9773E6989C1749A0F9EB698E8F586B8B16AE0B218B1A07FFD734C"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "1BB5C39DC38766AEDC62906F6193C645DDEDCF697E68FABC492345D395D55880"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "C6AFDEE529BDFE3D834D37CCE8F84FC17B2ABE887F2E7F8EB220D10E82DC0610"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "65E6AAC8D7116C617B3E2E0D687BAD3B6DFF884731C6E3B35261C91C515F2780"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "5EB89F2F77B9DAF8F602ACC364064F6C6150CD7E0964DD359E200B30DC392B54"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "2BEEFCB0711C2333ED62633BBD07D88670E625EBE14ED56D9AFB4E33E6C22DB7"
)
EXPECTED_BOUNDARY_SHA256 = (
    "E4ACF01E67BC70C94D25CE5942E03313CA10C74C135D6741D08C4E2F42E0FEC3"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "D5E56931B4652E411B0F23F0B4AC9E38A55D4227786F01F72D93E0431BB4D48F"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "30CEC61BEB35FF95317637F0B6FFB05C4A6327D024BA299A9A06F4DD6AB271A4"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "80965C05889D1A15E5CCED33ECDAC7C9F381206335867E4657C991A874EC40C8"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "FC8C67DA73CE8E5B1F487C253E2BC2186C11FD9C080FDF0F883B9E2BAA327FF3"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "BCB278A9573E6DE3F7AF507A8FFD12CD4C03CAF83702D70B3B1B884F1BE92313"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "1CBB5E875DFC31BA56B6D4B2F9D9892E42AED89A5C718E06A440105E2EE17667"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "FE4F9DBAD84F82CF979B92380DA7DFD813130584C77142CF2FA7DCEF94CD814D"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "601C5ABC4EDEEC9EF4D27A7EC41A53C75599C20BDDB47D0AC170A7F9D2E07BCD"
)
EXPECTED_CANDIDATE_SHA256 = (
    "68102BF1CA1781BD24B59EDC0C50E238404283CAFC2424DB00E71911B8226C34"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; thirty-seven Base exact-"
    "reuse prefill rows and thirty residual rows cover the assigned "
    "sixty-seven visible literals; twenty-one complete multi-literal "
    "records are assembled with twenty-one prefill companions and one "
    "invisible newline companion; nineteen Base record-minus-seven "
    "donors are literal-exact, while two semantically identical donor "
    "sentences are adapted only to PK literal and newline boundaries; "
    "Base wording is reused while Base runtime state is not inherited; "
    "gift preference, gratitude, honor, discernment, confiscation and "
    "formal protest terminology and polite, formal, blunt, humble and "
    "elder registers are reviewed; person, item and particle tokens, "
    "direct-call operands, inline controls, protected outer whitespace, "
    "line counts, complete-record assembly, multilingual context, "
    "boundaries, reverse overlay, two-run reproduction, tamper rejection, "
    "outside-scope records and read-only inputs are guarded; all thirty "
    "dynamic fragments remain runtime pending"
)
DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1125_common",
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
        len(queue_rows) != 108
        or len(visible) != 199
        or visible[0] != f"6:{QUEUE_FIRST_RECORD}:0"
        or visible[-1] != f"6:{QUEUE_LAST_RECORD}:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B038 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3644:0"
        or queue_slice[-1] != "6:3680:1"
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
    if len(prefilled) != 37:
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
                    records_by_label["current"][(BLOCK_ID, record_id)]
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
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
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
            "EXPECTED_GAP_CONTRACT_SHA256",
            gaps,
            EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "EXPECTED_BOUNDARY_SHA256",
            boundary,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "EXPECTED_RUNTIME_CONTROL_SHA256",
            controls,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if any(
        source != EXPECTED_GAPS_BY_RECORD[record_id]
        or current != source
        for record_id, source, current in gaps
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime gap layout drifted")
    if any(
        actual != EXPECTED_CONTROLS_BY_RECORD[record_id]
        for _, record_id, actual in controls
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime control drifted")


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
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    companion_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    complete_replacements: dict[tuple[int, int, int], str] = {}
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_invisible: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_literals = literal_texts(
            records_by_label["jp"], (BLOCK_ID, record_id)
        )
        base_literals = literal_texts(
            base_source, (BLOCK_ID, base_record_id)
        )
        base_current_literals = literal_texts(
            base_current, (BLOCK_ID, base_record_id)
        )
        if (
            record_id in EXACT_BASE_RECORD_IDS
            and pk_literals != base_literals
        ):
            raise RuntimeError(
                f"segment {SEGMENT} exact Base donor drifted: {record_id}"
            )
        base_translations: list[str] = []
        for literal_id in range(len(base_literals)):
            base_coordinate = f"6:{base_record_id}:{literal_id}"
            base_row = base_rows.get(base_coordinate)
            if base_row is None:
                if base_coordinate != "6:3673:0":
                    raise RuntimeError(
                        f"segment {SEGMENT} missing Base decision: "
                        f"{base_coordinate}"
                    )
                base_translations.append(base_current_literals[literal_id])
            else:
                base_translations.append(str(base_row["translation"]))
        base_evidence.append(
            (
                record_id,
                base_record_id,
                sha256_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)].data
                ),
                sha256_bytes(
                    base_source[(BLOCK_ID, base_record_id)].data
                ),
                pk_literals,
                base_literals,
                tuple(base_translations),
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
            elif coordinate in INVISIBLE_CURRENT_COORDINATES:
                translation = literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )[literal_id]
                owner = "invisible_current"
                seen_invisible.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: {coordinate}"
                )
            owners.append(owner)
            completed.append(translation)
            complete_replacements[key] = translation
        if record_id in EXACT_BASE_RECORD_IDS:
            if tuple(completed) != tuple(base_translations):
                raise RuntimeError(
                    f"segment {SEGMENT} exact Base wording drifted: "
                    f"{record_id}"
                )
        elif (
            re.sub(r"\s+", "", "".join(completed))
            != re.sub(r"\s+", "", "".join(base_translations))
        ):
            raise RuntimeError(
                f"segment {SEGMENT} split Base wording drifted: {record_id}"
            )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(completed),
                tuple(base_translations),
                runtime_controls(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                ),
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_invisible != set(INVISIBLE_CURRENT_COORDINATES)
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
        3644: "gift_affinity_intro",
        3645: "gift_preference_polite_question",
        3646: "gift_preference_formal_question",
        3648: "gift_preference_surprise",
        3652: "gift_preference_assertion",
        3655: "gift_preference_blunt_question",
        3656: "gift_honor_polite_question",
        3657: "gift_gratitude_humble",
        3658: "gift_delight_emphatic",
        3659: "gift_surprise_gratitude",
        3661: "gift_humble_receipt",
        3665: "gift_discernment_praise",
        3670: "gift_formal_gratitude",
        3672: "confiscation_shock",
        3673: "confiscation_elder_protest",
        3674: "confiscation_formal_protest",
        3675: "confiscation_feminine_protest",
        3676: "confiscation_emphatic_refusal",
        3677: "confiscation_blunt_disbelief",
        3678: "confiscation_humble_appeal",
        3680: "confiscation_polite_plea",
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
        ("preference", "취향"),
        ("fine_gift", "일품"),
        ("honor", "영광"),
        ("gratitude", "감사"),
        ("discernment", "안목"),
        ("take_away", "거두어 가다"),
        ("resolutely", "결단코"),
        ("allow", "용납하다"),
    )
    guarded_digest(
        "EXPECTED_TERMINOLOGY_POLICY_SHA256",
        terminology,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    categories = tuple(
        (
            record_id,
            runtime_category(record_id),
            "runtime_fragment_pending",
            "pending",
            "runtime_pending",
            record_id in SPLIT_ADAPTED_RECORD_IDS,
            False,
        )
        for record_id in TARGET_RECORD_IDS
    )
    guarded_digest(
        "EXPECTED_RUNTIME_CATEGORY_SHA256",
        categories,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
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


def assert_candidate_records(
    current_records: dict[tuple[int, int], Any],
    candidate_records: dict[tuple[int, int], Any],
    target_record_ids: tuple[int, ...],
) -> None:
    target_keys = {
        (BLOCK_ID, record_id) for record_id in target_record_ids
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
        if gap_bytes(candidate_records[key]) != gap_bytes(
            current_records[key]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed runtime gaps: {key}"
            )


def build_candidates(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    complete_replacements: dict[tuple[int, int, int], str],
) -> tuple[bytes, str, int, bytes]:
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
    assert_candidate_records(
        current_records, candidate_records, TARGET_RECORD_IDS
    )
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
    complete_candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob, complete_replacements
    )
    complete_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(complete_candidate).archive
    )
    assert_candidate_records(
        current_records, complete_records, TARGET_RECORD_IDS
    )
    for key, translation in complete_replacements.items():
        if literal_texts(complete_records, key[:2])[key[2]] != translation:
            raise RuntimeError(
                f"segment {SEGMENT} complete assembly drifted: {key}"
            )
    if (
        ENGINE.rebuild_packed_with_literals(
            complete_candidate, complete_reverse
        )
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} complete assembly reverse drifted"
        )
    guarded_raw_digest(
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256",
        complete_candidate,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )
    return candidate, candidate_sha256, changed, complete_candidate


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: {record_id}"
        )
    return {
        "runtime_category": runtime_category(record_id),
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companions_reviewed": True,
        "invisible_newline_companion_reviewed": record_id == 3680,
        "protected_outer_whitespace_preserved": True,
        "base_wording_contextually_adapted":
        record_id in SPLIT_ADAPTED_RECORD_IDS,
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
    candidate, candidate_sha256, changed, complete_candidate = (
        build_candidates(
            prepared, records_by_label, complete_replacements
        )
    )
    if DISCOVERED_PINS:
        return (
            prepared,
            [],
            candidate,
            candidate_sha256,
            changed,
            complete_candidate,
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
                "invisible_newline_companion_reviewed":
                record_id == 3680,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted":
                record_id in SPLIT_ADAPTED_RECORD_IDS,
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
        complete_candidate,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1125-tamper-", dir=DECISIONS_ROOT
    ) as directory:
        tampered_path = (
            Path(directory) / "tampered.private.v1.jsonl"
        )
        ENGINE.atomic_write(tampered_path, ENGINE.jsonl(tampered_rows))
        try:
            ENGINE.validate_decisions(
                prepared, tampered_path, require_complete=False
            )
        except ENGINE.RetranslationError:
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} source tamper was accepted"
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
        complete_candidate,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or complete_candidate != second[5]
        or optional_present != second[6]
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
    if (
        len(rows) != 30
        or len(validated) != 30
        or counts != Counter({"runtime_fragment_pending": 30})
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
    if sha256_bytes(steam_path.read_bytes()) != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B038_S1125",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 37,
                "base_semantic_reference_count": len(rows),
                "exact_base_record_count":
                len(EXACT_BASE_RECORD_IDS),
                "split_adapted_base_record_count":
                len(SPLIT_ADAPTED_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_newline_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "complete_assembly_sha256":
                EXPECTED_COMPLETE_ASSEMBLY_SHA256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_only": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "prefill_companions_guarded": True,
                "invisible_newline_companion_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "direct_calls_and_tokens_guarded": True,
                "protected_outer_whitespace_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
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
