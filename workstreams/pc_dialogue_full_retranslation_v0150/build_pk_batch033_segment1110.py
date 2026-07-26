#!/usr/bin/env python3
"""Build source-redacted PK B033 segment 1110 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch032_segment1107.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B033_S1110.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B031_S1104.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B031_S1105.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B031_S1106.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B032_S1107.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B032_S1108.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B032_S1109.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B033_S1111.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B033_S1112.private.v1.jsonl",
)

SEGMENT = 1110
QUEUE_BATCH_ID = "pk_msggame-B033"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:3062:1",
    "6:3065:1",
    "6:3070:1",
)
TRANSLATIONS = {
    "6:3062:1": "와(과)의 동맹은 앞으로",
    "6:3065:1": " 측과의 혼인 동맹도 ",
    "6:3070:1": "와(과)는\n",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (3062, 3065, 3070)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
SLICE_RECORD_IDS = tuple(range(3054, 3078))
DIVERGENT_BASE_RECORD_IDS = tuple(range(3054, 3063))
EXACT_BASE_RECORD_IDS = tuple(range(3063, 3078))
BOUNDARY_RECORD_IDS = (3053, 3078)
BASE_RECORD_MAPPING = {
    record_id: record_id - 6 for record_id in SLICE_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{int(coordinate.split(':')[1]) - 6}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
CONTEXT_ADAPTED_COORDINATES = {"6:3065:1"}
EXPECTED_TARGET_GAPS = {
    3062: (
        "",
        "025032",
        "0232",
        "014374020000",
        "014342010000050505",
    ),
    3065: ("", "025032", "0232", "050505"),
    3070: (
        "",
        "025032",
        "0232",
        "014308000000",
        "050505",
    ),
}
EXPECTED_PK_CALLS = {
    **{
        record_id: (34, 514)
        for record_id in range(3054, 3062)
    },
    3062: (628, 322),
    **{
        record_id: ()
        for record_id in range(3063, 3070)
    },
    3070: (8,),
    **{
        record_id: ()
        for record_id in range(3071, 3075)
    },
    **{
        record_id: (34,)
        for record_id in range(3075, 3078)
    },
}
EXPECTED_BASE_CALLS = {
    **{
        record_id: (34, 508)
        for record_id in range(3054, 3062)
    },
    3062: (616, 322),
    **{
        record_id: EXPECTED_PK_CALLS[record_id]
        for record_id in range(3063, 3078)
    },
}
EXPECTED_INLINE_CONTROLS = {
    record_id: ("025032", "0232")
    for record_id in SLICE_RECORD_IDS
}
EXPECTED_TARGET_ASSEMBLIES = {
    3062: (
        "혼인 관계를 더는 이어 갈 수 없게 되어\n",
        "와(과)의 동맹은 앞으로",
        "개월만 남게 되",
        "\n각별히 유의하여",
    ),
    3065: (
        "인척 관계가 끝났으므로,",
        " 측과의 혼인 동맹도 ",
        "개월 후에는\n"
        "효력을 잃사오니, 부디 유념하시옵소서",
    ),
    3070: (
        "관계가 끊어졌으므로,",
        "와(과)는\n",
        "개월 뒤면 동맹 관계도 끝나옵니다.\n"
        "양가의 관계를 어찌할지는",
        "님의 뜻에 달린 듯하옵니다",
    ),
}
TERMINOLOGY_SCOPE = {
    "marriage_alliance": (
        "혼인 관계",
        "인척 관계",
        "혼인 동맹",
        "동맹 관계",
    ),
    "houses": ("양가", "우리 가문"),
    "court_register": (
        "끝나옵니다",
        "잃사오니",
        "유념하시옵소서",
        "듯하옵니다",
    ),
    "runtime_values": (
        "세력명 5032",
        "개월 수 0232",
        "인물 호출 8",
    ),
}
REGISTER_POLICY = {
    3062: "advisor_warning_with_runtime_voice_endings",
    3065: "courtly_marriage_alliance_warning",
    3070: "courtly_two_house_relationship_advice",
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
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "5BBA9A2DD65CA4E511AE78A2884D471863A0D7DAD315DC61A935380E71B5F74A"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "0B476872A395999E1AEDFFA92F1E640E8653BE31C3E7342786F7C575601C5D40"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "F54944DB24A45E0BF5B0345B764A19348A5058192BC10720595B9D0084FDDD63"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "034AAAE14B2CF6BE5D069DDD634259989E6BAB3EBCD46D774A02A1C46B3A5716"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "DE93AF758B49B8E2CAF5C08638489D5C39076F9215E7BB4487392BE6CD847B61"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "718305A18FDB6D3A7CBE155998AEA25AC19C71C21DBFD1FED9CD9CE96FAC1F7C"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "5AA285BCB7889FB3F643EE432C54E07E52FEE3C20BBD63D4699A998704389FB9"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "996E7817BF73242A313D6F96FF771A7793D162BBEAEBEC3F4C9AD8021607226F"
)
EXPECTED_BOUNDARY_SHA256 = (
    "D90CDB4A7443068296BAEBACACB6FF52EA6F41ADDE61B1F1E716AB8D9AF8EF04"
)
EXPECTED_RUNTIME_RECORD_SHA256 = (
    "D8DD6193E2290443317A33F2BC29568915BDDAA3CA9E456B6EE37B13A99DEB5E"
)
EXPECTED_BASE_RECORD_SHA256 = (
    "31EA02EA3A9CA0B1A00E93C4AC1EC3CCC06F4865480CEA6AC2B5E983F4B33253"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "C0F4D653660F73A3EDB50FB30F0C123CDC5D1D434EF0DFC4ED5EBC2001DC882A"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "5B7B5D3189EB063D794B33E93CBB3F6F4E4A054EB08D0352978AE599B9CD66EB"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "007CD77747782B094B08A29B26A3CCBEAF9B78A91A27126B5FD030B204D90DDA"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "085ACD9B31E3A7E98E32542FCFB730936CE743677756F1841544309F839DAFB5"
)
EXPECTED_REGISTER_POLICY_SHA256 = (
    "65CA9B68E53F7D48BCCF4C83133EF04460819A9ABC5E1C7F02B5A7E2005AD91F"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "CDCEE78EB433561A778316406D4195C63CF920A317C33123741F135142B71483"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F39D91D2ECCEEDAECB59917569C701454F1D47C6469899896F5C3C732782616A"
)
EXPECTED_CHANGED_LITERAL_COUNT = 2

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; sixty-four Base exact-reuse "
    "prefill rows and three residual rows cover all twenty-four complete "
    "records and sixty-seven literals in the assigned queue slice without "
    "current-text fallback; corresponding Base source literals are exact "
    "semantic donors, but the first nine PK records deliberately retain "
    "PK-specific runtime call operands instead of inheriting Base runtime "
    "state; clan token 025032, month-value slot 0232, PK voice calls 628 "
    "and 322 in record 3062 and person call 8 in record 3070 are pinned "
    "at their literal boundaries; protected spaces and one-line layout in "
    "record 3065 are retained through a natural clan-side construction; "
    "marriage-alliance, two-house and courtly advisory terminology and "
    "register are reviewed; source/current gaps, Base runtime differences, "
    "protected signatures, line counts, reverse overlay, two-run "
    "reproduction, tamper rejection, outside-scope records and read-only "
    "inputs are guarded; all three PK residual fragments remain runtime "
    "pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1110_common",
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
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
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
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
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
        int.from_bytes(value[2:6], "little")
        for value in gaps
        if value.startswith(b"\x01\x43") and len(value) >= 6
    )


def inline_controls(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        value.hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )


def call_gap_compatible(
    pk_gap: bytes,
    base_gap: bytes,
) -> bool:
    if pk_gap == base_gap:
        return True
    return (
        pk_gap.startswith(b"\x01\x43")
        and base_gap.startswith(b"\x01\x43")
        and len(pk_gap) >= 6
        and len(base_gap) >= 6
        and pk_gap[:2] == base_gap[:2]
        and pk_gap[6:] == base_gap[6:]
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
        len(queue_rows) != 113
        or len(visible) != 199
        or visible[0] != "6:3054:0"
        or visible[-1] != "6:3166:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B033 queue universe drifted"
        )
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3054:0"
        or queue_slice[-1] != "6:3077:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue slice boundary drifted"
        )
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if len(prefilled) != 64:
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
    if residual != TARGET_COORDINATES or len(residual) != 3:
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
    base_source_records: dict[tuple[int, int], Any],
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
    context_ids = tuple(range(3053, 3079))
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
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    base_source_records[
                        (
                            BLOCK_ID,
                            BASE_RECORD_MAPPING[record_id],
                        )
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
            direct_calls(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            direct_calls(
                gap_bytes(
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            direct_calls(
                gap_bytes(
                    base_source_records[
                        (
                            BLOCK_ID,
                            BASE_RECORD_MAPPING[record_id],
                        )
                    ]
                )
            ),
            inline_controls(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            inline_controls(
                gap_bytes(
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            inline_controls(
                gap_bytes(
                    base_source_records[
                        (
                            BLOCK_ID,
                            BASE_RECORD_MAPPING[record_id],
                        )
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
            "runtime record",
            runtime_records,
            EXPECTED_RUNTIME_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)

    if any(source != current for _, source, current, _ in gaps):
        raise RuntimeError(
            f"segment {SEGMENT} source/current gap drifted"
        )
    for (
        record_id,
        source_calls,
        current_calls,
        base_calls,
        source_inline,
        current_inline,
        base_inline,
    ) in runtime_records:
        if (
            source_calls != EXPECTED_PK_CALLS[record_id]
            or current_calls != source_calls
            or base_calls != EXPECTED_BASE_CALLS[record_id]
            or source_inline
            != EXPECTED_INLINE_CONTROLS[record_id]
            or current_inline != source_inline
            or base_inline != source_inline
        ):
            raise RuntimeError(
                f"segment {SEGMENT} runtime record drifted: "
                f"{record_id}"
            )
    for record_id in TARGET_RECORD_IDS:
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        if tuple(
            value.hex().upper()
            for value in gap_bytes(source_record)
        ) != EXPECTED_TARGET_GAPS[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} target gap drifted: "
                f"{record_id}"
            )


def assert_base_prefill_and_assembly(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    base_source_records: dict[tuple[int, int], Any],
) -> dict[int, tuple[str, ...]]:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame")
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
        pk_gaps = gap_bytes(pk_record)
        base_gaps = gap_bytes(base_record)
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
        data_equal = pk_record.data == base_record.data
        compatible = (
            len(pk_gaps) == len(base_gaps)
            and all(
                call_gap_compatible(pk_gap, base_gap)
                for pk_gap, base_gap in zip(pk_gaps, base_gaps)
            )
        )
        base_record_evidence.append(
            (
                pk_record_id,
                base_record_id,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                source_equal,
                data_equal,
                compatible,
                tuple(
                    value.hex().upper() for value in pk_gaps
                ),
                tuple(
                    value.hex().upper() for value in base_gaps
                ),
                direct_calls(pk_gaps),
                direct_calls(base_gaps),
                inline_controls(pk_gaps),
                inline_controls(base_gaps),
            )
        )
        if (
            not source_equal
            or not compatible
            or direct_calls(pk_gaps)
            != EXPECTED_PK_CALLS[pk_record_id]
            or direct_calls(base_gaps)
            != EXPECTED_BASE_CALLS[pk_record_id]
            or inline_controls(pk_gaps)
            != EXPECTED_INLINE_CONTROLS[pk_record_id]
            or inline_controls(base_gaps)
            != EXPECTED_INLINE_CONTROLS[pk_record_id]
            or (
                pk_record_id in EXACT_BASE_RECORD_IDS
                and not data_equal
            )
            or (
                pk_record_id in DIVERGENT_BASE_RECORD_IDS
                and data_equal
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base record contract drifted: "
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
        len(full_coordinates) != 67
        or len(prefill_coordinates) != 64
        or any(
            coordinate in prefill_coordinates
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} full coordinate drifted"
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
    if any(
        semantic != "approved" or runtime != "pending"
        for _, _, semantic, runtime, _, _ in prefill_evidence
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
                owner = "prefill"
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} current fallback forbidden: "
                    f"{coordinate}"
                )
            base_row = base_rows[base_coordinate]
            base_translation = str(
                base_row.get("translation")
            )
            expected_translation = (
                TRANSLATIONS["6:3065:1"]
                if coordinate == "6:3065:1"
                else base_translation
            )
            if (
                base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
                or translation != expected_translation
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
                    base_translation,
                    coordinate in CONTEXT_ADAPTED_COORDINATES,
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
                inline_controls(gap_bytes(source_record)),
            )
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

    if (
        any(
            base_rows[BASE_CONTEXT_REFERENCES[coordinate]].get(
                "runtime_review"
            )
            != "verified"
            for coordinate in TARGET_COORDINATES
        )
        or any(
            assembly_map[record_id] != expected
            for record_id, expected
            in EXPECTED_TARGET_ASSEMBLIES.items()
        )
        or "혼인을 맺었던" not in assembly_map[3054][0]
        or "혼인 동맹" not in assembly_map[3063][0]
        or "인척 관계" not in assembly_map[3065][0]
        or "유념하시옵소서" not in assembly_map[3065][2]
        or "동맹 관계" not in assembly_map[3070][2]
        or "양가" not in assembly_map[3070][2]
        or "우리 가문" not in assembly_map[3076][0]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology or assembly drifted"
        )
    return assembly_map


def runtime_order(record_id: int) -> tuple[str, ...]:
    if record_id == 3062:
        return (
            "marriage_relation_expiry_premise",
            "dynamic_clan_name_5032",
            "alliance_remaining_intro",
            "runtime_month_value_0232",
            "remaining_month_suffix",
            "pk_voice_call_628",
            "warning_fragment",
            "pk_voice_call_322",
        )
    if record_id == 3065:
        return (
            "kinship_expiry_premise",
            "dynamic_clan_name_5032",
            "protected_clan_side_marriage_alliance",
            "runtime_month_value_0232",
            "courtly_expiry_warning",
        )
    return (
        "relationship_expiry_premise",
        "dynamic_clan_name_5032",
        "alliance_subject_fragment",
        "runtime_month_value_0232",
        "two_house_advice_fragment",
        "direct_call_8_person_name",
        "courtly_person_name_suffix",
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
        "register policy",
        REGISTER_POLICY,
        EXPECTED_REGISTER_POLICY_SHA256,
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
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
        or TRANSLATIONS["6:3062:1"]
        != "와(과)의 동맹은 앞으로"
        or TRANSLATIONS["6:3065:1"]
        != " 측과의 혼인 동맹도 "
        or TRANSLATIONS["6:3070:1"] != "와(과)는\n"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    changed_coordinates: list[str] = []
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
        if translation != current_text:
            changed_coordinates.append(coordinate)
    if tuple(changed_coordinates) != (
        "6:3062:1",
        "6:3070:1",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} changed coordinate drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


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
    source_inline = inline_controls(gap_bytes(source_record))
    current_inline = inline_controls(gap_bytes(current_record))
    base_inline = inline_controls(gap_bytes(base_record))
    if (
        source_gap_hex != EXPECTED_TARGET_GAPS[record_id]
        or current_gap_hex != source_gap_hex
        or source_calls != EXPECTED_PK_CALLS[record_id]
        or current_calls != source_calls
        or base_calls != EXPECTED_BASE_CALLS[record_id]
        or source_inline
        != EXPECTED_INLINE_CONTROLS[record_id]
        or current_inline != source_inline
        or base_inline != source_inline
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
        "base_direct_call_operands_equal":
        base_calls == source_calls,
        "source_inline_runtime_controls": source_inline,
        "current_inline_runtime_controls": current_inline,
        "base_inline_runtime_controls": base_inline,
        "runtime_order": runtime_order(record_id),
        "record_variant":
        "marriage_alliance_expiry_notification",
        "speaker_register_variant":
        REGISTER_POLICY[record_id],
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_companions_reviewed": True,
        "protected_token_spacing_reviewed":
        record_id == 3065,
        "pk_base_runtime_difference_reviewed":
        source_calls != base_calls,
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
    base_source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    assert_context_contracts(
        records_by_label,
        base_source_records,
    )
    assert_base_prefill_and_assembly(
        records_by_label,
        base_source_records,
    )
    assert_semantics(records_by_label)
    if DISCOVERED_PINS:
        return prepared, [], b"", "", -1, optional_present

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
        record_coordinates = tuple(
            f"6:{record_id}:{companion_id}"
            for companion_id in range(
                len(
                    literal_texts(
                        records_by_label["current"],
                        (block_id, record_id),
                    )
                )
            )
        )
        companion_coordinates = tuple(
            value
            for value in record_coordinates
            if value != coordinate
        )
        base_calls_equal = (
            EXPECTED_PK_CALLS[record_id]
            == EXPECTED_BASE_CALLS[record_id]
        )
        row = {
            "schema":
            "nobu16.kr.pc-dialogue-full-retranslation.v1."
            "private-decision",
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "runtime_review": "pending",
            "layout_review": "runtime_pending",
            "scope_classification": "runtime_fragment_pending",
            "basis": BASIS,
            "source_record_raw_sha256":
            prepared.visible_targets[
                ("pk_msggame", block_id, record_id, literal_id)
            ]["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            sha256_bytes(current_text.encode("utf-16le")),
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "protected_signature_review": True,
            "historical_term_review": True,
            "speaker_register_review": True,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_context_reference_coordinate":
            BASE_CONTEXT_REFERENCES[coordinate],
            "base_source_literal_exact": True,
            "base_record_opcode_family_exact": True,
            "base_record_call_operands_exact":
            base_calls_equal,
            "base_semantic_translation_reused": True,
            "base_translation_contextually_adapted":
            coordinate in CONTEXT_ADAPTED_COORDINATES,
            "base_exact_reuse_prefill_excluded": True,
            "base_runtime_state_inherited": False,
            "same_record_companion_coordinates":
            companion_coordinates,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "record_variant":
            "marriage_alliance_expiry_notification",
            "speaker_register_variant":
            REGISTER_POLICY[record_id],
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
        len(rows) != 3
        or len(validated) != 3
        or counts != Counter(
            {"runtime_fragment_pending": 3}
        )
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
                "segment": "pk_msggame_B033_S1110",
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
                "exact_reuse_prefill_count": 64,
                "residual_count": 3,
                "reviewed_complete_record_count":
                len(SLICE_RECORD_IDS),
                "reviewed_complete_literal_count": 67,
                "base_exact_record_count":
                len(EXACT_BASE_RECORD_IDS),
                "base_runtime_variant_record_count":
                len(DIVERGENT_BASE_RECORD_IDS),
                "context_adapted_coordinate_count":
                len(CONTEXT_ADAPTED_COORDINATES),
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
                "base_source_literals_exact": True,
                "base_runtime_differences_guarded": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "complete_record_assembly_guarded": True,
                "historical_terms_reviewed": True,
                "speaker_registers_reviewed": True,
                "protected_token_spacing_reviewed": True,
                "runtime_controls_guarded": True,
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
