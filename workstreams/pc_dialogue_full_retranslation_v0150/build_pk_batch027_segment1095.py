#!/usr/bin/env python3
"""Build source-redacted PK B027 segment 1095 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch026_segment1094.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B027_S1095.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B026_S1092.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B026_S1093.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B026_S1094.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B027_S1096.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B027_S1097.private.v1.jsonl",
)

SEGMENT = 1095
QUEUE_BATCH_ID = "pk_msggame-B027"
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
        "pc_dialogue_full_retranslation_v0150_pk_s1095_common",
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

DEFENSE_RECORD_IDS = tuple(range(2129, 2137))
ASSAULT_RECORD_IDS = tuple(range(2137, 2149))
FAILED_RECORD_IDS = (*DEFENSE_RECORD_IDS, *ASSAULT_RECORD_IDS)
SUCCESS_RECORD_IDS = tuple(range(2149, 2153))
SLICE_RECORD_IDS = (*FAILED_RECORD_IDS, *SUCCESS_RECORD_IDS)
TARGET_RECORD_IDS = FAILED_RECORD_IDS
TARGET_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in (1, 2)
)
TRANSLATIONS = {
    f"6:{record_id}:{literal_id}": (
        "지만\n"
        if literal_id == 1
        else "의 원군에는 감사"
    )
    for record_id in TARGET_RECORD_IDS
    for literal_id in (1, 2)
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (2128, 2153)
PK_SIBLING_RECORD_IDS = (2127, 2128)
HIDDEN_COORDINATES = ("6:2152:1",)
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

EXPECTED_FAILED_GAPS = (
    "026432",
    "014304030000",
    "025032",
    "01438E000000050505",
)
EXPECTED_BASE_FAILED_GAPS = (
    "026432",
    "0143F8020000",
    "025032",
    "01438E000000050505",
)
EXPECTED_FAILED_MASKED_GAPS = (
    "026432",
    "014300000000",
    "025032",
    "014300000000050505",
)
EXPECTED_SUCCESS_GAPS = (
    "026432",
    "025032",
    "01438E000000050505",
)
EXPECTED_GAPS_BY_RECORD = {
    **{
        record_id: EXPECTED_FAILED_GAPS
        for record_id in FAILED_RECORD_IDS
    },
    **{
        record_id: EXPECTED_SUCCESS_GAPS
        for record_id in SUCCESS_RECORD_IDS
    },
}
EXPECTED_BASE_GAPS_BY_RECORD = {
    **{
        record_id: EXPECTED_BASE_FAILED_GAPS
        for record_id in FAILED_RECORD_IDS
    },
    **{
        record_id: EXPECTED_SUCCESS_GAPS
        for record_id in SUCCESS_RECORD_IDS
    },
}
EXPECTED_PK_DIRECT_CALLS = {
    **{
        record_id: (772, 142)
        for record_id in FAILED_RECORD_IDS
    },
    **{
        record_id: (142,)
        for record_id in SUCCESS_RECORD_IDS
    },
}
EXPECTED_BASE_DIRECT_CALLS = {
    **{
        record_id: (760, 142)
        for record_id in FAILED_RECORD_IDS
    },
    **{
        record_id: (142,)
        for record_id in SUCCESS_RECORD_IDS
    },
}
EXPECTED_INLINE_TOKENS = {
    record_id: ("6432", "5032")
    for record_id in SLICE_RECORD_IDS
}
EXPECTED_OWNERS = {
    **{
        record_id: ("prefill", "segment", "segment")
        for record_id in FAILED_RECORD_IDS
    },
    2149: ("prefill", "prefill"),
    2150: ("prefill", "prefill"),
    2151: ("prefill", "prefill"),
    2152: ("prefill", "hidden_prefill"),
}
TERMINOLOGY_SCOPE = {
    "fief": ("지행", "reviewed_not_present_in_assigned_slice"),
    "loyalty": ("충성", "reviewed_not_present_in_assigned_slice"),
    "retainer_band": (
        "가신단",
        "reviewed_not_present_in_assigned_slice",
    ),
    "reinforcements": ("원군", "required"),
    "failed_defense": ("지켜 내", "required"),
    "failed_assault": ("함락시키", "required"),
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "1874490424C9CF544562E8A4843A53ED87D409CFA72527ED69E9336C9B7F47A9"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "489A8E05640130C06638481644446007E7F4F77E67BEF08DD17B1A2A78FC7512"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "2D0A71BC4B44E2FA7B194CFEA5E2E06F883C389DE2FC62C174BE1BCAF3045102"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "4A7A118D14731EBE40E47B6C687F6C956B4D02D371DC2969496AB8E1B4DD8673"
)
EXPECTED_HIDDEN_COORDINATE_SHA256 = (
    "415D909566D7685F6CABF099570F1BCA2BD4FCF2060A47A7B27D40824DB9EBC7"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "F8095AB57CE69C56CDC0CE37E65BCC027ABDA5675469B4C33F507CCD508DDD49"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "C1A642C92585D355C862013E6E4AB85AC670A3E013EB9B3591AE9243D512EDC5"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "496E8CFF444D50B55662B495B59A7228F58C0B186BA120E7D8E44364AFE3D4AC"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "B1242D72D31FD697B6E5CC308EB4039FF29794E76AAA6C9B654235B8B90DC913"
)
EXPECTED_BOUNDARY_SHA256 = (
    "DF23E7F21CD97FE3A151C2072F5D541CC53C0103A79FD6CAB7C4FC4A826B0A3C"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "FE0777E6DC7841444E4C7FCE7A66D2F08965F3DE48F04CDBCC53911CDC60C964"
)
EXPECTED_BASE_RECORD_SHA256 = (
    "D91E13274E11E8FE3B656DB61ACE1CB499A79A0BEA7F756D51BA021DCAA83DBF"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "C6A288D868DC058A36BBE0656A944B7B52AD865BAAC6F1920D26F170A4927A24"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "6395530E9A677FE82F2AEC5ACA8F1A08F5E0BB904AA8A906A95A64E3276B92D2"
)
EXPECTED_HIDDEN_CONTEXT_SHA256 = (
    "CBB35AC368592281E89479FE1A78A03E12C6108011AC49EA4D3EC9FA6D881800"
)
EXPECTED_SIBLING_CONTEXT_SHA256 = (
    "21F2BD0E54A1059A98165126E260EF67A0F085EAC3F19C26E63DCDC19E54982C"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "C8332F3FE24B30E436D06FC9C07BAB2036ECD2856D8C908B33B017CB08A53F72"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "D836A96534AC94BF3D4F1428C6C84416CDB9CF60CA280DF279198706738152D2"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3896D971D61A7D35950F86250D681ABF27C5163188DD8DA5A8564A815B6FE15F"
)
EXPECTED_CANDIDATE_SHA256 = (
    "6D23AA1B33FA572E0ACBCED53B3D96A8280107AAE99B153880F0DA0BA739585F"
)
EXPECTED_CHANGED_LITERAL_COUNT = 20

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; twenty-seven exact-reuse "
    "prefill rows in the assigned sixty-seven-visible queue slice, one "
    "same-record hidden companion just beyond the slice and forty "
    "residual fragments are pinned; completed Base Korean and completed "
    "PK sibling records 2127-2128 pin the failed-defense and failed-assault "
    "semantics while Base runtime state is not inherited; all twenty-four "
    "complete records are reconstructed without current-text fallback; "
    "dynamic castle and reinforcing-force tokens, shifted PK direct-call "
    "operand 772 versus Base 760, common terminal call 142 and their exact "
    "runtime order are guarded; fief, loyalty and retainer-band terms were "
    "reviewed and are not present in this slice, while historically "
    "appropriate reinforcement wording is required; all twenty runtime "
    "speaker variants, outer whitespace, protected signatures, line "
    "counts, reverse overlay, two-run reproduction, tamper rejection and "
    "read-only inputs are guarded; every residual PK fragment remains "
    "runtime pending"
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
        len(queue_rows) != 120
        or len(visible) != 200
        or visible[0] != "6:2129:0"
        or visible[-1] != "6:2248:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B027 queue universe drifted"
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
        or queue_slice[0] != "6:2129:0"
        or queue_slice[-1] != "6:2152:0"
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
    if len(prefilled) != 27:
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
    if residual != TARGET_COORDINATES or len(residual) != 40:
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
    context_ids = tuple(range(2127, 2154))
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
    dynamic_records = tuple(
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
            "dynamic record",
            dynamic_records,
            EXPECTED_DYNAMIC_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)

    for record_id, source, current in gaps:
        if (
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current != source
        ):
            raise RuntimeError(
                f"segment {SEGMENT} runtime gap drifted: "
                f"{record_id}"
            )
    for record_id, source_gaps, calls, tokens in dynamic_records:
        if (
            source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
            or calls != EXPECTED_PK_DIRECT_CALLS[record_id]
            or tokens != EXPECTED_INLINE_TOKENS[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} dynamic controls drifted: "
                f"{record_id}"
            )
    if tuple(
        record_id
        for record_id in SLICE_RECORD_IDS
        if direct_calls(
            gap_bytes(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
    ) != SLICE_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} direct-call universe drifted"
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
    pk_rows = decision_map("pk_msggame", True)
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
        pk_gaps = tuple(
            value.hex().upper() for value in gap_bytes(pk_record)
        )
        base_gaps = tuple(
            value.hex().upper() for value in gap_bytes(base_record)
        )
        pk_calls = direct_calls(gap_bytes(pk_record))
        base_calls = direct_calls(gap_bytes(base_record))
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
        expected_raw_equal = pk_record_id in SUCCESS_RECORD_IDS
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
                pk_calls,
                base_calls,
            )
        )
        if (
            not source_equal
            or raw_equal != expected_raw_equal
            or pk_gaps != EXPECTED_GAPS_BY_RECORD[pk_record_id]
            or base_gaps
            != EXPECTED_BASE_GAPS_BY_RECORD[pk_record_id]
            or pk_calls != EXPECTED_PK_DIRECT_CALLS[pk_record_id]
            or base_calls
            != EXPECTED_BASE_DIRECT_CALLS[pk_record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base mapping drifted: "
                f"{pk_record_id}"
            )
        if (
            pk_record_id in FAILED_RECORD_IDS
            and (
                masked_gap_tuple(pk_record)
                != EXPECTED_FAILED_MASKED_GAPS
                or masked_gap_tuple(base_record)
                != EXPECTED_FAILED_MASKED_GAPS
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base call template drifted: "
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
        or len(prefill_coordinates) != 28
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
        len(prefill_evidence) != 27
        or any(
            semantic != "approved" or runtime != "pending"
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
                or base_row.get("runtime_review") != "verified"
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
        owner_map[record_id] = tuple(owners)
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
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
            )
        )
        if owner_map[record_id] != EXPECTED_OWNERS[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} assembly owner drifted: "
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

    sibling_evidence: list[tuple[Any, ...]] = []
    for record_id in PK_SIBLING_RECORD_IDS:
        translations = tuple(
            str(
                pk_rows[f"6:{record_id}:{literal_id}"][
                    "translation"
                ]
            )
            for literal_id in range(3)
        )
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        sibling_evidence.append(
            (
                record_id,
                sha256_bytes(source_record.data),
                literal_texts(
                    records_by_label["jp"],
                    (BLOCK_ID, record_id),
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(source_record)
                ),
                direct_calls(gap_bytes(source_record)),
                translations,
                tuple(
                    pk_rows[f"6:{record_id}:{literal_id}"].get(
                        "runtime_review"
                    )
                    for literal_id in range(3)
                ),
            )
        )
        if (
            tuple(
                value.hex().upper()
                for value in gap_bytes(source_record)
            )
            != EXPECTED_FAILED_GAPS
            or direct_calls(gap_bytes(source_record))
            != (772, 142)
            or translations
            != ("만은 지켜 내", "지만\n", "의 원군에는 감사")
            or assembly_map[2129] != translations
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK sibling donor drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "sibling context",
        tuple(sibling_evidence),
        EXPECTED_SIBLING_CONTEXT_SHA256,
    )

    if (
        any(
            assembly_map[record_id]
            != ("만은 지켜 내", "지만\n", "의 원군에는 감사")
            for record_id in DEFENSE_RECORD_IDS
        )
        or any(
            assembly_map[record_id]
            != (
                "만은 함락시키",
                "지만\n",
                "의 원군에는 감사",
            )
            for record_id in ASSAULT_RECORD_IDS
        )
        or any(
            "원군" not in text
            for record_id in SLICE_RECORD_IDS
            for text in assembly_map[record_id]
            if "감사" in text or "있었기 때문" in text
        )
        or any(
            forbidden in text
            for record_id in SLICE_RECORD_IDS
            for text in assembly_map[record_id]
            for forbidden in ("지원군", "방어군")
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reinforcement terminology drifted"
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
        or len(TARGET_COORDINATES) != 40
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
            changed += 1
            changed_coordinates.append(coordinate)
    expected_changed = tuple(
        f"6:{record_id}:1" for record_id in TARGET_RECORD_IDS
    )
    if (
        changed != EXPECTED_CHANGED_LITERAL_COUNT
        or tuple(changed_coordinates) != expected_changed
        or any(
            TRANSLATIONS[f"6:{record_id}:1"] != "지만\n"
            or TRANSLATIONS[f"6:{record_id}:2"]
            != "의 원군에는 감사"
            for record_id in TARGET_RECORD_IDS
        )
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


def record_variant(record_id: int) -> str:
    if record_id in DEFENSE_RECORD_IDS:
        return "failed_defense_reinforcement_thanks"
    return "failed_assault_reinforcement_thanks"


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
    tokens = inline_tokens(gap_bytes(source_record))
    if (
        source_gap_hex != EXPECTED_FAILED_GAPS
        or current_gap_hex != source_gap_hex
        or base_gap_hex != EXPECTED_BASE_FAILED_GAPS
        or source_calls != (772, 142)
        or current_calls != source_calls
        or base_calls != (760, 142)
        or tokens != ("6432", "5032")
        or masked_gap_tuple(source_record)
        != masked_gap_tuple(base_record)
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
        "inline_runtime_tokens": tokens,
        "runtime_order": (
            "failed_castle_026432",
            "failure_verb_stem",
            "direct_call_772",
            "concessive_suffix",
            "reinforcing_force_025032",
            "reinforcement_thanks_stem",
            "direct_call_142",
        ),
        "base_runtime_order": (
            "failed_castle_026432",
            "failure_verb_stem",
            "direct_call_760",
            "concessive_suffix",
            "reinforcing_force_025032",
            "reinforcement_thanks_stem",
            "direct_call_142",
        ),
        "record_variant": record_variant(record_id),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_prefill_companion_reviewed": True,
        "hidden_runtime_grammar_companions_reviewed": True,
        "pk_sibling_runtime_template_reviewed": True,
        "speaker_register_routed_by_direct_calls": True,
        "speaker_register_reviewed": True,
        "fief_loyalty_retainer_band_scope_reviewed": True,
        "reinforcement_terminology_reviewed": True,
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
            for other_id in range(3)
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
            "fief_term_review": "reviewed_not_present",
            "loyalty_term_review": "reviewed_not_present",
            "retainer_band_term_review": "reviewed_not_present",
            "reinforcement_term_review": True,
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
            "base_record_opcode_variant": True,
            "base_runtime_state_inherited": False,
            "pk_sibling_runtime_template_coordinates": (
                "6:2127",
                "6:2128",
            ),
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "protected_signature_review": True,
            "same_record_prefill_companion_coordinates":
            companion_coordinates,
            "record_variant": record_variant(record_id),
            "speaker_register_variant": (
                f"runtime_routed_variant_{record_id - 2128:02d}"
            ),
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
        len(rows) != 40
        or len(validated) != 40
        or counts != Counter({"runtime_fragment_pending": 40})
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
                "segment": "pk_msggame_B027_S1095",
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
                "exact_reuse_prefill_count": 27,
                "residual_count": 40,
                "hidden_companion_count":
                len(HIDDEN_COORDINATES),
                "reviewed_complete_record_count":
                len(SLICE_RECORD_IDS),
                "failed_defense_record_count":
                len(DEFENSE_RECORD_IDS),
                "failed_assault_record_count":
                len(ASSAULT_RECORD_IDS),
                "direct_call_record_count":
                len(SLICE_RECORD_IDS),
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
                "base_source_records_guarded": True,
                "base_semantics_pinned": True,
                "base_shifted_direct_calls_guarded": True,
                "base_runtime_state_inherited": False,
                "pk_sibling_runtime_templates_guarded": True,
                "prefill_companions_guarded": True,
                "hidden_companion_guarded": True,
                "complete_record_assembly_guarded": True,
                "fief_loyalty_retainer_band_scope_reviewed": True,
                "reinforcement_terminology_reviewed": True,
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
