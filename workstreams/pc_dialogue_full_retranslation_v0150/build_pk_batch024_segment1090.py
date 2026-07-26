#!/usr/bin/env python3
"""Build source-redacted PK B024 segment 1090 residual decision."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B024_S1090.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B024_S1089.private.v1.jsonl",
)

SEGMENT = 1090
QUEUE_BATCH_ID = "pk_msggame-B024"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("6:1742:1",)
TRANSLATIONS = {
    "6:1742:1": " 측과의\n단교를 지시합니다",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (1742,)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (1741, 1743, 1744)
BASE_CONTEXT_REFERENCES = {"6:1742:1": "6:1736:1"}
BASE_COMPANION_COORDINATE = "6:1736:0"
PREFILL_COMPANION_COORDINATE = "6:1742:0"
PARALLEL_PREFILL_COORDINATES = ("6:1744:0", "6:1744:1")
EXPECTED_GAPS_BY_RECORD = {
    1742: ("", "025032", "050505"),
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
    "5315AD9185C4BBB30A6CAEB250B8734DD48514737945D85C1E15FB1375A63F9D"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "6768A4451733D03F1984D1B7B833EFED0E894DC460C0477B53E7F66D8CC72449"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5ED1AF9710738A86C34F22B598FEB2F8763F7D877F244E27AAC0B5155871451A"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "20221474A1F3C0DD1F8566B03D2708524E5C49D644A48DB15E07C8DDD4E1B3FC"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "BEEB3E08027AC27DADBEED99C5282569A4A75E455DF4441CC29FB86A46D145C8"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "DF3B6BC0C2A17EBDCA240D61F14AC1B1AEBB4F9B55665ECC9E366853304394F7"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "7EACC1E95BA72FEF5FE1D7CC52CE18BA34DE087BF006C4DADD25CF32C6842C85"
)
EXPECTED_BOUNDARY_SHA256 = (
    "C84F4EA1BAD7FA03E392CAA9C6648F53B0AC4BD40795B5AAEBC01CE95B1D97D5"
)
EXPECTED_RUNTIME_OPERAND_SHA256 = (
    "B5CDB4D993DC05E5CB50BAE067B284EBD39FEAA6EE25CD471BC92F6DD40B63D6"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "1FE4CC7E16ACE2A125BFA7F6B825677521DEED39C53473CC353445695233E081"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "D290E60212CE908F75B56509CE50A5936522E580D3EEF212D0C6ADAF799A55F3"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "B1BB3411953E686DABE85B5337BD6538E8E107C555E4135A9AB27A3027D0D518"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "0530F39B7FEC7C27AE9810ADA305752B2F508CCD2FA016A7D3818EBD068C83CB"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "9EE7F9ED53D38750260C687B61A128DC7CFE12738CE2576539D8E56C45FFE11C"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "6AC9DF70FE1569F47944BE2003135F59489F23D79D0E7E50DF56EFBB1A33DB7A"
)
EXPECTED_CANDIDATE_SHA256 = (
    "084544F78CDF7CB1E2B9B861E587D87EBBBE1DEBDAA5D68E7C17539FF05C38B7"
)
EXPECTED_CHANGED_LITERAL_COUNT = 1

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; the completed Base exact-"
    "source donor pins the sever-relations meaning and formal command "
    "register, while the PK fragment preserves its protected leading "
    "space and adapts the relational particle so the prefilled companion, "
    "inline clan-name token and target fragment form natural Korean; all "
    "available predecessor decisions are validated and excluded; the "
    "full record, direct-call absence, inline-name operand, parallel truce "
    "template, adjacent records, protected signature, line count, bytecode "
    "gaps, reverse overlay, two-run reproduction, tamper rejection and "
    "read-only inputs are guarded; Base runtime state is not inherited and "
    "the PK target remains runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1090_common",
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


def runtime_operands(
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
            *runtime_operands(
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
        if any(runtime_operands(
            records_by_label["jp"][(BLOCK_ID, record_id)]
        ))
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
            or current != source
            for record_id, source, current in gaps
        )
        or operand_evidence
        != (
            ("jp", 1742, (), ("025032",)),
            ("current", 1742, (), ("025032",)),
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def assert_base_companion_and_assembly(
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
    pk_coordinate = TARGET_COORDINATES[0]
    base_coordinate = BASE_CONTEXT_REFERENCES[pk_coordinate]
    pk_key = coordinate_key(pk_coordinate)
    base_key = coordinate_key(base_coordinate)
    base_row = base_rows[base_coordinate]
    base_companion_row = base_rows[BASE_COMPANION_COORDINATE]
    base_evidence = (
        pk_coordinate,
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
        BASE_COMPANION_COORDINATE,
        base_companion_row.get("translation"),
        base_companion_row.get("semantic_review"),
        base_companion_row.get("runtime_review"),
        tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["jp"][pk_key[:2]]
            )
        ),
        tuple(
            value.hex().upper()
            for value in gap_bytes(
                base_source_records[base_key[:2]]
            )
        ),
        "protected-leading-space relational-particle adaptation",
        TRANSLATIONS[pk_coordinate],
    )
    guarded_digest(
        "Base context",
        base_evidence,
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    if (
        base_evidence[2] != base_evidence[3]
        or base_row.get("translation")
        != "의\n단교를 지시합니다"
        or base_row.get("semantic_review") != "approved"
        or base_row.get("runtime_review") != "verified"
        or base_companion_row.get("translation") != "이 세력과"
        or base_companion_row.get("semantic_review") != "approved"
        or base_companion_row.get("runtime_review") != "verified"
        or TRANSLATIONS[pk_coordinate]
        != " 측과의\n단교를 지시합니다"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base semantic donor drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    companion_coordinates = (
        PREFILL_COMPANION_COORDINATE,
        *PARALLEL_PREFILL_COORDINATES,
    )
    companion_evidence = tuple(
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
        for coordinate in companion_coordinates
    )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    if any(
        semantic != "approved" or runtime != "pending"
        for _, _, semantic, runtime, _, _ in companion_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill companion drifted"
        )

    current_literals = literal_texts(
        records_by_label["current"],
        (BLOCK_ID, 1742),
    )
    assembled_literals = (
        str(
            prefill_rows[PREFILL_COMPANION_COORDINATE][
                "translation"
            ]
        ),
        TRANSLATIONS[pk_coordinate],
    )
    assembly_evidence = (
        ("owners", ("prefill", "segment")),
        ("source_literals", literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, 1742),
        )),
        ("current_literals", current_literals),
        ("assembled_literals", assembled_literals),
        ("gaps", tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["jp"][(BLOCK_ID, 1742)]
            )
        )),
        ("runtime_operands", runtime_operands(
            records_by_label["jp"][(BLOCK_ID, 1742)]
        )),
        ("parallel_truce", tuple(
            str(prefill_rows[coordinate]["translation"])
            for coordinate in PARALLEL_PREFILL_COORDINATES
        )),
    )
    guarded_digest(
        "assembly policy",
        assembly_evidence,
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )
    if (
        assembled_literals[0] != "이 세력과"
        or assembled_literals[1] != " 측과의\n단교를 지시합니다"
        or assembly_evidence[4][1]
        != ("", "025032", "050505")
        or assembly_evidence[5][1] != ((), ("025032",))
        or not all(
            term in "\u241f".join(assembled_literals)
            for term in ("세력", "측과의", "단교", "지시")
        )
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
    runtime_category = (
        (
            "6:1742:1",
            "inline_clan_name_sever_relations",
            "runtime_fragment_pending",
            "pending",
            "runtime_pending",
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
        (BLOCK_ID, 1742),
    )[1]
    translation = TRANSLATIONS[coordinate]
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or translation != " 측과의\n단교를 지시합니다"
        or not translation.startswith(" ")
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
        "runtime_pending",
        coordinate,
    )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    source_record = records_by_label["jp"][(BLOCK_ID, 1742)]
    current_record = records_by_label["current"][
        (BLOCK_ID, 1742)
    ]
    source_gaps = gap_bytes(source_record)
    current_gaps = gap_bytes(current_record)
    source_direct, source_inline = runtime_operands(source_record)
    current_direct, current_inline = runtime_operands(current_record)
    if (
        source_direct
        or current_direct
        or source_inline != ("025032",)
        or current_inline != source_inline
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic controls drifted"
        )
    return {
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in source_gaps)
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in current_gaps)
        ),
        "source_direct_call_operands": source_direct,
        "current_direct_call_operands": current_direct,
        "source_inline_name_token_hex": source_inline,
        "current_inline_name_token_hex": current_inline,
        "source_current_runtime_gap_equal":
        source_gaps == current_gaps,
        "complete_record_assembly_reviewed": True,
        "prefill_companion_reviewed": True,
        "parallel_truce_template_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "protected_leading_space_preserved": True,
        "relational_particle_contextually_adapted": True,
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
    assert_base_companion_and_assembly(records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    coordinate = TARGET_COORDINATES[0]
    current_text = literal_texts(
        records_by_label["current"],
        (BLOCK_ID, 1742),
    )[1]
    target = prepared.visible_targets[
        ("pk_msggame", BLOCK_ID, 1742, 1)
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
        "scope_classification": "runtime_fragment_pending",
        "layout_review": "runtime_pending",
        "runtime_review": "pending",
        "basis": BASIS,
        "historic_korean_used": False,
        "switch_korean_used": False,
        "base_exact_reuse_prefill_excluded": True,
        "all_available_predecessors_validated": True,
        "optional_s1089_validated_if_present": True,
        "manual_multilingual_context_review": True,
        "adjacent_record_context_review": True,
        "complete_record_fragment_review": True,
        "direct_call_absence_reviewed": True,
        "inline_name_token_reviewed": True,
        "prefill_companion_reviewed": True,
        "parallel_truce_template_reviewed": True,
        "base_context_reference_coordinate":
        BASE_CONTEXT_REFERENCES[coordinate],
        "base_context_is_automatic_reuse": False,
        "base_runtime_state_inherited": False,
        "protected_leading_space_preserved": True,
        "relational_particle_contextually_adapted": True,
        "line_count_before": current_text.count("\n") + 1,
        "line_count_after":
        TRANSLATIONS[coordinate].count("\n") + 1,
        "line_count_preserved": True,
        "runtime_assembly_evidence":
        runtime_control_evidence(records_by_label),
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
        or rows[0]["scope_classification"]
        != "runtime_fragment_pending"
        or rows[0]["runtime_review"] != "pending"
        or rows[0]["layout_review"] != "runtime_pending"
        or rows[0]["base_runtime_state_inherited"] is not False
        or rows[0]["protected_leading_space_preserved"]
        is not True
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
                "segment": "pk_msggame_B024_S1090",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": 1,
                "scope_classification_counts": {
                    "runtime_fragment_pending": 1
                },
                "exact_reuse_prefill_count": 66,
                "base_semantic_reference_count": 1,
                "prefill_companion_count": 1,
                "parallel_template_count": 1,
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
                "prefill_companion_guarded": True,
                "direct_call_absence_guarded": True,
                "inline_name_token_guarded": True,
                "protected_leading_space_preserved": True,
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
