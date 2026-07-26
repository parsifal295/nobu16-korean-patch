#!/usr/bin/env python3
"""Build source-redacted PK B023 segment 1086 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B023_S1086.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B022_S1083.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B022_S1084.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B022_S1085.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B023_S1087.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B023_S1088.private.v1.jsonl",
)

SEGMENT = 1086
QUEUE_BATCH_ID = "pk_msggame-B023"
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
        "pc_dialogue_full_retranslation_v0150_pk_s1086_common",
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
    "6:1570:1",
    "6:1575:0",
    "6:1578:1",
    "6:1590:1",
    "6:1594:0",
    "6:1594:1",
    "6:1599:0",
    "6:1601:1",
)
TRANSLATIONS = {
    "6:1570:1": (
        " 의 무리\n뿐만 아니라, 우리를 배신하면 어떤\n"
        "꼴이 되는지 여러 나라에 보여 줘야 하오!"
    ),
    "6:1575:0": "이놈,",
    "6:1578:1": (
        " 이(가) 단교 같은 짓을 저지르다니.\n"
        "내버려 두면 후환이 될 것입니다"
    ),
    "6:1590:1": " 은(는)\n저처럼",
    "6:1594:0": "흠,",
    "6:1594:1": (
        " 이(가) 우리 가문에 종속했다고.\n"
        "그렇다면 그들과 말고삐를 나란히 하고\n"
        "무공을 겨루겠군. 벌써 팔이 근질거리는구려"
    ),
    "6:1599:0": "설마",
    "6:1601:1": (
        " 은(는)\n이제 우리가 뒷받침하여 더욱\n"
        "강해지게 해야겠지요"
    ),
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (1570, 1575, 1578, 1590, 1594, 1599, 1601)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
SLICE_RECORD_IDS = tuple(range(1567, 1608))
BOUNDARY_RECORD_IDS = (1566, 1608)
DIRECT_CALL_RECORD_IDS = (1582, 1590)
BASE_RECORD_MAPPING = {
    record_id: record_id - 6 for record_id in SLICE_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{coordinate_key(coordinate)[1] - 6}:"
        f"{coordinate_key(coordinate)[2]}"
    )
    for coordinate in TARGET_COORDINATES
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0C8AFBB92655741DC6447409E3BB0075696E0CD6B9A066FBD4AC776BBFB4AB97"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "B8E4FBA5E723A6391FFA597D2E9761FFE7952B06540B2903595E1A7C9E00F942"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "B831A8AD316740F728FE157BB760FBE6DE11C7CFE9F8503F99410B1623D08DFE"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "010C121DF136908D2B46297787276A70AC68814884EE71359E0ED12F4BF5381A"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "1766BA63C3B86563BD4D049B697A8712BD8CE89C340E03960B8EAB3E146D66D9"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "5C70CC17055FB3CEB7EE17B1F984ADCF41D527A454C07DD0FFFD3F127C205EB5"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "488D897269F948BA303AEF1C1845AD88A1E7F7D9B0A0847BA29A4C7F40A7DA29"
)
EXPECTED_BOUNDARY_SHA256 = (
    "F7B3505498F74B842EB6BB97CB6D27B253D8D59A09E15BB9B3BE1ABCDC3411C1"
)
EXPECTED_DIRECT_CALL_SHA256 = (
    "BA4BADAB5A1A62554C8281DF49C59665D38117BFDCE79D993CD6B438D94F0D93"
)
EXPECTED_BASE_EXACT_RECORD_SHA256 = (
    "B60D723C9CF7CFA74F92B35E29969FA3F7EA052822301A6C54EB7AED23CB2AA0"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "9F14D1B73EBC6E839CE3F9FC3BD254ADB528C3A26DDB27D0B26D1E437BF4DD6C"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "FB2AA27F4039BDBC403CBC4BC7EEAD291CC66AB08A5D6157E25ADEDAFDFC6700"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "A7B6D4B57FFB445555E8DB6B765BEC73C7E68FC90F27CD855E8A78643A11E756"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "79BFE6214D05A651CEF841AEB6B85D65481AC170F7DF5ABF4F656A6B58E0C2E6"
)
EXPECTED_CANDIDATE_SHA256 = (
    "D13D11D0AD694D3BDE7C6E4E3CEED6719244D636F60D8375F8D516FC36258F82"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6

EXPECTED_DIRECT_CALL_GAPS = {
    1582: ("025032", "014308000000", "050505"),
    1590: ("", "025032", "014308000000", "050505"),
}
EXPECTED_DIRECT_CALL_OPERANDS = {1582: (8,), 1590: (8,)}

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; all fifty-eight exact-reuse "
    "prefill rows in the queue slice and completed Base runtime-verified "
    "semantic donors are pinned; all forty-one slice records exactly map "
    "to their completed Base source records; the one Base three-line "
    "donor is folded once to retain the PK two-line layout without changing "
    "meaning; the complete hostile severance and vassalage statements, "
    "single force-name particle relations and the target-force plus "
    "direct-call-8 retainer sentence are reviewed; the B019 dash rule is "
    "inapplicable because every name participates in a possessive, subject "
    "or topic relation inside a complete sentence; alliance, faith, "
    "punishment, vassalage, retainer and military-merit terminology, "
    "historical horse imagery, seven speaker registers, protected "
    "signatures, line counts, bytecode gaps, complete assembly ownership, "
    "reverse overlay, two-run reproduction, tamper rejection and read-only "
    "inputs are guarded; Base runtime state is not inherited and every "
    "residual PK fragment remains runtime pending"
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
        len(queue_rows) != 109
        or len(visible) != 196
        or visible[0] != "6:1567:0"
        or visible[-1] != "6:1675:5"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B023 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:1567:0"
        or queue_slice[-1] != "6:1607:0"
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
    if len(prefilled) != 58:
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
    if residual != TARGET_COORDINATES or len(residual) != 8:
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
    context_ids = tuple(range(1566, 1609))
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


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()):]
    return leading + donor.strip() + trailing


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
    exact_records = tuple(
        (
            pk_record_id,
            BASE_RECORD_MAPPING[pk_record_id],
            sha256_bytes(
                records_by_label["jp"][
                    (BLOCK_ID, pk_record_id)
                ].data
            ),
            sha256_bytes(
                base_source_records[
                    (BLOCK_ID, BASE_RECORD_MAPPING[pk_record_id])
                ].data
            ),
        )
        for pk_record_id in SLICE_RECORD_IDS
    )
    if any(pk_sha != base_sha for _, _, pk_sha, base_sha in exact_records):
        raise RuntimeError(
            f"segment {SEGMENT} Base exact record drifted"
        )
    guarded_digest(
        "Base exact record",
        exact_records,
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
        current_text = literal_texts(
            records_by_label["current"],
            pk_key[:2],
        )[pk_key[2]]
        base_row = base_rows[base_coordinate]
        adapted = adapt_outer_whitespace(
            str(base_row.get("translation")),
            current_text,
        )
        expected_translation = (
            adapted.replace("\n", " ", 1)
            if coordinate == "6:1578:1"
            else adapted
        )
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                pk_source,
                base_source,
                base_row.get("translation"),
                adapted,
                expected_translation,
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
            )
        )
        if (
            pk_source != base_source
            or TRANSLATIONS[coordinate] != expected_translation
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
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
        len(prefill_coordinates) != 58
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
        if "current" in owners or source_gaps != current_gaps:
            raise RuntimeError(
                f"segment {SEGMENT} complete assembly drifted: "
                f"{record_id}"
            )

    expected_assemblies = {
        1570: (
            "이렇게 된 이상",
            " 의 무리\n뿐만 아니라, 우리를 배신하면 어떤\n"
            "꼴이 되는지 여러 나라에 보여 줘야 하오!",
        ),
        1575: (
            "이놈,",
            "! 우리를\n배신한 대가는 톡톡히\n치르게 해야겠구나",
        ),
        1578: (
            "우리 가문의 산하에 있던",
            " 이(가) 단교 같은 짓을 저지르다니.\n"
            "내버려 두면 후환이 될 것입니다",
        ),
        1590: (
            "우리 가문에 종속했다고 해서",
            " 은(는)\n저처럼",
            "의 가신은 아닙니다.\n대우에 신경 써야 하겠지요",
        ),
        1594: (
            "흠,",
            " 이(가) 우리 가문에 종속했다고.\n"
            "그렇다면 그들과 말고삐를 나란히 하고\n"
            "무공을 겨루겠군. 벌써 팔이 근질거리는구려",
        ),
        1599: (
            "설마",
            "이(가) 우리 가문에 복종할 줄은\n"
            "젊었을 때는 생각지도 못했지.\n"
            "오래 살고 볼 일이로구나",
        ),
        1601: (
            "종속한 이상,",
            " 은(는)\n이제 우리가 뒷받침하여 더욱\n"
            "강해지게 해야겠지요",
        ),
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
        or len(TARGET_COORDINATES) != 8
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
        any("—" in value for value in TRANSLATIONS.values())
        or not TRANSLATIONS["6:1570:1"].startswith(" 의 무리\n")
        or TRANSLATIONS["6:1578:1"].count("\n") != 1
        or TRANSLATIONS["6:1590:1"] != " 은(는)\n저처럼"
        or "말고삐를 나란히" not in TRANSLATIONS["6:1594:1"]
        or TRANSLATIONS["6:1601:1"]
        != " 은(는)\n이제 우리가 뒷받침하여 더욱\n강해지게 해야겠지요"
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
    if record_id <= 1578:
        return "hostile_severance_response"
    if record_id == 1590:
        return "vassalage_force_and_direct_call_retainer"
    if record_id == 1594:
        return "vassalage_historical_horse_register"
    if record_id == 1599:
        return "vassalage_aged_speaker_surprise"
    return "vassalage_protection_obligation"


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
    if (
        record_id == 1590
        and (
            source_gap_hex != EXPECTED_DIRECT_CALL_GAPS[1590]
            or source_operands != (8,)
            or current_operands != source_operands
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target direct call drifted"
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
        "record_variant": record_variant(record_id),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_prefill_companions_reviewed": True,
        "target_force_particle_relation_preserved": True,
        "direct_call_8_position_preserved": record_id == 1590,
        "single_target_dash_rule_applicable": False,
        "single_target_dash_rule_applied": False,
        "hostile_or_vassalage_register_reviewed": True,
        "historical_terminology_and_imagery_reviewed": True,
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
            "base_linefold_adapted":
            coordinate == "6:1578:1",
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
        len(rows) != 8
        or len(validated) != 8
        or counts != Counter({"runtime_fragment_pending": 8})
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
                "segment": "pk_msggame_B023_S1086",
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
                "exact_reuse_prefill_count": 58,
                "residual_count": 8,
                "reviewed_slice_record_count":
                len(SLICE_RECORD_IDS),
                "reviewed_target_record_count":
                len(TARGET_RECORD_IDS),
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
                "base_linefold_adaptation_guarded": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "complete_slice_assembly_guarded": True,
                "direct_call_8_position_guarded": True,
                "target_force_particle_relations_preserved": True,
                "single_target_dash_rule_applied": False,
                "hostile_and_vassalage_registers_reviewed": True,
                "historical_terms_and_horse_imagery_reviewed": True,
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
