#!/usr/bin/env python3
"""Build source-redacted PK B023 segment 1088 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B023_S1088.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B023_S1087.private.v1.jsonl",
)

SEGMENT = 1088
QUEUE_BATCH_ID = "pk_msggame-B023"
QUEUE_START = 131
QUEUE_STOP = 196
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
        "pc_dialogue_full_retranslation_v0150_pk_s1088_common",
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

RELATION_RECORD_IDS = (1643, 1644)
DEPARTMENT_RECORD_IDS = tuple(range(1670, 1676))
TARGET_RECORD_IDS = (*RELATION_RECORD_IDS, *DEPARTMENT_RECORD_IDS)
TARGET_COORDINATES = (
    "6:1643:0",
    "6:1644:0",
    *(
        f"6:{record_id}:{literal_id}"
        for record_id in DEPARTMENT_RECORD_IDS
        for literal_id in (2, 3, 4, 5)
    ),
)
TRANSLATIONS = {
    "6:1643:0": "와(과)",
    "6:1644:0": "와(과)",
    **{
        f"6:{record_id}:{literal_id}": (
            ", 상공"
            if literal_id == 2
            else (
                ", 토목"
                if literal_id == 3
                else (
                    ", 문화" if literal_id == 4 else ", 치안"
                )
            )
        )
        for record_id in DEPARTMENT_RECORD_IDS
        for literal_id in (2, 3, 4, 5)
    },
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (1642, 1645, 1669)
PREFILL_COORDINATES = (
    "6:1643:1",
    "6:1644:1",
    *(f"6:{record_id}:0" for record_id in range(1645, 1670)),
    *(
        f"6:{record_id}:{literal_id}"
        for record_id in DEPARTMENT_RECORD_IDS
        for literal_id in (0, 1)
    ),
)
BASE_RECORD_MAPPING = {
    1643: 1637,
    1644: 1638,
    **{
        record_id: record_id - 6
        for record_id in DEPARTMENT_RECORD_IDS
    },
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[coordinate_key(coordinate)[1]]}:"
        f"{coordinate_key(coordinate)[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
EXPECTED_GAPS_BY_RECORD = {
    1643: ("014322000000", "014332000000", "050505"),
    1644: ("014322000000", "014332000000", "050505"),
    **{
        record_id: (
            "",
            "0232",
            "0232",
            "0233",
            "0234",
            "0235",
            "0236050505",
        )
        for record_id in DEPARTMENT_RECORD_IDS
    },
}
EXPECTED_OWNERS = {
    1643: ("segment", "prefill"),
    1644: ("segment", "prefill"),
    **{
        record_id: (
            "prefill",
            "prefill",
            "segment",
            "segment",
            "segment",
            "segment",
        )
        for record_id in DEPARTMENT_RECORD_IDS
    },
}

EXPECTED_TARGET_COORDINATE_SHA256 = "C7FDF83F5FB0373AD8FD4A84BCE508454BCE0ACD9D208EFE99A58CB86F5F9941"
EXPECTED_QUEUE_SLICE_SHA256 = "50B15303CEB35F164EC976BE96BAF3113D900BC6FB5D9714DC7F9C4F9D0A4C5E"
EXPECTED_PREFILLED_COORDINATE_SHA256 = "3E968F1B2AC380E142559938B40AB391BD4F126683EB184BAE592A4D2BB7CF9A"
EXPECTED_SOURCE_TARGET_SHA256 = "92B48DECEEFB7290A20A3FD30BDBB58AC9A828CF751D3788774035E04C756DCD"
EXPECTED_CURRENT_TARGET_SHA256 = "F5205EAA646A9CA164742BC7C66C0DE2A0FB13A181A384FA89F250029A15A388"
EXPECTED_CONTEXT_CORPUS_SHA256 = "AA03A83BF7EF988A8894C606F6AFFDDE6DEB6327F163F648D5F1749F95703FE4"
EXPECTED_GAP_CONTRACT_SHA256 = "CE05540CEEF2EC8984C31D3FD90774E101B714B38567CD4B3F61A670BECAFC7D"
EXPECTED_BOUNDARY_SHA256 = "CCADD17E63D2C09764F74A68C712B4634B9AA4C6987FDC3891F975D500F37913"
EXPECTED_DYNAMIC_RECORD_SHA256 = "B1C1B14F947F8D853DFC2EAEC579637A77050C5A66931F2F8253573AAF9CFEED"
EXPECTED_BASE_CONTEXT_SHA256 = "E8EAABA5F5F9653265EBE6F40AF7443EAF4E277E24F075F45ADD9397306F4209"
EXPECTED_PREFILL_CONTEXT_SHA256 = "D31290DCB3174C2A87B058C25331308522138FD2B2DD429714F13269726E76EE"
EXPECTED_ASSEMBLY_POLICY_SHA256 = "E69C66C66340B81A31828F4DFCBC92315585E18D5F32DA05573225FDEC040781"
EXPECTED_TRANSLATION_POLICY_SHA256 = "756846390473B2AB7A90C371635A1BC206AE1A82DDCE24CE81D94122F6BB377F"
EXPECTED_CANDIDATE_SHA256 = "D86E1BA464EF420DF830D95B04658097B7F6A6561087FF172B62EAEEECBD816B"
EXPECTED_CHANGED_LITERAL_COUNT = 8

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "translations pin semantics, terminology, punctuation and register "
    "while Base runtime state is not inherited; exact-reuse prefill and "
    "every available predecessor are validated and excluded; the complete "
    "two-direct-call relationship records and six-literal conditional "
    "department reports are reviewed with every literal and opcode gap; "
    "source, current and Base gaps are exact for all targets; political "
    "marriage, two-house alliance, farming, industry, civil engineering, "
    "culture and public-order terminology, six speaker registers, outer "
    "whitespace, adjacent records, protected signatures, line counts, "
    "reverse overlay, two-run reproduction, tamper rejection and read-only "
    "inputs are guarded; every target remains PK runtime pending"
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
    if (
        len(queue_slice) != 65
        or queue_slice[0] != "6:1643:0"
        or queue_slice[-1] != "6:1675:5"
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
    if len(prefilled) != 39 or prefilled != PREFILL_COORDINATES:
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
    if residual != TARGET_COORDINATES or len(residual) != 26:
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
        for record_id in range(1642, 1676)
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
            or current != source
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
        base_record_id = BASE_RECORD_MAPPING[record_id]
        translations: list[str] = []
        owners: list[str] = []
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source_records,
            (BLOCK_ID, base_record_id),
        )
        expected_translations: list[str] = []
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = (
                f"6:{base_record_id}:{literal_id}"
            )
            expected_translations.append(
                adapt_outer_whitespace(
                    str(base_rows[base_coordinate]["translation"]),
                    current_text,
                )
            )
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
        base_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                base_source_records[
                    (BLOCK_ID, base_record_id)
                ]
            )
        )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(expected_translations),
                literal_texts(
                    records_by_label["jp"],
                    (BLOCK_ID, record_id),
                ),
                base_literals,
                source_gaps,
                base_gaps,
            )
        )
        joined = "\u241f".join(translations)
        if (
            tuple(owners) != EXPECTED_OWNERS[record_id]
            or tuple(translations)
            != tuple(expected_translations)
            or literal_texts(
                records_by_label["jp"],
                (BLOCK_ID, record_id),
            )
            != base_literals
            or source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
            or base_gaps != source_gaps
            or (
                record_id == 1643
                and any(
                    term not in joined
                    for term in ("정략", "행복", "두 가문")
                )
            )
            or (
                record_id == 1644
                and any(
                    term not in joined
                    for term in ("결연", "혼인", "동맹")
                )
            )
            or (
                record_id in DEPARTMENT_RECORD_IDS
                and any(
                    term not in joined
                    for term in (
                        "권농",
                        "상공",
                        "토목",
                        "문화",
                        "치안",
                    )
                )
            )
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
        or len(TARGET_COORDINATES) != 26
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
    if (
        TRANSLATIONS["6:1643:0"] != "와(과)"
        or TRANSLATIONS["6:1644:0"] != "와(과)"
        or any(
            TRANSLATIONS[f"6:{record_id}:2"] != ", 상공"
            or TRANSLATIONS[f"6:{record_id}:3"] != ", 토목"
            or TRANSLATIONS[f"6:{record_id}:4"] != ", 문화"
            or TRANSLATIONS[f"6:{record_id}:5"] != ", 치안"
            for record_id in DEPARTMENT_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology policy drifted"
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
    relation = record_id in RELATION_RECORD_IDS
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
        "runtime_order": (
            (
                "direct_call_34",
                "relationship_particle",
                "direct_call_50",
                "relationship_report",
            )
            if relation
            else (
                "financial_report",
                "conditional_value_32",
                "farming",
                "conditional_industry_32",
                "conditional_civil_engineering_33",
                "conditional_culture_34",
                "conditional_public_order_35",
                "conditional_terminator_36",
            )
        ),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companions_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "base_source_opcode_gap_equal": True,
        "relationship_particle_preserved": relation,
        "conditional_department_order_preserved": not relation,
        "historical_civil_engineering_term_preserved":
        not relation,
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
                "record_variant": (
                    "political_relationship"
                    if record_id in RELATION_RECORD_IDS
                    else "financial_department_decline"
                ),
                "speaker_register_variant": (
                    f"variant_{record_id - 1669}"
                    if record_id in DEPARTMENT_RECORD_IDS
                    else "formal_relationship_report"
                ),
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
        len(rows) != 26
        or len(validated) != 26
        or counts != Counter({"runtime_fragment_pending": 26})
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
                "segment": "pk_msggame_B023_S1088",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 39,
                "residual_count": 26,
                "base_semantic_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "record_variant_counts": {
                    "political_relationship": 2,
                    "financial_department_decline": 6,
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
                "direct_calls_and_inline_tokens_guarded": True,
                "source_current_opcode_gap_divergence_records": [],
                "base_source_opcode_gaps_exact": True,
                "relationship_particles_preserved": True,
                "conditional_department_order_preserved": True,
                "six_speaker_registers_reviewed": True,
                "historical_terms_reviewed": [
                    "political_marriage",
                    "two_house_alliance",
                    "farming",
                    "industry",
                    "civil_engineering",
                    "culture",
                    "public_order",
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
