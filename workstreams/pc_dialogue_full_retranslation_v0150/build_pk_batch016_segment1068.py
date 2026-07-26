#!/usr/bin/env python3
"""Build source-redacted PK B016 segment 1068 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch015_segment1065.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B016_S1068.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_DECISIONS = (
    DECISIONS_ROOT / "base_msggame_B001_S45.private.v1.jsonl",
    DECISIONS_ROOT / "base_msggame_B001_S46.private.v1.jsonl",
    DECISIONS_ROOT / "base_msggame_B001_S47.private.v1.jsonl",
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B015_S1065.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B015_S1066.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B015_S1067.private.v1.jsonl",
)

SEGMENT = 1068
QUEUE_BATCH_ID = "pk_msggame-B016"
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
    "7E9B3AFFA98F26658BFA93569CCFC8CB8F776426C69B0EDF7230D38C1F98FC06",
    "1E4654DA1CEB018DBC53F786A2CDF7389717A59329FF114CBE9EAA86F33B3793",
    "216E442E0F41A312FAC5D0654E968E504E0DCFCCA4D4EA3FC57108041CF8AC7D",
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1068_common",
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

TARGET_COORDINATES = (
    "6:608:0",
    "6:619:0",
    "6:647:0",
    "6:647:1",
    "6:650:0",
)
TRANSLATIONS = {
    "6:608:0": "에게\n무운이 따르기를",
    "6:619:0": "…\n이겨 주세요!",
    "6:647:0": "아아… ",
    "6:647:1": " 이(가)\n쳐들어올 것 같습니다",
    "6:650:0": "아무래도",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (608, 619, 647, 650)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
CONTEXT_RECORD_IDS = (
    tuple(range(605, 622)) + tuple(range(644, 653))
)
BOUNDARY_RECORD_IDS = (607, 609, 618, 620, 646, 648, 649, 651)
BASE_RECORD_MAPPING = (
    (608, 606),
    (619, 617),
    (647, 645),
    (650, 648),
)

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "1BDD5C08F61620E30E05D31CD7965BFBE3710E3F7F47A5F98CB72F3A5F3C40EC"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "8D3F7359FB8068FC18496F237E949C4AD05D94DD2457E992CD35814F5D948D43"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "DE6D887E4F288AA647B8C3A081276BD373140E8D3BE0BD48F812AF1BBF77277A"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "619413069314EF88224A8F01142DD0C6E09DCA4BC443FF2A4EB7F81D1D378243"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "93FCAF72697565E875E079417CE48771C628C9E845E27DAE234D81280B9A7B84"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "51F8A9EC292C20EA344BA114AA1516204951A5D54AE0C4F267A896A228D05622"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "77322E07D1AD42AAD409F90B6EE2943C700BE0D29A097A8908E49AEFDB76CCAB"
)
EXPECTED_BOUNDARY_SHA256 = (
    "25F90E9E75AEA45E26B232EEAD745D68055A78EE0BB814BC81CC5019A531BACC"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "4552EA8FC7BDD370A455371E8D869E0BACED98E3C4B3FC36AB7D633EB5F1675E"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "612314458786A8876B9132035813AC3FEE65D185EFF523F028C265C455A07CDA"
)
EXPECTED_BASE_REUSE_ROWS_SHA256 = (
    "6B0EA005D6F167CCB48A18EB0AB5D2A7108A8E2F5A2658021DD8F17C1819855D"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "5569F65B9C9B7EDAB47D997F475B2F802E9BB6F7F034B96A724272FFFD7FC5DB"
)
EXPECTED_PROTECTED_SIGNATURE_SHA256 = (
    "9B843CC8AE937303DD9F607CC24BEAF4C1C2B8183D3ED9D04288C409660B828B"
)
EXPECTED_CANDIDATE_SHA256 = (
    "98DCCBEADC8CC33D6634EB1B715B3FBCD8D628286724377B6F69C65BF82F3B65"
)
EXPECTED_CHANGED_LITERAL_COUNT = 3

EXPECTED_PREFILL_COMPANION = (
    (
        "6:650:1",
        "에서\n수상한 움직임이",
        "approved",
        "pending",
        "D4E10BDEF9DD01E264E643EC2041E1E2DE0683878928725545625B2120F0D077",
        "6:648:1",
    ),
)
EXPECTED_BASE_REUSE_ROWS = (
    (
        "6:606:0",
        "에게\n무운이 따르기를",
        "approved",
        "verified",
        "3775C4FDC88223058A861764D5BF8F84C665F47419CE44A6B6C3ED6CED7BD971",
    ),
    (
        "6:617:0",
        "…\n이겨 주세요!",
        "approved",
        "verified",
        "B3F58E176EE66A61D3FAA2ADB3710E201F5E01B3E4DE2D77AA03BF482E9504F2",
    ),
    (
        "6:645:0",
        "아아…",
        "approved",
        "verified",
        "6F72EEF366E5E881DE2FC6D27E48FFC125C739E75508106442DF0F466CE8ED03",
    ),
    (
        "6:645:1",
        "이(가)\n쳐들어올 것 같습니다",
        "approved",
        "verified",
        "6F72EEF366E5E881DE2FC6D27E48FFC125C739E75508106442DF0F466CE8ED03",
    ),
    (
        "6:648:0",
        "아무래도",
        "approved",
        "verified",
        "D4E10BDEF9DD01E264E643EC2041E1E2DE0683878928725545625B2120F0D077",
    ),
    (
        "6:648:1",
        "에서\n수상한 움직임이",
        "approved",
        "verified",
        "D4E10BDEF9DD01E264E643EC2041E1E2DE0683878928725545625B2120F0D077",
    ),
)
BASE_COORDINATE_LINKS = {
    "6:608:0": ("6:606:0",),
    "6:619:0": ("6:617:0",),
    "6:647:0": ("6:645:0", "6:645:1"),
    "6:647:1": ("6:645:0", "6:645:1"),
    "6:650:0": ("6:648:0", "6:648:1"),
}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC neighboring records are context only; completed Base "
    "identical whole records and exact-reuse prefill companion are "
    "pinned semantic evidence; all existing PK decisions are validated "
    "and excluded; dynamic target grammar, speaker register, historical "
    "battle terminology, protected signatures, line counts, bytecode "
    "gaps, reverse overlay, two-run reproduction, tamper rejection and "
    "read-only inputs are guarded; Base Korean wording is reused with "
    "PK outer whitespace retained but "
    "Base runtime verification is not inherited and all PK fragments "
    "remain runtime pending"
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


def assert_reuse_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        tuple(sha256_bytes(path.read_bytes()) for path in BASE_DECISIONS)
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
    companion = prefill_rows["6:650:1"]
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
    base_coordinates = tuple(
        row[0] for row in EXPECTED_BASE_REUSE_ROWS
    )
    base_evidence = tuple(
        (
            coordinate,
            promoted_rows[coordinate].get("translation"),
            promoted_rows[coordinate].get("semantic_review"),
            promoted_rows[coordinate].get("runtime_review"),
            promoted_rows[coordinate].get("source_record_raw_sha256"),
        )
        for coordinate in base_coordinates
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

    pending_rows: dict[str, dict[str, Any]] = {}
    for path in BASE_DECISIONS:
        pending_rows.update(
            {
                str(row["coordinate"]): row
                for row in read_jsonl(path)
            }
        )
    for coordinate, translation, _, _, source_sha in (
        EXPECTED_BASE_REUSE_ROWS
    ):
        row = pending_rows[coordinate]
        if (
            row.get("translation") != translation
            or row.get("runtime_review") != "pending"
            or row.get("source_record_raw_sha256") != source_sha
        ):
            raise RuntimeError(
                f"segment {SEGMENT} original Base row drifted: "
                f"{coordinate}"
            )

    base_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    for pk_record_id, base_record_id in BASE_RECORD_MAPPING:
        if (
            records_by_label["jp"][(BLOCK_ID, pk_record_id)].data
            != base_records[(BLOCK_ID, base_record_id)].data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base exact record drifted: "
                f"{pk_record_id}"
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
        len(queue_rows) != 188
        or len(visible) != 200
        or visible[0] != "6:605:0"
        or visible[-1] != "6:792:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B016 queue universe drifted"
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
    if len(prefilled) != 62:
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

    base_translation = {
        row[0]: row[1] for row in EXPECTED_BASE_REUSE_ROWS
    }
    if (
        TRANSLATIONS["6:608:0"] != base_translation["6:606:0"]
        or TRANSLATIONS["6:619:0"] != base_translation["6:617:0"]
        or TRANSLATIONS["6:647:0"].rstrip()
        != base_translation["6:645:0"]
        or TRANSLATIONS["6:647:1"].lstrip()
        != base_translation["6:645:1"]
        or TRANSLATIONS["6:650:0"] != base_translation["6:648:0"]
        or EXPECTED_PREFILL_COMPANION[0][1]
        != base_translation["6:648:1"]
        or not TRANSLATIONS["6:608:0"].startswith("에게")
        or not TRANSLATIONS["6:647:1"].lstrip().startswith("이(가)")
        or not TRANSLATIONS["6:650:0"].endswith("도")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base reuse or grammar drifted"
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
    evidence = COMMON.COMMON.runtime_control_evidence(
        records_by_label,
        record_id,
    )
    base_record_id = dict(BASE_RECORD_MAPPING)[record_id]
    evidence.update(
        {
            "base_exact_record_id": base_record_id,
            "base_source_record_exact": True,
            "base_semantic_translation_reused": True,
            "base_runtime_verification_inherited": False,
        }
    )
    if record_id == 650:
        evidence[
            "same_record_prefill_companion_coordinate"
        ] = "6:650:1"
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
    assert_reuse_evidence(records_by_label)
    assert_context_contracts(records_by_label)
    assert_semantics(records_by_label)
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
            "base_exact_record_semantics_reused": True,
            "base_literal_exact_reuse": (
                coordinate not in {"6:647:0", "6:647:1"}
            ),
            "pk_outer_whitespace_preserved": True,
            "base_context_coordinates": list(
                BASE_COORDINATE_LINKS[coordinate]
            ),
            "base_runtime_verification_inherited": False,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "runtime_assembly_evidence": runtime_control_evidence(
                records_by_label,
                record_id,
            ),
        }
        if coordinate == "6:650:0":
            row[
                "same_record_prefill_companion_coordinate"
            ] = "6:650:1"
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
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["protected_signature_review"] is not True
            or row["base_exact_record_semantics_reused"] is not True
            or row["pk_outer_whitespace_preserved"] is not True
            or row["base_runtime_verification_inherited"] is not False
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
                "segment": "pk_msggame_B016_S1068",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": QUEUE_STOP - QUEUE_START,
                "prefill_excluded_count": 62,
                "residual_count": len(rows),
                "context_record_count": len(CONTEXT_RECORD_IDS),
                "optional_predecessors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "completed_base_exact_record_semantics_reused": True,
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
