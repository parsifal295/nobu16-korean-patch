#!/usr/bin/env python3
"""Build source-redacted PK B015 segment 1065 residual decisions."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch014_segment1063.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B015_S1065.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_DECISION = (
    DECISIONS_ROOT / "base_msggame_B001_S36.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B014_S1063.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B014_S1064.private.v1.jsonl",
)

SEGMENT = 1065
QUEUE_BATCH_ID = "pk_msggame-B015"
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
EXPECTED_BASE_DECISION_SHA256 = (
    "538E54FF54F720F9091FEB482B19C226FB3B2AC17CC8F7F8458934B4BACA4B73"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1065_common",
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

TARGET_COORDINATES = ("6:443:1",)
TRANSLATIONS = {"6:443:1": "도…"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (443,)
DYNAMIC_RECORD_IDS = (443,)
CONTEXT_RECORD_IDS = tuple(range(439, 448))
BOUNDARY_RECORD_IDS = (442, 444)

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "84BE990F918CF3C13478D9FD01B7F4BA80113676DCB756C0535AB6A7161F05AD"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "71C551F80FDCC7CBEF45DCF9C08670F8965727FC626160EC935EE64635697961"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "10A50B683CFA8CC8C03E9C74FD7B5CB66B3E3C4DC15D4B01019C323192996DF8"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3B953EEA1AE5BCDB5F4498127B7DB4E8F4511934478103833911F0934BE7BCB1"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "F194CB62224BEAA145B8CFC971803B9C19A4973DAD9E7AF293331792E9A5743F"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "34FD09ACD003F261C96160B40BF3C5813022BC699EF6A6F905ED623DC08EE02B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "8DEE3D5D75F9551B28852123A69F4977433719D13351290EC893D197166A700A"
)
EXPECTED_BOUNDARY_SHA256 = (
    "051ADDF360BD84E8FC322A4545562C194A90D762C2EF8D4E89596D985033E3D4"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "75E634CF468CC5AFF711C3B5DAFBAA893700DED6C65CDF50385313A3C6D3146D"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "B5919935B2048A0346543CFC2D05AAAA2955ECC2D56D69AFAB3A9FAF342E43DC"
)
EXPECTED_BASE_REUSE_ROWS_SHA256 = (
    "CD6B17849E318C8EBD0BCB41A646404206B257628089061BCF6C086BB37C6A3C"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "F194CB62224BEAA145B8CFC971803B9C19A4973DAD9E7AF293331792E9A5743F"
)
EXPECTED_PROTECTED_SIGNATURE_SHA256 = (
    "6BD92E1017E45930AE8FF8163E0FCB6FD507C06E7698AE4F0EDF6213C3090C8F"
)
EXPECTED_CANDIDATE_SHA256 = EXPECTED_STEAM_PK_SHA256
EXPECTED_CHANGED_LITERAL_COUNT = 0

EXPECTED_PREFILL_COMPANION = (
    (
        "6:443:0",
        "이러한 영예를\n언젠가는",
        "approved",
        "pending",
        "5239B06A9788ABDD2E239CD7CB56499653DC8F0C52729B1D586C6F0F3ECD11E4",
        "6:441:0",
    ),
)
EXPECTED_BASE_REUSE_ROWS = (
    (
        "6:441:0",
        "이러한 영예를\n언젠가는",
        "approved",
        "verified",
        "5239B06A9788ABDD2E239CD7CB56499653DC8F0C52729B1D586C6F0F3ECD11E4",
    ),
    (
        "6:441:1",
        "도…",
        "approved",
        "verified",
        "5239B06A9788ABDD2E239CD7CB56499653DC8F0C52729B1D586C6F0F3ECD11E4",
    ),
)

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC neighboring records are context only; exact-reuse "
    "prefill companion and completed Base identical whole-record Korean "
    "are pinned evidence; all existing PK decisions are validated and "
    "excluded; complete dynamic assembly, speaker register, protected "
    "signature, line count, bytecode gaps, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are guarded; "
    "Base semantic wording is reused but Base runtime verification is "
    "not inherited and the PK fragment remains runtime pending"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def coordinate_key(value: str) -> tuple[int, int, int]:
    return COMMON.coordinate_key(value)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return COMMON.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return COMMON.gap_bytes(record)


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return COMMON.read_jsonl(path)


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


def context_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    patch_common_globals()
    return COMMON.context_records(prepared)


def assert_reuse_evidence() -> None:
    if (
        sha256_bytes(BASE_DECISION.read_bytes())
        != EXPECTED_BASE_DECISION_SHA256
        or sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} completed Base evidence drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(PREFILL)
    }
    companion = prefill_rows["6:443:0"]
    companion_evidence = (
        (
            str(companion["coordinate"]),
            companion.get("translation"),
            companion.get("semantic_review"),
            companion.get("runtime_review"),
            companion.get("source_record_raw_sha256"),
            companion["base_exact_reuse_prefill"].get("base_coordinate"),
        ),
    )
    if companion_evidence != EXPECTED_PREFILL_COMPANION:
        raise RuntimeError(
            f"segment {SEGMENT} prefill companion drifted"
        )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )

    promoted_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_PROMOTED)
    }
    base_evidence = tuple(
        (
            coordinate,
            promoted_rows[coordinate].get("translation"),
            promoted_rows[coordinate].get("semantic_review"),
            promoted_rows[coordinate].get("runtime_review"),
            promoted_rows[coordinate].get("source_record_raw_sha256"),
        )
        for coordinate in ("6:441:0", "6:441:1")
    )
    if base_evidence != EXPECTED_BASE_REUSE_ROWS:
        raise RuntimeError(
            f"segment {SEGMENT} completed Base rows drifted"
        )
    guarded_digest(
        "completed Base rows",
        base_evidence,
        EXPECTED_BASE_REUSE_ROWS_SHA256,
    )

    base_pending_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_DECISION)
    }
    if (
        base_pending_rows["6:441:0"].get("translation")
        != EXPECTED_BASE_REUSE_ROWS[0][1]
        or base_pending_rows["6:441:1"].get("translation")
        != EXPECTED_BASE_REUSE_ROWS[1][1]
        or base_pending_rows["6:441:0"].get("runtime_review")
        != "pending"
        or base_pending_rows["6:441:1"].get("runtime_review")
        != "pending"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} original Base decisions drifted"
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
    assert_reuse_evidence()

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
        len(queue_rows) != 188
        or len(visible) != 200
        or visible[0] != "6:417:0"
        or visible[-1] != "6:604:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B015 queue universe drifted"
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
        for record_id in CONTEXT_RECORD_IDS
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
    protected = tuple(
        (
            coordinate,
            ENGINE.protected_signature(
                literal_texts(
                    records_by_label["current"],
                    coordinate_key(coordinate)[:2],
                )[coordinate_key(coordinate)[2]]
            ),
            ENGINE.protected_signature(TRANSLATIONS[coordinate]),
        )
        for coordinate in TARGET_COORDINATES
    )
    guarded_digest(
        "source target",
        source_target,
        EXPECTED_SOURCE_TARGET_SHA256,
    )
    guarded_digest(
        "current target",
        current_target,
        EXPECTED_CURRENT_TARGET_SHA256,
    )
    guarded_digest(
        "multilingual context",
        corpus,
        EXPECTED_CONTEXT_CORPUS_SHA256,
    )
    guarded_digest(
        "gap contract",
        gaps,
        EXPECTED_GAP_CONTRACT_SHA256,
    )
    guarded_digest(
        "boundary",
        boundary,
        EXPECTED_BOUNDARY_SHA256,
    )
    guarded_digest(
        "protected signature",
        protected,
        EXPECTED_PROTECTED_SIGNATURE_SHA256,
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
    guarded_digest(
        "dynamic record",
        actual_dynamic,
        EXPECTED_DYNAMIC_RECORD_SHA256,
    )
    if actual_dynamic != DYNAMIC_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic classification drifted"
        )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation ordering drifted"
        )
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
        ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source-redaction policy drifted"
        )

    current = records_by_label["current"]
    coordinate = TARGET_COORDINATES[0]
    block_id, record_id, literal_id = coordinate_key(coordinate)
    current_text = literal_texts(
        current,
        (block_id, record_id),
    )[literal_id]
    translation = TRANSLATIONS[coordinate]
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
        or translation != EXPECTED_BASE_REUSE_ROWS[1][1]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} shape or Base reuse drifted"
        )

    companion = EXPECTED_PREFILL_COMPANION[0][1]
    if (
        not companion.endswith("언젠가는")
        or not translation.startswith("도")
        or translation != "도…"
        or gap_bytes(
            records_by_label["jp"][(BLOCK_ID, record_id)]
        )[1]
        != bytes.fromhex("014301000000")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} complete assembly drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    patch_common_globals()
    evidence = COMMON.runtime_control_evidence(
        records_by_label,
        record_id,
    )
    evidence.update(
        {
            "same_record_prefill_companion_coordinate": "6:443:0",
            "base_exact_record_coordinates": ["6:441:0", "6:441:1"],
            "base_source_record_exact": True,
            "base_semantic_translation_reused": True,
            "base_runtime_verification_inherited": False,
        }
    )
    return evidence


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
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )

    coordinate = TARGET_COORDINATES[0]
    block_id, record_id, literal_id = coordinate_key(coordinate)
    current_text = literal_texts(
        records_by_label["current"],
        (block_id, record_id),
    )[literal_id]
    target = prepared.visible_targets[
        ("pk_msggame", block_id, record_id, literal_id)
    ]
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
        "base_exact_reuse_prefill_excluded": True,
        "all_available_predecessors_validated": True,
        "manual_multilingual_context_review": True,
        "adjacent_record_context_review": True,
        "complete_record_fragment_review": True,
        "speaker_register_review": True,
        "historical_term_review": True,
        "protected_signature_review": True,
        "base_exact_record_translation_reused": True,
        "base_context_coordinates": ["6:441:0", "6:441:1"],
        "base_runtime_verification_inherited": False,
        "same_record_prefill_companion_coordinate": "6:443:0",
        "line_count_before": current_text.count("\n") + 1,
        "line_count_after": TRANSLATIONS[coordinate].count("\n") + 1,
        "line_count_preserved": True,
        "runtime_assembly_evidence": runtime_control_evidence(
            records_by_label,
            record_id,
        ),
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
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    row = rows[0]
    if (
        len(rows) != 1
        or len(validated) != 1
        or counts != Counter({"runtime_fragment_pending": 1})
        or row["semantic_review"] != "approved"
        or row["runtime_review"] != "pending"
        or row["layout_review"] != "runtime_pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        or row["line_count_preserved"] is not True
        or row["protected_signature_review"] is not True
        or row["base_exact_record_translation_reused"] is not True
        or row["base_runtime_verification_inherited"] is not False
        or row["runtime_assembly_evidence"][
            "runtime_promotion_authorized"
        ]
        is not False
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
                "segment": "pk_msggame_B015_S1065",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "coordinate": TARGET_COORDINATES[0],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": QUEUE_STOP - QUEUE_START,
                "prefill_excluded_count": 66,
                "residual_count": 1,
                "optional_predecessors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "completed_base_exact_record_reused": True,
                "base_runtime_verification_inherited": False,
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
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
