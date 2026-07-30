#!/usr/bin/env python3
"""Build source-redacted PK B044 segment 1143 residual decisions."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch043_segment1140.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B044_S1143.private.v1.jsonl"
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
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B044_S1144.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B044_S1145.private.v1.jsonl",
)

SEGMENT = 1143
QUEUE_BATCH_ID = "pk_msggame-B044"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4263:0",
    "6:4264:0",
    "6:4265:0",
    "6:4266:0",
    "6:4267:0",
    "6:4268:0",
    "6:4269:0",
    "6:4270:0",
    "6:4270:1",
    "6:4270:2",
    "6:4271:0",
    "6:4271:1",
    "6:4271:2",
    "6:4272:0",
    "6:4272:1",
    "6:4272:2",
    "6:4273:0",
    "6:4273:1",
    "6:4273:2",
    "6:4274:0",
    "6:4274:1",
    "6:4274:2",
    "6:4275:0",
    "6:4275:1",
    "6:4275:2",
    "6:4276:0",
    "6:4276:1",
    "6:4276:2",
    "6:4277:0",
    "6:4277:1",
    "6:4277:2",
    "6:4278:0",
    "6:4279:0",
    "6:4280:0",
    "6:4281:0",
    "6:4282:0",
    "6:4283:0",
    "6:4283:1",
    "6:4284:0",
    "6:4285:0",
    "6:4285:2",
    "6:4286:1",
    "6:4289:0",
    "6:4290:0",
    "6:4290:2",
    "6:4291:0",
    "6:4291:2",
    "6:4292:0",
    "6:4292:2",
    "6:4293:0",
    "6:4294:0",
    "6:4294:2",
    "6:4295:0",
    "6:4295:2",
    "6:4296:0",
    "6:4296:2",
    "6:4297:0",
    "6:4297:2",
    "6:4298:0",
    "6:4298:1",
    "6:4298:2",
    "6:4298:3",
    "6:4298:4",
    "6:4298:5",
    "6:4298:6",
    "6:4299:0",
    "6:4299:1",
)
TRANSLATIONS = {
    "6:4263:0": "무",
    "6:4264:0": "지",
    "6:4265:0": "정",
    "6:4266:0": "통",
    "6:4267:0": "무",
    "6:4268:0": "지",
    "6:4269:0": "정",
    "6:4270:0": "통",
    "6:4270:1": "(",
    "6:4270:2": ")",
    "6:4271:0": "무",
    "6:4271:1": "(",
    "6:4271:2": ")",
    "6:4272:0": "지",
    "6:4272:1": "(",
    "6:4272:2": ")",
    "6:4273:0": "정",
    "6:4273:1": "(",
    "6:4273:2": ")",
    "6:4274:0": "통",
    "6:4274:1": "(+",
    "6:4274:2": ")",
    "6:4275:0": "무",
    "6:4275:1": "(+",
    "6:4275:2": ")",
    "6:4276:0": "지",
    "6:4276:1": "(+",
    "6:4276:2": ")",
    "6:4277:0": "정",
    "6:4277:1": "(+",
    "6:4277:2": ")",
    "6:4278:0": "통",
    "6:4279:0": "무",
    "6:4280:0": "지",
    "6:4281:0": "정",
    "6:4282:0": "+",
    "6:4283:0": "+",
    "6:4283:1": "％",
    "6:4284:0": "+",
    "6:4285:0": "+",
    "6:4285:2": "+",
    "6:4286:1": "+",
    "6:4289:0": "+",
    "6:4290:0": "+",
    "6:4290:2": "+",
    "6:4291:0": "+",
    "6:4291:2": "+",
    "6:4292:0": "+",
    "6:4292:2": "+",
    "6:4293:0": "+",
    "6:4294:0": "+",
    "6:4294:2": "+",
    "6:4295:0": "+",
    "6:4295:2": "+",
    "6:4296:0": "+",
    "6:4296:2": "+",
    "6:4297:0": "+",
    "6:4297:2": "+",
    "6:4298:0": "(",
    "6:4298:1": "㊥",
    "6:4298:2": "+",
    "6:4298:3": "/월 ",
    "6:4298:4": "㊨",
    "6:4298:5": "+",
    "6:4298:6": ")",
    "6:4299:0": "\n(각",
    "6:4299:1": "㊥",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    *range(4263, 4287),
    *range(4289, 4300),
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    **{record_id: 1 for record_id in range(4263, 4270)},
    **{record_id: 3 for record_id in range(4270, 4278)},
    **{record_id: 1 for record_id in range(4278, 4283)},
    4283: 2,
    4284: 2,
    4285: 3,
    4286: 2,
    4289: 1,
    4290: 3,
    4291: 3,
    4292: 3,
    4293: 1,
    4294: 3,
    4295: 3,
    4296: 3,
    4297: 3,
    4298: 7,
    4299: 9,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 30
    for record_id in TARGET_RECORD_IDS
}
BASE_DONOR_COORDINATES = {
    coordinate: (
        f"{BLOCK_ID}:{coordinate_key_record - 30}:"
        f"{coordinate_key_literal}",
    )
    for coordinate in TARGET_COORDINATES
    for _, coordinate_key_record, coordinate_key_literal in (
        (tuple(int(part) for part in coordinate.split(":"))),
    )
}
CONTEXT_RECORD_IDS = tuple(range(4260, 4303))
BOUNDARY_RECORD_IDS = (
    4260,
    4261,
    4262,
    4300,
    4301,
    4302,
)
SPEAKER_STYLE = {
    record_id: "speaker_independent_runtime_ui_stat_fragment"
    for record_id in TARGET_RECORD_IDS
}
TERMINOLOGY_POLICY = (
    ("leadership_stat_abbreviation", "통"),
    ("valor_stat_abbreviation", "무"),
    ("intelligence_stat_abbreviation", "지"),
    ("politics_stat_abbreviation", "정"),
    ("monthly_unit", "월"),
    ("each_prefix", "각"),
    ("control_status", "장악"),
    ("engine_circled_glyphs", "㊥/㊨ 그대로 보존"),
    ("numeric_operators", "괄호·부호·전각 퍼센트 그대로 보존"),
)
BASIS = (
    "순정 PK 원문과 PC 영어·간체·번체의 완전 레코드 문맥을 "
    "수동 대조하고, raw-exact Base 완료 번역을 semantic donor로 "
    "검증했다. 간결한 능력치 약칭과 엔진 기호를 보존했으며 PK의 "
    "런타임·VM 검증 상태는 승계하지 않았다."
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017C"
    "CEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E16078296"
    "35AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A"
    "67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA8"
    "28FA4794509454263170E82ABA3600CF"
)
EXPECTED_CHANGED_LITERAL_COUNT = 5

EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "A8F5DAA3CC50D65FAAF50AAB7AEEA95E"
    "ACC6A2A58B720A1D3EAA4157A37E5179"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "65F1C3FD4CA1A6E7EA2642AC325AE643"
    "CCA7D9D99D09B3C52910C61C3913747B"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5"
    "ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5"
    "ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "65F1C3FD4CA1A6E7EA2642AC325AE643"
    "CCA7D9D99D09B3C52910C61C3913747B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "5E92E11AEC1BC2730CF091857844BF7BB"
    "723A055B8145FC0A11E9E9C942703C3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "882139271990A514161D4F37B65FD358"
    "4BF843A91B4DFCAB61141F22F1C36376"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "5D0805B89A3D96454DD8E171AF15B84A"
    "B384D61E5B8C17C4B6D3370CEF98F68B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "96F1CB6161F5BB5FB7077977F1C3628E"
    "CD7A61FFA6DAC3813532E164507FB375"
)
EXPECTED_BOUNDARY_SHA256 = (
    "218C940971844A4E24755644583CF1C53"
    "E482707497A338AC70EE19A8969D4DF"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "354C2E3AF3D525AACEA0EB012F54E852"
    "C78BF71C534F06CFE6F3D7FA43394882"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "55F2C1A31FAD5A9061EC3BCE957996A6"
    "EE9934A23F6E0A1462EBCDDCDA8EBFFC"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "577EA486E0F456DC0D1D58017116A582"
    "6CCBD4DAC9BFF496F6A72D8F5CD108B0"
)
EXPECTED_CALL_CONTRACT_SHA256 = (
    "C0E014658A4C97E531B9D171BC61A6D9"
    "9C106013F5CDD4F0C54176976E9E4BB1"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "D00DAF58DE20BAA11A3F5FA4072CECFC"
    "053755E051167C5296F93406F258DF8A"
)
EXPECTED_CANDIDATE_INTEGRITY_SHA256 = (
    "5EA98F38A15A88E29F2550CABBFBA53D"
    "517BF1569B0C9168F20416DF86E5ADAF"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "7088D7B01B10298AF6C8587F41C12B0A"
    "FFAA917846632E1FC3657151544E79DB"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "182239E6A420688344D26BE07E2D8D97"
    "79979841126BEF066E9E63C575FE1D75"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "66E53854209221B5ABD76BDB243E4368"
    "A568D322DE75E930F5F5A5837D2B7FBF"
)
EXPECTED_CANDIDATE_SHA256 = (
    "110B5CB4C983BF12108E2D964FC1F675"
    "F82CB8AC5EDAA40D449BD4B9CB94E054"
)

DISCOVERED_PINS: dict[str, str] = {}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_module(
    "pc_dialogue_full_retranslation_v0150_pk_s1143_template",
    TEMPLATE_PATH,
)
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
runtime_controls = TEMPLATE.runtime_controls


def patch_template_globals(
    *,
    candidate_sha256: str | None = None,
) -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
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
        candidate_sha256 or EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "DISCOVERED_PINS": DISCOVERED_PINS,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()


def guarded_digest(
    label: str,
    value: Any,
    expected: str,
) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def all_existing_decisions(
    prepared: Any,
) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    owners: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared, path, require_complete=False
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
            previous = owners.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )
            existing[coordinate] = row
    return existing


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} source input drifted")
    ENGINE.validate_decisions(
        prepared, PREFILL, require_complete=False
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
        len(queue_rows) != 104
        or len(visible) != 200
        or visible[0] != "6:4263:0"
        or visible[-1] != "6:4369:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue universe drifted")
    guarded_digest(
        "EXPECTED_QUEUE_UNIVERSE_SHA256",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice != TARGET_COORDINATES
        or queue_slice[0] != "6:4263:0"
        or queue_slice[-1] != "6:4299:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "EXPECTED_QUEUE_SLICE_SHA256",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if prefilled:
        raise RuntimeError(f"segment {SEGMENT} prefill drifted")
    guarded_digest(
        "EXPECTED_PREFILLED_COORDINATE_SHA256",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    guarded_digest(
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256",
        (),
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing = all_existing_decisions(prepared)
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual drifted: {len(residual)}"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared, path, require_complete=False
            )
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_context_contracts(
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
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
            label,
            record_id,
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
        for record_id in TARGET_RECORD_IDS
    )
    boundaries = tuple(
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
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
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
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        (
            "EXPECTED_SOURCE_TARGET_SHA256",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "EXPECTED_CURRENT_TARGET_SHA256",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "EXPECTED_CONTEXT_CORPUS_SHA256",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "EXPECTED_GAP_CONTRACT_SHA256",
            gaps,
            EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "EXPECTED_BOUNDARY_SHA256",
            boundaries,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "EXPECTED_RUNTIME_CONTROL_SHA256",
            controls,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    for record_id in TARGET_RECORD_IDS:
        source = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        current = records_by_label["current"][
            (BLOCK_ID, record_id)
        ]
        if (
            gap_bytes(source) != gap_bytes(current)
            or runtime_controls(source)
            != runtime_controls(current)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source/current runtime drifted: "
                f"{record_id}"
            )


def base_row_is_approved(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") in ("verified", "not_required")
    )


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} Base input drifted")
    base_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_PROMOTED)
    }
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        pk_key = (BLOCK_ID, record_id)
        base_record_id = BASE_RECORD_MAPPING[record_id]
        base_key = (BLOCK_ID, base_record_id)
        pk_record = records_by_label["jp"][pk_key]
        base_record = base_source[base_key]
        pk_literals = literal_texts(
            records_by_label["jp"], pk_key
        )
        current_literals = literal_texts(
            records_by_label["current"], pk_key
        )
        base_literals = literal_texts(base_source, base_key)
        base_current_literals = literal_texts(
            base_current, base_key
        )
        if (
            len(pk_literals) != EXPECTED_ARITY[record_id]
            or pk_record.data != base_record.data
            or pk_literals != base_literals
        ):
            raise RuntimeError(
                f"segment {SEGMENT} raw-exact Base drifted: "
                f"{record_id}"
            )
        owners: list[str] = []
        translations: list[str] = []
        donor_values: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = (
                f"{BLOCK_ID}:{record_id}:{literal_id}"
            )
            donor = (
                f"{BLOCK_ID}:{base_record_id}:{literal_id}"
            )
            row = base_rows.get(donor)
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                if (
                    not base_row_is_approved(row)
                    or actual != str(row["translation"])
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} Base target drifted: "
                        f"{coordinate}"
                    )
                owners.append("target")
                seen_target.add(coordinate)
                donor_value = str(row["translation"])
                base_evidence.append(
                    (
                        coordinate,
                        donor,
                        sha256_bytes(pk_record.data),
                        sha256_bytes(base_record.data),
                        pk_literals[literal_id],
                        current_literals[literal_id],
                        base_current_literals[literal_id],
                        donor_value,
                        str(row["runtime_review"]),
                    )
                )
            else:
                actual = current_literals[literal_id]
                owners.append("reviewed_untouched_companion")
                if base_row_is_approved(row):
                    assert row is not None
                    donor_value = str(row["translation"])
                    if actual != donor_value:
                        raise RuntimeError(
                            f"segment {SEGMENT} companion donor "
                            f"drifted: {coordinate}"
                        )
                else:
                    donor_value = base_current_literals[literal_id]
                    if (
                        actual != donor_value
                        or actual != pk_literals[literal_id]
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} invisible companion "
                            f"drifted: {coordinate}"
                        )
            translations.append(actual)
            donor_values.append(donor_value)
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(donor_values),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(pk_record)
                ),
                runtime_controls(pk_record),
            )
        )
    if seen_target != set(TARGET_COORDINATES):
        raise RuntimeError(
            f"segment {SEGMENT} assembly ownership drifted"
        )
    guarded_digest(
        "EXPECTED_BASE_CONTEXT_SHA256",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def assert_runtime_and_semantics(
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> None:
    guarded_digest(
        "EXPECTED_TARGET_COORDINATE_SHA256",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TRANSLATION_POLICY_SHA256",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "EXPECTED_SPEAKER_STYLE_SHA256",
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TERMINOLOGY_POLICY_SHA256",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or len(TRANSLATIONS) != 67
        or TRANSLATIONS["6:4265:0"] != "정"
        or TRANSLATIONS["6:4283:1"] != "％"
        or TRANSLATIONS["6:4298:3"] != "/월 "
        or TRANSLATIONS["6:4299:0"] != "\n(각"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    call_evidence: list[tuple[Any, ...]] = []
    tokenized_record_count = 0
    for record_id in TARGET_RECORD_IDS:
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        current_record = records_by_label["current"][
            (BLOCK_ID, record_id)
        ]
        source_controls = runtime_controls(source_record)
        current_controls = runtime_controls(current_record)
        if (
            source_controls != current_controls
            or source_controls[0]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} direct-call contract drifted: "
                f"{record_id}"
            )
        if source_controls[1]:
            tokenized_record_count += 1
        call_evidence.append(
            (
                record_id,
                source_controls,
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(source_record)
                ),
            )
        )
    guarded_digest(
        "EXPECTED_CALL_CONTRACT_SHA256",
        tuple(call_evidence),
        EXPECTED_CALL_CONTRACT_SHA256,
    )
    conflict_summary = (
        len(TARGET_RECORD_IDS),
        tokenized_record_count,
        0,
        "no_direct_call_roots",
        "inline_runtime_ui_tokens_preserved",
        "base_runtime_and_vm_state_not_inherited",
        "all_rows_remain_runtime_pending",
    )
    guarded_digest(
        "EXPECTED_RUNTIME_CONFLICT_SHA256",
        conflict_summary,
        EXPECTED_RUNTIME_CONFLICT_SHA256,
    )
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(
            coordinate
        )
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n")
            != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> tuple[bytes, str, int]:
    updates = {
        coordinate_key(coordinate): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    probe = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        updates,
    )
    probe_sha256 = sha256_bytes(probe)
    effective_expected = EXPECTED_CANDIDATE_SHA256
    if effective_expected == "TO_PIN":
        DISCOVERED_PINS[
            "EXPECTED_CANDIDATE_SHA256"
        ] = probe_sha256
        effective_expected = probe_sha256
    patch_template_globals(candidate_sha256=effective_expected)
    candidate, candidate_sha256, changed = (
        TEMPLATE.build_candidate(prepared, records_by_label)
    )
    if (
        candidate != probe
        or candidate_sha256 != probe_sha256
        or changed != EXPECTED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate reconstruction drifted"
        )
    return candidate, candidate_sha256, changed


def assert_candidate_integrity(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
    candidate: bytes,
) -> None:
    current_blob = prepared.resources["pk_msggame"].current_blob
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    target_keys = {
        coordinate_key(coordinate)
        for coordinate in TARGET_COORDINATES
    }
    outside_count = 0
    target_evidence: list[tuple[Any, ...]] = []
    for key, current_record in current_records.items():
        candidate_record = candidate_records[key]
        if key[1] not in TARGET_RECORD_IDS:
            if candidate_record.data != current_record.data:
                raise RuntimeError(
                    f"segment {SEGMENT} outside-scope record changed: "
                    f"{key}"
                )
            outside_count += 1
            continue
        current_literals = literal_texts(current_records, key)
        candidate_literals = literal_texts(candidate_records, key)
        if gap_bytes(current_record) != gap_bytes(candidate_record):
            raise RuntimeError(
                f"segment {SEGMENT} target gap changed: {key}"
            )
        for literal_id, current_text in enumerate(
            current_literals
        ):
            coordinate = (key[0], key[1], literal_id)
            if (
                coordinate not in target_keys
                and candidate_literals[literal_id] != current_text
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} companion changed: "
                    f"{coordinate}"
                )
        target_evidence.append(
            (
                key,
                sha256_bytes(current_record.data),
                sha256_bytes(candidate_record.data),
                current_literals,
                candidate_literals,
            )
        )
    reverse_updates = {
        coordinate_key(coordinate):
        literal_texts(
            records_by_label["current"],
            coordinate_key(coordinate)[:2],
        )[coordinate_key(coordinate)[2]]
        for coordinate in TARGET_COORDINATES
    }
    reversed_blob = ENGINE.rebuild_packed_with_literals(
        candidate, reverse_updates
    )
    if reversed_blob != current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay drifted"
        )
    integrity = (
        outside_count,
        tuple(target_evidence),
        sha256_bytes(reversed_blob),
        len(target_keys),
    )
    guarded_digest(
        "EXPECTED_CANDIDATE_INTEGRITY_SHA256",
        integrity,
        EXPECTED_CANDIDATE_INTEGRITY_SHA256,
    )


def runtime_evidence(
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    source_controls = runtime_controls(source_record)
    current_controls = runtime_controls(current_record)
    if (
        source_controls != current_controls
        or gap_bytes(source_record) != gap_bytes(current_record)
        or source_controls[0]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
        )
    return {
        "runtime_category":
        "pk_runtime_ui_fragment_raw_exact_base_semantic_donor",
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
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal": True,
        "base_record_coordinate":
        f"{BLOCK_ID}:{BASE_RECORD_MAPPING[record_id]}",
        "base_match_kind": "raw_exact_semantic_donor",
        "complete_record_assembly_reviewed": True,
        "all_same_record_companions_reviewed": True,
        "all_slice_prefill_rows_reviewed": True,
        "manual_pc_english_simplified_traditional_review": True,
        "live_pk_call_graphs_reviewed": False,
        "no_direct_call_roots_verified": True,
        "runtime_morphology_conflict_detected": False,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
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
    patch_template_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(
        prepared
    )
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_and_complete_assembly(
        prepared, records_by_label
    )
    assert_runtime_and_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared, records_by_label
    )
    assert_candidate_integrity(
        prepared, records_by_label, candidate
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(
            coordinate
        )
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
                "optional_neighbor_outputs_validated_if_present":
                True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "same_record_non_target_companions_reviewed": True,
                "all_slice_prefill_rows_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate":
                BASE_DONOR_COORDINATES[coordinate][0],
                "base_context_is_automatic_reuse": False,
                "base_match_kind":
                "raw_exact_semantic_donor",
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "speaker_style": SPEAKER_STYLE[record_id],
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records_by_label, record_id),
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
    tampered_policy = dict(TRANSLATIONS)
    tampered_policy["6:4263:0"] += "X"
    if (
        canonical_sha256(tuple(tampered_policy.items()))
        == EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} policy tamper accepted"
        )
    tampered_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        {
            coordinate_key(coordinate): translation
            for coordinate, translation
            in tampered_policy.items()
        },
    )
    if (
        tampered_candidate == candidate
        or sha256_bytes(tampered_candidate)
        == EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate tamper accepted"
        )
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="s1143_tamper_",
        dir=OUTPUT.parent,
    ) as temporary:
        tampered_path = (
            Path(temporary) / "tampered.private.v1.jsonl"
        )
        ENGINE.atomic_write(
            tampered_path, ENGINE.jsonl(tampered_rows)
        )
        try:
            ENGINE.validate_decisions(
                prepared,
                tampered_path,
                require_complete=False,
            )
        except (RuntimeError, ValueError):
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} decision tamper accepted"
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
                    "changed_literal_count": changed,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    resource = prepared.resources["pk_msggame"]
    steam_path = resource.current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: "
            f"{steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 67
        or len(validated) != 67
        or counts
        != Counter({"runtime_fragment_pending": 67})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["line_count_preserved"] is not True
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
    if sha256_bytes(steam_path.read_bytes()) != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B044_S1143",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": TARGET_COORDINATES[0],
                "slice_last_coordinate": TARGET_COORDINATES[-1],
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 0,
                "residual_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(TARGET_RECORD_IDS),
                "direct_call_root_count": 0,
                "optional_neighbors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "call_contract_sha256":
                EXPECTED_CALL_CONTRACT_SHA256,
                "runtime_conflict_sha256":
                EXPECTED_RUNTIME_CONFLICT_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "zero_prefill_guarded": True,
                "manual_pk_jp_pc_en_sc_tc_review": True,
                "complete_multi_literal_records_guarded": True,
                "raw_exact_base_semantic_donors_guarded": True,
                "live_pk_direct_calls_verified_absent": True,
                "runtime_tokens_and_gaps_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_promotion_authorized": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
