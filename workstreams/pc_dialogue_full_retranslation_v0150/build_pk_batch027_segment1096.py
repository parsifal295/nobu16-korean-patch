#!/usr/bin/env python3
"""Build source-redacted PK B027 segment 1096 residual decision."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch014_segment1063.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B027_S1096.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B027_S1095.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B027_S1097.private.v1.jsonl",
)

SEGMENT = 1096
QUEUE_BATCH_ID = "pk_msggame-B027"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("6:2180:0",)
TRANSLATIONS = {
    "6:2180:0": "이 세력과 외교를 진행합니다",
}
DYNAMIC_COORDINATES: set[str] = set()
STATIC_COORDINATES = set(TARGET_COORDINATES)
TARGET_RECORD_IDS = (2180,)
DYNAMIC_RECORD_IDS: tuple[int, ...] = ()
BOUNDARY_RECORD_IDS = (2179, 2181)
BASE_RECORD_MAPPING = {
    2179: 2173,
    2180: 2174,
    2181: 2175,
}
BASE_CONTEXT_REFERENCES = {"6:2180:0": "6:2174:0"}
PREFILL_COMPANION_COORDINATES = (
    "6:2179:0",
    "6:2181:0",
)
EXPECTED_GAPS_BY_RECORD = {
    2179: ("", "050505"),
    2180: ("", "050505"),
    2181: ("", "050505"),
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
    "293674ACAB71B2F17D754CF2B4798C49EAFAACA5A172DE6BE17DFB7B2DEFB5CA"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "593BAF086366675BC4A4622470A4EEF3C5BCBBFEBA4F4F5FDBD0208D788A069D"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "71386FBF810FBA62C212DFFFAA95594E183629C35AC58A9A8E0A3B1267F20AAF"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "2D6912E3C1860058E37CB4F5423430055C6BBE9F6E1032912D774F97CF8D5C59"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "D50D85320A7D41EDB6A859A96A169DD7A9DEB14D122328A157102A66A5F5B7A7"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "ABFB3AC25D32422DE542252A8EC5293AF43C4D5E0C0719E1777F9FF73840C623"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "5DA07674E4DC165DFA91429F34B747508CF14D5F2E56EF75825E0E98E5D26A28"
)
EXPECTED_BOUNDARY_SHA256 = (
    "44CCBDA01D3A126AFDC4908BF3F1B138048C5FE179EECFDB8EA01C54778BC74D"
)
EXPECTED_RUNTIME_ABSENCE_SHA256 = (
    "3D215D569DDCA3862AD20919B427C4C6106D654DED52E02FA34C017E677EEC25"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "86C233D77F0A3A6B63152F47AB9E8FED5966ACAF47FB2C9D673D1BEC25E4C02C"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "1702EE96B3A690C5E730C3C0C5571E67A3DACCA4C80D7AE37976716A156497FA"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "FD9300E68D9C87C22F0D326B26CF8C63DBDA657CDD707FE2EB1DDAE77457BAAB"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "AAFB62ECBEF0A00A32A0682A275BBFF7460EA6F746D2BBEC50390A5A572B1E2E"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "47A25950013DB339D4A8E5853F31A86D67481BC2CF8FF7D1B14F46134F349510"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "2822688D0BB54C8FAFDE2D6584566729D9A619227576B17C1E324079E76D9497"
)
EXPECTED_CANDIDATE_SHA256 = (
    "3240E36374B81A3E3D3D30B05B475ABAEF58DFA7EEDA8836875A66F1D74E453C"
)
EXPECTED_CHANGED_LITERAL_COUNT = 1

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; the nearest completed Base "
    "full-record donor and its adjacent diplomacy UI sequence pin the "
    "formal declarative wording and terminology; the target is a "
    "single-literal static record with no inline token, direct call or "
    "same-record companion, while both adjacent exact-reuse prefill "
    "companions are guarded; all available predecessors are validated and "
    "excluded; full-record assembly, adjacent source/current/Base records, "
    "protected signature, line count, bytecode gaps, reverse overlay, "
    "two-run reproduction, tamper rejection and read-only inputs are "
    "guarded; Base runtime state is not inherited and PK runtime status is "
    "independently classified as not required"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1096_common",
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
        len(queue_rows) != 120
        or len(visible) != 200
        or visible[0] != "6:2129:0"
        or visible[-1] != "6:2248:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B027 queue universe drifted"
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
    if len(prefilled) != 66:
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice count drifted"
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


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    direct_calls = tuple(
        int.from_bytes(value[2:6], "little")
        for value in gaps
        if value.startswith(b"\x01\x43")
    )
    inline_tokens = tuple(
        value.hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )
    return direct_calls, inline_tokens


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
            label,
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records[(BLOCK_ID, record_id)]
                )
            ),
        )
        for label, records in records_by_label.items()
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
    runtime_absence = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ]
            ),
        )
        for label in ("jp", "current")
        for record_id in (
            *BOUNDARY_RECORD_IDS,
            *TARGET_RECORD_IDS,
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
            "runtime absence",
            runtime_absence,
            EXPECTED_RUNTIME_ABSENCE_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        any(
            gap != EXPECTED_GAPS_BY_RECORD[record_id]
            for _, record_id, gap in gaps
        )
        or any(
            controls != ((), ())
            for _, _, controls in runtime_absence
        )
        or any(
            len(
                literal_texts(
                    records_by_label[label],
                    (BLOCK_ID, 2180),
                )
            )
            != 1
            for label in records_by_label
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} static record layout drifted"
        )


def assert_base_companion_and_assembly(
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
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    sequence_evidence: list[tuple[Any, ...]] = []
    for pk_record_id, base_record_id in (
        BASE_RECORD_MAPPING.items()
    ):
        pk_source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, pk_record_id),
        )
        base_source_literals = literal_texts(
            base_source_records,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current_records,
            (BLOCK_ID, base_record_id),
        )
        base_row = base_rows[
            f"6:{base_record_id}:0"
        ]
        sequence_evidence.append(
            (
                pk_record_id,
                base_record_id,
                pk_source_literals,
                base_source_literals,
                base_current_literals,
                base_row.get("translation"),
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(
                        records_by_label["jp"][
                            (BLOCK_ID, pk_record_id)
                        ]
                    )
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(
                        base_source_records[
                            (BLOCK_ID, base_record_id)
                        ]
                    )
                ),
                runtime_controls(
                    base_source_records[
                        (BLOCK_ID, base_record_id)
                    ]
                ),
                runtime_controls(
                    base_current_records[
                        (BLOCK_ID, base_record_id)
                    ]
                ),
            )
        )
        if (
            pk_source_literals != base_source_literals
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "not_required"
            or sequence_evidence[-1][8]
            != sequence_evidence[-1][9]
            or sequence_evidence[-1][10] != ((), ())
            or sequence_evidence[-1][11] != ((), ())
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base sequence drifted: "
                f"{pk_record_id}"
            )
    guarded_digest(
        "Base context",
        tuple(sequence_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    target_base_row = base_rows[
        BASE_CONTEXT_REFERENCES[TARGET_COORDINATES[0]]
    ]
    if (
        target_base_row.get("translation")
        != TRANSLATIONS[TARGET_COORDINATES[0]]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base target donor drifted"
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
        or runtime != "not_required"
        for _, _, semantic, runtime, _, _, _ in companion_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} adjacent companion drifted"
        )

    current_literals = literal_texts(
        records_by_label["current"],
        (BLOCK_ID, 2180),
    )
    assembly_evidence = (
        ("record_id", 2180),
        ("owners", ("segment",)),
        ("source_literals", literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, 2180),
        )),
        ("current_literals", current_literals),
        ("assembled_literals", (
            TRANSLATIONS[TARGET_COORDINATES[0]],
        )),
        ("gaps", tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["jp"][(BLOCK_ID, 2180)]
            )
        )),
        ("runtime_controls", runtime_controls(
            records_by_label["jp"][(BLOCK_ID, 2180)]
        )),
        ("same_record_companion_count", 0),
        (
            "adjacent_prefill_companions",
            PREFILL_COMPANION_COORDINATES,
        ),
    )
    guarded_digest(
        "assembly policy",
        assembly_evidence,
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )
    if (
        assembly_evidence[1][1] != ("segment",)
        or assembly_evidence[4][1]
        != ("이 세력과 외교를 진행합니다",)
        or assembly_evidence[5][1] != ("", "050505")
        or assembly_evidence[6][1] != ((), ())
        or assembly_evidence[7][1] != 0
    ):
        raise RuntimeError(
            f"segment {SEGMENT} full-record assembly drifted"
        )


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
        ("diplomacy", "외교"),
        ("negotiation", "교섭"),
        ("action_register", "진행합니다"),
        ("ui_style", "formal_declarative"),
    )
    guarded_digest(
        "terminology policy",
        terminology_policy,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    runtime_category = (
        (
            "6:2180:0",
            "static_single_literal_diplomacy_ui",
            "retranslated",
            "not_required",
            "unchanged_from_current",
            False,
        ),
    )
    guarded_digest(
        "runtime category",
        runtime_category,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
    )
    coordinate = TARGET_COORDINATES[0]
    current_text = literal_texts(
        records_by_label["current"],
        (BLOCK_ID, 2180),
    )[0]
    translation = TRANSLATIONS[coordinate]
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or STATIC_COORDINATES != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES
        or DYNAMIC_RECORD_IDS
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or translation != "이 세력과 외교를 진행합니다"
        or translation.count("\n") != current_text.count("\n")
        or ENGINE.protected_signature(translation)
        != ENGINE.protected_signature(current_text)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    ENGINE.validate_translation_shape(
        current_text,
        translation,
        "unchanged_from_current",
        coordinate,
    )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    source_record = records_by_label["jp"][(BLOCK_ID, 2180)]
    current_record = records_by_label["current"][
        (BLOCK_ID, 2180)
    ]
    base_record = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )[(BLOCK_ID, 2174)]
    controls = (
        runtime_controls(source_record),
        runtime_controls(current_record),
        runtime_controls(base_record),
    )
    if controls != (((), ()), ((), ()), ((), ())):
        raise RuntimeError(
            f"segment {SEGMENT} static controls drifted"
        )
    return {
        "runtime_category":
        "static_single_literal_diplomacy_ui",
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
        "source_direct_call_operands": (),
        "current_direct_call_operands": (),
        "source_inline_token_hex": (),
        "current_inline_token_hex": (),
        "single_literal_full_record_reviewed": True,
        "same_record_companion_count": 0,
        "adjacent_prefill_companions_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "pk_runtime_classified_independently": True,
        "runtime_review_required": False,
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
    assert_base_companion_and_assembly(
        prepared,
        records_by_label,
    )
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    coordinate = TARGET_COORDINATES[0]
    current_text = literal_texts(
        records_by_label["current"],
        (BLOCK_ID, 2180),
    )[0]
    target = prepared.visible_targets[
        ("pk_msggame", BLOCK_ID, 2180, 0)
    ]
    row = {
        "schema": ENGINE.DECISION_SCHEMA,
        "resource": "pk_msggame",
        "coordinate": coordinate,
        "source_record_raw_sha256":
        target["source_record_raw_sha256"],
        "current_ko_utf16le_sha256":
        target["current_ko_utf16le_sha256"],
        "translation": TRANSLATIONS[coordinate],
        "semantic_review": "approved",
        "scope_classification": "retranslated",
        "layout_review": "unchanged_from_current",
        "runtime_review": "not_required",
        "basis": BASIS,
        "historic_korean_used": False,
        "switch_korean_used": False,
        "base_exact_reuse_prefill_excluded": True,
        "all_available_predecessors_validated": True,
        "optional_s1095_s1097_validated_if_present": True,
        "manual_multilingual_context_review": True,
        "adjacent_record_context_review": True,
        "complete_record_fragment_review": True,
        "same_record_companion_count": 0,
        "adjacent_prefill_companions_reviewed": True,
        "diplomacy_terminology_reviewed": True,
        "formal_ui_register_reviewed": True,
        "base_context_reference_coordinate":
        BASE_CONTEXT_REFERENCES[coordinate],
        "base_context_is_automatic_reuse": False,
        "base_runtime_state_inherited": False,
        "line_count_before": current_text.count("\n") + 1,
        "line_count_after":
        TRANSLATIONS[coordinate].count("\n") + 1,
        "line_count_preserved": True,
        "runtime_assembly_evidence":
        runtime_control_evidence(prepared, records_by_label),
    }
    return (
        prepared,
        [row],
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
    if (
        len(validated) != 1
        or rows[0]["semantic_review"] != "approved"
        or rows[0]["scope_classification"] != "retranslated"
        or rows[0]["runtime_review"] != "not_required"
        or rows[0]["layout_review"]
        != "unchanged_from_current"
        or rows[0]["base_runtime_state_inherited"] is not False
        or rows[0]["runtime_assembly_evidence"][
            "runtime_promotion_authorized"
        ]
        is not False
        or rows[0]["line_count_preserved"] is not True
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
                "segment": "pk_msggame_B027_S1096",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": 1,
                "scope_classification_counts": {
                    "retranslated": 1
                },
                "exact_reuse_prefill_count": 66,
                "base_semantic_reference_count": 1,
                "same_record_companion_count": 0,
                "adjacent_prefill_companion_count": 2,
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
                "adjacent_prefill_companions_guarded": True,
                "direct_call_absence_guarded": True,
                "inline_token_absence_guarded": True,
                "diplomacy_terminology_guarded": True,
                "formal_ui_register_guarded": True,
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
