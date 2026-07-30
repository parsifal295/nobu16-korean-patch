#!/usr/bin/env python3
"""Build source-redacted PK B034 segment 1115 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch034_segment1114.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B034_S1115.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B033_S1110.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B033_S1111.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B033_S1112.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B034_S1113.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B034_S1114.private.v1.jsonl",
)

SEGMENT = 1115
QUEUE_BATCH_ID = "pk_msggame-B034"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:3281:0",
    "6:3283:0",
    "6:3286:1",
    "6:3325:0",
)
TRANSLATIONS = {
    "6:3281:0": "잘 알겠소\n",
    "6:3283:0": "잘 알겠소\n",
    "6:3286:1": " 공략쯤은 일도 아니겠지",
    "6:3325:0": "금전이",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (3281, 3283, 3286, 3325)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (
    3276,
    3277,
    3280,
    3282,
    3284,
    3285,
    3287,
    3324,
    3326,
    3331,
    3332,
)
BASE_RECORD_MAPPING = {
    3281: 3274,
    3283: 3276,
    3286: 3279,
    3325: 3318,
}
BASE_CONTEXT_REFERENCES = {
    "6:3281:0": "6:3274:0",
    "6:3283:0": "6:3276:0",
    "6:3286:1": "6:3279:1",
    "6:3325:0": "6:3318:0",
}
PREFILL_COMPANION_COORDINATES = (
    "6:3281:1",
    "6:3283:1",
    "6:3286:0",
    "6:3325:1",
)
BOUNDARY_PREFILL_COORDINATES = ("6:3276:1",)
EXPECTED_GAPS_BY_RECORD = {
    3281: ("", "026432", "050505"),
    3283: ("", "026432", "050505"),
    3286: ("", "026432", "050505"),
    3325: ("", "0232", "050505"),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3281: ((), ("026432",)),
    3283: ((), ("026432",)),
    3286: ((), ("026432",)),
    3325: ((), ("0232",)),
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
EXPECTED_TARGET_COORDINATE_SHA256 = "4C8CE57D78547A3D1459C9614BE32609B3607F9B8DB16513052AF17CD80EC11A"
EXPECTED_QUEUE_SLICE_SHA256 = "AC528985FECC3DE86A44A7332849E9A68386B63F2CCA4E49326B8160780A2D87"
EXPECTED_PREFILLED_COORDINATE_SHA256 = "45ED36D28C61BA89BDC93F106BF3371CE4A44D75A61E120E44BDFD40672A6318"
EXPECTED_SOURCE_TARGET_SHA256 = "F735F87D215C9621B1A6358E68B03DEF7AA18272C81C7A1CCEFA1332523574D9"
EXPECTED_CURRENT_TARGET_SHA256 = "FEDEDE4A9A165685D06DB8B9EA5FA7D2683231196CB6C696EFEDF6DCA179017C"
EXPECTED_CONTEXT_CORPUS_SHA256 = "AB2A86B7D2D8D45981274D96D666E20C5CF6C8EBE3A8EA6F318BA005E6666C4B"
EXPECTED_GAP_CONTRACT_SHA256 = "12C3E509F4234BCE294661C9C3BEEDD6B8117C738A68725789156B2C783C5870"
EXPECTED_BOUNDARY_SHA256 = "24CFC3F58373EE8F48A6200583A6108F7E5D4CB19E75F8A663F7F7EE7D7F40BF"
EXPECTED_RUNTIME_OPERAND_SHA256 = "57E7D3636B4EDA51994B1211439DAD3CDD2794E29389F74841D2791599063717"
EXPECTED_DYNAMIC_RECORD_SHA256 = "CAE7E031DE8C51C69736974D40357A3FF3FEA94E76BF9E0FB16DB34D3AB88037"
EXPECTED_BASE_CONTEXT_SHA256 = "F3753BB26D470BCD44CACCA1E8BF67B1A64A85F9E0F1C7959E296CF19AEC98CA"
EXPECTED_PREFILL_COMPANION_SHA256 = "561BEE417166382481AE2F282E687F0E1FF8E636A75D26F741709E6FB393895C"
EXPECTED_BOUNDARY_PREFILL_SHA256 = "784BA228B7EB7D7DE721F563CA859A97E0718A7111B15BB7747F49282879F3DB"
EXPECTED_ASSEMBLY_POLICY_SHA256 = "A45E477C9DA2E76DC3CA5D2F42DE278A15501ABCB50840B4867136000A6D670C"
EXPECTED_TERMINOLOGY_POLICY_SHA256 = "13048F7735A80EC5A5264957E059541A4FC701959EB30373CE46B5A75F42CDDC"
EXPECTED_RUNTIME_CATEGORY_SHA256 = "650BD09BA398F344C27DDB76D84A9CB194ADCDCA7D02A8DC7873EE792D6CC209"
EXPECTED_TRANSLATION_POLICY_SHA256 = "1AB5EB6A8C3896865BD73097E81C1CD2A31A4961F00D8CFE268D7CDD1494C120"
EXPECTED_CANDIDATE_SHA256 = "38B48779410C9FA0093C96BCF06BA8EEB8957BB226835512BB450B19EC334751"
EXPECTED_CHANGED_LITERAL_COUNT = 3

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; four completed Base exact "
    "full-record donors pin castle protection, castle assault and money "
    "requirement semantics, historical register and speaker voice; the "
    "post-castle assault fragment adapts the Base possessive construction "
    "to the protected PK leading space with a natural Korean predicate, "
    "while the other three targets use completed Base wording; four "
    "same-record prefilled companions and the 3276 start-boundary prefill "
    "are guarded; all 62 prefilled queue rows and new B033/B034 "
    "predecessors are optional validated inputs rather than execution "
    "dependencies; full-record assembly, direct-call absence, castle and "
    "numeric tokens, adjacent records, historical terminology, protected "
    "outer spaces, line counts, bytecode gaps, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are guarded; "
    "Base runtime state is not inherited and all four PK targets remain "
    "runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1115_common",
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


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
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
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
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
        len(queue_rows) != 165
        or len(visible) != 200
        or visible[0] != "6:3167:0"
        or visible[-1] != "6:3331:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B034 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:3276:1"
        or queue_slice[-1] != "6:3331:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue bounds drifted"
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


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    direct_calls = tuple(
        int.from_bytes(value[2:6], "little")
        for value in gap_bytes(record)
        if value.startswith(b"\x01\x43")
    )
    inline_tokens = tuple(
        value.hex().upper()
        for value in gap_bytes(record)
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
            runtime_controls(
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
        if any(
            runtime_controls(
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
        or any(
            controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, controls in operand_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def assert_base_companions_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame")
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    for coordinate in TARGET_COORDINATES:
        pk_key = coordinate_key(coordinate)
        base_coordinate = BASE_CONTEXT_REFERENCES[coordinate]
        base_key = coordinate_key(base_coordinate)
        base_record_id = BASE_RECORD_MAPPING[pk_key[1]]
        pk_record = records_by_label["jp"][pk_key[:2]]
        base_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        base_current_record = base_current_records[
            (BLOCK_ID, base_record_id)
        ]
        base_row = base_rows[base_coordinate]
        base_companion_rows = tuple(
            base_rows[f"6:{base_record_id}:{literal_id}"]
            for literal_id in range(
                len(
                    literal_texts(
                        base_source_records,
                        (BLOCK_ID, base_record_id),
                    )
                )
            )
        )
        expected_translation = (
            " 공략쯤은 일도 아니겠지"
            if coordinate == "6:3286:1"
            else str(base_row["translation"])
        )
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                literal_texts(
                    records_by_label["jp"],
                    pk_key[:2],
                ),
                literal_texts(
                    base_source_records,
                    (BLOCK_ID, base_record_id),
                ),
                literal_texts(
                    base_current_records,
                    (BLOCK_ID, base_record_id),
                ),
                base_row.get("translation"),
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
                tuple(
                    (
                        row.get("translation"),
                        row.get("semantic_review"),
                        row.get("runtime_review"),
                    )
                    for row in base_companion_rows
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_current_record)
                ),
                runtime_controls(pk_record),
                runtime_controls(base_record),
                runtime_controls(base_current_record),
                expected_translation,
            )
        )
        if (
            base_evidence[-1][2] != base_evidence[-1][3]
            or TRANSLATIONS[coordinate] != expected_translation
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
            or any(
                semantic != "approved" or runtime != "verified"
                for _, semantic, runtime in base_evidence[-1][8]
            )
            or base_evidence[-1][9]
            != base_evidence[-1][10]
            or base_evidence[-1][10]
            != base_evidence[-1][11]
            or base_evidence[-1][12]
            != base_evidence[-1][13]
            or base_evidence[-1][13]
            != base_evidence[-1][14]
            or base_key[1] != base_record_id
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: "
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

    def prefill_evidence(
        coordinates: tuple[str, ...],
    ) -> tuple[tuple[Any, ...], ...]:
        return tuple(
            (
                coordinate,
                prefill_rows[coordinate].get("translation"),
                prefill_rows[coordinate].get("semantic_review"),
                prefill_rows[coordinate].get("runtime_review"),
                prefill_rows[coordinate].get("layout_review"),
                prefill_rows[coordinate].get(
                    "scope_classification"
                ),
                prefill_rows[coordinate].get(
                    "source_record_raw_sha256"
                ),
                prefill_rows[coordinate]
                .get("base_exact_reuse_prefill", {})
                .get("base_coordinate"),
            )
            for coordinate in coordinates
        )

    companion_evidence = prefill_evidence(
        PREFILL_COMPANION_COORDINATES
    )
    boundary_prefill_evidence = prefill_evidence(
        BOUNDARY_PREFILL_COORDINATES
    )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    guarded_digest(
        "boundary prefill",
        boundary_prefill_evidence,
        EXPECTED_BOUNDARY_PREFILL_SHA256,
    )
    if any(
        semantic != "approved"
        or runtime != "pending"
        or scope != "runtime_fragment_pending"
        for evidence in (
            companion_evidence,
            boundary_prefill_evidence,
        )
        for (
            _,
            _,
            semantic,
            runtime,
            _,
            scope,
            _,
            _,
        ) in evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill evidence drifted"
        )

    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        owners: list[str] = []
        translations: list[str] = []
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                owners.append("segment")
                translations.append(TRANSLATIONS[coordinate])
            elif coordinate in prefill_rows:
                owners.append("prefill")
                translations.append(
                    str(prefill_rows[coordinate]["translation"])
                )
            else:
                owners.append("current_outside_slice")
                translations.append(current_text)
        controls = runtime_controls(
            records_by_label["jp"][(BLOCK_ID, record_id)]
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                source_literals,
                current_literals,
                tuple(translations),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(
                        records_by_label["jp"][
                            (BLOCK_ID, record_id)
                        ]
                    )
                ),
                controls,
                runtime_category(record_id),
            )
        )
        joined = "\u241f".join(translations)
        expected_owners = {
            3281: ("segment", "prefill"),
            3283: ("segment", "prefill"),
            3286: ("prefill", "segment"),
            3325: ("segment", "prefill"),
        }[record_id]
        expected_terms = {
            3281: ("잘 알겠소", "우리가 지키겠소"),
            3283: ("잘 알겠소", "우리 병력으로 반드시 지켜 내겠소"),
            3286: ("용맹으로 이름난 귀 가문", " 공략쯤은 일도 아니겠지"),
            3325: ("금전이", "이상 필요합니다"),
        }[record_id]
        if (
            tuple(owners) != expected_owners
            or controls
            != EXPECTED_CONTROLS_BY_RECORD[record_id]
            or not all(term in joined for term in expected_terms)
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
    return {
        3281: "castle_protection_acceptance_formal",
        3283: "castle_protection_acceptance_old_male",
        3286: "castle_assault_capability_praise",
        3325: "numeric_money_requirement",
    }[record_id]


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
    terminology_policy = (
        ("castle_protection", "지키다/지켜 내다"),
        ("castle_assault", "공략"),
        ("military_renown", "용맹으로 이름나다"),
        ("troops", "병력"),
        ("money", "금전"),
        ("old_male_register", "알겠소"),
        ("capability_register", "일도 아니겠지"),
        ("requirement_register", "필요합니다"),
    )
    guarded_digest(
        "terminology policy",
        terminology_policy,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    runtime_categories = tuple(
        (
            record_id,
            runtime_category(record_id),
            "runtime_fragment_pending",
            "pending",
            "runtime_pending",
            False,
        )
        for record_id in TARGET_RECORD_IDS
    )
    guarded_digest(
        "runtime category",
        runtime_categories,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
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
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
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
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
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
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    source_controls = runtime_controls(source_record)
    current_controls = runtime_controls(current_record)
    if (
        source_controls
        != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic controls drifted"
        )
    return {
        "runtime_category": runtime_category(record_id),
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
        "source_current_runtime_gap_equal":
        gap_bytes(source_record) == gap_bytes(current_record),
        "complete_record_assembly_reviewed": True,
        "prefill_companion_reviewed": True,
        "start_boundary_prefill_reviewed": True,
        "protected_outer_space_preserved":
        record_id in (3281, 3283, 3286),
        "base_wording_contextually_adapted":
        record_id == 3286,
        "castle_token_reviewed":
        record_id in (3281, 3283, 3286),
        "numeric_token_reviewed": record_id == 3325,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
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
    assert_base_companions_and_assembly(
        prepared,
        records_by_label,
    )
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
                "optional_new_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companion_reviewed": True,
                "start_boundary_prefill_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_space_preserved":
                coordinate != "6:3325:0",
                "base_wording_contextually_adapted":
                coordinate == "6:3286:1",
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
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
        len(rows) != 4
        or len(validated) != 4
        or counts
        != Counter({"runtime_fragment_pending": 4})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
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
    steam_after = sha256_bytes(steam_path.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B034_S1115",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 62,
                "base_semantic_reference_count": len(rows),
                "prefill_companion_count": 4,
                "boundary_prefill_count": 1,
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
                "optional_new_outputs_only": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "start_boundary_prefill_guarded": True,
                "prefill_companions_guarded": True,
                "complete_two_literal_records_guarded": True,
                "direct_call_absence_guarded": True,
                "castle_and_numeric_tokens_guarded": True,
                "protected_outer_spaces_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
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
