#!/usr/bin/env python3
"""Build source-redacted PK B021 segment 1080 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch021_segment1081.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B021_S1080.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_DECISION = (
    DECISIONS_ROOT / "base_msggame_B001_S85.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B020_S1077.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B020_S1078.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B020_S1079.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B021_S1081.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B021_S1082.private.v1.jsonl",
)

SEGMENT = 1080
QUEUE_BATCH_ID = "pk_msggame-B021"
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
    "3E1AFA41FB9D2599172B9883EA4DA5F065CCFB1AB5A2A5FD55FE6BC86D98F687"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1080_common",
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

TARGET_COORDINATES = tuple(
    f"6:{record_id}:1" for record_id in range(1347, 1359)
) + tuple(
    coordinate
    for record_id in range(1359, 1367)
    for coordinate in (
        f"6:{record_id}:0",
        f"6:{record_id}:2",
    )
)
TRANSLATIONS = {
    coordinate: (
        "의\n"
        if coordinate_key(coordinate)[1] <= 1358
        else (
            "우리는"
            if coordinate_key(coordinate)[2] == 0
            else "의"
        )
    )
    for coordinate in TARGET_COORDINATES
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = tuple(range(1347, 1367))
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
CONTEXT_RECORD_IDS = tuple(range(1344, 1370))
BOUNDARY_RECORD_IDS = (1346, 1367)
BASE_RECORD_MAPPING = {
    **{record_id: 1343 for record_id in range(1347, 1359)},
    **{record_id: 1355 for record_id in range(1359, 1367)},
}
BASE_COORDINATE_MAPPING = {
    **{
        f"6:{record_id}:1": "6:1343:1"
        for record_id in range(1347, 1359)
    },
    **{
        f"6:{record_id}:0": "6:1355:0"
        for record_id in range(1359, 1367)
    },
    **{
        f"6:{record_id}:2": "6:1355:2"
        for record_id in range(1359, 1367)
    },
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "14C508D9C481787196F28F22AC27A6CC0927B8D7261AC8EDDC3CBA456B320E2C"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "44871E7B6CD42F9CF44FF34A570C05E8BD9CC6D8E80C001BC1C5DE9561716957"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "7417FD4D558D89ED87665BAD211118CD8767B944FB0B70C0D217AFB3803347A1"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "C05F52BC749033BE27A1E715C24C7A24E7D3CC6A2C51F8815948D08D6F55C639"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "3692B3E4BFDFFA994D7092E45F663C2F2FDE9B331F5D26DBD8D46457402555F8"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "AA76C3E52B8AB0536029A6C7CCCEA5EEEC0421D7B02D09A3D08F42E8A8AD5DB7"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "6C3FEA43D5EEAD05EA7EF82A7C5CFC2DA7EB412550CB748F34CB206C6DD4D7A2"
)
EXPECTED_BOUNDARY_SHA256 = (
    "C69F85DD8C188265BD20EC19FD79CF882177C77600180C0D16E2E9D044AB022D"
)
EXPECTED_PROTECTED_SIGNATURE_SHA256 = (
    "2A976712CCD614587AC6ECB998FD17AF7D3F3FDEF2CA8E0F0103DBA38A62EA37"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "9C33B9EAFFDD601F41EB174DA005DF262E973C2EAB82C4D7AECB1F0E6AE513BC"
)
EXPECTED_COMPANION_COORDINATE_SHA256 = (
    "612F0AF3502E1EC92343D40391C88970A5204E5DD363ED956CC421ADB01F0DB6"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "BA4AD18E4CE6071DA9CE95BA3B4DD53CF0A7EFC80BE01E886E8CA4155DCAD326"
)
EXPECTED_BASE_REUSE_ROWS_SHA256 = (
    "8F0B708E46222D8C15C2D34E69D285B6748AFD1D6573F3ACEEBF388A6D4C3B15"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "D5A0D95872BAB7C73698639AD900F16ECBE67F15E13BA98AB3BD8EC94B49F265"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "010B56C94E982E831A8A7F6554E405086501C39F03C0117DF8BB329BFA6745FF"
)
EXPECTED_CANDIDATE_SHA256 = (
    "809B9453B8E08607C93C817A56E1754263BEC2B0341F9EAFEF49E561E8D800DF"
)
EXPECTED_CHANGED_LITERAL_COUNT = 8

BASE_REUSE_ROWS = (
    (
        "6:1343:0",
        "우리의 현 상황을 고려하면",
        "approved",
        "verified",
        "08E685B40D5EFC95F40814509CE24FA94F1682D47307ACFB2446D7A406839FDD",
    ),
    (
        "6:1343:1",
        "의\n",
        "approved",
        "verified",
        "08E685B40D5EFC95F40814509CE24FA94F1682D47307ACFB2446D7A406839FDD",
    ),
    (
        "6:1343:2",
        "을(를) 당면 목표로 삼아야 합니다\n지도를 보며 설명드리지요",
        "approved",
        "verified",
        "08E685B40D5EFC95F40814509CE24FA94F1682D47307ACFB2446D7A406839FDD",
    ),
    (
        "6:1355:0",
        "우리는",
        "approved",
        "verified",
        "F66A72713EF5BBDA601D3F9A836BD5E214888918E534274FE18B2B736614DE94",
    ),
    (
        "6:1355:1",
        "공략을 목표로 삼되\n우선",
        "approved",
        "verified",
        "F66A72713EF5BBDA601D3F9A836BD5E214888918E534274FE18B2B736614DE94",
    ),
    (
        "6:1355:2",
        "의",
        "approved",
        "verified",
        "F66A72713EF5BBDA601D3F9A836BD5E214888918E534274FE18B2B736614DE94",
    ),
    (
        "6:1355:3",
        "을(를) 먼저 목표로 삼아야 합니다\n지도를 보며 설명드리지요",
        "approved",
        "verified",
        "F66A72713EF5BBDA601D3F9A836BD5E214888918E534274FE18B2B736614DE94",
    ),
)

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC neighboring records are context only; completed Base "
    "exact records and all forty same-record exact-prefill companions "
    "are pinned semantic evidence; the first group assembles target "
    "force 026433 plus a possessive literal plus target base 026432; "
    "the second group assembles a long-term target 025032 and then a "
    "second target force 025032 plus a possessive literal plus target "
    "base 026432; the source possessive relation is retained in every "
    "record and the B019 single-name dash rule is inapplicable; Base "
    "runtime state is not inherited; protected signatures, line counts, "
    "bytecode gaps, complete assembly ownership, reverse overlay, "
    "two-run reproduction, tamper rejection and read-only inputs are "
    "guarded; every row remains PK runtime pending"
)


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


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
        len(queue_rows) != 103
        or len(visible) != 200
        or visible[0] != "6:1347:0"
        or visible[-1] != "6:1449:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B021 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:1347:0"
        or queue_slice[-1] != "6:1366:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue slice bounds drifted"
        )
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
    if len(prefilled) != 39:
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
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if b"\x02"
        in b"".join(
            gap_bytes(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
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
            "protected signature",
            protected,
            EXPECTED_PROTECTED_SIGNATURE_SHA256,
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


def companion_coordinates() -> tuple[str, ...]:
    return tuple(
        f"6:{record_id}:{literal_id}"
        for record_id in range(1347, 1359)
        for literal_id in (0, 2)
    ) + tuple(
        f"6:{record_id}:{literal_id}"
        for record_id in range(1359, 1367)
        for literal_id in (1, 3)
    )


def assert_base_companion_and_assembly(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_DECISION.read_bytes())
        != EXPECTED_BASE_DECISION_SHA256
        or sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} completed Base evidence drifted"
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
            promoted_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
        )
        for coordinate, *_ in BASE_REUSE_ROWS
    )
    if base_evidence != BASE_REUSE_ROWS:
        raise RuntimeError(
            f"segment {SEGMENT} completed Base rows drifted"
        )
    guarded_digest(
        "completed Base rows",
        base_evidence,
        EXPECTED_BASE_REUSE_ROWS_SHA256,
    )

    pending_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_DECISION)
    }
    for coordinate, translation, _, _, source_sha in BASE_REUSE_ROWS:
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
    for pk_record_id, base_record_id in BASE_RECORD_MAPPING.items():
        if (
            records_by_label["jp"][(BLOCK_ID, pk_record_id)].data
            != base_records[(BLOCK_ID, base_record_id)].data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base exact record drifted: "
                f"{pk_record_id}"
            )

    companions = companion_coordinates()
    guarded_digest(
        "companion coordinate",
        companions,
        EXPECTED_COMPANION_COORDINATE_SHA256,
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
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate][
                "base_exact_reuse_prefill"
            ].get("base_coordinate"),
        )
        for coordinate in companions
    )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    if any(
        semantic != "approved"
        or runtime != "pending"
        for _, _, semantic, runtime, _, _ in companion_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill companion drifted"
        )

    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
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
            )
        )
    guarded_digest(
        "complete assembly",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
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
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
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

    if (
        any(
            TRANSLATIONS[f"6:{record_id}:1"] != "의\n"
            for record_id in range(1347, 1359)
        )
        or any(
            TRANSLATIONS[f"6:{record_id}:0"] != "우리는"
            or TRANSLATIONS[f"6:{record_id}:2"] != "의"
            for record_id in range(1359, 1367)
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} possessive assembly drifted"
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
    source_gaps = gap_bytes(
        records_by_label["jp"][(BLOCK_ID, record_id)]
    )
    current_gaps = gap_bytes(
        records_by_label["current"][(BLOCK_ID, record_id)]
    )
    source_gap_hex = tuple(
        value.hex().upper() for value in source_gaps
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in current_gaps
    )
    expected = (
        ("", "026433", "026432", "050505")
        if record_id <= 1358
        else (
            "",
            "025032",
            "025032",
            "026432",
            "050505",
        )
    )
    if source_gap_hex != expected or current_gap_hex != expected:
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
        )
    return {
        "source_record_gap_sha256":
        canonical_sha256(source_gap_hex),
        "current_record_gap_sha256":
        canonical_sha256(current_gap_hex),
        "source_current_gap_equal": True,
        "token_sequence": (
            (
                "reviewed_literal_0",
                "026433",
                "reviewed_possessive_literal",
                "026432",
                "reviewed_literal_2",
                "050505",
            )
            if record_id <= 1358
            else (
                "reviewed_literal_0",
                "025032_long_term_target",
                "reviewed_literal_1",
                "025032_immediate_target_force",
                "reviewed_possessive_literal",
                "026432_target_base",
                "reviewed_literal_3",
                "050505",
            )
        ),
        "base_exact_record_id":
        BASE_RECORD_MAPPING[record_id],
        "base_source_record_exact": True,
        "base_semantic_translation_reused": True,
        "base_runtime_state_inherited": False,
        "same_record_prefill_companion_coordinates": (
            [
                f"6:{record_id}:0",
                f"6:{record_id}:2",
            ]
            if record_id <= 1358
            else [
                f"6:{record_id}:1",
                f"6:{record_id}:3",
            ]
        ),
        "complete_record_assembly_reviewed": True,
        "target_force_possessive_target_base_relation_preserved":
        True,
        "single_target_dash_rule_applicable": False,
        "protected_whitespace_preserved": True,
        "automatic_space_assumed": False,
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
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification":
                "runtime_fragment_pending",
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
                "same_record_prefill_companion_reviewed": True,
                "historical_term_review": True,
                "speaker_register_review": True,
                "protected_signature_review": True,
                "target_force_possessive_target_base_relation_preserved":
                True,
                "single_target_dash_rule_applicable": False,
                "base_semantic_donor_coordinate":
                BASE_COORDINATE_MAPPING[coordinate],
                "base_semantic_translation_reused": True,
                "base_literal_exact_reuse": True,
                "base_runtime_state_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
                    records_by_label,
                    record_id,
                ),
            }
        )
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
        len(rows) != 28
        or len(validated) != 28
        or counts != Counter({"runtime_fragment_pending": 28})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["protected_signature_review"] is not True
            or row[
                "target_force_possessive_target_base_relation_preserved"
            ]
            is not True
            or row["single_target_dash_rule_applicable"] is not False
            or row["base_literal_exact_reuse"] is not True
            or row["base_runtime_state_inherited"] is not False
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
                "segment": "pk_msggame_B021_S1080",
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
                "prefill_excluded_count": 39,
                "same_record_prefill_companion_count": 40,
                "residual_count": len(rows),
                "context_record_count": len(CONTEXT_RECORD_IDS),
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "completed_base_exact_records_reused": True,
                "multi_token_records_reviewed": 20,
                "possessive_relations_preserved": True,
                "single_target_dash_rule_applied": False,
                "base_runtime_state_inherited": False,
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
