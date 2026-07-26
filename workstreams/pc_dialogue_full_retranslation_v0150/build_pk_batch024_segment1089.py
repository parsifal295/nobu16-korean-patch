#!/usr/bin/env python3
"""Build source-redacted PK B024 segment 1089 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch023_segment1088.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B024_S1089.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B023_S1086.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B023_S1087.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B023_S1088.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B024_S1090.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B024_S1091.private.v1.jsonl",
)

SEGMENT = 1089
QUEUE_BATCH_ID = "pk_msggame-B024"
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
        "pc_dialogue_full_retranslation_v0150_pk_s1089_common",
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

DEPARTMENT_RECORD_IDS = tuple(range(1676, 1682))
QUESTION_RECORD_ID = 1701
TARGET_RECORD_IDS = (*DEPARTMENT_RECORD_IDS, QUESTION_RECORD_ID)
TARGET_COORDINATES = (
    *(
        f"6:{record_id}:{literal_id}"
        for record_id in DEPARTMENT_RECORD_IDS
        for literal_id in (2, 3, 4, 5)
    ),
    "6:1701:1",
    "6:1701:2",
)
TRANSLATIONS = {
    **{
        f"6:{record_id}:{literal_id}": (
            ", 상공"
            if literal_id == 2
            else (
                ", 토목"
                if literal_id == 3
                else (
                    ", 문화" if literal_id == 4 else ", 치안"
                )
            )
        )
        for record_id in DEPARTMENT_RECORD_IDS
        for literal_id in (2, 3, 4, 5)
    },
    "6:1701:1": "\n정말 그래도 괜찮겠",
    "6:1701:2": "습니까?",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
SLICE_RECORD_IDS = tuple(range(1676, 1710))
BOUNDARY_RECORD_IDS = (1675, 1710)
DIRECT_CALL_RECORD_IDS = (1694, 1701)
BASE_CONTEXT_REFERENCES = {
    **{
        f"6:{record_id}:{literal_id}":
        f"6:{record_id - 6}:{literal_id}"
        for record_id in DEPARTMENT_RECORD_IDS
        for literal_id in (2, 3, 4, 5)
    },
    "6:1701:1": "6:1695:1",
    "6:1701:2": "6:1695:2",
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0700D956E19D22BB5E610B07FE961A7CAA75069A1EADC26718EFEAA6C75A5C99"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "92E33EAFDEF29F4B60B2D57605B5456BD05CA234EAD2A551C3499B5285963ECE"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "CE84C28D628A913D63301CC1760EBADA1203936AC22C1640E936DBEEC52AD63E"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "18A4D07ABBD16AF58E0811ED76F56514A024413B5BF22BA79BB2B98C1473219C"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "68BA53C4303EC2893243FCDF140152D109863BC20A6924A530073AD319F3B6AA"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "BC8D623CC92EFCB0EB3CDCE0FCA97C8DE57D4CEBD8234E29304AB80FD35535AD"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "152614D9605103B41935E7CB0990F10D6EEDE3D2A9B219A42D3BF4C4FFFBC6F0"
)
EXPECTED_BOUNDARY_SHA256 = (
    "772984B54B003AE4C5C22A6FC3C7B007B1B85D20151690B5C20518882D661468"
)
EXPECTED_DIRECT_CALL_SHA256 = (
    "2F08E2495A94584BD4C579DB12BE7774C10F73BA2D8457DFF18A7E4AC3589D55"
)
EXPECTED_BASE_EXACT_RECORD_SHA256 = (
    "348DC962B53E5B7AF089DE0D4D8827E71DDC2FCB1FA3D813976689672D13B3E8"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "7A4962DBC7541C5C821EBA85C271D5676E7A3BA0AD1F54A532D3BEBD975A4EBA"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "44B1F6DA8DA63FA7BB4806412301C6ABB3195DD7BBF27A744664B5B86538FEAD"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "119FEB56C3AE90C63774AB63EF5832888E3B0A2C9AFF49419645405FCB702104"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "FCD3A2D6EF8BA4B1A7892CF8481C9404B7F0D34A65F5C240BEA0598575B069A7"
)
EXPECTED_CANDIDATE_SHA256 = (
    "252E9F514B038E2B413EF1B498FE5DEA7C74270CD22C7977447D093980A652F5"
)
EXPECTED_CHANGED_LITERAL_COUNT = 8

EXPECTED_DEPARTMENT_GAPS = (
    "",
    "0232",
    "0232",
    "0233",
    "0234",
    "0235",
    "0236050505",
)
EXPECTED_DIRECT_CALL_GAPS = {
    1694: ("", "014308000000", "050505"),
    1701: (
        "025032",
        "014348040000",
        "01430C010000",
        "050505",
    ),
}
EXPECTED_DIRECT_CALL_OPERANDS = {
    1694: (8,),
    1701: (1096, 268),
}
EXPECTED_BASE_1701_MASKED_GAPS = (
    "025032",
    "014300000000",
    "014300000000",
    "050505",
)

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; all forty-one exact-reuse "
    "prefill rows in the queue slice and completed Base runtime-verified "
    "semantic donors are pinned; six six-literal financial reports are "
    "reviewed as complete amount, farming, industry, civil-works, culture "
    "and public-order assemblies with every conditional department token; "
    "the historical policy department is consistently rendered as civil "
    "works rather than generic infrastructure or corvee labor; the PK-only "
    "orthographic question variant reuses the completed Base question "
    "semantics while its shifted first direct-call operand and unchanged "
    "second terminal-call operand are independently guarded; all thirty-four "
    "slice records, both direct-call records, six speaker registers, policy, "
    "diplomacy, submission, court-conciliation and rank terminology, "
    "protected signatures, line counts, bytecode gaps, complete assembly "
    "ownership, reverse overlay, two-run reproduction, tamper rejection and "
    "read-only inputs are guarded; Base runtime state is not inherited and "
    "every residual PK fragment remains runtime pending"
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
        len(queue_rows) != 160
        or len(visible) != 200
        or visible[0] != "6:1676:0"
        or visible[-1] != "6:1835:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B024 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:1676:0"
        or queue_slice[-1] != "6:1709:0"
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
    if len(prefilled) != 41:
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
    if residual != TARGET_COORDINATES or len(residual) != 26:
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
    context_ids = tuple(range(1675, 1711))
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
    for (
        record_id,
        source_gaps,
        source_operands,
        current_gaps,
        current_operands,
    ) in direct_calls:
        if (
            source_gaps != EXPECTED_DIRECT_CALL_GAPS[record_id]
            or current_gaps != source_gaps
            or source_operands
            != EXPECTED_DIRECT_CALL_OPERANDS[record_id]
            or current_operands != source_operands
        ):
            raise RuntimeError(
                f"segment {SEGMENT} direct call drifted: "
                f"{record_id}"
            )
    if any(
        source != EXPECTED_DEPARTMENT_GAPS
        for record_id, source, _ in gaps
        if record_id in DEPARTMENT_RECORD_IDS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} department token drifted"
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
        if pk_record_id == QUESTION_RECORD_ID:
            continue
        first_coordinate = f"6:{pk_record_id}:0"
        base_coordinate = (
            prefill_rows[first_coordinate][
                "base_exact_reuse_prefill"
            ]["base_coordinate"]
        )
        base_record_id = coordinate_key(base_coordinate)[1]
        pk_sha = sha256_bytes(
            records_by_label["jp"][
                (BLOCK_ID, pk_record_id)
            ].data
        )
        base_sha = sha256_bytes(
            base_source_records[
                (BLOCK_ID, base_record_id)
            ].data
        )
        exact_records.append(
            (
                pk_record_id,
                base_record_id,
                pk_sha,
                base_sha,
            )
        )
        if pk_sha != base_sha:
            raise RuntimeError(
                f"segment {SEGMENT} Base exact record drifted: "
                f"{pk_record_id}"
            )
    guarded_digest(
        "Base exact record",
        tuple(exact_records),
        EXPECTED_BASE_EXACT_RECORD_SHA256,
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
        exact_source = pk_source == base_source
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                pk_source,
                base_source,
                exact_source,
                base_row.get("translation"),
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
            )
        )
        expected_exact = coordinate != "6:1701:1"
        if (
            exact_source is not expected_exact
            or TRANSLATIONS[coordinate]
            != base_row.get("translation")
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base semantic donor drifted: "
                f"{coordinate}"
            )
    pk_question = records_by_label["jp"][
        (BLOCK_ID, QUESTION_RECORD_ID)
    ]
    base_question = base_source_records[(BLOCK_ID, 1695)]
    if (
        masked_gap_tuple(pk_question)
        != EXPECTED_BASE_1701_MASKED_GAPS
        or masked_gap_tuple(base_question)
        != EXPECTED_BASE_1701_MASKED_GAPS
        or direct_call_operands(pk_question) != (1096, 268)
        or direct_call_operands(base_question) != (1084, 268)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base question template drifted"
        )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
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
        len(prefill_coordinates) != 41
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
    owner_map: dict[int, tuple[str, ...]] = {}
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
        if "current" in owners or source_gaps != current_gaps:
            raise RuntimeError(
                f"segment {SEGMENT} complete assembly drifted: "
                f"{record_id}"
            )

    for record_id in DEPARTMENT_RECORD_IDS:
        if (
            owner_map[record_id]
            != (
                "prefill",
                "prefill",
                "segment",
                "segment",
                "segment",
                "segment",
            )
            or assembly_map[record_id][2:]
            != (", 상공", ", 토목", ", 문화", ", 치안")
        ):
            raise RuntimeError(
                f"segment {SEGMENT} department assembly drifted: "
                f"{record_id}"
            )
    if (
        owner_map[QUESTION_RECORD_ID]
        != ("prefill", "segment", "segment")
        or assembly_map[QUESTION_RECORD_ID]
        != (
            "에게 종속하면\n다른 외교 관계는 모두 해소되고",
            "\n정말 그래도 괜찮겠",
            "습니까?",
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} question assembly drifted"
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
        or len(TARGET_COORDINATES) != 26
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
            TRANSLATIONS[f"6:{record_id}:2"] != ", 상공"
            or TRANSLATIONS[f"6:{record_id}:3"] != ", 토목"
            or TRANSLATIONS[f"6:{record_id}:4"] != ", 문화"
            or TRANSLATIONS[f"6:{record_id}:5"] != ", 치안"
            for record_id in DEPARTMENT_RECORD_IDS
        )
        or any(
            unwanted in TRANSLATIONS.values()
            for unwanted in (", 기반 시설", ", 부역")
        )
        or TRANSLATIONS["6:1701:1"]
        != "\n정말 그래도 괜찮겠"
        or TRANSLATIONS["6:1701:2"] != "습니까?"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} wording or terminology drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def record_variant(record_id: int) -> str:
    if record_id in DEPARTMENT_RECORD_IDS:
        return "six_literal_department_decrease_report"
    return "submission_confirmation_direct_calls"


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
    source_operands = direct_call_operands(source_record)
    current_operands = direct_call_operands(current_record)
    if source_gap_hex != current_gap_hex:
        raise RuntimeError(
            f"segment {SEGMENT} runtime controls drifted: "
            f"{record_id}"
        )
    if record_id in DEPARTMENT_RECORD_IDS:
        if source_gap_hex != EXPECTED_DEPARTMENT_GAPS:
            raise RuntimeError(
                f"segment {SEGMENT} department controls drifted"
            )
        runtime_order = (
            "report_prefix",
            "decrease_amount_0232",
            "farming_label",
            "farming_condition_0232",
            "industry_label",
            "industry_condition_0233",
            "civil_works_label",
            "civil_works_condition_0234",
            "culture_label",
            "culture_condition_0235",
            "public_order_label",
            "public_order_condition_0236",
        )
    else:
        if (
            source_gap_hex != EXPECTED_DIRECT_CALL_GAPS[1701]
            or source_operands != (1096, 268)
            or current_operands != source_operands
        ):
            raise RuntimeError(
                f"segment {SEGMENT} question controls drifted"
            )
        runtime_order = (
            "target_force_025032",
            "submission_consequence_prefix",
            "direct_call_1096",
            "question_stem",
            "direct_call_268",
            "polite_question_ending",
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
        "source_current_runtime_gap_equal": True,
        "source_direct_call_operands": source_operands,
        "current_direct_call_operands": current_operands,
        "runtime_order": runtime_order,
        "record_variant": record_variant(record_id),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_prefill_companions_reviewed": True,
        "department_condition_tokens_reviewed":
        record_id in DEPARTMENT_RECORD_IDS,
        "historical_civil_works_term_reviewed":
        record_id in DEPARTMENT_RECORD_IDS,
        "question_direct_call_positions_reviewed":
        record_id == QUESTION_RECORD_ID,
        "speaker_register_reviewed": True,
        "historical_and_policy_terminology_reviewed": True,
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
            BASE_CONTEXT_REFERENCES[coordinate],
            "base_semantic_translation_reused": True,
            "base_source_orthographic_variant":
            coordinate == "6:1701:1",
            "base_runtime_state_inherited": False,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "protected_signature_review": True,
            "same_record_prefill_companion_coordinates":
            companion_coordinates,
            "record_variant": record_variant(record_id),
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
        len(rows) != 26
        or len(validated) != 26
        or counts != Counter({"runtime_fragment_pending": 26})
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
                "segment": "pk_msggame_B024_S1089",
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
                "exact_reuse_prefill_count": 41,
                "residual_count": 26,
                "reviewed_slice_record_count":
                len(SLICE_RECORD_IDS),
                "department_record_count":
                len(DEPARTMENT_RECORD_IDS),
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
                "base_question_variant_guarded": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "complete_slice_assembly_guarded": True,
                "department_condition_tokens_guarded": True,
                "question_direct_call_operands_guarded": True,
                "historical_civil_works_term_reviewed": True,
                "six_speaker_registers_reviewed": True,
                "policy_diplomacy_court_terms_reviewed": True,
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
