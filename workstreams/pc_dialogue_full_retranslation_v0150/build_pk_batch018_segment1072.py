#!/usr/bin/env python3
"""Build source-redacted PK B018 segment 1072 residual decision."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B018_S1072.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B016_S1068.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B016_S1069.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B017_S1070.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B018_S1071.private.v1.jsonl",
)

SEGMENT = 1072
QUEUE_BATCH_ID = "pk_msggame-B018"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = ("6:1098:0",)
TRANSLATIONS = {"6:1098:0": "자—"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (1098,)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (1097, 1099)
BASE_CONTEXT_REFERENCES = {"6:1098:0": "7:1914:0"}
PREFILL_COMPANION_COORDINATES = {"6:1098:1"}

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
    "FB8AD8C8881F962650ED919D1FC801BDCD469EEBC6D2154951B6E89E155E9CC6"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "5A7614D6E602EABC7DE23689B8DEC1D9C53D25D60576231A722D72B6A73142B1"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "77DB01FAC691537A75561015797C0BAF7BECD8A0EF02EB0AA153295A166749D0"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "75251CBC67F0648C8E95CAEB6C8B94C81B484F907DD0A29C94ADBE3634419C24"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "B0CD3599486FF4DE4A251A5D024BFE9D6D917AC5F0CB2F692854E32C2A36DCDE"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "A6676B526013F286C8CC943659A80C7FA195FB5F40F1F49E928786BD729490D2"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "DD919BE9BA293F81B912C16B96BD9CE47EDF4B86DC29014EF86E9258C8393D03"
)
EXPECTED_BOUNDARY_SHA256 = (
    "2DAC15849D68CD2F2ABD6982D705633A505AFF8E09D1B16C4F8C3D5D7124EEE7"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "257ADED37DD54C11F65AC36B3FE3E648E7EB7C890B14CF008286851C0786CE78"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "1C34B6A2ABAEB0419E799B5F6AD301DA86C6DAB2C5AE9616DCFCA9CE2233EDD6"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "8850AA641CBDBC8C72A291918A0EE53F2DDAD50165CF4E052B93AF1ED2A8D808"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "2F03D23DB0CA86980F71C0151DE7E6813754285D7630F02B3DB043EBA5D73EBA"
)
EXPECTED_CANDIDATE_SHA256 = (
    "05440BC919D5C5A0EC185A4E1D71BB285834ED13D21C1D5B9F9DDFC62D8B82AC"
)
EXPECTED_CHANGED_LITERAL_COUNT = 1

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; Base exact reuse prefill and "
    "all available predecessor decisions are validated and excluded; "
    "the completed Base exact-record donor pins semantic register, but "
    "its runtime state is not automatically inherited; the prefilled "
    "companion, complete dynamic-name assembly, adjacent records, "
    "protected signature, line count, bytecode gaps, reverse overlay, "
    "two-run reproduction, tamper rejection and read-only inputs are "
    "guarded; the target remains runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1072_common",
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
        len(queue_rows) != 182
        or len(visible) != 200
        or visible[0] != "6:985:0"
        or visible[-1] != "6:1166:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B018 queue universe drifted"
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
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if (
            b"\x01\x43"
            in b"".join(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            )
            or b"\x02"
            in b"".join(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
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
            "dynamic record",
            actual_dynamic,
            EXPECTED_DYNAMIC_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if actual_dynamic != DYNAMIC_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic classification drifted"
        )


def assert_base_and_companion_context(
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
    evidence = (
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
    )
    guarded_digest(
        "Base context",
        evidence,
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    if (
        evidence[2] != evidence[3]
        or base_row.get("translation")
        != TRANSLATIONS[pk_coordinate]
        or base_row.get("semantic_review") != "approved"
        or base_row.get("runtime_review") != "verified"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base semantic donor drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    companion = next(iter(PREFILL_COMPANION_COORDINATES))
    companion_row = prefill_rows[companion]
    companion_evidence = (
        companion,
        companion_row.get("translation"),
        companion_row.get("semantic_review"),
        companion_row.get("runtime_review"),
        companion_row.get("source_record_raw_sha256"),
    )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    if (
        companion_row.get("semantic_review") != "approved"
        or companion_row.get("runtime_review") != "pending"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} companion decision drifted"
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
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or TRANSLATIONS["6:1098:0"] != "자—"
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    current_text = literal_texts(
        records_by_label["current"],
        (BLOCK_ID, 1098),
    )[0]
    translation = TRANSLATIONS["6:1098:0"]
    ENGINE.validate_translation_shape(
        current_text,
        translation,
        "runtime_pending",
        "6:1098:0",
    )
    if (
        translation.count("\n") != current_text.count("\n")
        or ENGINE.protected_signature(translation)
        != ENGINE.protected_signature(current_text)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} shape drifted"
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
    source_gaps = gap_bytes(
        records_by_label["jp"][(BLOCK_ID, 1098)]
    )
    current_gaps = gap_bytes(
        records_by_label["current"][(BLOCK_ID, 1098)]
    )
    source_runtime = tuple(
        value.hex().upper()
        for value in source_gaps
        if b"\x01\x43" in value or b"\x02" in value
    )
    current_runtime = tuple(
        value.hex().upper()
        for value in current_gaps
        if b"\x01\x43" in value or b"\x02" in value
    )
    if not source_runtime or not current_runtime:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic record lost controls"
        )
    return {
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in source_gaps)
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in current_gaps)
        ),
        "source_runtime_gap_hex": source_runtime,
        "current_runtime_gap_hex": current_runtime,
        "source_current_runtime_gap_equal":
        source_runtime == current_runtime,
        "complete_record_assembly_reviewed": True,
        "prefill_companion_reviewed": True,
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
    assert_base_and_companion_context(records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    coordinate = TARGET_COORDINATES[0]
    current_text = literal_texts(
        records_by_label["current"],
        (BLOCK_ID, 1098),
    )[0]
    target = prepared.visible_targets[
        ("pk_msggame", BLOCK_ID, 1098, 0)
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
        "optional_s1071_validated_if_present": True,
        "manual_multilingual_context_review": True,
        "adjacent_record_context_review": True,
        "complete_record_fragment_review": True,
        "prefill_companion_reviewed": True,
        "base_context_reference_coordinate":
        BASE_CONTEXT_REFERENCES[coordinate],
        "base_context_is_automatic_reuse": False,
        "base_runtime_state_inherited": False,
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
                "segment": "pk_msggame_B018_S1072",
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
