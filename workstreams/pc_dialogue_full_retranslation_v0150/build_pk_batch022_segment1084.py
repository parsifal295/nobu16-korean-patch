#!/usr/bin/env python3
"""Build source-redacted PK B022 segment 1084 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B022_S1084.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B022_S1085.private.v1.jsonl",
)

SEGMENT = 1084
QUEUE_BATCH_ID = "pk_msggame-B022"
QUEUE_START = 67
QUEUE_STOP = 134
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
        "pc_dialogue_full_retranslation_v0150_pk_s1084_common",
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
    "6:1485:0",
    "6:1485:1",
    "6:1486:0",
    "6:1487:0",
    "6:1488:0",
    "6:1489:0",
    "6:1490:0",
    "6:1491:0",
    "6:1491:1",
    "6:1492:0",
    "6:1493:0",
    "6:1493:1",
    "6:1494:0",
    "6:1514:0",
    "6:1518:1",
    "6:1520:1",
    "6:1521:1",
    "6:1522:1",
    "6:1523:1",
)
TRANSLATIONS = {
    coordinate: (
        "공성 중이므로—"
        if coordinate == "6:1514:0"
        else (
            "으로(로) 변경"
            if coordinate in ("6:1518:1", "6:1520:1")
            else (
                "와(과)의 친선을 중지"
                if coordinate_key(coordinate)[1] >= 1521
                else (
                    " 양측이\n서로 "
                    if coordinate == "6:1491:1"
                    else (
                        "이(가)"
                        if coordinate_key(coordinate)[2] == 1
                        else "와(과)"
                    )
                )
            )
        )
    )
    for coordinate in TARGET_COORDINATES
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    *range(1485, 1495),
    1514,
    1518,
    1520,
    1521,
    1522,
    1523,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (
    1484,
    1495,
    1513,
    1515,
    1517,
    1519,
    1524,
)
PREFILL_COMPANION_COORDINATES = (
    "6:1485:2",
    "6:1486:1",
    "6:1486:2",
    "6:1487:1",
    "6:1488:1",
    "6:1489:1",
    "6:1490:1",
    "6:1491:2",
    "6:1492:1",
    "6:1492:2",
    "6:1493:2",
    "6:1494:1",
    "6:1494:2",
    "6:1514:1",
    "6:1518:0",
    "6:1520:0",
    "6:1521:0",
    "6:1522:0",
    "6:1523:0",
)
BASE_CONTEXT_REFERENCES = {
    "6:1485:0": "6:1477:0",
    "6:1485:1": "6:1477:1",
    "6:1486:0": "6:1478:0",
    "6:1487:0": "6:1481:0",
    "6:1488:0": "6:1481:0",
    "6:1489:0": "6:1483:0",
    "6:1490:0": "6:1483:0",
    "6:1491:0": "6:1485:0",
    "6:1491:1": "6:1485:1",
    "6:1492:0": "6:1486:0",
    "6:1493:0": "6:1485:0",
    "6:1493:1": "6:1485:1",
    "6:1494:0": "6:1486:0",
    "6:1518:1": "6:1512:1",
    "6:1520:1": "6:1512:1",
    "6:1521:1": "6:1515:1",
    "6:1522:1": "6:1516:1",
    "6:1523:1": "6:1517:1",
}
EXPECTED_RUNTIME_GAPS = {
    1485: ("025032", "025132", "0232"),
    1486: ("025032", "025132", "0232"),
    1487: ("025032", "025132"),
    1488: ("025032", "025132"),
    1489: ("025032", "025132"),
    1490: ("025032", "025132"),
    1491: ("025032", "025132", "0232"),
    1492: ("025032", "025132", "0232"),
    1493: ("025032", "025132", "0232"),
    1494: ("025032", "025132", "0232"),
    1514: ("025032",),
    1518: ("025032", "023D"),
    1520: ("025032", "023D"),
    1521: ("025032",),
    1522: ("025032",),
    1523: ("025032",),
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "8AA3015CFD717C2A9096EB994CA56C86C05B8ABC5059AFAF3DEE65E45EECE605"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "4EB798C8FAAEC6E061B63B7436865DE180F04759C5A250229DD03F45FA2B3C73"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "91EF1593C186E6A35867F72F1CD466223737A1539A5B946E84C71CDBD085ADFD"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "EA694AB0B9BB004BAE8C1B50F639CC14A4CCC586AADA549C8881CDAE180B78C4"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "2DF3D048DEFF1DD7AAE2FDF028AE65E23DE5C67619709A975E02E76426E46C92"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "AE027F6799E9FE5D921A74B57A978F3855F87137D60751E119B5E1DFE355BE21"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "278D89BBF548AC8C3E7D5BB25557B2D465BCCF60CBFE81AFBC8CEA6E72FABA73"
)
EXPECTED_BOUNDARY_SHA256 = (
    "5BD06B6383B2EBF18D1445DD764DC23C5F92E762D93699A8DE8E9989B82A8BEF"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "6F7B1AD863A1BC43F9B98BBB2B98B4DB4D968DE2C28291EC0C81E24E52A2CB34"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "C8BCB971014E00E6955816C6FF7D7380D6F3F8B3C44B6855DDEF4E67FAF606CA"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "16D801AA5294939229F5E59AF0736C14F8C64BC30DE70628076A3F64879C8A13"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "F3D27B6208ACC78D229A423AD0CBE2386C9C9D442EFA4F05C697AE697324D669"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "C97776FDF517F7039077C6F5A8C570D4267E8A29F47DB445472BE381C9E07D21"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "FDF278E76CDA336732FF5174C0299012A2D3A840816433A893BEA13E79E293FB"
)
EXPECTED_CANDIDATE_SHA256 = (
    "7F40CA1F6A713B1654A4DD6F7090AB38F95BD0A89A6B64C1EBF22C04520F1CF3"
)
EXPECTED_CHANGED_LITERAL_COUNT = 19

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "translations pin particles, diplomatic terminology and register "
    "where present; one Base particle donor is contextually expanded to "
    "make the two-faction subject explicit within the protected PK outer-"
    "whitespace and line-count contract; the PK-only siege fragment "
    "uses a visible dash before its single dynamic target; exact-reuse "
    "prefill and all available predecessor decisions are validated and "
    "excluded; faction-pair, month-number, indefinite-truce, imperial-"
    "peace, alliance, reinforcement, diplomatic-stance and goodwill-stop "
    "assemblies, historical terms, adjacent records, protected signatures, "
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
    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 48:
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
            b"\x02" in value
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
    if actual_dynamic != DYNAMIC_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic classification drifted"
        )
    for record_id, source, current in gaps:
        expected_runtime = EXPECTED_RUNTIME_GAPS[record_id]
        actual_source_runtime = tuple(
            value for value in source if value.startswith("02")
        )
        actual_current_runtime = tuple(
            value for value in current if value.startswith("02")
        )
        if (
            actual_source_runtime != expected_runtime
            or actual_current_runtime != expected_runtime
            or source != current
        ):
            raise RuntimeError(
                f"segment {SEGMENT} runtime gap drifted: "
                f"{record_id}"
            )


def assert_base_and_prefill_context(
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
        if coordinate == "6:1491:1":
            expected_translation = " 양측이\n서로 "
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
        required_terms = (
            ("정전",)
            if record_id <= 1488
            else (
                ("칙명", "강화")
                if record_id <= 1490
                else (
                    ("동맹",)
                    if record_id <= 1494
                    else (
                        ("공성", "원군", "연장")
                        if record_id == 1514
                        else (
                            ("외교 자세", "변경")
                            if record_id in (1518, 1520)
                            else ("친선", "중지")
                        )
                    )
                )
            )
        )
        if not all(term in joined for term in required_terms):
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
    if record_id == 1485:
        return "fixed_month_truce"
    if record_id == 1486:
        return "extended_truce"
    if record_id in (1487, 1488):
        return "indefinite_truce"
    if record_id in (1489, 1490):
        return "imperial_peace"
    if record_id in (1491, 1493):
        return "fixed_month_alliance"
    if record_id in (1492, 1494):
        return "extended_alliance"
    if record_id == 1514:
        return "siege_reinforcement_extension"
    if record_id in (1518, 1520):
        return "diplomatic_stance_change"
    return "goodwill_stop"


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
        or len(TARGET_COORDINATES) != 19
        or sum(
            "—" in translation
            for translation in TRANSLATIONS.values()
        )
        != 1
        or "—" not in TRANSLATIONS["6:1514:0"]
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
    source_runtime = tuple(
        value.hex().upper()
        for value in source_gaps
        if b"\x02" in value
    )
    current_runtime = tuple(
        value.hex().upper()
        for value in current_gaps
        if b"\x02" in value
    )
    expected = EXPECTED_RUNTIME_GAPS[record_id]
    if source_runtime != expected or current_runtime != expected:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic controls drifted: "
            f"{record_id}"
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
        "source_current_runtime_gap_equal": True,
        "runtime_category": runtime_category(record_id),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "particle_and_possessive_policy_reviewed": True,
        "single_name_visible_boundary_inserted":
        record_id == 1514,
        "month_or_stance_operand_reviewed":
        record_id in {
            1485,
            1486,
            1491,
            1492,
            1493,
            1494,
            1518,
            1520,
        },
        "prefill_companions_reviewed": True,
        "base_semantic_donor_reviewed":
        record_id != 1514,
        "base_runtime_state_inherited": False,
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
    assert_base_and_prefill_context(records_by_label)
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
                "diplomatic_term_review": True,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_record_literals_reviewed": True,
                "prefill_companions_reviewed": True,
                "runtime_category": runtime_category(record_id),
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES.get(coordinate),
                "base_translation_shape_adapted":
                coordinate == "6:1491:1",
                "pk_only_manual_translation":
                coordinate == "6:1514:0",
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
    category_counts = Counter(
        str(row["runtime_category"]) for row in rows
    )
    if (
        len(rows) != 19
        or len(validated) != 19
        or counts != Counter({"runtime_fragment_pending": 19})
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
                "segment": "pk_msggame_B022_S1084",
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
                "exact_reuse_prefill_count": 48,
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
                "pk_only_siege_fragment_reviewed": True,
                "runtime_boundary_types_distinguished": True,
                "prefill_companions_guarded": True,
                "complete_record_assembly_guarded": True,
                "runtime_operands_guarded": True,
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
