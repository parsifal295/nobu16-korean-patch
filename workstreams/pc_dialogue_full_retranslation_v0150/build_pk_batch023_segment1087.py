#!/usr/bin/env python3
"""Build source-redacted PK B023 segment 1087 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch014_segment1063.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B023_S1087.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B023_S1086.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B023_S1088.private.v1.jsonl",
)

SEGMENT = 1087
QUEUE_BATCH_ID = "pk_msggame-B023"
QUEUE_START = 66
QUEUE_STOP = 131
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
        "pc_dialogue_full_retranslation_v0150_pk_s1087_common",
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
    "6:1616:1",
    "6:1618:0",
    "6:1630:0",
    "6:1633:0",
    "6:1633:1",
    "6:1634:0",
    "6:1635:0",
    "6:1636:0",
    "6:1637:0",
    "6:1638:1",
    "6:1639:0",
    "6:1640:0",
    "6:1641:0",
    "6:1642:1",
)
TRANSLATIONS = {
    "6:1616:1":
    " 측과 운명을 함께할 각오는 하되,\n우리도 스스로 서야 합니다",
    "6:1618:0": "에게",
    "6:1630:0": "께서는",
    "6:1633:0": "이야,",
    "6:1633:1": "와(과)",
    "6:1634:0": "와(과)",
    "6:1635:0": "와(과)",
    "6:1636:0": "와(과)",
    "6:1637:0": " 및 ",
    "6:1638:1": "와(과)\n",
    "6:1639:0": "와(과)",
    "6:1640:0": "와(과)",
    "6:1641:0": " 및 ",
    "6:1642:1": "와(과)",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    1616,
    1618,
    1630,
    *range(1633, 1643),
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (
    1615,
    1617,
    1619,
    1629,
    1631,
    1632,
    1643,
)
PREFILL_COMPANION_COORDINATES = (
    "6:1616:0",
    "6:1618:1",
    "6:1630:1",
    "6:1633:2",
    "6:1634:1",
    "6:1635:1",
    "6:1636:1",
    "6:1637:1",
    "6:1638:0",
    "6:1638:2",
    "6:1639:1",
    "6:1640:1",
    "6:1641:1",
    "6:1642:0",
    "6:1642:2",
)
BASE_CONTEXT_REFERENCES = {
    "6:1616:1": "6:1610:1",
    "6:1618:0": "6:1612:0",
    "6:1630:0": "6:1624:0",
    "6:1633:0": "6:1627:0",
    "6:1633:1": "6:1627:1",
    "6:1634:0": "6:1628:0",
    "6:1635:0": "6:1629:0",
    "6:1636:0": "6:1630:0",
    "6:1637:0": "6:1631:0",
    "6:1638:1": "6:1632:1",
    "6:1639:0": "6:1633:0",
    "6:1640:0": "6:1634:0",
    "6:1641:0": "6:1635:0",
    "6:1642:1": "6:1636:1",
}
EXPECTED_GAPS_BY_RECORD = {
    1616: ("", "025032", "050505"),
    1618: ("025032", "014308000000", "050505"),
    1630: ("014308000000", "025032", "050505"),
    1633: ("", "014322000000", "014332000000", "050505"),
    1634: ("014322000000", "014332000000", "050505"),
    1635: ("014322000000", "014332000000", "050505"),
    1636: ("014322000000", "014332000000", "050505"),
    1637: ("014322000000", "014332000000", "050505"),
    1638: ("", "014322000000", "014332000000", "050505"),
    1639: ("014322000000", "014332000000", "050505"),
    1640: ("014322000000", "014332000000", "050505"),
    1641: ("014322000000", "014332000000", "050505"),
    1642: ("", "014322000000", "014332000000", "050505"),
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "10471EC6A4085B37CA06CDC767269B5A7AEDA7AA87556F35A822C523E6A95BC7"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "9B0AF4ABF986AE946F26B50CFCBFCF10D6C483A49AE0DC703E7AE8CCE58D8F00"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "C7CCEAB0CC86256C9FAA1D4C2015A0A8A796A7EB6601B1F8D3C4B1660866A1E3"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "9DCD40917F1B1A81951078419ACCDF895018850B134D3F4B70831A9AB1256689"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "41A9B93F4F01CF1633BDF6DA8272A9FA0740E0BDBCEC99844FA14D6FD8B6D0E4"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "2E57B3E8D4BD22F7878B12CAA50BD9994818D5075FF14C636054FBDCDD835DA5"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "A4D6E69A8810010DFB0BA284F0EFF38BEAEC36195078C2FB2B4870FC293B9B71"
)
EXPECTED_BOUNDARY_SHA256 = (
    "4DB1238AFCC07C3D0D82EDEF3FE55EAB33BA80DEB22AB8014480CFBBD65D3D44"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "427920063EFCAA2E37C93F36732F50FEFC2B493966ECC7DD8A01F715B82402D2"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "33CCCC98E1195C829C53121BEECA63989446EC508E632C2CEA47C5D5FBD1F72B"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "9C0A1CA34F1E61B33E6C876FA2A069FEC81803C3FF1D94E849719035C2A05E67"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "C1A933F73EB8393D0EF82798A1D6C710AFB580DCE0217C45DD8815E0F0E19028"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "DCC865A91AE7C52D298714E7F281046BAD32165172C6625A95FAD3735DA915D1"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "9A4AEB9F165661C25BACAC6761FDF4C4973C4E1EE5638858424B5EA583C10BB0"
)
EXPECTED_CANDIDATE_SHA256 = (
    "D62CAD95530202A9DC6330EC07A563D227640F3FDD9C2C8B3BE20D06ADE2F34D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "translations pin semantics, historical terminology and speaker "
    "register; three Base particles are contextually adapted only where "
    "protected PK leading/trailing whitespace would otherwise expose an "
    "unnatural particle boundary; exact-reuse prefill and every available "
    "predecessor are validated and excluded; standard inline names, mixed "
    "inline-name/direct-call order and dual direct-call marriage records "
    "are distinguished; all literals, direct-call operands, inline tokens, "
    "possessives, conjunctions, adjacent records, protected signatures, "
    "line counts, bytecode gaps, reverse overlay, two-run reproduction, "
    "tamper rejection and read-only inputs are guarded; Base runtime state "
    "is not inherited and every PK target remains runtime pending"
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
    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 51:
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
        if any(
            b"\x01\x43" in value or b"\x02" in value
            for value in gap_bytes(
                records_by_label["jp"][(BLOCK_ID, record_id)]
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
    if (
        actual_dynamic != DYNAMIC_RECORD_IDS
        or any(
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current != source
            for record_id, source, current in gaps
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def assert_base_prefill_and_assembly(
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
    base_evidence: list[tuple[Any, ...]] = []
    for coordinate, base_coordinate in (
        BASE_CONTEXT_REFERENCES.items()
    ):
        pk_key = coordinate_key(coordinate)
        base_key = coordinate_key(base_coordinate)
        base_row = base_rows[base_coordinate]
        pk_source = literal_texts(
            records_by_label["jp"],
            pk_key[:2],
        )[pk_key[2]]
        base_source = literal_texts(
            base_source_records,
            base_key[:2],
        )[base_key[2]]
        expected_translation = str(base_row["translation"])
        if coordinate in {
            "6:1616:1",
            "6:1637:0",
            "6:1641:0",
        }:
            expected_translation = TRANSLATIONS[coordinate]
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                pk_source,
                base_source,
                base_row.get("translation"),
                expected_translation,
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
        for coordinate in PREFILL_COMPANION_COORDINATES
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
        joined = "\u241f".join(translations)
        if (
            record_id == 1616
            and not all(
                term in joined
                for term in ("종속", "운명", "스스로")
            )
        ) or (
            record_id == 1618
            and not all(
                term in joined
                for term in ("머리", "힘", "정진")
            )
        ) or (
            record_id == 1630
            and not all(
                term in joined
                for term in ("종속", "가문", "최선")
            )
        ) or (
            1633 <= record_id <= 1641
            and not any(
                term in joined
                for term in ("혼례", "결연", "혼인", "혼약", "정략")
            )
        ) or (
            record_id == 1642
            and not all(
                term in joined for term in ("경사", "축하")
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly semantics drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def runtime_category(record_id: int) -> str:
    if record_id == 1616:
        return "inline_name_vassalage"
    if record_id in (1618, 1630):
        return "mixed_inline_and_direct_call"
    return "dual_direct_call_marriage"


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
    guarded_digest(
        "runtime category",
        tuple(
            (record_id, runtime_category(record_id))
            for record_id in TARGET_RECORD_IDS
        ),
        EXPECTED_RUNTIME_CATEGORY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or len(TARGET_COORDINATES) != 14
        or TRANSLATIONS["6:1637:0"] != " 및 "
        or TRANSLATIONS["6:1641:0"] != " 및 "
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
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


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def control_evidence(
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
    direct_operands = tuple(
        int.from_bytes(value[2:6], "little")
        for value in source_gaps
        if value.startswith(b"\x01\x43")
    )
    inline_tokens = tuple(
        value[1:].hex().upper()
        for value in source_gaps
        if value.startswith(b"\x02")
    )
    if (
        source_gap_hex != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gap_hex != source_gap_hex
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic controls drifted: "
            f"{record_id}"
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
        "direct_call_operands": direct_operands,
        "inline_runtime_tokens": inline_tokens,
        "runtime_category": runtime_category(record_id),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companions_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "historical_relationship_terms_reviewed": True,
        "possessive_and_conjunction_policy_reviewed": True,
        "outer_whitespace_preserved": True,
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
    assert_base_prefill_and_assembly(records_by_label)
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
                "historical_term_review": True,
                "speaker_register_review": True,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_record_literals_reviewed": True,
                "prefill_companions_reviewed": True,
                "runtime_category": runtime_category(record_id),
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_translation_contextually_adapted":
                coordinate
                in {
                    "6:1616:1",
                    "6:1637:0",
                    "6:1641:0",
                },
                "base_runtime_state_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                control_evidence(
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
    category_counts = Counter(
        str(row["runtime_category"]) for row in rows
    )
    if (
        len(rows) != 14
        or len(validated) != 14
        or counts != Counter({"runtime_fragment_pending": 14})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            or row["base_runtime_state_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
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
                "segment": "pk_msggame_B023_S1087",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "runtime_category_counts": dict(category_counts),
                "exact_reuse_prefill_count": 51,
                "base_semantic_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "full_record_count": len(TARGET_RECORD_IDS),
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
                "contextual_particle_adaptations_guarded": True,
                "prefill_companions_guarded": True,
                "complete_record_assembly_guarded": True,
                "direct_calls_and_inline_tokens_guarded": True,
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
