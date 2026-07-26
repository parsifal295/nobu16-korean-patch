#!/usr/bin/env python3
"""Build source-redacted PK B028 segment 1098 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch027_segment1095.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B028_S1098.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B027_S1095.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B027_S1096.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B027_S1097.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B028_S1099.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B028_S1100.private.v1.jsonl",
)

SEGMENT = 1098
QUEUE_BATCH_ID = "pk_msggame-B028"
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
        "pc_dialogue_full_retranslation_v0150_pk_s1098_common",
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
    "6:2251:0",
    "6:2252:0",
    "6:2253:0",
    "6:2261:0",
    "6:2291:0",
)
TRANSLATIONS = {
    "6:2251:0": "분명…",
    "6:2252:0": "어머…",
    "6:2253:0": "이런,",
    "6:2261:0": "뭐,",
    "6:2291:0": "우선",
}
TARGET_RECORD_IDS = tuple(
    coordinate_key(value)[1] for value in TARGET_COORDINATES
)
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
SLICE_RECORD_IDS = tuple(range(2249, 2307))
BOUNDARY_RECORD_IDS = (2248, 2307)
HIDDEN_COORDINATES = ("6:2306:1",)
DIRECT_CALL_RECORD_IDS = (2249, 2255, 2259, 2289, 2291, 2306)
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
EXPECTED_TARGET_GAPS = {
    2251: ("", "024635", "050505"),
    2252: ("", "024634", "050505"),
    2253: ("", "024635", "050505"),
    2261: ("", "024634", "050505"),
    2291: ("", "014308000000", "050505"),
}
EXPECTED_TARGET_DIRECT_CALLS = {
    2251: (),
    2252: (),
    2253: (),
    2261: (),
    2291: (8,),
}
EXPECTED_TARGET_INLINE_TOKENS = {
    2251: ("4635",),
    2252: ("4634",),
    2253: ("4635",),
    2261: ("4634",),
    2291: (),
}
EXPECTED_DIRECT_CALLS = {
    2249: (8,),
    2255: (8,),
    2259: (8,),
    2289: (8,),
    2291: (8,),
    2306: (1,),
}
EXPECTED_ASSEMBLIES = {
    2251: ("분명…", "님이었지. 와 있었나"),
    2252: ("어머…", "님이신가요…"),
    2253: ("이런,", "님이 나타나다니…"),
    2261: (
        "뭐,",
        "? 꾀병을 핑계로 돌려보내라\n"
        "…이런, 벌써 들어와 앉았구먼",
    ),
    2291: (
        "우선",
        "이(가) 성의를 보여라\n이야기는 그다음이다",
    ),
}
TERMINOLOGY_SCOPE = {
    "honorific": ("님", "required_with_dynamic_person_name"),
    "retainers": ("가신들", "required_in_full_slice"),
    "musket_unit": ("철포대", "required_in_full_slice"),
    "clan_house": ("가문", "required_in_full_slice"),
    "negotiation": ("교섭", "required_in_hidden_record"),
    "speaker_register": (
        "plain_female_polite_elder_brisk",
        "required",
    ),
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "D45E9138B4227C31D2038E93F0BBBE6899350520F687798F77A39E631EEF4267"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "478E5E73AD5AE8BD76FCD0CE19AF2E766803E72E54566BAA8D732067CD24C029"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "A538865AC60E5533D8F885B814541EDC734DFABA74E6E12D266D5873F5B94638"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "90774DEB329CCCF908684058E85DDF796A74C22EE93A8C4C6410E76782536672"
)
EXPECTED_HIDDEN_COORDINATE_SHA256 = (
    "24AC0F2A5B6AB2989730B702D40894EB4189E13C7CA1564893CB2270725CCCB2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "302D1A7C7B0C1975D076EEDCE7520DF2CCA64B4FB8BFB387DF8E6ED96EAACC61"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "4E6A40A7E882DF50453DDB289F3CC9B1654A9D93D22B739DA7362F088626BEAD"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "518D2686CB1E533E728662BC114C13CB53127DB8AFBDA6F13D3108766A71F780"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "62CCC158623E558D5E7BBD2F1D6C0BCDDE2423E3002E664564E2AD2439D7A084"
)
EXPECTED_BOUNDARY_SHA256 = (
    "11E495F96AF489DC3D9BD8A43C5342823F55CD65E2506A838DF7D31D333DDF76"
)
EXPECTED_RUNTIME_RECORD_SHA256 = (
    "D4DD3DFFD74B546AB9C2A2618FF262DB30D0D94F844829EFA9670A4595DB269A"
)
EXPECTED_BASE_RECORD_SHA256 = (
    "0DA6F21D0DABE66905ABE3EE198617E84AFE22EB34E154A1343BB137B7254C17"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "91A3D453B3C6D0192D5AEDACB63C82ED522CAC3A7FFE5C42B6D94DADEB52B44A"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "33D1CBD85ADEC2F5C46871A6EE9D105CEE395DF183ED1684C681BCF03ED07218"
)
EXPECTED_HIDDEN_CONTEXT_SHA256 = (
    "E55DD953BE4AF4BF98703FB5EBED41C3E082FED57518D35DBAC349C44C5BC6D4"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "5D3E77F0DBF238ACD1FC6A31828A0042F277BEC63D4D1C251195AD90060F8923"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "0A4BC9FC7A16CC36A942BB54D85EA5F9489F1CC99080B68DA4A7038DDAD9EFC7"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3E459FB9BF319B811935B0C14AF242ABF7BBAF055FC83AF8ABC41E6AE5D9E6A8"
)
EXPECTED_CANDIDATE_SHA256 = "D88A40450E898A5F3C2C27017880D9B4D9DC0A74C53A226AC8541DC5D7742969"
EXPECTED_CHANGED_LITERAL_COUNT = 1

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; sixty-two exact-overlap "
    "prefill rows in the assigned sixty-seven-visible queue slice, one "
    "same-record hidden companion just beyond the slice and five residual "
    "fragments are pinned; every one of the fifty-eight complete records "
    "is reconstructed from segment and Base-backed prefill decisions "
    "without current-text fallback; corresponding Base records are exact "
    "raw, literal, opcode and runtime-token donors but Base runtime state "
    "is not inherited; dynamic person-name tokens 4634 and 4635, direct "
    "call 8, all six direct-call records in the full slice and the hidden "
    "record's call 1 are guarded; plain recognition, female polite "
    "surprise, reserved surprise, elder speech and brusque negotiation "
    "registers are reviewed with honorific, retainer, musket-unit, clan "
    "and negotiation terminology; outer whitespace, protected signatures, "
    "line counts, reverse overlay, two-run reproduction, tamper rejection "
    "and read-only inputs are guarded; all five residual PK fragments "
    "remain runtime pending"
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


def direct_calls(gaps: tuple[bytes, ...]) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gaps
        for match in re.finditer(
            b"\x01\x43(.{4})",
            gap,
            re.DOTALL,
        )
    )


def inline_tokens(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        match.group(1).hex().upper()
        for gap in gaps
        for match in re.finditer(
            b"\x02(.{2})",
            gap,
            re.DOTALL,
        )
    )


def requires_runtime(record: Any) -> bool:
    gaps = gap_bytes(record)
    return bool(direct_calls(gaps) or inline_tokens(gaps))


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
        len(queue_rows) != 174
        or len(visible) != 200
        or visible[0] != "6:2249:0"
        or visible[-1] != "6:2422:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B028 queue universe drifted"
        )
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:2249:0"
        or queue_slice[-1] != "6:2306:0"
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
    if len(prefilled) != 62:
        raise RuntimeError(
            f"segment {SEGMENT} prefill count drifted: "
            f"{len(prefilled)}"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    hidden = tuple(
        coordinate
        for coordinate in HIDDEN_COORDINATES
        if coordinate in prefill_rows
        and coordinate not in queue_slice
    )
    if hidden != HIDDEN_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} hidden companion drifted"
        )
    guarded_digest(
        "hidden coordinate",
        hidden,
        EXPECTED_HIDDEN_COORDINATE_SHA256,
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
    if residual != TARGET_COORDINATES or len(residual) != 5:
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
    context_ids = tuple(range(2248, 2308))
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
    runtime_records = tuple(
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
            direct_calls(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            inline_tokens(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for record_id in SLICE_RECORD_IDS
        if requires_runtime(
            records_by_label["jp"][(BLOCK_ID, record_id)]
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
            "runtime record",
            runtime_records,
            EXPECTED_RUNTIME_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)

    if any(source != current for _, source, current in gaps):
        raise RuntimeError(
            f"segment {SEGMENT} source/current gap drifted"
        )
    actual_direct_records = tuple(
        record_id
        for record_id, _, calls, _ in runtime_records
        if calls
    )
    if actual_direct_records != DIRECT_CALL_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} direct-call universe drifted"
        )
    for record_id, _, calls, _ in runtime_records:
        if (
            record_id in DIRECT_CALL_RECORD_IDS
            and calls != EXPECTED_DIRECT_CALLS[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} direct call drifted: "
                f"{record_id}"
            )
    for record_id in TARGET_RECORD_IDS:
        record = records_by_label["jp"][(BLOCK_ID, record_id)]
        actual_gaps = tuple(
            value.hex().upper() for value in gap_bytes(record)
        )
        if (
            actual_gaps != EXPECTED_TARGET_GAPS[record_id]
            or direct_calls(gap_bytes(record))
            != EXPECTED_TARGET_DIRECT_CALLS[record_id]
            or inline_tokens(gap_bytes(record))
            != EXPECTED_TARGET_INLINE_TOKENS[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target runtime drifted: "
                f"{record_id}"
            )


def assert_base_prefill_hidden_and_assembly(
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

    base_record_evidence: list[tuple[Any, ...]] = []
    for pk_record_id in SLICE_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[pk_record_id]
        pk_record = records_by_label["jp"][
            (BLOCK_ID, pk_record_id)
        ]
        base_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        source_equal = (
            literal_texts(
                records_by_label["jp"],
                (BLOCK_ID, pk_record_id),
            )
            == literal_texts(
                base_source_records,
                (BLOCK_ID, base_record_id),
            )
        )
        raw_equal = pk_record.data == base_record.data
        pk_gaps = tuple(
            value.hex().upper() for value in gap_bytes(pk_record)
        )
        base_gaps = tuple(
            value.hex().upper() for value in gap_bytes(base_record)
        )
        base_record_evidence.append(
            (
                pk_record_id,
                base_record_id,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                source_equal,
                raw_equal,
                pk_gaps,
                base_gaps,
                direct_calls(gap_bytes(pk_record)),
                direct_calls(gap_bytes(base_record)),
                inline_tokens(gap_bytes(pk_record)),
                inline_tokens(gap_bytes(base_record)),
            )
        )
        if (
            not source_equal
            or not raw_equal
            or pk_gaps != base_gaps
            or direct_calls(gap_bytes(pk_record))
            != direct_calls(gap_bytes(base_record))
            or inline_tokens(gap_bytes(pk_record))
            != inline_tokens(gap_bytes(base_record))
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base exact record drifted: "
                f"{pk_record_id}"
            )
    guarded_digest(
        "Base record",
        tuple(base_record_evidence),
        EXPECTED_BASE_RECORD_SHA256,
    )

    full_coordinates = tuple(
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
        for coordinate in full_coordinates
        if coordinate in prefill_rows
    )
    if (
        len(full_coordinates) != 68
        or len(prefill_coordinates) != 63
        or HIDDEN_COORDINATES[0] not in prefill_coordinates
    ):
        raise RuntimeError(
            f"segment {SEGMENT} full assembly coordinate drifted"
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
        if coordinate not in HIDDEN_COORDINATES
    )
    hidden_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
        )
        for coordinate in HIDDEN_COORDINATES
    )
    if (
        len(prefill_evidence) != 62
        or any(
            semantic != "approved"
            or runtime not in ("pending", "not_required")
            for _, _, semantic, runtime, _, _ in prefill_evidence
        )
        or any(
            semantic != "approved" or runtime != "pending"
            for _, _, semantic, runtime, _ in hidden_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill or hidden context drifted"
        )
    guarded_digest(
        "prefill context",
        prefill_evidence,
        EXPECTED_PREFILL_CONTEXT_SHA256,
    )
    guarded_digest(
        "hidden context",
        hidden_evidence,
        EXPECTED_HIDDEN_CONTEXT_SHA256,
    )

    assembly_evidence: list[tuple[Any, ...]] = []
    base_evidence: list[tuple[Any, ...]] = []
    assembly_map: dict[int, tuple[str, ...]] = {}
    for record_id in SLICE_RECORD_IDS:
        translations: list[str] = []
        owners: list[str] = []
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
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
                owner = (
                    "hidden_prefill"
                    if coordinate in HIDDEN_COORDINATES
                    else "prefill"
                )
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} current fallback forbidden: "
                    f"{coordinate}"
                )
            base_row = base_rows[base_coordinate]
            if (
                base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review")
                not in ("verified", "not_required")
                or translation != base_row.get("translation")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base semantic donor drifted: "
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
        assembly_map[record_id] = tuple(translations)
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(source_record)
                ),
                direct_calls(gap_bytes(source_record)),
                inline_tokens(gap_bytes(source_record)),
            )
        )
        if "current" in owners:
            raise RuntimeError(
                f"segment {SEGMENT} current assembly fallback: "
                f"{record_id}"
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

    if any(
        base_rows[BASE_CONTEXT_REFERENCES[coordinate]].get(
            "runtime_review"
        )
        != "verified"
        for coordinate in TARGET_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target Base runtime donor drifted"
        )
    if any(
        assembly_map[record_id] != expected
        for record_id, expected in EXPECTED_ASSEMBLIES.items()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target assembly drifted"
        )
    if (
        "철포대" not in assembly_map[2259][0]
        or "가신들" not in assembly_map[2283][0]
        or "우리 가문" not in assembly_map[2280][0]
        or "그대 가문" not in assembly_map[2280][0]
        or assembly_map[2306]
        != ("교섭 또한 싸움이니\n", "을(를) 납득시켜 보시오")
        or any(
            "주군" in text
            for record_id in TARGET_RECORD_IDS
            for text in assembly_map[record_id]
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} historical terminology drifted"
        )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_SCOPE,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or len(TARGET_COORDINATES) != 5
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
    changed_coordinates: list[str] = []
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
        if translation != current_text:
            changed_coordinates.append(coordinate)
    if (
        tuple(changed_coordinates) != ("6:2253:0",)
        or TRANSLATIONS["6:2253:0"] != "이런,"
        or TRANSLATIONS["6:2251:0"] != "분명…"
        or TRANSLATIONS["6:2252:0"] != "어머…"
        or TRANSLATIONS["6:2261:0"] != "뭐,"
        or TRANSLATIONS["6:2291:0"] != "우선"
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
        2251: "plain_recognition",
        2252: "female_polite_surprise",
        2253: "reserved_surprise",
        2261: "elder_plain_command",
        2291: "brusque_negotiation_order",
    }[record_id]


def runtime_order(record_id: int) -> tuple[str, ...]:
    if record_id == 2291:
        return (
            "brusque_negotiation_intro",
            "direct_call_8_subject",
            "imperative_sincerity_demand",
        )
    return (
        "speaker_reaction_intro",
        (
            "dynamic_person_name_4635"
            if record_id in (2251, 2253)
            else "dynamic_person_name_4634"
        ),
        "same_record_register_companion",
    )


def control_evidence(
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
    base_record = base_source_records[
        (BLOCK_ID, BASE_RECORD_MAPPING[record_id])
    ]
    source_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(source_record)
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(current_record)
    )
    base_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(base_record)
    )
    source_calls = direct_calls(gap_bytes(source_record))
    current_calls = direct_calls(gap_bytes(current_record))
    base_calls = direct_calls(gap_bytes(base_record))
    source_tokens = inline_tokens(gap_bytes(source_record))
    current_tokens = inline_tokens(gap_bytes(current_record))
    base_tokens = inline_tokens(gap_bytes(base_record))
    if (
        source_gap_hex != EXPECTED_TARGET_GAPS[record_id]
        or current_gap_hex != source_gap_hex
        or base_gap_hex != source_gap_hex
        or source_calls
        != EXPECTED_TARGET_DIRECT_CALLS[record_id]
        or current_calls != source_calls
        or base_calls != source_calls
        or source_tokens
        != EXPECTED_TARGET_INLINE_TOKENS[record_id]
        or current_tokens != source_tokens
        or base_tokens != source_tokens
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
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
        "source_direct_call_operands": source_calls,
        "current_direct_call_operands": current_calls,
        "base_direct_call_operands": base_calls,
        "source_inline_runtime_tokens": source_tokens,
        "current_inline_runtime_tokens": current_tokens,
        "base_inline_runtime_tokens": base_tokens,
        "runtime_order": runtime_order(record_id),
        "record_variant": "hostile_diplomatic_reception",
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_prefill_companion_reviewed": True,
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
    assert_base_prefill_hidden_and_assembly(records_by_label)
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
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "same_record_hidden_companion_review": True,
            "base_context_reference_coordinate":
            BASE_CONTEXT_REFERENCES[coordinate],
            "base_semantic_translation_reused": True,
            "base_source_literal_exact": True,
            "base_record_opcode_exact": True,
            "base_runtime_state_inherited": False,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "protected_signature_review": True,
            "same_record_prefill_companion_coordinates":
            companion_coordinates,
            "record_variant": "hostile_diplomatic_reception",
            "speaker_register_variant":
            speaker_register_variant(record_id),
            "runtime_assembly_evidence":
            control_evidence(
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
        len(rows) != 5
        or len(validated) != 5
        or counts != Counter({"runtime_fragment_pending": 5})
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
                "segment": "pk_msggame_B028_S1098",
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
                "exact_reuse_prefill_count": 62,
                "residual_count": 5,
                "hidden_companion_count":
                len(HIDDEN_COORDINATES),
                "reviewed_complete_record_count":
                len(SLICE_RECORD_IDS),
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
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "hidden_companion_guarded": True,
                "complete_record_assembly_guarded": True,
                "historical_terms_reviewed": True,
                "speaker_registers_reviewed": True,
                "runtime_tokens_guarded": True,
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
