#!/usr/bin/env python3
"""Build source-redacted PK B022 segment 1085 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B022_S1085.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B021_S1080.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B021_S1081.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B021_S1082.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B022_S1083.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B022_S1084.private.v1.jsonl",
)

SEGMENT = 1085
QUEUE_BATCH_ID = "pk_msggame-B022"
QUEUE_START = 134
QUEUE_STOP = 200
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
        "pc_dialogue_full_retranslation_v0150_pk_s1085_common",
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

TARGET_RECORD_IDS = (
    1527,
    1528,
    1529,
    1543,
    1545,
    1558,
    1560,
)
TARGET_COORDINATES = (
    "6:1527:0",
    "6:1527:1",
    "6:1528:0",
    "6:1528:1",
    "6:1529:0",
    "6:1543:0",
    "6:1543:1",
    "6:1545:0",
    "6:1545:1",
    "6:1558:0",
    "6:1558:1",
    "6:1560:0",
    "6:1560:1",
)
TRANSLATIONS = {
    "6:1527:0": "의 신용이 ",
    "6:1527:1": "에 도달",
    "6:1528:0": "와(과)",
    "6:1528:1": "의 동맹이 종료",
    "6:1529:0": "와(과)",
    "6:1543:0": "우리 가문이",
    "6:1543:1": (
        " 와(과) 단교한 이상\n"
        "여러 나라도 우리를 가만두지 않을 것입니다.\n"
        "만전을 기해 대비해야 합니다"
    ),
    "6:1545:0": "역시",
    "6:1545:1": "님,",
    "6:1558:0": "우리 가문이",
    "6:1558:1": (
        " 와(과) 단교한 이상\n"
        "여러 나라도 우리를 가만두지 않을 터…\n"
        "만전을 기해 대비해야 한다"
    ),
    "6:1560:0": "역시",
    "6:1560:1": "님,",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (
    1526,
    1530,
    1542,
    1544,
    1546,
    1557,
    1559,
    1561,
    1566,
)
PREFILL_COORDINATES = (
    "6:1526:0",
    "6:1526:1",
    "6:1526:2",
    "6:1529:1",
    "6:1530:0",
    "6:1531:0",
    "6:1532:0",
    "6:1533:0",
    "6:1534:0",
    "6:1535:0",
    "6:1535:1",
    "6:1536:0",
    "6:1536:1",
    "6:1537:0",
    "6:1538:0",
    "6:1538:1",
    "6:1539:0",
    "6:1539:1",
    "6:1540:0",
    "6:1540:1",
    "6:1541:0",
    "6:1542:0",
    "6:1544:0",
    "6:1544:1",
    "6:1545:2",
    "6:1546:0",
    "6:1546:1",
    "6:1547:0",
    "6:1547:1",
    "6:1548:0",
    "6:1548:1",
    "6:1549:0",
    "6:1549:1",
    "6:1550:0",
    "6:1551:0",
    "6:1552:0",
    "6:1552:1",
    "6:1553:0",
    "6:1554:0",
    "6:1554:1",
    "6:1555:0",
    "6:1556:0",
    "6:1557:0",
    "6:1559:0",
    "6:1560:2",
    "6:1561:0",
    "6:1562:0",
    "6:1562:1",
    "6:1563:0",
    "6:1564:0",
    "6:1564:1",
    "6:1565:0",
    "6:1566:0",
)
BASE_CONTEXT_REFERENCES = {
    "6:1527:0": "6:1521:0",
    "6:1527:1": "6:1521:1",
    "6:1528:0": "6:1522:0",
    "6:1528:1": "6:1522:1",
    "6:1529:0": "6:1523:0",
    "6:1543:0": "6:1537:0",
    "6:1543:1": "6:1537:1",
    "6:1545:0": "6:1539:0",
    "6:1545:1": "6:1539:1",
    "6:1558:0": "6:1552:0",
    "6:1558:1": "6:1552:1",
    "6:1560:0": "6:1554:0",
    "6:1560:1": "6:1554:1",
}
EXPECTED_GAPS_BY_RECORD = {
    1527: ("025032", "023C", "050505"),
    1528: ("025032", "025132", "050505"),
    1529: ("025032", "025132", "050505"),
    1543: ("", "025032", "050505"),
    1545: ("", "014308000000", "025032", "050505"),
    1558: ("", "025032", "014336040000050505"),
    1560: ("", "014308000000", "025032", "050505"),
}
EXPECTED_CURRENT_GAPS_BY_RECORD = {
    **EXPECTED_GAPS_BY_RECORD,
    1558: ("", "025032", "050505"),
}
EXPECTED_ASSEMBLIES = {
    1527: ("의 신용이 ", "에 도달"),
    1528: ("와(과)", "의 동맹이 종료"),
    1529: ("와(과)", "의 정전이 종료"),
    1543: (
        "우리 가문이",
        " 와(과) 단교한 이상\n"
        "여러 나라도 우리를 가만두지 않을 것입니다.\n"
        "만전을 기해 대비해야 합니다",
    ),
    1545: (
        "역시",
        "님,",
        "와(과) 단교하여\n"
        "악평이 높아지더라도 뜻한 길을 가시다니,\n"
        "이래야 우리 가문의 주군이시지요",
    ),
    1558: (
        "우리 가문이",
        " 와(과) 단교한 이상\n"
        "여러 나라도 우리를 가만두지 않을 터…\n"
        "만전을 기해 대비해야 한다",
    ),
    1560: (
        "역시",
        "님,",
        "와(과) 단교하여\n"
        "악평이 높아지더라도 뜻한 길을 가시다니…\n"
        "이래야 우리 가문의 주군이시지요",
    ),
}
EXPECTED_OWNERS = {
    1527: ("segment", "segment"),
    1528: ("segment", "segment"),
    1529: ("segment", "prefill"),
    1543: ("segment", "segment"),
    1545: ("segment", "segment", "prefill"),
    1558: ("segment", "segment"),
    1560: ("segment", "segment", "prefill"),
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "8321D2630B51085BB6D51E34ECCC35367C8582D66B23704CF2B18A7052CFD925"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "C1FC4AD3F0D6B7C6A8E8BF1ADE4D246982937AF96BFD2E6E637357CD65848709"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "4C735E842E35EE5A19B45A3E9A49BFBACA5C4B38DE0988663DF2D80CAF9BF456"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "41E44FE92686DD0E9286B65DCD0BFA425CEE9D5D18093F187457E32EEF7C0CC4"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "773618B0CB273567F7C1F41C880316F59520C04765C37BEA3307F5C7BEC6EBA8"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "FC68B2492E3EE49334E46FC3D72335ACB7E53346E4A175FC4A21591CBD2123B9"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "FB36237D5EAAA83006559DFCD1370430790B2EA4F8CB313F133031D8000787F9"
)
EXPECTED_BOUNDARY_SHA256 = (
    "E4165AA6AB45C2CF4FAB153EB067A46377C76772FD17597103F9C4F0E42BDD44"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "7AB080E04153AD096B40FFD80C91473B9CB48122E2135E9FD63CB4D35E4132C5"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "3B64ED6430744DAAE1FE72B293E84361A1B8F786F0FBA2A869B6E653C3D66E4D"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "2BCE4AED77D8164AFA2FF6487A8EC022ADA50ACF0AD88E799BD8DACE6E479527"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "DEBDA3E7994C942F60349D4A9660A79C98346FED21985C884CEFFB40CB577D84"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "D1010BFC49D6DA2001760AC62B5D1306231F5380C38C50688518C3FFF7AAEA26"
)
EXPECTED_CANDIDATE_SHA256 = (
    "75025F79844608828864A9B1943B9C6FB8EF301F3E32B02F0ECD5372CFA7F487"
)
EXPECTED_CHANGED_LITERAL_COUNT = 10

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "translations pin semantics, terminology, punctuation and register "
    "while Base runtime state is not inherited; exact-reuse prefill and "
    "every available predecessor are validated and excluded; complete "
    "trust-threshold, force-pair alliance and truce, house-severance "
    "preparation, and lord-praise assemblies are reviewed with every "
    "inline token and direct call; force particles, honorific name suffix, "
    "our-house, severance, preparedness, ill-repute and lord terminology, "
    "formal and plain endings, outer whitespace, adjacent records, "
    "protected signatures, line counts, the record 1558 source/current "
    "direct-call divergence, bytecode gaps, reverse overlay, "
    "two-run reproduction, tamper rejection and read-only inputs are "
    "guarded; every target remains PK runtime pending"
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
        len(queue_rows) != 117
        or len(visible) != 200
        or visible[0] != "6:1450:0"
        or visible[-1] != "6:1566:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B022 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:1526:0"
        or queue_slice[-1] != "6:1566:0"
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
    if len(prefilled) != 53 or prefilled != PREFILL_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice drifted"
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
    if residual != TARGET_COORDINATES or len(residual) != 13:
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
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in range(1526, 1567)
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
            or current
            != EXPECTED_CURRENT_GAPS_BY_RECORD[record_id]
            for record_id, source, current in gaps
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
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
    base_evidence: list[tuple[Any, ...]] = []
    for coordinate in TARGET_COORDINATES:
        base_coordinate = BASE_CONTEXT_REFERENCES[coordinate]
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
        current_text = literal_texts(
            records_by_label["current"],
            pk_key[:2],
        )[pk_key[2]]
        adapted = adapt_outer_whitespace(
            str(base_row["translation"]),
            current_text,
        )
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                pk_source,
                base_source,
                base_row.get("translation"),
                adapted,
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
            )
        )
        if (
            pk_source != base_source
            or TRANSLATIONS[coordinate] != adapted
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
        for coordinate in PREFILL_COORDINATES
    )
    guarded_digest(
        "prefill context",
        prefill_evidence,
        EXPECTED_PREFILL_CONTEXT_SHA256,
    )
    if any(
        semantic != "approved"
        or runtime
        not in ("pending", "not_required")
        for _, _, semantic, runtime, _, _ in prefill_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill context drifted"
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
        source_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                source_gaps,
            )
        )
        if (
            tuple(owners) != EXPECTED_OWNERS[record_id]
            or tuple(translations)
            != EXPECTED_ASSEMBLIES[record_id]
            or source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly drifted: {record_id}"
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
        or len(TARGET_COORDINATES) != 13
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
    if (
        EXPECTED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} changed policy drifted: {changed}"
        )
    joined = "\u241f".join(
        text
        for assembly in EXPECTED_ASSEMBLIES.values()
        for text in assembly
    )
    if (
        TRANSLATIONS["6:1527:0"] != "의 신용이 "
        or TRANSLATIONS["6:1528:0"] != "와(과)"
        or TRANSLATIONS["6:1529:0"] != "와(과)"
        or TRANSLATIONS["6:1545:1"] != "님,"
        or TRANSLATIONS["6:1560:1"] != "님,"
        or any(
            term not in joined
            for term in (
                "우리 가문",
                "단교",
                "만전",
                "악평",
                "주군",
            )
        )
        or not TRANSLATIONS["6:1543:1"].endswith("합니다")
        or not TRANSLATIONS["6:1558:1"].endswith("한다")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology or register drifted"
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
        or current_gap_hex
        != EXPECTED_CURRENT_GAPS_BY_RECORD[record_id]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic controls drifted: "
            f"{record_id}"
        )
    variant = (
        "trust_threshold"
        if record_id == 1527
        else (
            "force_pair_relation_end"
            if record_id in (1528, 1529)
            else (
                "house_severance_preparation"
                if record_id in (1543, 1558)
                else "lord_praise_after_severance"
            )
        )
    )
    current_direct_operands = tuple(
        int.from_bytes(value[2:6], "little")
        for value in current_gaps
        if value.startswith(b"\x01\x43")
    )
    evidence = {
        "source_record_gap_sha256": canonical_sha256(
            source_gap_hex
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gap_hex
        ),
        "source_runtime_gap_hex": source_gap_hex,
        "current_runtime_gap_hex": current_gap_hex,
        "source_current_runtime_gap_equal":
        current_gap_hex == source_gap_hex,
        "direct_call_operands": direct_operands,
        "current_direct_call_operands": current_direct_operands,
        "inline_runtime_tokens": inline_tokens,
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companions_reviewed": (
            record_id in (1529, 1545, 1560)
        ),
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "structure_variant": variant,
        "particle_boundary_preserved": (
            record_id != 1527
        ),
        "honorific_name_suffix_preserved": (
            record_id in (1545, 1560)
        ),
        "outer_whitespace_preserved": True,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }
    if record_id == 1558:
        evidence["source_only_direct_call_operands"] = (1078,)
        evidence["runtime_gap_divergence_followup_required"] = True
    else:
        evidence["runtime_gap_divergence_followup_required"] = False
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
    assert_base_prefill_and_assembly_context(records_by_label)
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
        variant = (
            "trust_threshold"
            if record_id == 1527
            else (
                "alliance_end"
                if record_id == 1528
                else (
                    "truce_end"
                    if record_id == 1529
                    else (
                        "house_severance_preparation"
                        if record_id in (1543, 1558)
                        else "lord_praise_after_severance"
                    )
                )
            )
        )
        companions = tuple(
            f"6:{record_id}:{companion_id}"
            for companion_id in range(
                len(
                    literal_texts(
                        records_by_label["current"],
                        (block_id, record_id),
                    )
                )
            )
            if f"6:{record_id}:{companion_id}"
            in PREFILL_COORDINATES
        )
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
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_record_literals_reviewed": True,
                "record_variant": variant,
                "prefill_companion_coordinates": companions,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
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
    if DISCOVERED_PINS:
        print(
            json.dumps(
                {
                    **DISCOVERED_PINS,
                    "candidate": candidate_sha256,
                    "changed literal count": changed,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2

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
        len(rows) != 13
        or len(validated) != 13
        or counts != Counter({"runtime_fragment_pending": 13})
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
                "segment": "pk_msggame_B022_S1085",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 53,
                "residual_count": 13,
                "base_semantic_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "record_variant_counts": {
                    "trust_threshold": 1,
                    "alliance_end": 1,
                    "truce_end": 1,
                    "house_severance_preparation": 2,
                    "lord_praise_after_severance": 2,
                },
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
                "prefill_companions_guarded": True,
                "complete_record_assembly_guarded": True,
                "inline_tokens_and_direct_calls_guarded": True,
                "source_current_runtime_gap_divergence_records": [
                    "6:1558",
                ],
                "source_only_direct_call_operands": {
                    "6:1558": [1078],
                },
                "particle_boundaries_preserved": True,
                "honorific_name_suffix_preserved": True,
                "outer_spacing_preserved": True,
                "formal_and_plain_registers_reviewed": True,
                "historical_terms_reviewed": [
                    "our_house",
                    "severance",
                    "preparedness",
                    "ill_repute",
                    "lord",
                ],
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
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
